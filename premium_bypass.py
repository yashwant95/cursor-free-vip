import requests
import json

# Your working token
TOKEN = "user_01KDYKWSASHZ0RZ65WD8M9NRJT::eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfHVzZXJfMDFLRFlLV1NBU0haMFJaNjVXRDhNOU5SSlQiLCJ0aW1lIjoiMTc2NzkwMzU3NiIsInJhbmRvbW5lc3MiOiI0ZjI1NDQ2Zi0yOTYxLTQxYzciLCJleHAiOjE3NzMwODc1NzYsImlzcyI6Imh0dHBzOi8vYXV0aGVudGljYXRpb24uY3Vyc29yLnNoIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBvZmZsaW5lX2FjY2VzcyIsImF1ZCI6Imh0dHBzOi8vY3Vyc29yLmNvbSIsInR5cGUiOiJ3ZWIifQ.1GQh24EQ1zs3oMVP02WyBmP9JcLgIR4_xRXvjiTUdhc"

def bypass_premium():
    """Try to bypass premium checks via API"""
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Client-Version': '999.0.0',  # Fake version
        'X-Subscription-Tier': 'premium',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.cursor.com',
        'Referer': 'https://www.cursor.com/'
    }
    
    # Try to get premium status
    try:
        response = requests.get(
            'https://api.cursor.sh/v1/subscription',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Subscription data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Run it
bypass_premium()