import os
import requests
import base64
from datetime import datetime
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Define the output directory
OUTPUT_DIR = r"C:\Users\SPT\Desktop\TR-103"

def load_and_validate_stability_key():
    """
    Loads keys from .env and checks if they are valid by querying the balance endpoint.
    """
    load_dotenv()
    
    keys = []
    i = 1
    while True:
        key = os.getenv(f"STABILITY_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break

    if not keys:
        print("❌ No STABILITY_API_KEY found in .env")
        return None

    print(f"🔑 Found {len(keys)} Stability AI keys. Validating...")

    for idx, key in enumerate(keys):
        print(f"\n--- Validating Key #{idx + 1} ---")
        try:
            # Check balance to validate key (doesn't cost credits)
            url = "https://api.stability.ai/v1/user/balance"
            response = requests.get(url, headers={"Authorization": f"Bearer {key}"})

            if response.status_code == 200:
                balance = response.json().get('credits', 0)
                print(f"✅ Valid Key! Current Balance: {balance} credits")
                if balance < 1:
                    print("⚠️ Warning: Low balance.")
                return key
            else:
                print(f"❌ Invalid Key (Status {response.status_code})")
        except Exception as e:
            print(f"❌ Error checking key: {e}")

    return None

def generate_image(prompt: str, api_key: str):
    print("\n--- Generating Image with Stability AI ---")
    
    # SDXL Endpoint
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30
    }

    print("⏳ Sending request to Stability AI...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        
        # Ensure output directory exists
        if not os.path.exists(OUTPUT_DIR):
            try:
                os.makedirs(OUTPUT_DIR)
                print(f"fv Created directory: {OUTPUT_DIR}")
            except OSError as e:
                print(f"❌ Error creating directory: {e}")
                return

        for i, image_obj in enumerate(data["artifacts"]):
            # Decode Base64
            image_base64 = image_obj["base64"]
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}_{i}.png"
            output_path = os.path.join(OUTPUT_DIR, filename)

            # Save and Show
            image.save(output_path)
            print(f"✅ Image saved to: {output_path}")
            image.show()
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    # 1. Find a working key
    valid_key = load_and_validate_stability_key()

    # 2. If key exists, ask for prompt and generate
    if valid_key:
        user_prompt = input("Enter your image description (prompt): ")
        if user_prompt.strip():
            generate_image(user_prompt, valid_key)
        else:
            print("⚠️ No prompt entered.")
    else:
        print("🚨 No valid Stability AI key available.")