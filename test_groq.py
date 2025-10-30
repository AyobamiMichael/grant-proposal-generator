"""


# ==================== test_groq.py ====================
# Quick test to verify Groq works

"""

from groq import Groq
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not found in .env file!")
    exit(1)

print("✅ API key loaded")
print(f"Key starts with: {api_key[:10]}...")


# Initialize client
client = Groq(api_key=api_key)
print("✅ Groq client initialized")



# Test API call
print("\n🧪 Testing Groq API...")
try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": "Say 'Hello from Groq!' and nothing else."}
        ],
        max_tokens=50,
        temperature=0.0
    )
    
    result = response.choices[0].message.content
    print(f"\n📨 Response: {result}")
    print("\n✅ Groq is working perfectly!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key is correct")
    print("2. Verify you have internet connection")
    print("3. Make sure you're within free tier limits")