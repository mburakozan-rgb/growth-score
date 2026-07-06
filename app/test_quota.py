from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load .env from the project root directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def test_model(model_name):
    print(f"Testing model: {model_name}...")
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello' in one word."
        )
        print(f"✓ Success! Response: {response.text}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}\n")
        return False

def main():
    models = [
        "gemini-2.0-flash-lite", 
        "gemini-2.5-flash-lite", 
        "gemini-3.1-flash-lite", 
        "gemini-3-flash-preview", 
        "gemma-4-31b-it"
    ]
    for m in models:
        test_model(m)

if __name__ == "__main__":
    main()
