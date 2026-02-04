#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🚀 VPS SSH/VPN PAYLOAD GENERATOR WITH WEB SOCKET API
================================================================================
Générateur de payloads connecté à l'API WebSocket du VPS
- Génération aléatoire de comptes via API
- Durée de validité configurable
- Encodage Base64/Base85 renforcé
- Configuration SSH/VPN prête à l'emploi
================================================================================
"""

import asyncio
import websockets
import json
import base64
import hashlib
import secrets
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import argparse
import re

class VPSPayloadGenerator:
    """Générateur de payloads connecté à l'API VPS"""
    
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token
        self.generated_payloads = []
        
    async def create_vps_account(self, duration_hours: int = 24) -> Dict[str, Any]:
        """Crée un compte via l'API WebSocket"""
        try:
            async with websockets.connect(self.api_url) as websocket:
                request = {
                    "action": "create_account",
                    "api_token": self.api_token,
                    "duration_hours": duration_hours
                }
                
                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get("success"):
                    return result
                else:
                    raise Exception(result.get("error", "Unknown error"))
                    
        except Exception as e:
            print(f"❌ Erreur création compte: {e}")
            return None
    
    def encode_payload(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Encode le payload avec multiples couches de sécurité"""
        # Conversion en JSON
        json_data = json.dumps(data, separators=(',', ':'))
        
        # Encodages multiples
        encodings = {
            "base64": base64.b64encode(json_data.encode()).decode('ascii'),
            "base85": base64.b85encode(json_data.encode()).decode('ascii'),
            "base64_url": base64.urlsafe_b64encode(json_data.encode()).decode('ascii'),
            "hex": json_data.encode().hex()
        }
        
        # Double encodage
        double_encoded = {}
        for name, encoded in encodings.items():
            double_encoded[f"{name}_double"] = base64.b85encode(
                base64.b64encode(encoded.encode())
            ).decode('ascii')
        
        return {**encodings, **double_encoded}
    
    def generate_ssh_config(self, account_data: Dict[str, Any]) -> str:
        """Génère une configuration SSH"""
        return f"""# SSH Configuration for {account_data['username']}
# Generated: {datetime.now().isoformat()}
# Expires: {account_data['expires_at']}

Host vps_{account_data['username']}
    HostName {socket.gethostname() if 'socket' in globals() else 'vps-server.com'}
    Port {account_data['ssh_port']}
    User {account_data['username']}
    PasswordAuthentication yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
    TCPKeepAlive yes
    Compression yes
    CompressionLevel 9
    
# Connection command:
# ssh {account_data['username']}@$(hostname) -p {account_data['ssh_port']}
# Password: {account_data['password']}

# For tunneling:
# ssh -D 1080 {account_data['username']}@$(hostname) -p {account_data['ssh_port']}
"""
    
    def generate_vpn_config(self, account_data: Dict[str, Any]) -> str:
        """Génère une configuration VPN"""
        vpn_config = account_data.get('vpn_config', {})
        
        config = f"""# OpenVPN Configuration for {account_data['username']}
# Server: {vpn_config.get('server', 'vps-server.com')}
# Port: {account_data['vpn_port']}
# Username: {account_data['username']}
# Password: {account_data['vpn_password']}
# Expires: {account_data['expires_at']}

{vpn_config.get('config', '')}
"""
        
        # Ajouter les identifiants dans le fichier
        config += f"\n# Authentication file (auth.txt):"
        config += f"\n{account_data['username']}"
        config += f"\n{account_data['vpn_password']}"
        
        return config
    
    def create_payload_package(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un package de payload complet"""
        # Données de base
        payload_data = {
            "account": {
                "username": account_data["username"],
                "password": account_data["password"],
                "vpn_password": account_data["vpn_password"],
                "ssh_port": account_data["ssh_port"],
                "vpn_port": account_data["vpn_port"],
                "created_at": account_data["created_at"],
                "expires_at": account_data["expires_at"],
                "duration_hours": account_data["duration_hours"]
            },
            "server": {
                "hostname": socket.gethostname() if 'socket' in globals() else 'vps-server.com',
                "api_url": self.api_url,
                "protocol": "ssh_v2/openvpn"
            },
            "security": {
                "signature": hashlib.sha256(
                    f"{account_data['username']}:{account_data['password']}:{int(time.time())}".encode()
                ).hexdigest(),
                "generated_at": datetime.now().isoformat()
            }
        }
        
        # Configurations
        ssh_config = self.generate_ssh_config(account_data)
        vpn_config = self.generate_vpn_config(account_data)
        
        # Encodages
        encoded_payloads = self.encode_payload(payload_data)
        
        return {
            "account_data": payload_data,
            "configs": {
                "ssh": ssh_config,
                "vpn": vpn_config,
                "ssh_b64": base64.b64encode(ssh_config.encode()).decode(),
                "vpn_b64": base64.b64encode(vpn_config.encode()).decode(),
                "ssh_b85": base64.b85encode(ssh_config.encode()).decode(),
                "vpn_b85": base64.b85encode(vpn_config.encode()).decode()
            },
            "encoded_payloads": encoded_payloads
        }
    
    async def generate_payloads(self, count: int = 1, 
                               duration_hours: int = 24) -> List[Dict[str, Any]]:
        """Génère plusieurs payloads"""
        print(f"\n🚀 Démarrage génération de {count} payloads...")
        print(f"⏱️  Durée de validité: {duration_hours} heures")
        print(f"🔗 API Server: {self.api_url}")
        print("=" * 60)
        
        all_payloads = []
        
        for i in range(1, count + 1):
            print(f"\n[{i}/{count}] Création du compte #{i}...")
            
            try:
                # Création du compte via API
                account_data = await self.create_vps_account(duration_hours)
                
                if not account_data:
                    print(f"   ❌ Échec création compte")
                    continue
                
                # Création du package de payload
                package = self.create_payload_package(account_data)
                all_payloads.append(package)
                
                # Sauvegarde des fichiers
                self._save_payload_files(package, i)
                
                print(f"   ✅ Compte créé: {account_data['username']}")
                print(f"   🔐 SSH: {account_data['password'][:12]}...")
                print(f"   🔒 VPN: {account_data['vpn_password'][:12]}...")
                print(f"   ⏱️  Expire: {account_data['expires_at'].split('T')[0]}")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        self.generated_payloads = all_payloads
        return all_payloads
    
    def _save_payload_files(self, package: Dict[str, Any], index: int):
        """Sauvegarde les fichiers de payload"""
        username = package['account_data']['account']['username']
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', username)
        
        # Répertoire de sortie
        output_dir = f"vps_payloads/{safe_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Données du compte
        with open(f"{output_dir}/account_data.json", 'w') as f:
            json.dump(package['account_data'], f, indent=2)
        
        # 2. Configurations
        with open(f"{output_dir}/ssh_config", 'w') as f:
            f.write(package['configs']['ssh'])
        
        with open(f"{output_dir}/vpn_config.ovpn", 'w') as f:
            f.write(package['configs']['vpn'])
        
        # 3. Configurations encodées
        with open(f"{output_dir}/ssh_config_b64.txt", 'w') as f:
            f.write(package['configs']['ssh_b64'])
        
        with open(f"{output_dir}/vpn_config_b64.txt", 'w') as f:
            f.write(package['configs']['vpn_b64'])
        
        with open(f"{output_dir}/ssh_config_b85.txt", 'w') as f:
            f.write(package['configs']['ssh_b85'])
        
        with open(f"{output_dir}/vpn_config_b85.txt", 'w') as f:
            f.write(package['configs']['vpn_b85'])
        
        # 4. Payloads encodés
        with open(f"{output_dir}/payloads_encoded.json", 'w') as f:
            json.dump(package['encoded_payloads'], f, indent=2)
        
        # 5. Fichier d'instructions
        self._create_instructions_file(output_dir, package, index)
    
    def _create_instructions_file(self, output_dir: str, 
                                 package: Dict[str, Any], index: int):
        """Crée un fichier d'instructions"""
        account = package['account_data']['account']
        
        instructions = f"""# INSTRUCTIONS D'UTILISATION - Compte #{index}
# Généré le: {datetime.now().isoformat()}
# Compte: {account['username']}

## 🔐 INFORMATIONS DE CONNEXION

### SSH:
- Serveur: {package['account_data']['server']['hostname']}
- Port: {account['ssh_port']}
- Utilisateur: {account['username']}
- Mot de passe: {account['password']}

### VPN (OpenVPN):
- Serveur: {package['account_data']['server']['hostname']}
- Port: {account['vpn_port']}
- Utilisateur: {account['username']}
- Mot de passe: {account['vpn_password']}

## ⏱️  VALIDITÉ
- Créé le: {account['created_at']}
- Expire le: {account['expires_at']}
- Durée: {account['duration_hours']} heures

## 🚀 UTILISATION

### 1. Connexion SSH:
```bash
# Méthode simple
ssh {account['username']}@{package['account_data']['server']['hostname']} -p {account['ssh_port']}

# Avec tunneling SOCKS5
ssh -D 1080 {account['username']}@{package['account_data']['server']['hostname']} -p {account['ssh_port']}
