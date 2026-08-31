import os
import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.skipif(not os.getenv("HF_TOKEN"), reason="HF_TOKEN is missing from backend/.env")
def test_hf_recommendation():
    token = os.getenv("HF_TOKEN")
    from huggingface_hub import InferenceClient

    model = "Qwen/Qwen3-4B-Instruct-2507"
    client = InferenceClient(api_key=token, provider="nscale")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an agricultural advisory assistant."},
            {
                "role": "user",
                "content": "A tomato crop has leaf mold with 55% affected area. Humidity is 67% and temperature is 18.4 C. Give concise treatment advice.",
            },
        ],
        max_tokens=200,
        temperature=0.2,
    )

    assert response.choices
    assert response.choices[0].message.content

