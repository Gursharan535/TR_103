# AB_Testing.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- PHASE 1: SETUP AND FIND A WORKING API KEY ---

print("🚀 Starting Test Script...")

# Load variables from the .env file
load_dotenv()

# Load all available API keys into a list
api_keys = []
for i in range(1, 7): # Tries to load keys GOOGLE_API_KEY_1 through 6
    key = os.getenv(f"GOOGLE_API_KEY_{i}")
    if key:
        api_keys.append(key)

if not api_keys:
    print("❌ Critical Error: No API keys found in the .env file.")
    exit()

print(f"🔑 Found {len(api_keys)} API keys. Now finding a working one...")

# Loop through keys to find the first one that works
working_api_key = None
for i, key in enumerate(api_keys):
    print(f"\n--- Attempting with Key #{i + 1}...")
    try:
        genai.configure(api_key=key)
        # Make a tiny, cheap test call to validate the key
        test_model = genai.GenerativeModel('models/gemini-2.5-flash')
        test_model.generate_content("test", generation_config={'max_output_tokens': 5})
        
        # If the call above succeeds, we have our key
        print(f"✅ Success! Key #{i + 1} is working.")
        working_api_key = key
        break # Exit the loop as soon as we find a working key

    except Exception as e:
        print(f"❌ Failed. This key is likely invalid or has been disabled.")

# After the loop, check if we found a working key
if not working_api_key:
    print("\n🚨 Critical Error: All API keys failed. Cannot proceed with prompt testing.")
    exit()


# --- PHASE 2: PERFORM A/B PROMPT TESTING WITH THE WORKING KEY ---

print("\n" + "="*50)
print("⚡️ Proceeding to A/B Prompt Test using the validated key.")
print("="*50)

# The model is already configured with the working key from the loop above
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Define our two different prompts for the test
character_class = "a rogue assassin from a fallen kingdom"

# Prompt A: Simple and direct
prompt_a = f"Write a backstory for {character_class}."

# Prompt B: More detailed with specific requirements
prompt_b = f"""
Write a compelling backstory for {character_class}.
Please include these three elements in the story:
1. A hidden secret they carry.
2. A motivation for their actions (e.g., revenge, redemption).
3. A mentor who taught them their skills.
"""

try:
    print("\nGenerating response for Prompt A (Simple)...")
    response_a = model.generate_content(prompt_a)

    print("Generating response for Prompt B (Detailed)...")
    response_b = model.generate_content(prompt_b)

    # --- PHASE 3: DISPLAY RESULTS AND GET USER FEEDBACK ---

    print("\n" + "🟥" * 20)
    print("Prompt A Output (Simple Request):")
    print("🟥" * 20)
    print(response_a.text)

    print("\n" + "🟦" * 20)
    print("Prompt B Output (Detailed Request):")
    print("🟦" * 20)
    print(response_b.text)

    print("\n" + "="*50)
    choice = input("👉 Which backstory is more interesting and useful? (A/B): ")

    if choice.strip().upper() == "A":
        print("\n✅ You selected Prompt A. Sometimes simple is best!")
    elif choice.strip().upper() == "B":
        print("\n✅ You selected Prompt B. More detailed prompts often yield better results!")
    else:
        print("\n❌ Invalid input.")

except Exception as e:
    print(f"\n🚨 An error occurred during content generation: {e}")