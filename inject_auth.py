import sqlite3
import os
import json
import sys

# Database will be created here after first Cursor launch
DB_PATH = r"C:\Users\yashw.000\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"

# Your authentication data from backup
AUTH_DATA = {
    "accessToken": "user_01KDYKWSASHZ0RZ65WD8M9NRJT::eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfHVzZXJfMDFLRFlLV1NBU0haMFJaNjVXRDhNOU5SSlQiLCJ0aW1lIjoiMTc2NzkwMzU3NiIsInJhbmRvbW5lc3MiOiI0ZjI1NDQ2Zi0yOTYxLTQxYzciLCJleHAiOjE3NzMwODc1NzYsImlzcyI6Imh0dHBzOi8vYXV0aGVudGljYXRpb24uY3Vyc29yLnNoIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsImF1ZCI6Imh0dHBzOi8vY3Vyc29yLmNvbSIsInR5cGUiOiJ3ZWIifQ.1GQh24EQ1zs3oMVP02WyBmP9JcLgIR4_xRXvjiTUdhc",
    "refreshToken": "user_01KDYKWSASHZ0RZ65WD8M9NRJT::eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfHVzZXJfMDFLRFlLV1NBU0haMFJaNjVXRDhNOU5SSlQiLCJ0aW1lIjoiMTc2NzkwMzU3NiIsInJhbmRvbW5lc3MiOiI0ZjI1NDQ2Zi0yOTYxLTQxYzciLCJleHAiOjE3NzMwODc1NzYsImlzcyI6Imh0dHBzOi8vYXV0aGVudGljYXRpb24uY3Vyc29yLnNoIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsImF1ZCI6Imh0dHBzOi8vY3Vyc29yLmNvbSIsInR5cGUiOiJ3ZWIifQ.1GQh24EQ1zs3oMVP02WyBmP9JcLgIR4_xRXvjiTUdhc",
    "email": "yashwant1ins@gmail.com",
    "provider": "google-oauth2",
    "cachedSignUpType": "google"
}

def create_cursor_database():
    """Create Cursor database with authentication pre-loaded"""
    
    print("🚀 Creating Cursor authentication database...")
    
    # Create directory if doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        # Create new SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables (based on your earlier schema analysis)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ItemTable (
                key TEXT PRIMARY KEY ON CONFLICT REPLACE,
                value BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursorDiskKV (
                key TEXT PRIMARY KEY ON CONFLICT REPLACE,
                value BLOB
            )
        ''')
        
        print("✅ Database tables created")
        
        # Inject authentication data
        auth_items = [
            ("cursorAuth/accessToken", AUTH_DATA["accessToken"]),
            ("cursorAuth/refreshToken", AUTH_DATA["refreshToken"]),
            ("cursorAuth/cachedEmail", AUTH_DATA["email"]),
            ("cursorAuth/cachedSignUpType", AUTH_DATA["cachedSignUpType"]),
            ("cursorAuth/stripeMembershipType", "free"),
            ("telemetry.firstSessionDate", "2026-01-09T01:17:00.084Z"),
            ("telemetry.lastSessionDate", "2026-01-09T01:42:57.809Z"),
            ("telemetry.currentSessionDate", "2026-01-09T01:42:57.809Z"),
        ]
        
        # Also create JSON format for Chat/API
        chat_auth = {
            "accessToken": AUTH_DATA["accessToken"],
            "refreshToken": AUTH_DATA["refreshToken"],
            "email": AUTH_DATA["email"],
            "provider": AUTH_DATA["provider"],
            "expiresAt": 1773087576,
            "scope": "openid profile email offline_access"
        }
        
        auth_items.append(("cursor.chat.auth", json.dumps(chat_auth)))
        auth_items.append(("cursor.api.auth", json.dumps(chat_auth)))
        
        # Insert all items
        for key, value in auth_items:
            cursor.execute(
                "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                (key, value.encode('utf-8') if isinstance(value, str) else value)
            )
            cursor.execute(
                "INSERT OR REPLACE INTO cursorDiskKV (key, value) VALUES (?, ?)",
                (key, value.encode('utf-8') if isinstance(value, str) else value)
            )
        
        conn.commit()
        conn.close()
        
        print("✅ Authentication data injected")
        print(f"📁 Database created at: {DB_PATH}")
        
        # Verify
        print("\n🔍 Verifying injection...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%auth%' OR key LIKE '%token%'")
        results = cursor.fetchall()
        conn.close()
        
        print(f"✅ Found {len(results)} authentication items")
        for key in results:
            print(f"   - {key[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """Check if database was created successfully"""
    if os.path.exists(DB_PATH):
        print(f"✅ Database exists: {DB_PATH}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tables: {[t[0] for t in tables]}")
        
        # Check auth items
        cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%auth%' OR key LIKE '%token%'")
        auth_count = cursor.fetchone()[0]
        print(f"🔑 Authentication items: {auth_count}")
        
        conn.close()
        return True
    else:
        print(f"❌ Database not found at: {DB_PATH}")
        return False

def main():
    print("=" * 60)
    print("🚀 Cursor Fresh Install with Pre-Authentication")
    print("=" * 60)
    
    print("\n📋 This script will:")
    print("1. Create Cursor database with your authentication")
    print("2. Pre-load all tokens so Cursor opens logged in")
    print("3. Skip the sign-in screen")
    
    print("\n" + "=" * 60)
    
    # First, install Cursor if not already
    if not os.path.exists(r"C:\Users\yashw.000\AppData\Local\Programs\Cursor"):
        print("\n⚠️ Cursor not installed yet!")
        print("1. Please install from: https://cursor.com/downloads")
        print("2. Run this script again AFTER installation")
        input("\nPress Enter to open download page...")
        import webbrowser
        webbrowser.open("https://cursor.com/downloads")
        return
    
    print("\n✅ Cursor is installed")
    
    # Create database
    if create_cursor_database():
        print("\n" + "=" * 60)
        print("🎉 DATABASE READY!")
        print("\n📋 Next steps:")
        print("1. Open Cursor (it should show you're already logged in)")
        print("2. Check bottom left corner for your email")
        print("3. Test Chat/Agent features")
        print("\n⚠️ If it asks to sign in, use Option 3 in your tool")
    else:
        print("\n❌ Failed to create database")
        print("\nAlternative: Use your tool's Option 3 after opening Cursor")

if __name__ == "__main__":
    main()