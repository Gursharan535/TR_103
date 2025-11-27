import pandas as pd
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

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
# Sample C++ dataset for prompt-code completion
data = [
    {
        "prompt": "Write a C++ program to add two numbers.",
        "completion": "#include<iostream>\nusing namespace std;\nint main() {\n  int a = 5, b = 10;\n  cout << a + b;\n  return 0;\n}"
    },
    {
        "prompt": "Write a C++ function to check if a number is prime.",
        "completion": "bool isPrime(int n) {\n  if(n <= 1) return false;\n  for(int i=2; i*i<=n; i++)\n    if(n % i == 0) return false;\n  return true;\n}"
    }
]

# Save to DataFrame
df = pd.DataFrame(data)
df.to_csv("cpp_code_generation.csv", index=False)

# Convert to JSONL format
def save_jsonl(df, filename):
    with open(filename, "w") as f:
        for _, row in df.iterrows():
            entry = {
                "messages": [
                    {"role": "user", "content": row['prompt']},
                    {"role": "model", "content": row['completion']}
                ]
            }
            f.write(json.dumps(entry) + "\n")

# 80-20 split
train_df = df.sample(frac=0.8, random_state=42)
test_df = df.drop(train_df.index)

save_jsonl(train_df, "train_cpp.jsonl")
save_jsonl(test_df, "test_cpp.jsonl")