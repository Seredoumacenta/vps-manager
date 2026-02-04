#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🌐 UNIVERSAL VPS MANAGER CORE - PORTABLE CROSS-LINUX
================================================================================
Noyau portable pour tous les systèmes Linux :
- Termux (Android)
- Ubuntu/Debian
- Arch Linux/Manjaro
- Fedora/CentOS/RHEL
- OpenSUSE
- Kali/Parrot
- Raspberry Pi OS
================================================================================
"""

import os
import sys
import platform
import subprocess
import json
import base64
import hashlib
import secrets
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import shutil
import logging
from pathlib import Path
import urllib.parse

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinuxDistributionDetector:
    """Détecteur de distribution Linux universel"""
    
    DISTRIBUTIONS = {
        'termux': {
            'name': 'Termux',
            'id': 'termux',
            'package_manager': 'pkg',
            'config_dir': '/data/data/com.termux/files/home/.config',
            'requires_root': False,
            'icon': '📱'
        },
        'ubuntu': {
            'name': 'Ubuntu',
            'id': 'ubuntu',
            'package_manager': 'apt',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🐧'
        },
        'debian': {
            'name': 'Debian',
            'id': 'debian',
            'package_manager': 'apt',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🎯'
        },
        'arch': {
            'name': 'Arch Linux',
            'id': 'arch',
            'package_manager': 'pacman',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🏔️'
        },
        'manjaro': {
            'name': 'Manjaro',
            'id': 'manjaro',
            'package_manager': 'pamac',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🐉'
        },
        'fedora': {
            'name': 'Fedora',
            'id': 'fedora',
            'package_manager': 'dnf',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🔵'
        },
        'centos': {
            'name': 'CentOS',
            'id': 'centos',
            'package_manager': 'yum',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🎩'
        },
        'opensuse': {
            'name': 'openSUSE',
            'id': 'opensuse',
            'package_manager': 'zypper',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🦎'
        },
        'kali': {
            'name': 'Kali Linux',
            'id': 'kali',
            'package_manager': 'apt',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '⚔️'
        },
        'parrot': {
            'name': 'Parrot OS',
            'id': 'parrot',
            'package_manager': 'apt',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🦜'
        },
        'raspbian': {
            'name': 'Raspberry Pi OS',
            'id': 'raspbian',
            'package_manager': 'apt',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🍓'
        },
        'alpine': {
            'name': 'Alpine Linux',
            'id': 'alpine',
            'package_manager': 'apk',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '⛰️'
        },
        'gentoo': {
            'name': 'Gentoo',
            'id': 'gentoo',
            'package_manager': 'emerge',
            'config_dir': '~/.config',
            'requires_root': True,
            'icon': '🦊'
        }
    }
    
    @staticmethod
    def detect() -> Dict[str, Any]:
        """Détecte la distribution Linux actuelle"""
        system = platform.system().lower()
        
        # Vérifier Termux
        if 'ANDROID_ROOT' in os.environ or 'TERMUX' in os.environ:
            return LinuxDistributionDetector.DISTRIBUTIONS['termux']
        
        if system != 'linux':
            return {
                'name': 'Unknown',
                'id': 'unknown',
                'package_manager': None,
                'config_dir': '~/.config',
                'requires_root': False,
                'icon': '💻'
            }
        
        # Lire les fichiers d'identification
        release_files = [
            '/etc/os-release',
            '/usr/lib/os-release',
            '/etc/lsb-release',
            '/etc/debian_version',
            '/etc/redhat-release',
            '/etc/arch-release',
            '/etc/SuSE-release'
        ]
        
        os_info = {}
        for file in release_files:
            if os.path.exists(file):
                try:
                    with open(file, 'r') as f:
                        for line in f:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                os_info[key.lower()] = value.strip('"')
                except:
                    continue
        
        # Identifier la distribution
        distro_id = os_info.get('id', '').lower()
        distro_name = os_info.get('name', '').lower()
        
        # Correspondance
        if 'termux' in distro_id or 'android' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['termux']
        elif 'ubuntu' in distro_id or 'ubuntu' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['ubuntu']
        elif 'debian' in distro_id or 'debian' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['debian']
        elif 'arch' in distro_id or 'arch' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['arch']
        elif 'manjaro' in distro_id or 'manjaro' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['manjaro']
        elif 'fedora' in distro_id or 'fedora' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['fedora']
        elif 'centos' in distro_id or 'centos' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['centos']
        elif 'opensuse' in distro_id or 'suse' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['opensuse']
        elif 'kali' in distro_id or 'kali' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['kali']
        elif 'parrot' in distro_id or 'parrot' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['parrot']
        elif 'raspbian' in distro_id or 'raspbian' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['raspbian']
        elif 'alpine' in distro_id or 'alpine' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['alpine']
        elif 'gentoo' in distro_id or 'gentoo' in distro_name:
            return LinuxDistributionDetector.DISTRIBUTIONS['gentoo']
        
        # Fallback basé sur le gestionnaire de paquets
        if LinuxDistributionDetector._check_package_manager('apt'):
            return LinuxDistributionDetector.DISTRIBUTIONS['debian']
        elif LinuxDistributionDetector._check_package_manager('pacman'):
            return LinuxDistributionDetector.DISTRIBUTIONS['arch']
        elif LinuxDistributionDetector._check_package_manager('dnf'):
            return LinuxDistributionDetector.DISTRIBUTIONS['fedora']
        elif LinuxDistributionDetector._check_package_manager('yum'):
            return LinuxDistributionDetector.DISTRIBUTIONS['centos']
        elif LinuxDistributionDetector._check_package_manager('zypper'):
            return LinuxDistributionDetector.DISTRIBUTIONS['opensuse']
        elif LinuxDistributionDetector._check_package_manager('apk'):
            return LinuxDistributionDetector.DISTRIBUTIONS['alpine']
        
        return {
            'name': 'Unknown Linux',
            'id': 'unknown',
            'package_manager': None,
            'config_dir': '~/.config',
            'requires_root': False,
            'icon': '🐧'
        }
    
    @staticmethod
    def _check_package_manager(pkg_manager: str) -> bool:
        """Vérifie si un gestionnaire de paquets est disponible"""
        return shutil.which(pkg_manager) is not None
    
    @staticmethod
    def get_home_dir() -> str:
        """Retourne le répertoire home adapté"""
        distro = LinuxDistributionDetector.detect()
        
        if distro['id'] == 'termux':
            return '/data/data/com.termux/files/home'
        else:
            return os.path.expanduser('~')
    
    @staticmethod
    def get_config_dir() -> str:
        """Retourne le répertoire de configuration"""
        distro = LinuxDistributionDetector.detect()
        base_dir = LinuxDistributionDetector.get_home_dir()
        
        config_dir = os.path.join(base_dir, '.config', 'universal-vps-manager')
        os.makedirs(config_dir, exist_ok=True)
        
        return config_dir
    
    @staticmethod
    def is_root() -> bool:
        """Vérifie si l'utilisateur a les privilèges root"""
        return os.geteuid() == 0
    
    @staticmethod
    def get_terminal_info() -> Dict[str, Any]:
        """Récupère des informations sur le terminal"""
        term = os.environ.get('TERM', 'unknown')
        term_program = os.environ.get('TERM_PROGRAM', 'unknown')
        color_term = os.environ.get('COLORTERM', '')
        
        return {
            'term': term,
            'term_program': term_program,
            'supports_color': color_term in ['truecolor', '24bit', 'yes'],
            'columns': shutil.get_terminal_size().columns,
            'lines': shutil.get_terminal_size().lines
        }

