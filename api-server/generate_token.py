#!/usr/bin/env python3
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta

def generate_api_token(name="admin", expires_days=365):
    """Génère un nouveau token API"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    expires_at = datetime.now() + timedelta(days=expires_days)
    
    conn = sqlite3.connect("/var/lib/vps-manager/accounts.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO api_tokens (token_hash, name, expires_at)
        VALUES (?, ?, ?)
    ''', (token_hash, name, expires_at.isoformat()))
    conn.commit()
    conn.close()
    
    print(f"\n🔐 TOKEN API GÉNÉRÉ:")
    print(f"   Nom: {name}")
    print(f"   Token: {token}")
    print(f"   Expire le: {expires_at.date()}")
    print(f"\n⚠️  Sauvegardez ce token, il ne sera plus affiché!")

if __name__ == "__main__":
    generate_api_token("admin", 365)
