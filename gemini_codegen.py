# gemini_codegen.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- PHASE 1: LOAD KEYS AND FIND A WORKING ONE ---

print("🚀 Starting Code Generator...")

# Load variables from the .env file
load_dotenv()

# Load all available API keys from the .env file into a list
api_keys = []
i = 1
while True:
    key = os.getenv(f"GOOGLE_API_KEY_{i}")
    if key:
        api_keys.append(key)
        i += 1
    else:
        break # Stop when the next numbered key isn't found

if not api_keys:
    print("❌ Critical Error: No API keys found in the format GOOGLE_API_KEY_1, etc.")
    exit()

print(f"🔑 Found {len(api_keys)} keys. Validating...")

# Loop through keys to find the first one that works
working_key_found = False
for i, key in enumerate(api_keys):
    print(f"--- Attempting with Key #{i + 1}...")
    try:
        # Configure the library with the current key to test it
        genai.configure(api_key=key)
        
        # Make a small, quick call to validate the key
        model = genai.GenerativeModel("models/gemini-2.5-flash") # Use a model from your available list
        model.generate_content("test", generation_config={'max_output_tokens': 5})
        
        print(f"✅ Success! Key #{i + 1} is active.")
        working_key_found = True
        break # Exit the loop as soon as we find a working key

    except Exception as e:
        print(f"❌ Failed. This key is likely invalid or disabled.")

if not working_key_found:
    print("\n🚨 Critical Error: None of the provided API keys are working. Halting script.")
    exit()

# --- PHASE 2: GENERATE THE CODE USING THE VALIDATED KEY ---

# The model is already configured and validated from the loop above
# We can just re-initialize the model object to be safe
model = genai.GenerativeModel("models/gemini-2.5-flash") 

def generate_cpp_code(prompt):
    """Generates C++ code using the successfully validated API key."""
    # Add some prompt engineering for better results
    engineered_prompt = f"You are an expert C++ developer. Write a simple and correct C++ program for the following task:\n\nTASK: {prompt}"
    response = model.generate_content(engineered_prompt)
    return response.text

# Test the function
prompt = "Write a C++ program to print Fibonacci numbers up to 100."
print("\n" + "="*50)
print("Prompt:", prompt)
print("="*50)

# Generate and print the code
generated_code = generate_cpp_code(prompt)
print("✅ Generated C++ Code:\n", generated_code)