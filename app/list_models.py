from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load .env from the project root directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def main():
    print("Listing models available on the API key...")
    try:
        client = genai.Client()
        # List models
        models = client.models.list()
        for m in models:
            print(f"Model Name: {m.name}")
            print(f"Supported Actions: {m.supported_actions}")
            print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
