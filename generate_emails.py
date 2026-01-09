def generate_gmail_aliases(base_email, count=10):
    """Generate Gmail + aliases"""
    
    # Extract username (before @)
    username = base_email.split('@')[0]
    
    print("📧 Generated Gmail + Aliases:")
    print("=" * 50)
    
    aliases = []
    for i in range(1, count + 1):
        alias = f"{username}+cursor{i}@gmail.com"
        aliases.append(alias)
        print(f"{i}. {alias}")
    
    print("\n💡 All emails deliver to:", base_email)
    print(f"✅ You now have {count} 'separate' Cursor accounts!")
    
    # Save to file
    with open('cursor_accounts.txt', 'w') as f:
        for alias in aliases:
            f.write(f"{alias}\n")
    
    print("\n📁 Saved to: cursor_accounts.txt")
    
    return aliases

# Your base email
BASE_EMAIL = "yashwant1ins@gmail.com"

# Generate 10 aliases
aliases = generate_gmail_aliases(BASE_EMAIL, 10)

print("\n" + "=" * 50)
print("🚀 HOW TO USE:")
print("1. Run your tool → Option 3")
print("2. Use email: yashwant1ins+cursor1@gmail.com")
print("3. Verify with code sent to yashwant1ins@gmail.com")
print("4. Repeat for cursor2, cursor3, etc.")
print("5. Each gets 50K tokens → 10 accounts = 500K tokens/month!")