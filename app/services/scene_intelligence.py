import re

def extract_keywords(text):

    text = text.lower()

    words = re.findall(r'\b[a-z]{4,}\b', text)

    stop_words = {
        "this","that","with","from","your","have","will",
        "make","more","just","like","into","about"
    }

    keywords = [w for w in words if w not in stop_words]

    return list(set(keywords))[:5]


def generate_scene_queries(parsed, product, tone):

    tone_map = {

        "gym": "gym workout fitness training exercise",
        "fitness": "gym workout training fitness lifestyle",
        "coding": "programming laptop workspace developer coding screen",
        "tech": "technology workspace laptop coding modern office",
        "gaming": "gaming setup rgb computer gamer desk",
        "travel": "travel adventure backpack hiking outdoor",
        "lifestyle": "modern lifestyle coffee workspace aesthetic",
        "business": "business office professional working laptop",
        "study": "student studying laptop desk books",
        "education": "student studying learning workspace",
        "fashion": "fashion lifestyle studio aesthetic",
        "beauty": "beauty skincare product lifestyle",
        "food": "food cooking kitchen preparation",
        "minimal": "minimal workspace aesthetic desk",
        "productivity": "productive workspace laptop working"
    }

    tone_keywords = tone_map.get(tone.lower(), tone)

    # HOOK
    hook_query = f"{product} aesthetic lifestyle inspiration"

    # BODY
    body_query = f"{product} {tone_keywords}"

    # CTA (product-focused instead of generic)
    cta_query = f"{product} product close up holding {product} happy customer"

    return {
        "hook": hook_query,
        "body": body_query,
        "cta": cta_query
    }