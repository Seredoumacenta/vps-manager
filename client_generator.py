#!/usr/bin/env python3
"""
Client de génération de comptes SSH/VPN
À exécuter depuis n'importe quelle machine
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def generate_accounts(api_url, api_token, count=1, duration_hours=24):
    """Génère des comptes via l'API"""
    print(f"\n🔗 Connexion à l'API: {api_url}")
    
    accounts = []
    
    for i in range(count):
        print(f"\n[{i+1}/{count}] Création du compte...")
        
        try:
            async with websockets.connect(api_url) as websocket:
                request = {
                    "action": "create_account",
                    "api_token": api_token,
                    "duration_hours": duration_hours
                }
                
                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get("success"):
                    accounts.append(result)
                    print(f"   ✅ Compte créé: {result['username']}")
                    print(f"   🔐 SSH: {result['password']}")
                    print(f"   🔒 VPN: {result['vpn_password']}")
                    print(f"   ⏱️  Expire: {result['expires_at'].split('T')[0]}")
                else:
                    print(f"   ❌ Erreur: {result.get('error')}")
                    
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
    
    return accounts

async def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   🚀 CLIENT GÉNÉRATION COMPTES SSH/VPN                  ║
    ║   ----------------------------------------------------   ║
    ║   • Génération via API WebSocket                        ║
    ║   • Comptes à durée limitée                            ║
    ║   • Configuration automatique                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Configuration
    API_URL = input("🌐 URL de l'API (ex: wss://api.votre-domaine.com): ").strip()
    API_TOKEN = input("🔑 Token API: ").strip()
    
    try:
        COUNT = int(input("📊 Nombre de comptes à générer [1]: ").strip() or "1")
        DURATION = int(input("⏱️  Durée de validité (heures) [24]: ").strip() or "24")
    except:
        COUNT = 1
        DURATION = 24
    
    # Génération
    accounts = await generate_accounts(API_URL, API_TOKEN, COUNT, DURATION)
    
    # Sauvegarde
    if accounts:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vps_accounts_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(accounts, f, indent=2)
        
        print(f"\n✅ {len(accounts)} comptes générés avec succès!")
        print(f"📁 Sauvegardés dans: {filename}")
        
        # Affichage récapitulatif
        print("\n📋 RÉCAPITULATIF:")
        for acc in accounts:
            print(f"\n  👤 {acc['username']}")
            print(f"    🔐 SSH: port {acc['ssh_port']} | {acc['password']}")
            print(f"    🔒 VPN: port {acc['vpn_port']} | {acc['vpn_password']}")
            print(f"    ⏱️  Valide jusqu'au: {acc['expires_at'].split('T')[0]}")
    
    else:
        print("\n❌ Aucun compte généré")

if __name__ == "__main__":
    asyncio.run(main())
