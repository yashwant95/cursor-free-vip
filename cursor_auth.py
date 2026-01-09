import sqlite3
import os
import sys
import json
import time
from colorama import Fore, Style, init
from config import get_config

# Initialize colorama
init()

# Define emoji and color constants
EMOJI = {
    'DB': '🗄️',
    'UPDATE': '🔄',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WARN': '⚠️',
    'INFO': 'ℹ️',
    'FILE': '📄',
    'KEY': '🔐',
    'ACCOUNT': '👤',
    'SWITCH': '🔀'
}

class CursorAuth:
    def __init__(self, translator=None):
        self.translator = translator
        self.current_account = None
        self.accounts_file = "cursor_accounts_data.json"
        
        # Get configuration
        config = get_config(translator)
        if not config:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('auth.config_error') if self.translator else 'Failed to load configuration'}{Style.RESET_ALL}")
            sys.exit(1)
            
        # Get path based on operating system
        try:
            if sys.platform == "win32":  # Windows
                if not config.has_section('WindowsPaths'):
                    raise ValueError("Windows paths not configured")
                self.db_path = config.get('WindowsPaths', 'sqlite_path')
                
            elif sys.platform == 'linux':  # Linux
                if not config.has_section('LinuxPaths'):
                    raise ValueError("Linux paths not configured")
                self.db_path = config.get('LinuxPaths', 'sqlite_path')
                
            elif sys.platform == 'darwin':  # macOS
                if not config.has_section('MacPaths'):
                    raise ValueError("macOS paths not configured")
                self.db_path = config.get('MacPaths', 'sqlite_path')
                
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('auth.unsupported_platform') if self.translator else 'Unsupported platform'}{Style.RESET_ALL}")
                sys.exit(1)
                
            # Verify if the path exists
            if not os.path.exists(os.path.dirname(self.db_path)):
                raise FileNotFoundError(f"Database directory not found: {os.path.dirname(self.db_path)}")
                
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} {self.translator.get('auth.path_error', error=str(e)) if self.translator else f'Error getting database path: {str(e)}'}{Style.RESET_ALL}")
            sys.exit(1)

        # Check if the database file exists
        if not os.path.exists(self.db_path):
            print(f"{Fore.YELLOW}{EMOJI['WARN']} {self.translator.get('auth.db_not_found', path=self.db_path) if self.translator else f'Database not found, will create: {self.db_path}'}{Style.RESET_ALL}")

        # Load existing accounts
        self.load_accounts()

    def load_accounts(self):
        """Load all saved accounts from file"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r') as f:
                    self.accounts = json.load(f)
                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Loaded {len(self.accounts)} accounts{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}{EMOJI['WARN']} Error loading accounts: {e}, creating new...{Style.RESET_ALL}")
                self.accounts = {}
        else:
            self.accounts = {}
            print(f"{Fore.CYAN}{EMOJI['INFO']} No accounts file found, starting fresh{Style.RESET_ALL}")

    def save_accounts(self):
        """Save all accounts to file"""
        try:
            with open(self.accounts_file, 'w') as f:
                json.dump(self.accounts, f, indent=2)
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Saved {len(self.accounts)} accounts{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error saving accounts: {e}{Style.RESET_ALL}")

    def update_auth(self, email=None, access_token=None, refresh_token=None, account_name=None):
        """Update authentication for specific account"""
        conn = None
        try:
            # Ensure the directory exists and set the correct permissions
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, mode=0o755, exist_ok=True)
            
            # If the database file does not exist, create a new one
            if not os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ItemTable (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                conn.commit()
                if sys.platform != "win32":
                    os.chmod(self.db_path, 0o644)
                conn.close()

            # Reconnect to the database
            conn = sqlite3.connect(self.db_path)
            print(f"{EMOJI['INFO']} {Fore.GREEN} {self.translator.get('auth.connected_to_database') if self.translator else 'Connected to Database'}{Style.RESET_ALL}")
            cursor = conn.cursor()
            
            # Add timeout and other optimization settings
            conn.execute("PRAGMA busy_timeout = 5000")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # If account_name is provided, use it as identifier
            account_id = account_name if account_name else email
            
            # Save account data
            if email and access_token:
                self.accounts[account_id] = {
                    "email": email,
                    "access_token": access_token,
                    "refresh_token": refresh_token if refresh_token else access_token,
                    "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_used": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "usage": 0
                }
                self.save_accounts()
                self.current_account = account_id
                print(f"{Fore.GREEN}{EMOJI['ACCOUNT']} Account saved: {account_id}{Style.RESET_ALL}")

            # Set the key-value pairs to update in Cursor database
            updates = []
            updates.append(("cursorAuth/cachedSignUpType", "Auth_0"))

            if email is not None:
                updates.append(("cursorAuth/cachedEmail", email))
            if access_token is not None:
                updates.append(("cursorAuth/accessToken", access_token))
            if refresh_token is not None:
                updates.append(("cursorAuth/refreshToken", refresh_token))

            # Use transactions to ensure data integrity
            cursor.execute("BEGIN TRANSACTION")
            try:
                for key, value in updates:
                    # Check if the key exists
                    cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key = ?", (key,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO ItemTable (key, value) 
                            VALUES (?, ?)
                        """, (key, value))
                    else:
                        cursor.execute("""
                            UPDATE ItemTable SET value = ?
                            WHERE key = ?
                        """, (value, key))
                    print(f"{EMOJI['INFO']} {Fore.CYAN} {self.translator.get('auth.updating_pair') if self.translator else 'Updating Key-Value Pair'} {key.split('/')[-1]}...{Style.RESET_ALL}")
                
                cursor.execute("COMMIT")
                print(f"{EMOJI['SUCCESS']} {Fore.GREEN}{self.translator.get('auth.database_updated_successfully') if self.translator else 'Database Updated Successfully'}{Style.RESET_ALL}")
                return True
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e

        except sqlite3.Error as e:
            print(f"\n{EMOJI['ERROR']} {Fore.RED} {self.translator.get('auth.database_error', error=str(e)) if self.translator else f'Database Error: {str(e)}'}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"\n{EMOJI['ERROR']} {Fore.RED} {self.translator.get('auth.an_error_occurred', error=str(e)) if self.translator else f'An error occurred: {str(e)}'}{Style.RESET_ALL}")
            return False
        finally:
            if conn:
                conn.close()
                print(f"{EMOJI['DB']} {Fore.CYAN} {self.translator.get('auth.database_connection_closed') if self.translator else 'Database Connection Closed'}{Style.RESET_ALL}")

    def switch_account(self, account_id):
        """Switch to a different saved account"""
        if account_id not in self.accounts:
            print(f"{Fore.RED}{EMOJI['ERROR']} Account not found: {account_id}{Style.RESET_ALL}")
            return False
        
        account = self.accounts[account_id]
        
        # Close Cursor if running
        if sys.platform == "win32":
            os.system('taskkill /f /im cursor.exe 2>nul')
        
        print(f"{Fore.CYAN}{EMOJI['SWITCH']} Switching to account: {account_id}{Style.RESET_ALL}")
        
        # Update Cursor database with this account's tokens
        success = self.update_auth(
            email=account["email"],
            access_token=account["access_token"],
            refresh_token=account["refresh_token"],
            account_name=account_id
        )
        
        if success:
            self.current_account = account_id
            account["last_used"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.save_accounts()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Switched to account: {account_id}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} Open Cursor to use this account{Style.RESET_ALL}")
        
        return success

    def list_accounts(self):
        """List all saved accounts"""
        if not self.accounts:
            print(f"{Fore.YELLOW}{EMOJI['WARN']} No accounts saved{Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}{EMOJI['ACCOUNT']} Saved Accounts ({len(self.accounts)}):{Style.RESET_ALL}")
        print("-" * 60)
        
        for i, (account_id, data) in enumerate(self.accounts.items(), 1):
            current = " ⭐" if account_id == self.current_account else ""
            print(f"{i}. {account_id}{current}")
            print(f"   Email: {data['email']}")
            print(f"   Created: {data['created']}")
            print(f"   Last used: {data['last_used']}")
            print(f"   Usage: {data['usage']:,} tokens")
            print()

    def delete_account(self, account_id):
        """Delete a saved account"""
        if account_id not in self.accounts:
            print(f"{Fore.RED}{EMOJI['ERROR']} Account not found: {account_id}{Style.RESET_ALL}")
            return False
        
        del self.accounts[account_id]
        self.save_accounts()
        
        if self.current_account == account_id:
            self.current_account = None
        
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Deleted account: {account_id}{Style.RESET_ALL}")
        return True

    def update_usage(self, account_id, tokens_used):
        """Update token usage for an account"""
        if account_id in self.accounts:
            self.accounts[account_id]["usage"] += tokens_used
            self.save_accounts()
            print(f"{Fore.CYAN}{EMOJI['INFO']} Updated usage for {account_id}: {self.accounts[account_id]['usage']:,} tokens{Style.RESET_ALL}")

    def get_lowest_usage_account(self):
        """Get account with lowest token usage"""
        if not self.accounts:
            return None
        
        # Sort by usage (lowest first)
        sorted_accounts = sorted(self.accounts.items(), key=lambda x: x[1]["usage"])
        return sorted_accounts[0][0]  # Return account_id

    def auto_switch(self):
        """Automatically switch to account with lowest usage"""
        if not self.accounts:
            print(f"{Fore.YELLOW}{EMOJI['WARN']} No accounts available{Style.RESET_ALL}")
            return False
        
        account_id = self.get_lowest_usage_account()
        if account_id:
            return self.switch_account(account_id)
        
        return False