# account_manager.py
import json
import sqlite3
import time
from datetime import datetime, timedelta
import requests
from colorama import Fore, Style
from cursor_auth import CursorAuth

class AccountManager:
    def __init__(self, translator=None):
        self.translator = translator
        self.db_path = "cursor_accounts.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize the accounts database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            token TEXT NOT NULL,
            profile_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            total_used INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            chrome_profile TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            check_time TIMESTAMP,
            used_count INTEGER,
            total_limit INTEGER,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_account(self, email, token, chrome_profile=None, profile_name=None):
        """Add a new account to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO accounts 
            (email, token, chrome_profile, profile_name, last_used, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, token, chrome_profile, profile_name, datetime.now(), 1))
            
            conn.commit()
            print(f"{Fore.GREEN}✅ Account added: {email}{Style.RESET_ALL}")
            return cursor.lastrowid
        except Exception as e:
            print(f"{Fore.RED}❌ Error adding account: {e}{Style.RESET_ALL}")
            return None
        finally:
            conn.close()
    
    def get_active_accounts(self):
        """Get all active accounts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, email, token, chrome_profile, profile_name, total_used 
        FROM accounts 
        WHERE is_active = 1 
        ORDER BY total_used ASC, last_used ASC
        ''')
        
        accounts = []
        for row in cursor.fetchall():
            accounts.append({
                'id': row[0],
                'email': row[1],
                'token': row[2],
                'chrome_profile': row[3],
                'profile_name': row[4],
                'total_used': row[5]
            })
        
        conn.close()
        return accounts
    
    def get_current_account(self):
        """Get the currently active account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, email, token, chrome_profile 
        FROM accounts 
        WHERE is_active = 1 
        ORDER BY last_used DESC 
        LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'token': row[2],
                'chrome_profile': row[3]
            }
        return None
    
    def update_usage(self, account_id, used_count, total_limit):
        """Update usage statistics for an account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update account
        cursor.execute('''
        UPDATE accounts 
        SET total_used = ?, last_used = ?
        WHERE id = ?
        ''', (used_count, datetime.now(), account_id))
        
        # Add to history
        cursor.execute('''
        INSERT INTO usage_history (account_id, check_time, used_count, total_limit)
        VALUES (?, ?, ?, ?)
        ''', (account_id, datetime.now(), used_count, total_limit))
        
        conn.commit()
        conn.close()
        
        print(f"{Fore.CYAN}📊 Usage updated: {used_count}/{total_limit}{Style.RESET_ALL}")
    
    def deactivate_account(self, account_id):
        """Deactivate an account (mark as expired)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE accounts SET is_active = 0 WHERE id = ?
        ''', (account_id,))
        
        conn.commit()
        conn.close()
        print(f"{Fore.YELLOW}⚠️  Account deactivated: {account_id}{Style.RESET_ALL}")
    
    def switch_to_account(self, account_id):
        """Switch to a specific account (update Cursor config)"""
        account = self.get_account_by_id(account_id)
        if not account:
            return False
        
        # Update Cursor authentication
        auth_manager = CursorAuth(self.translator)
        if auth_manager.update_auth(
            email=account['email'],
            access_token=account['token'],
            refresh_token=account['token']
        ):
            # Update last used timestamp
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE accounts SET last_used = ? WHERE id = ?', 
                          (datetime.now(), account_id))
            conn.commit()
            conn.close()
            
            print(f"{Fore.GREEN}✅ Switched to account: {account['email']}{Style.RESET_ALL}")
            return True
        
        return False
    
    def get_account_by_id(self, account_id):
        """Get account details by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, email, token FROM accounts WHERE id = ?', (account_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {'id': row[0], 'email': row[1], 'token': row[2]}
        return None