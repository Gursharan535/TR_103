import google.generativeai as genai
from dotenv import load_dotenv
import os

# === Load and Configure the Gemini API Key ===
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
# Using a model from your available list
model = genai.GenerativeModel("models/gemini-2.5-flash")

# === 1. Generate a Base Travel Itinerary ===
def generate_base_itinerary(destination, duration, season):
    """Generates a high-level, day-by-day itinerary."""
    engineered_prompt = f"""
    You are a helpful and experienced travel agent.
    Create a balanced, day-by-day travel itinerary for a trip to '{destination}' for '{duration}' days during the '{season}' season.
    Focus on a logical flow of activities and include a mix of popular sights and local experiences.
    Keep the descriptions for each day brief and clear.
    """
    print("🧠 Generating a base itinerary...")
    response = model.generate_content(engineered_prompt)
    return response.text

# === 2. Enrich the Itinerary with Specific Interests ===
def enrich_itinerary(base_itinerary, interests):
    """Adds specific activities to an existing itinerary based on user interests."""
    prompt = f"""
    Given the following base travel itinerary, enrich it with specific suggestions based on the user's interests.
    User's Interests: '{interests}'.

    For each day in the itinerary, add 1-2 specific activity suggestions (like a particular museum, restaurant, hiking trail, or market) that align with the user's interests.
    Do not change the original structure or flow. Integrate your suggestions smoothly into the existing plan.

    Base Itinerary:
    ---
    {base_itinerary}
    ---
    """
    print("🎨 Enriching the itinerary with your interests...")
    response = model.generate_content(prompt)
    return response.text

# === 3. Create a Smart Packing List ===
def create_packing_list(final_itinerary, destination, season):
    """Generates a context-aware packing list based on the planned activities."""
    prompt = f"""
    You are a practical and seasoned traveler. Based on the following finalized travel itinerary for a trip to '{destination}' during the '{season}', create a smart, categorized packing list.
    The list should be practical and consider the specific activities mentioned in the plan.
    Use categories like 'Clothing', 'Electronics', 'Documents', and 'Miscellaneous'.

    Final Itinerary:
    ---
    {final_itinerary}
    ---
    """
    print("🎒 Creating a smart packing list...")
    response = model.generate_content(prompt)
    return response.text

# === Main Application Logic ===
def main():
    """Controls the interactive user flow of the travel planner."""
    print("\n✈️ Welcome to the Gemini Travel Itinerary Planner!")

    # Step 1: Generate the base itinerary
    destination = input("\n📍 Where would you like to go? (e.g., Kyoto, Japan): ")
    duration = input("📅 How many days will your trip be? (e.g., 5): ")
    season = input("☀️ What season will you be traveling in? (e.g., Spring): ")
    
    base_itinerary = generate_base_itinerary(destination, duration, season)
    print("\n✅ Here is your base itinerary:\n", base_itinerary)

    # Step 2: Ask if the user wants to enrich the itinerary
    choice_enrich = input("\n✨ Do you want to add specific activities based on your interests? (y/n): ").strip().lower()
    if choice_enrich == 'y':
        interests = input("👍 What are your interests? (e.g., history, foodie, hiking, art): ")
        enriched_itinerary = enrich_itinerary(base_itinerary, interests)
        print("\n✅ Here is your enriched, personalized itinerary:\n", enriched_itinerary)
    else:
        enriched_itinerary = base_itinerary # If they say no, the final plan is the base plan

    # Step 3: Ask if the user wants a packing list
    choice_pack = input("\n🧳 Do you want a smart packing list for this trip? (y/n): ").strip().lower()
    if choice_pack == 'y':
        packing_list = create_packing_list(enriched_itinerary, destination, season)
        print("\n✅ Here is your suggested packing list:\n", packing_list)

    print("\n🎉 Have a wonderful trip! Your planning session is complete.")

# === Run the Application ===
if __name__ == "__main__":
    main()