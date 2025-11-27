# advanced_gemini_codegen.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

# === Load Gemini API Key ===
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


# === Initialize Gemini Model ===
model = genai.GenerativeModel("models/gemini-2.5-flash")

# === Multiline Input Helper ===
def read_multiline_input(prompt):
    print(prompt)
    print("👉 Paste your code. Press Enter twice to finish.")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

# === 1. Generate Simple C++ Code ===
def generate_cpp_code(task_prompt):
    engineered_prompt = (
        "You are an expert C++ developer. Write a very simple, clean and readable C++ code for the following task:\n\n"
        + task_prompt
    )
    response = model.generate_content(engineered_prompt)
    return response.text

# === 2. Optimize C++ Code ===
def optimize_cpp_code(code):
    prompt = (
        "Optimize the following C++ code for readability, performance, and simplicity. Add comments where necessary:\n\n"
        + code
    )
    response = model.generate_content(prompt)
    return response.text

# === 3. Debug C++ Code ===
def debug_cpp_code(code):
    prompt = (
        "The following C++ code contains bugs. Fix them and explain the changes:\n\n"
        + code
    )
    response = model.generate_content(prompt)
    return response.text

# === Main App Logic ===
def main():
    print("\n🧠 Welcome to Gemini C++ Assistant (Full Flow)")

    # Step 1: C++ Code Generation
    task = input("\n💬 Enter the task you want a C++ program for: ")
    generated_code = generate_cpp_code(task)
    print("\n✅ Generated Simple C++ Code:\n", generated_code)

    # Step 2: Ask if user wants optimization
    choice_opt = input("\n⚙️ Do you want to optimize this code? (y/n): ").strip().lower()
    if choice_opt == "y":
        optimized_code = optimize_cpp_code(generated_code)
        print("\n🚀 Optimized C++ Code:\n", optimized_code)
    else:
        optimized_code = generated_code

    # Step 3: Ask if user wants debugging
    choice_debug = input("\n🧪 Do you want to debug this code? (y/n): ").strip().lower()
    if choice_debug == "y":
        use_last = input("🔍 Use the above optimized/generated code? (y/n): ").strip().lower()
        if use_last == "y":
            code_to_debug = optimized_code
        else:
            code_to_debug = read_multiline_input("\n📥 Paste your buggy C++ code:")
        debugged_code = debug_cpp_code(code_to_debug)
        print("\n🔧 Debugged Code and Explanation:\n", debugged_code)

    print("\n✅ Session complete. You can re-run for another task.")

# === Run It ===
if __name__ == "__main__":
    main()