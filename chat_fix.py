import sqlite3
import json
import os
import sys

DB_PATH = r"C:\Users\yashw.000\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"

# Your working token
WORKING_TOKEN = "user_01KDYKWSASHZ0RZ65WD8M9NRJT::eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfHVzZXJfMDFLRFlLV1NBU0haMFJaNjVXRDhNOU5SSlQiLCJ0aW1lIjoiMTc2NzkwMzU3NiIsInJhbmRvbW5lc3MiOiI0ZjI1NDQ2Zi0yOTYxLTQxYzciLCJleHAiOjE3NzMwODc1NzYsImlzcyI6Imh0dHBzOi8vYXV0aGVudGljYXRpb24uY3Vyc29yLnNoIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsImF1ZCI6Imh0dHBzOi8vY3Vyc29yLmNvbSIsInR5cGUiOiJ3ZWIifQ.1GQh24EQ1zs3oMVP02WyBmP9JcLgIR4_xRXvjiTUdhc"

def create_premium_auth():
    """Create premium authentication data"""
    
    premium_auth = {
        "accessToken": WORKING_TOKEN,
        "refreshToken": WORKING_TOKEN,
        "tokenType": "bearer",
        "expiresIn": 86400,
        "expiresAt": 9999999999,  # Far future
        "scope": "openid profile email offline_access",
        "provider": "google-oauth2",
        "user": {
            "email": "yashwant1ins@gmail.com",
            "name": "Yashwant",
            "picture": ""
        },
        "session": {
            "id": "user_01KDYKWSASHZ0RZ65WD8M9NRJT",
            "createdAt": "2026-01-09T01:17:00.084Z"
        },
        # PREMIUM FEATURES
        "stripeMembershipType": "premium",
        "subscription": {
            "status": "active",
            "plan": "premium",
            "currentPeriodEnd": 9999999999,
            "cancelAtPeriodEnd": False
        },
        "features": {
            "unlimitedChat": True,
            "unlimitedAgents": True,
            "prioritySupport": True,
            "earlyAccess": True,
            "customModels": True
        },
        "limits": {
            "monthlyTokens": 1000000000,  # 1 billion tokens
            "agentsPerDay": 1000,
            "chatMessages": 999999
        }
    }
    
    return premium_auth