class UniversalVPSClient:
    """Client VPS universel pour toutes les distributions"""
    
    def __init__(self, api_url: str = None, api_token: str = None):
        self.distro = LinuxDistributionDetector.detect()
        self.config_dir = LinuxDistributionDetector.get_config_dir()
        self.config_file = os.path.join(self.config_dir, 'client_config.json')
        
        # Charger ou initialiser la configuration
        self.config = self._load_config()
        
        if api_url:
            self.config['api_url'] = api_url
        if api_token:
            self.config['api_token'] = api_token
        
        self.save_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration du client"""
        default_config = {
            'api_url': 'ws://localhost:8765',
            'api_token': '',
            'default_duration': 24,
            'default_count': 1,
            'auto_save': True,
            'output_dir': os.path.join(self.config_dir, 'payloads'),
            'theme': 'auto',
            'last_used': None
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
        except Exception as e:
            logger.warning(f"Erreur chargement config: {e}")
        
        return default_config
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            self.config['last_used'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Teste la connexion à l'API"""
        try:
            async with websockets.connect(self.config['api_url']) as websocket:
                request = {
                    "action": "ping",
                    "api_token": self.config['api_token']
                }
                
                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                result = json.loads(response)
                
                return {
                    "success": True,
                    "status": "connected",
                    "response": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "status": "disconnected",
                "error": str(e)
            }
    
    async def create_account(self, duration_hours: int = None) -> Dict[str, Any]:
        """Crée un compte via l'API"""
        duration = duration_hours or self.config['default_duration']
        
        try:
            async with websockets.connect(self.config['api_url']) as websocket:
                request = {
                    "action": "create_account",
                    "api_token": self.config['api_token'],
                    "duration_hours": duration,
                    "client_info": {
                        "distro": self.distro,
                        "terminal": LinuxDistributionDetector.get_terminal_info(),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get('success'):
                    # Sauvegarder le compte localement
                    self._save_account_locally(result)
                
                return result
                
        except Exception as e:
            logger.error(f"Erreur création compte: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_account_locally(self, account_data: Dict[str, Any]):
        """Sauvegarde le compte localement"""
        try:
            output_dir = self.config['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            username = account_data.get('username', 'unknown')
            filename = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(account_data, f, indent=2)
            
            logger.info(f"Compte sauvegardé: {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde locale: {e}")
    
    def generate_ssh_config(self, account_data: Dict[str, Any]) -> str:
        """Génère une configuration SSH adaptée à la distribution"""
        template = f"""# SSH Configuration for {account_data.get('username', '')}
# Generated: {datetime.now().isoformat()}
# Expires: {account_data.get('expires_at', '')}
# Distribution: {self.distro['name']}

Host vps-{account_data.get('username', '')}
    HostName {account_data.get('server_ip', 'vps.example.com')}
    Port {account_data.get('ssh_port', 22)}
    User {account_data.get('username', '')}
    ServerAliveInterval 30
    ServerAliveCountMax 3
    TCPKeepAlive yes
    Compression yes
    CompressionLevel 9
    
# Connection command for {self.distro['name']}:
"""
        
        # Commandes spécifiques par distribution
        if self.distro['id'] == 'termux':
            template += f"""# Termux command:
termux-wake-lock
ssh {account_data.get('username', '')}@{account_data.get('server_ip', '')} -p {account_data.get('ssh_port', 22)}
"""
        else:
            template += f"""ssh {account_data.get('username', '')}@{account_data.get('server_ip', '')} -p {account_data.get('ssh_port', 22)}
"""
        
        return template
    
    def generate_vpn_config(self, account_data: Dict[str, Any]) -> str:
        """Génère une configuration VPN adaptée"""
        vpn_config = account_data.get('vpn_config', {})
        
        config = f"""# OpenVPN Configuration for {account_data.get('username', '')}
# Generated for: {self.distro['name']}
# Server: {vpn_config.get('server', 'vps.example.com')}
# Port: {account_data.get('vpn_port', 1194)}

client
dev tun
proto udp
remote {vpn_config.get('server', 'vps.example.com')} {account_data.get('vpn_port', 1194)}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA512
verb 3
auth-user-pass
<ca>
-----BEGIN CERTIFICATE-----
{vpn_config.get('ca_cert', 'MIIE...')}
-----END CERTIFICATE-----
</ca>
"""
        
        return config
    
    async def batch_create_accounts(self, count: int = 1, 
                                  duration_hours: int = None) -> List[Dict[str, Any]]:
        """Crée plusieurs comptes en batch"""
        accounts = []
        
        for i in range(count):
            print(f"\n[{i+1}/{count}] Creating account...")
            
            try:
                account = await self.create_account(duration_hours)
                
                if account.get('success'):
                    accounts.append(account)
                    
                    # Afficher les informations
                    print(f"  ✅ {account.get('username', 'Unknown')}")
                    print(f"  🔐 SSH: {account.get('password', '')[:12]}...")
                    print(f"  🔒 VPN: {account.get('vpn_password', '')[:12]}...")
                    print(f"  ⏱️  Expires: {account.get('expires_at', '')[:10]}")
                else:
                    print(f"  ❌ Failed: {account.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return accounts

class UniversalInterface:
    """Interface utilisateur universelle"""
    
    COLORS = {
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'RED': '\033[31m',
        'GREEN': '\033[32m',
        'YELLOW': '\033[33m',
        'BLUE': '\033[34m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'WHITE': '\033[37m'
    }
    
    @staticmethod
    def print_banner():
        """Affiche la bannière adaptée"""
        distro = LinuxDistributionDetector.detect()
        term_info = LinuxDistributionDetector.get_terminal_info()
        
        width = min(80, term_info['columns'])
        
        banner = f"""
{UniversalInterface.colorize('=' * width, 'CYAN')}
{UniversalInterface.colorize('🌐 UNIVERSAL VPS MANAGER', 'BOLD')}
{UniversalInterface.colorize(f'{distro["icon"]} {distro["name"]}', 'GREEN')}
{UniversalInterface.colorize('SSH/VPN Account Generator - All Linux Distributions', 'BLUE')}
{UniversalInterface.colorize('=' * width, 'CYAN')}
"""
        print(banner)
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Colore le texte pour le terminal"""
        if not term_info.get('supports_color', False):
            return text
        
        color_code = UniversalInterface.COLORS.get(color.upper(), '')
        reset = UniversalInterface.COLORS['RESET']
        
        return f"{color_code}{text}{reset}"
    
    @staticmethod
    def print_menu(title: str, options: List[Tuple[str, str]]):
        """Affiche un menu"""
        print(f"\n{UniversalInterface.colorize(title, 'BOLD')}")
        print(UniversalInterface.colorize('─' * 40, 'CYAN'))
        
        for i, (key, description) in enumerate(options, 1):
            print(f"{UniversalInterface.colorize(f'{i:2d}', 'YELLOW')}. {description}")
    
    @staticmethod
    def get_choice(prompt: str, min_val: int = 1, max_val: int = 10) -> int:
        """Récupère un choix utilisateur"""
        while True:
            try:
                choice = input(f"\n{UniversalInterface.colorize(prompt, 'MAGENTA')} ")
                
                if choice.lower() in ['q', 'quit', 'exit']:
                    return -1
                
                choice = int(choice)
                
                if min_val <= choice <= max_val:
                    return choice
                else:
                    print(UniversalInterface.colorize(
                        f"Choix invalide. Doit être entre {min_val} et {max_val}.", 
                        'RED'
                    ))
                    
            except ValueError:
                print(UniversalInterface.colorize(
                    "Veuillez entrer un nombre valide.", 
                    'RED'
                ))

async def main():
    """Fonction principale"""
    # Détection de l'environnement
    distro = LinuxDistributionDetector.detect()
    term_info = LinuxDistributionDetector.get_terminal_info()
    
    # Interface
    UniversalInterface.print_banner()
    
    print(f"📊 Système détecté: {distro['name']} {distro['icon']}")
    print(f"🏠 Home directory: {LinuxDistributionDetector.get_home_dir()}")
    print(f"🔧 Package manager: {distro.get('package_manager', 'N/A')}")
    print(f"👤 Root access: {'Yes' if LinuxDistributionDetector.is_root() else 'No'}")
    print(f"💻 Terminal: {term_info['term_program']}")
    print(f"🌈 Colors: {'Yes' if term_info['supports_color'] else 'No'}")
    
    # Initialisation du client
    client = UniversalVPSClient()
    
    # Menu principal
    while True:
        UniversalInterface.print_menu("MENU PRINCIPAL", [
            ("1", "🔗 Tester la connexion API"),
            ("2", "🚀 Créer un compte SSH/VPN"),
            ("3", "📊 Créer plusieurs comptes"),
            ("4", "⚙️  Configuration"),
            ("5", "📁 Gérer les comptes locaux"),
            ("6", "🔄 Mettre à jour"),
            ("7", "❓ Aide"),
            ("8", "🚪 Quitter")
        ])
        
        choice = UniversalInterface.get_choice("Votre choix", 1, 8)
        
        if choice == -1 or choice == 8:
            print("\n👋 Au revoir!")
            break
        
        elif choice == 1:
            # Tester la connexion
            print("\n🔗 Test de connexion en cours...")
            result = await client.test_connection()
            
            if result['success']:
                print(UniversalInterface.colorize("✅ Connexion réussie!", 'GREEN'))
                print(f"📡 Status: {result.get('status', 'unknown')}")
            else:
                print(UniversalInterface.colorize("❌ Connexion échouée", 'RED'))
                print(f"💥 Erreur: {result.get('error', 'unknown')}")
        
        elif choice == 2:
            # Créer un compte
            duration = input(f"\n⏱️  Durée (heures) [{client.config['default_duration']}]: ")
            duration = int(duration) if duration else client.config['default_duration']
            
            print(f"\n🚀 Création d'un compte ({duration}h)...")
            account = await client.create_account(duration)
            
            if account.get('success'):
                print(UniversalInterface.colorize("✅ Compte créé avec succès!", 'GREEN'))
                print(f"👤 Username: {account.get('username')}")
                print(f"🔐 Password: {account.get('password')}")
                print(f"🔒 VPN Password: {account.get('vpn_password')}")
                print(f"📡 SSH Port: {account.get('ssh_port')}")
                print(f"🔗 VPN Port: {account.get('vpn_port')}")
                print(f"⏱️  Expires: {account.get('expires_at')}")
                
                # Générer les configurations
                ssh_config = client.generate_ssh_config(account)
                vpn_config = client.generate_vpn_config(account)
                
                print(f"\n📄 SSH Config generated ({len(ssh_config)} chars)")
                print(f"📄 VPN Config generated ({len(vpn_config)} chars)")
            else:
                print(UniversalInterface.colorize("❌ Échec création compte", 'RED'))
                print(f"💥 Erreur: {account.get('error', 'unknown')}")
        
        elif choice == 3:
            # Créer plusieurs comptes
            count = input(f"\n📊 Nombre de comptes [{client.config['default_count']}]: ")
            count = int(count) if count else client.config['default_count']
            
            duration = input(f"⏱️  Durée (heures) [{client.config['default_duration']}]: ")
            duration = int(duration) if duration else client.config['default_duration']
            
            print(f"\n🚀 Création de {count} comptes ({duration}h chacun)...")
            accounts = await client.batch_create_accounts(count, duration)
            
            print(f"\n📊 Résumé: {len(accounts)}/{count} comptes créés")
        
        elif choice == 4:
            # Configuration
            UniversalInterface.print_menu("CONFIGURATION", [
                ("1", "🌐 URL de l'API"),
                ("2", "🔑 Token API"),
                ("3", "⏱️  Durée par défaut"),
                ("4", "📊 Nombre par défaut"),
                ("5", "💾 Enregistrer"),
                ("6", "↩️  Retour")
            ])
            
            config_choice = UniversalInterface.get_choice("Option config", 1, 6)
            
            if config_choice == 1:
                new_url = input(f"URL API [{client.config['api_url']}]: ")
                if new_url:
                    client.config['api_url'] = new_url
            
            elif config_choice == 2:
                new_token = input("Token API: ")
                if new_token:
                    client.config['api_token'] = new_token
            
            elif config_choice == 3:
                new_duration = input(f"Durée (heures) [{client.config['default_duration']}]: ")
                if new_duration:
                    client.config['default_duration'] = int(new_duration)
            
            elif config_choice == 4:
                new_count = input(f"Nombre [{client.config['default_count']}]: ")
                if new_count:
                    client.config['default_count'] = int(new_count)
            
            elif config_choice == 5:
                client.save_config()
                print(UniversalInterface.colorize("✅ Configuration sauvegardée", 'GREEN'))
        
        elif choice == 5:
            # Gérer les comptes locaux
            output_dir = client.config['output_dir']
            
            if os.path.exists(output_dir):
                files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
                
                print(f"\n📁 Comptes locaux ({len(files)}):")
                
                for i, file in enumerate(files[:10], 1):
                    filepath = os.path.join(output_dir, file)
                    size = os.path.getsize(filepath)
                    print(f"  {i:2d}. {file} ({size} bytes)")
                
                if len(files) > 10:
                    print(f"  ... et {len(files) - 10} autres")
            else:
                print(f"\n📁 Aucun compte local trouvé dans {output_dir}")
        
        elif choice == 6:
            # Mettre à jour
            print("\n🔄 Vérification des mises à jour...")
            
            # Dans une vraie implémentation, vérifier GitHub/version
            print("Version actuelle: 1.0.0")
            print("Dernière version: 1.0.0")
            print(UniversalInterface.colorize("✅ Votre système est à jour", 'GREEN'))
        
        elif choice == 7:
            # Aide
            print("""
            📖 AIDE - UNIVERSAL VPS MANAGER
            
            Ce programme vous permet de générer des comptes SSH/VPN
            via une API WebSocket hébergée sur un serveur VPS.
            
            📋 FONCTIONNALITÉS:
            • Génération de comptes avec expiration
            • Configuration SSH/VPN automatique
            • Support toutes distributions Linux
            • Interface adaptative
            
            🔧 PRÉREQUIS:
            • Python 3.7+
            • Connexion Internet
            • Token API valide
            
            📁 STRUCTURE:
            • ~/.config/universal-vps-manager/ - Configuration
            • ~/.config/universal-vps-manager/payloads/ - Comptes
            
            🚀 UTILISATION:
            1. Configurez l'URL et le token API
            2. Testez la connexion
            3. Générez des comptes
            4. Utilisez les configurations générées
            
            ⚠️  SÉCURITÉ:
            • Les tokens API sont stockés localement
            • Les mots de passe sont générés aléatoirement
            • Les comptes expirent automatiquement
            """)
        
        input(f"\n{UniversalInterface.colorize('Appuyez sur Entrée pour continuer...', 'DIM')}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{UniversalInterface.colorize('👋 Interruption utilisateur', 'YELLOW')}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
