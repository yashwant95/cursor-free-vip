import subprocess
import time

# List of aliases to authenticate
aliases = [
    "yashwant1ins+cursor1@gmail.com",
    "yashwant1ins+cursor2@gmail.com",
    "yashwant1ins+cursor3@gmail.com",
    "yashwant1ins+cursor4@gmail.com",
    "yashwant1ins+cursor5@gmail.com",
]

def authenticate_account(alias):
    """Run authentication for one account"""
    print(f"\n🔐 Authenticating: {alias}")
    print("-" * 40)
    
    # This assumes your tool can be automated
    # You might need to modify your tool to accept email as parameter
    
    # For now, manual steps:
    print("Manual steps:")
    print(f"1. Run your tool → Option 3")
    print(f"2. Enter email: {alias}")
    print(f"3. Check yashwant1ins@gmail.com for verification")
    print(f"4. Complete OAuth flow")
    
    input(f"Press Enter after authenticating {alias}...")

print("🚀 Cursor Account Authenticator")
print("=" * 50)
print(f"Base email: yashwant1ins@gmail.com")
print(f"Total accounts to create: {len(aliases)}")
print(f"Total tokens/month: {len(aliases) * 50000:,}")
print("=" * 50)

for i, alias in enumerate(aliases, 1):
    print(f"\n📋 Account {i}/{len(aliases)}")
    authenticate_account(alias)

print("\n" + "=" * 50)
print("🎉 AUTHENTICATION COMPLETE!")
print(f"✅ Created {len(aliases)} Cursor accounts")
print(f"💰 Total capacity: {len(aliases) * 50000:,} tokens/month")
print("\n📋 Account List:")
for alias in aliases:
    print(f"  • {alias}")