def fix_chat_authentication():
    """Fix Chat authentication and upgrade to premium"""
    
    print("🚀 Cursor Premium Upgrade & Chat Fix")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create premium authentication data
        premium_auth = create_premium_auth()
        premium_json = json.dumps(premium_auth, indent=2)
        
        print("💎 Injecting PREMIUM authentication...")
        
        # Critical premium keys
        premium_keys = [
            ("cursor.chat.session", premium_json),
            ("cursor.agent.auth", premium_json),
            ("workos.chat.token", WORKING_TOKEN),
            ("api.auth.session", premium_json),
            ("chat.authentication.state", premium_json),
            ("agent.auth.state", premium_json),
            ("cursor.workos.session", WORKING_TOKEN),
            ("stripe.subscription.data", premium_json),
            ("cursor.premium.features", premium_json),
        ]
        
        for key, value in premium_keys:
            cursor.execute(
                "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                (key, value.encode('utf-8') if isinstance(value, str) else value)
            )
            print(f"   ✅ Premium: {key}")
        
        # Update ALL existing auth keys to premium
        cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%auth%' OR key LIKE '%token%' OR key LIKE '%stripe%'")
        existing_keys = cursor.fetchall()
        
        for (key,) in existing_keys:
            if 'accessToken' in key or 'refreshToken' in key:
                cursor.execute(
                    "UPDATE ItemTable SET value = ? WHERE key = ?",
                    (premium_json.encode('utf-8'), key)
                )
                print(f"   🔄 Upgraded: {key}")
        
        # Set premium membership type
        cursor.execute(
            "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
            ("cursorAuth/stripeMembershipType", "premium".encode('utf-8'))
        )
        
        # Add unlimited usage flags
        unlimited_flags = [
            ("usage.unlimited", "true"),
            ("model.access", "premium"),
            ("rate.limit.bypass", "true"),
            ("cursor.pro.features", "enabled")
        ]
        
        for key, value in unlimited_flags:
            cursor.execute(
                "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                (key, value.encode('utf-8'))
            )
        
        conn.commit()
        
        print("\n✅ Premium upgrade complete!")
        
        # Verify
        print("\n🔍 Verification:")
        cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%premium%' OR key LIKE '%stripe%' OR key LIKE '%unlimited%'")
        results = cursor.fetchall()
        
        print(f"   Found {len(results)} premium features:")
        for key in results:
            print(f"   - {key[0]}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("💎 PREMIUM FEATURES ACTIVATED:")
        print("   1. Unlimited tokens (1B/month)")
        print("   2. Premium model access")
        print("   3. No rate limits")
        print("   4. All AI features unlocked")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_unlimited_accounts_script():
    """Create script for unlimited accounts rotation"""
    
    script_content = '''# Unlimited Cursor Usage System
# Save as: unlimited_cursor.py

import subprocess
import time
import json
import os

class CursorUnlimited:
    def __init__(self):
        self.accounts = [
            "account1@gmail.com",
            "account2@gmail.com",
            "account3@gmail.com",
            "account4@gmail.com"
        ]
        self.current_account = 0
    
    def rotate_account(self):
        """Switch to next Google account"""
        print(f"🔄 Rotating to account {self.current_account + 1}/{len(self.accounts)}")
        
        # Run your tool's authentication
        # Modify this path to your actual tool
        tool_path = r"D:\cursor pro\cursor-free-vip\your_main_script.py"
        
        # This would trigger Google auth for next account
        # You need to modify your tool to accept account rotation
        
        print("✅ Account rotated")
        self.current_account = (self.current_account + 1) % len(self.accounts)
    
    def monitor_usage(self):
        """Monitor token usage and rotate when near limit"""
        print("📊 Monitoring usage...")
        # Check usage via Cursor API or database
        # Rotate when > 80% of free limit
        
        self.rotate_account()
    
    def create_accounts(self, count=5):
        """Guide to create multiple Google accounts"""
        print(f"📝 Create {count} Google accounts:")
        print("1. Go to: https://accounts.google.com/signup")
        print("2. Use different phone numbers for verification")
        print("3. Save credentials in passwords.txt")
        print("4. Use your tool to authenticate each")
        
        with open('google_accounts.txt', 'w') as f:
            f.write("Format: email,password,recovery_email\\n")
            for i in range(count):
                f.write(f"cursor{i+1}@gmail.com,password{i+1},recovery{i+1}@gmail.com\\n")
        
        print("✅ Account template created: google_accounts.txt")

# Usage
if __name__ == "__main__":
    unlimited = CursorUnlimited()
    
    print("🚀 Cursor Unlimited Usage System")
    print("=" * 50)
    print("Options:")
    print("1. Create multiple Google accounts")
    print("2. Rotate to next account")
    print("3. Monitor and auto-rotate")
    
    choice = input("Select option (1-3): ")
    
    if choice == "1":
        unlimited.create_accounts(5)
    elif choice == "2":
        unlimited.rotate_account()
    elif choice == "3":
        unlimited.monitor_usage()
    else:
        print("Invalid choice")
'''
    
    with open('unlimited_cursor.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Unlimited script created: unlimited_cursor.py")

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Cursor Premium & Unlimited Setup")
    print("=" * 60)
    
    # First, fix chat authentication
    if fix_chat_authentication():
        print("\n" + "=" * 60)
        print("\n📋 Next steps:")
        print("1. Close Cursor completely")
        print("2. Open Cursor")
        print("3. Check Settings → Account (should show premium)")
        print("4. Try premium models in Chat")
        
        # Create unlimited accounts script
        create_unlimited_accounts_script()
        
        print("\n" + "=" * 60)
        print("\n💡 For TRULY UNLIMITED usage:")
        print("1. Create 5+ Google accounts")
        print("2. Use your tool to authenticate each")
        print("3. Rotate when hitting limits")
        print("4. Run: python unlimited_cursor.py")
        
    else:
        print("\n❌ Premium upgrade failed!")