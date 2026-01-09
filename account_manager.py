import os
import json
import sys
from colorama import Fore, Style, init
from cursor_auth import CursorAuth

# Initialize colorama
init()

# Define emoji constants
EMOJI = {
    'ACCOUNT': '👤',
    'SWITCH': '🔀',
    'LIST': '📋',
    'DELETE': '🗑️',
    'AUTO': '🤖',
    'ADD': '➕',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'INFO': 'ℹ️',
    'WARN': '⚠️',
    'ARROW': '➜'
}

def switch_account_menu(translator):
    """Menu for switching between saved accounts"""
    print(f"\n{Fore.CYAN}{EMOJI['SWITCH']} Switch Cursor Account{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    
    auth = CursorAuth(translator)
    
    if not auth.accounts:
        print(f"{Fore.YELLOW}{EMOJI['WARN']} No accounts saved{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['INFO']} Use Option 3 (Google Auth) to add accounts{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}{EMOJI['LIST']} Select account to switch to:{Style.RESET_ALL}")
    
    accounts_list = list(auth.accounts.keys())
    for i, account_id in enumerate(accounts_list, 1):
        account = auth.accounts[account_id]
        current = " ⭐" if account_id == auth.current_account else ""
        print(f"{i}. {account_id}{current}")
        print(f"   Email: {account['email']}")
        print(f"   Usage: {account['usage']:,} tokens")
    
    try:
        choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}Select account (1-{len(accounts_list)}): {Style.RESET_ALL}")
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(accounts_list):
                selected_account = accounts_list[choice_num - 1]
                print(f"\n{Fore.CYAN}{EMOJI['SWITCH']} Switching to: {selected_account}{Style.RESET_ALL}")
                
                # Ask for confirmation
                confirm = input(f"{EMOJI['ARROW']} {Fore.YELLOW}Close Cursor and switch? (y/N): {Style.RESET_ALL}").lower()
                if confirm == 'y':
                    success = auth.switch_account(selected_account)
                    if success:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Switched to {selected_account}{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{EMOJI['INFO']} Open Cursor to use this account{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to switch account{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Cancelled{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Invalid selection{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Please enter a number{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error: {e}{Style.RESET_ALL}")

def list_accounts_menu(translator):
    """Menu for listing all saved accounts"""
    print(f"\n{Fore.CYAN}{EMOJI['LIST']} Saved Accounts{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 60}{Style.RESET_ALL}")
    
    auth = CursorAuth(translator)
    auth.list_accounts()
    
    if auth.accounts:
        total_accounts = len(auth.accounts)
        total_tokens = sum(acc['usage'] for acc in auth.accounts.values())
        total_capacity = total_accounts * 50000
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"{EMOJI['INFO']} Summary:")
        print(f"  • Total accounts: {total_accounts}")
        print(f"  • Total tokens used: {total_tokens:,}")
        print(f"  • Monthly capacity: {total_capacity:,} tokens")
        print(f"  • Remaining capacity: {total_capacity - total_tokens:,} tokens")
        
        # Usage recommendations
        if total_tokens > total_capacity * 0.8:
            print(f"\n{Fore.YELLOW}{EMOJI['WARN']} Warning: High usage!{Style.RESET_ALL}")
            print(f"  Consider adding more accounts with Option 3")
        elif total_tokens > total_capacity * 0.5:
            print(f"\n{Fore.CYAN}{EMOJI['INFO']} Moderate usage{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Good capacity remaining{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{EMOJI['WARN']} No accounts saved{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} To add accounts:{Style.RESET_ALL}")
        print(f"  1. Use Option 3: Register with Google Account")
        print(f"  2. When asked, give the account a name (e.g., 'cursor1', 'work')")
        print(f"  3. Repeat for multiple accounts")

def delete_account_menu(translator):
    """Menu for deleting saved accounts"""
    print(f"\n{Fore.CYAN}{EMOJI['DELETE']} Delete Account{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 40}{Style.RESET_ALL}")
    
    auth = CursorAuth(translator)
    
    if not auth.accounts:
        print(f"{Fore.YELLOW}{EMOJI['WARN']} No accounts to delete{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}{EMOJI['LIST']} Select account to delete:{Style.RESET_ALL}")
    
    accounts_list = list(auth.accounts.keys())
    for i, account_id in enumerate(accounts_list, 1):
        account = auth.accounts[account_id]
        print(f"{i}. {account_id}")
        print(f"   Email: {account['email']}")
        print(f"   Created: {account['created']}")
    
    try:
        choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}Select account (1-{len(accounts_list)}): {Style.RESET_ALL}")
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(accounts_list):
                selected_account = accounts_list[choice_num - 1]
                
                # Show warning if this is the current account
                if selected_account == auth.current_account:
                    print(f"{Fore.YELLOW}{EMOJI['WARN']} This is your current active account!{Style.RESET_ALL}")
                
                # Ask for confirmation
                confirm = input(f"{EMOJI['ARROW']} {Fore.RED}DELETE account '{selected_account}'? (type 'DELETE' to confirm): {Style.RESET_ALL}")
                if confirm == 'DELETE':
                    success = auth.delete_account(selected_account)
                    if success:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Account '{selected_account}' deleted{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Failed to delete account{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Cancelled{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Invalid selection{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Please enter a number{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error: {e}{Style.RESET_ALL}")

def auto_switch_menu(translator):
    """Menu for auto-switching to account with lowest usage"""
    print(f"\n{Fore.CYAN}{EMOJI['AUTO']} Auto-switch to Lowest Usage Account{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
    
    auth = CursorAuth(translator)
    
    if not auth.accounts:
        print(f"{Fore.YELLOW}{EMOJI['WARN']} No accounts available{Style.RESET_ALL}")
        return
    
    # Find account with lowest usage
    lowest_account = auth.get_lowest_usage_account()
    if not lowest_account:
        print(f"{Fore.RED}{EMOJI['ERROR']} Could not find account{Style.RESET_ALL}")
        return
    
    account_data = auth.accounts[lowest_account]
    
    print(f"{EMOJI['INFO']} Analysis:")
    print(f"  • Total accounts: {len(auth.accounts)}")
    
    # Show usage for all accounts
    print(f"\n{EMOJI['LIST']} Account usage:")
    sorted_accounts = sorted(auth.accounts.items(), key=lambda x: x[1]["usage"])
    
    for account_id, data in sorted_accounts:
        usage_pct = (data["usage"] / 50000) * 100
        bar = "█" * int(usage_pct / 5) + "░" * (20 - int(usage_pct / 5))
        current = " ⭐" if account_id == auth.current_account else ""
        print(f"  {account_id}{current}: {data['usage']:,} tokens")
        print(f"    [{bar}] {usage_pct:.1f}%")
    
    print(f"\n{EMOJI['AUTO']} Recommended switch:")
    print(f"  • Account: {lowest_account}")
    print(f"  • Email: {account_data['email']}")
    print(f"  • Usage: {account_data['usage']:,} tokens (lowest)")
    
    # Ask for confirmation
    confirm = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}Switch to '{lowest_account}'? (y/N): {Style.RESET_ALL}").lower()
    if confirm == 'y':
        success = auth.switch_account(lowest_account)
        if success:
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Switched to {lowest_account}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} Open Cursor to use this account{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Failed to switch account{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{EMOJI['INFO']} Cancelled{Style.RESET_ALL}")

if __name__ == "__main__":
    # Test the functions
    class TestTranslator:
        def get(self, key, **kwargs):
            return key
    
    translator = TestTranslator()
    print("Testing account manager...")
    list_accounts_menu(translator)