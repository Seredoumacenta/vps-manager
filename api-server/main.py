#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🔐 VPS SSH/VPN MANAGEMENT API - WEB SOCKET SERVER
================================================================================
API sécurisée pour la gestion des comptes SSH/VPN avec expiration automatique
Hébergé sur VPS Ubuntu - Isolé du système principal
================================================================================
"""

import asyncio
import websockets
import json
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import ssl
import os

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VPSAccountManager:
    """Gestionnaire de comptes SSH/VPN sécurisé"""
    
    def __init__(self, db_path: str = "/var/lib/vps-manager/accounts.db"):
        self.db_path = db_path
        self.init_database()
        self.api_tokens = self.load_api_tokens()
    
    def init_database(self):
        """Initialise la base de données"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des comptes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                vpn_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                max_bandwidth_gb INTEGER DEFAULT 100,
                used_bandwidth_gb REAL DEFAULT 0,
                ip_address TEXT,
                ssh_port INTEGER DEFAULT 22,
                vpn_port INTEGER DEFAULT 1194,
                config_data TEXT
            )
        ''')
        
        # Table des sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                session_token TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        # Table des tokens API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de données initialisée")
    
    def load_api_tokens(self) -> Dict[str, Dict]:
        """Charge les tokens API depuis la base de données"""
        tokens = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT token_hash, name, expires_at FROM api_tokens WHERE is_active = 1"
            )
            for token_hash, name, expires_at in cursor.fetchall():
                tokens[token_hash] = {
                    'name': name,
                    'expires_at': expires_at
                }
            conn.close()
        except Exception as e:
            logger.error(f"Erreur chargement tokens API: {e}")
        
        return tokens
    
    def validate_api_token(self, token: str) -> bool:
        """Valide un token API"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash in self.api_tokens
    
    def create_account(self, duration_hours: int, client_ip: str = None) -> Dict[str, Any]:
        """Crée un nouveau compte SSH/VPN"""
        try:
            # Génération des identifiants
            username = self._generate_username()
            password = secrets.token_urlsafe(16)
            vpn_password = secrets.token_urlsafe(12)
            
            # Ports aléatoires pour sécurité
            ssh_port = secrets.choice([2222, 2223, 2224, 2225, 2226])
            vpn_port = secrets.choice([1194, 1195, 1196, 1197, 1198])
            
            # Calcul expiration
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=duration_hours)
            
            # Hash du mot de passe
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Configuration SSH
            ssh_config = {
                "username": username,
                "password": password,
                "port": ssh_port,
                "host": socket.gethostname(),
                "allowed_ips": ["0.0.0.0/0"],
                "max_sessions": 3,
                "idle_timeout": 300
            }
            
            # Configuration VPN (OpenVPN)
            vpn_config = self._generate_openvpn_config(username, vpn_password, vpn_port)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO accounts 
                (username, password_hash, vpn_password, expires_at, ip_address, ssh_port, vpn_port, config_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, 
                password_hash,
                vpn_password,
                expires_at.isoformat(),
                client_ip,
                ssh_port,
                vpn_port,
                json.dumps({
                    "ssh": ssh_config,
                    "vpn": vpn_config,
                    "created_at": created_at.isoformat()
                })
            ))
            
            account_id = cursor.lastrowid
            conn.commit()
            
            # Récupération des données
            cursor.execute(
                "SELECT * FROM accounts WHERE id = ?", 
                (account_id,)
            )
            account_data = cursor.fetchone()
            conn.close()
            
            return {
                "success": True,
                "account_id": account_id,
                "username": username,
                "password": password,
                "vpn_password": vpn_password,
                "ssh_port": ssh_port,
                "vpn_port": vpn_port,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "duration_hours": duration_hours,
                "ssh_config": ssh_config,
                "vpn_config": vpn_config
            }
            
        except Exception as e:
            logger.error(f"Erreur création compte: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_username(self) -> str:
        """Génère un nom d'utilisateur unique"""
        prefixes = ["vps", "ssh", "vpn", "user", "client", "node"]
        while True:
            username = f"{secrets.choice(prefixes)}_{secrets.token_hex(4)}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM accounts WHERE username = ?", (username,))
            exists = cursor.fetchone()
            conn.close()
            
            if not exists:
                return username
    
    def _generate_openvpn_config(self, username: str, password: str, port: int) -> Dict:
        """Génère une configuration OpenVPN"""
        config = f"""client
dev tun
proto udp
remote {socket.gethostname()} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA512
auth-nocache
tls-version-min 1.2
tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
verb 3
auth-user-pass
<ca>
-----BEGIN CERTIFICATE-----
{secrets.token_hex(128)}
-----END CERTIFICATE-----
</ca>
<cert>
-----BEGIN CERTIFICATE-----
{secrets.token_hex(128)}
-----END CERTIFICATE-----
</cert>
<key>
-----BEGIN PRIVATE KEY-----
{secrets.token_hex(128)}
-----END PRIVATE KEY-----
</key>
<tls-crypt>
-----BEGIN OpenVPN Static key V1-----
{secrets.token_hex(128)}
-----END OpenVPN Static key V1-----
</tls-crypt>
"""
        
        return {
            "config": config,
            "username": username,
            "password": password,
            "port": port,
            "server": socket.gethostname()
        }
    
    def validate_account(self, username: str, password: str) -> Dict[str, Any]:
        """Valide un compte utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, password_hash, expires_at, is_active 
                FROM accounts 
                WHERE username = ?
            ''', (username,))
            
            account = cursor.fetchone()
            
            if not account:
                return {"valid": False, "error": "Compte inexistant"}
            
            account_id, stored_hash, expires_at_str, is_active = account
            
            # Vérifier expiration
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                cursor.execute(
                    "UPDATE accounts SET is_active = 0 WHERE id = ?", 
                    (account_id,)
                )
                conn.commit()
                return {"valid": False, "error": "Compte expiré"}
            
            # Vérifier activité
            if not is_active:
                return {"valid": False, "error": "Compte désactivé"}
            
            # Vérifier mot de passe
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_hash != stored_hash:
                return {"valid": False, "error": "Mot de passe incorrect"}
            
            # Mettre à jour dernière utilisation
            cursor.execute('''
                UPDATE accounts 
                SET last_used = CURRENT_TIMESTAMP, 
                    usage_count = usage_count + 1 
                WHERE id = ?
            ''', (account_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "valid": True,
                "account_id": account_id,
                "expires_at": expires_at_str,
                "remaining_hours": int((expires_at - datetime.now()).total_seconds() / 3600)
            }
            
        except Exception as e:
            logger.error(f"Erreur validation compte: {e}")
            return {"valid": False, "error": str(e)}
    
    def get_account_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques des comptes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN datetime(expires_at) < datetime('now') THEN 1 ELSE 0 END) as expired,
                    SUM(usage_count) as total_connections,
                    SUM(used_bandwidth_gb) as total_bandwidth
                FROM accounts
            ''')
            
            stats = cursor.fetchone()
            conn.close()
            
            return {
                "total_accounts": stats[0],
                "active_accounts": stats[1],
                "expired_accounts": stats[2],
                "total_connections": stats[3],
                "total_bandwidth_gb": stats[4] or 0
            }
            
        except Exception as e:
            logger.error(f"Erreur stats: {e}")
            return {}

class WebSocketAPIServer:
    """Serveur WebSocket API sécurisé"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.account_manager = VPSAccountManager()
        self.clients = set()
    
    async def handler(self, websocket, path):
        """Gestionnaire de connexions WebSocket"""
        client_ip = websocket.remote_address[0]
        self.clients.add(websocket)
        
        try:
            async for message in self.clients:
                try:
                    data = json.loads(message)
                    response = await self.process_request(data, client_ip)
                    await websocket.send(json.dumps(response))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "error": "Invalid JSON format"
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client déconnecté: {client_ip}")
        finally:
            self.clients.remove(websocket)
    
    async def process_request(self, data: Dict, client_ip: str) -> Dict[str, Any]:
        """Traite une requête API"""
        action = data.get("action", "")
        api_token = data.get("api_token", "")
        
        # Validation token API
        if not self.account_manager.validate_api_token(api_token):
            return {"error": "Invalid API token"}
        
        if action == "create_account":
            duration = data.get("duration_hours", 24)
            result = self.account_manager.create_account(duration, client_ip)
            return result
            
        elif action == "validate_account":
            username = data.get("username", "")
            password = data.get("password", "")
            result = self.account_manager.validate_account(username, password)
            return result
            
        elif action == "get_stats":
            stats = self.account_manager.get_account_stats()
            return {"stats": stats}
            
        elif action == "ping":
            return {"status": "alive", "timestamp": datetime.now().isoformat()}
            
        else:
            return {"error": "Unknown action"}
    
    async def start(self):
        """Démarre le serveur WebSocket"""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # Configuration SSL (à adapter avec vos certificats)
        # ssl_context.load_cert_chain('cert.pem', 'key.pem')
        
        async with websockets.serve(
            self.handler, 
            self.host, 
            self.port
            # ssl=ssl_context  # Décommenter pour SSL
        ):
            logger.info(f"✅ Serveur WebSocket démarré sur {self.host}:{self.port}")
            logger.info(f"📊 Gestionnaire de comptes: {self.account_manager.db_path}")
            await asyncio.Future()  # Run forever
    
    def generate_api_token(self, name: str = "default", 
                          expires_days: int = 30) -> str:
        """Génère un nouveau token API"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        conn = sqlite3.connect(self.account_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO api_tokens (token_hash, name, expires_at)
            VALUES (?, ?, ?)
        ''', (token_hash, name, expires_at.isoformat()))
        conn.commit()
        conn.close()
        
        # Recharger les tokens
        self.account_manager.api_tokens = self.account_manager.load_api_tokens()
        
        logger.info(f"✅ Token API généré: {name}")
        return token

async def main():
    """Fonction principale"""
    server = WebSocketAPIServer()
    
    # Générer un token API par défaut si aucun n'existe
    if not server.account_manager.api_tokens:
        token = server.generate_api_token("admin", 365)
        print(f"\n🔐 TOKEN API ADMIN GÉNÉRÉ (sauvegardez-le):")
        print(f"   {token}")
        print(f"\n⚠️  Ce token ne sera plus affiché!")
    
    await server.start()

if __name__ == "__main__":
    import socket
    asyncio.run(main())
