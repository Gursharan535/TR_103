import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- PHASE 1: FIND A WORKING API KEY AND SETUP THE MODEL ---

def setup_model_with_fallback():
    """
    Loads API keys from .env and finds the first one that works to initialize the model.
    Returns the initialized model object or None if all keys fail.
    """
    load_dotenv()
    
    # Load all keys that follow the GOOGLE_API_KEY_n pattern
    api_keys = []
    i = 1
    while True:
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if key:
            api_keys.append(key)
            i += 1
        else:
            break
            
    if not api_keys:
        print("❌ Critical Error: No API keys found in the .env file.")
        return None

    print(f"🔑 Found {len(api_keys)} API keys. Now finding a working one...")
    
    # Loop through the keys and try to initialize the model with each one
    for i, key in enumerate(api_keys):
        print(f"\n--- Attempting with Key #{i + 1}...")
        try:
            genai.configure(api_key=key)
            # Use the model name from your original script
            model = genai.GenerativeModel("gemini-2.5-flash")
            # Make a small, low-cost call to validate that the key is working
            model.generate_content("test", generation_config={'max_output_tokens': 5})
            print(f"✅ Success! Key #{i + 1} is working.")
            return model # Return the successfully initialized model
        except Exception as e:
            print(f"❌ Failed. This key is likely invalid or has been disabled.")
            
    # If the loop completes without returning, all keys have failed
    return None

# --- PHASE 2: RUN THE EVALUATION ---

def run_evaluation():
    """
    Uses the initialized model to run prompts and display them with human ratings.
    """
    model = setup_model_with_fallback()
    
    # Check if model setup was successful
    if not model:
        print("\n🚨 Halting script: Could not initialize model with any of the provided API keys.")
        return # Exit the function

    # === Prompts to Evaluate ===
    print("\n📝 Generating responses for evaluation prompts...")
    prompts = ["Explain AI to a 5-year-old.", "Write a short, hopeful poem about the stars."]
    
    responses = []
    for prompt in prompts:
        try:
            response = model.generate_content(prompt)
            responses.append(response.text)
        except Exception as e:
            print(f"An error occurred while generating content for prompt: '{prompt}'")
            responses.append(f"--- ERROR: {e} ---") # Add an error message to the list

    # === Simulated Human Ratings ===
    # These correspond to the prompts above
    human_ratings = [4.5, 3.8]

    # --- PHASE 3: DISPLAY THE RESULTS ---
    
    print("\n" + "="*50)
    print("📊 Human Evaluation Results")
    print("="*50)
    
    for i, r in enumerate(responses):
        print(f"\nPrompt: {prompts[i]}\n\nResponse:\n{r}\n\nHuman Rating: {human_ratings[i]}/5.0")
        print("-"*30)

# --- This makes the script runnable from the command line ---
if __name__ == "__main__":
    run_evaluation()