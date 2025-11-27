import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, HfApi

# ✅ BEST FREE MODEL FOR TEXT-TO-IMAGE
MODEL_NAME = "stabilityai/stable-diffusion-xl-base-1.0"

def load_and_validate_tokens():
    load_dotenv()
    
    tokens = []
    i = 1
    while True:
        token = os.getenv(f"HUGGINGFACE_TOKEN_{i}")
        if token:
            tokens.append(token)
            i += 1
        else:
            break

    if not tokens:
        print("❌ No Hugging Face tokens found in .env")
        return None

    print(f"🔍 Found {len(tokens)} tokens. Validating...")

    for idx, token in enumerate(tokens):
        print(f"\n--- Validating Token #{idx + 1} ---")
        try:
            api = HfApi(token=token)
            info = api.whoami()
            print(f"✅ Valid token: {info['name']}")
            return token
        except Exception as e:
            print(f"❌ Invalid token: {e}")

    return None


def generate_image(prompt: str, token: str, output_path="output.png"):
    print("\n--- Generating Image ---")

    try:
        # ✅ Use model directly in client (VERY IMPORTANT)
        client = InferenceClient(
            model=MODEL_NAME,
            token=token
        )

        print("⏳ Generating image using Free Hugging Face Serverless API...")

        img = client.text_to_image(prompt)
        img.save(output_path)

        print(f"✅ Image saved successfully: {output_path}")

    except Exception as e:
        print(f"❌ ERROR while generating image: {e}")


if __name__ == "__main__":
    token = load_and_validate_tokens()
    
    if token:
        prompt = input("Enter your image prompt: ")
        if prompt.strip():
            generate_image(prompt, token)
        else:
            print("⚠️ No prompt entered.")
    else:
        print("🚨 No valid token available.")
