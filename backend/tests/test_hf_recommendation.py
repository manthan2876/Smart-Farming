import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
token = os.getenv("HF_TOKEN")

if not token:
    raise RuntimeError("HF_TOKEN is missing from backend/.env")

MODEL = "Qwen/Qwen3-4B-Instruct-2507"
client = InferenceClient(api_key=token, provider="nscale")

print("=" * 70)
print("HUGGING FACE INFERENCE TEST")
print("=" * 70)
print(f"Model:\n{MODEL}")
print("Provider:\nnscale")
print("\nSending request...")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are an agricultural advisory assistant."},
        {"role": "user", "content": "A tomato crop has leaf mold with 55% affected area. Humidity is 67% and temperature is 18.4 C. Give concise treatment advice."},
    ],
    max_tokens=200,
    temperature=0.2,
)

print("\nResponse:")
print("-" * 70)
print(response.choices[0].message.content)
print("\n[SUCCESS] Hugging Face inference completed.")