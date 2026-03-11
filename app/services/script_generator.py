import requests
import math

def generate_block(product, tone, words_per_block):
    prompt = f"""
    You are writing a UGC video ad.

    STRICT RULES:
    - Spoken dialogue only.
    - Around {words_per_block} words.
    - Keep HOOK, BODY, CTA format.
    - No explanations.

    Product: {product}
    Tone: {tone}

    Format:

    HOOK:
    ...

    BODY:
    ...

    CTA:
    ...
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def generate_script(product, tone, duration):

    target_words = int(duration * 3.5)
    blocks = math.ceil(target_words / 80)

    final_hook = ""
    final_body = ""
    final_cta = ""

    for i in range(blocks):
        block = generate_block(product, tone, int(target_words / blocks))

        if "HOOK:" in block and not final_hook:
            final_hook = block.split("HOOK:")[1].split("BODY:")[0].strip()

        if "BODY:" in block:
            body_part = block.split("BODY:")[1].split("CTA:")[0].strip()
            final_body += " " + body_part

        if "CTA:" in block:
            final_cta = block.split("CTA:")[1].strip()

    return f"""
HOOK:
{final_hook}

BODY:
{final_body.strip()}

CTA:
{final_cta}
"""