def generate_scene_queries(parsed, product, tone):

    tone_map = {
        "gym": "gym workout fitness training",
        "coding": "programming laptop developer workspace",
        "tech": "modern technology workspace gadgets",
        "gaming": "gaming computer setup rgb lights",
        "travel": "travel adventure backpack journey",
        "lifestyle": "modern lifestyle daily routine aesthetic",
        "business": "business office laptop productivity",
        "study": "student studying laptop books desk",
        "food": "cooking kitchen preparation food",
        "fashion": "fashion lifestyle studio photoshoot",
        "fitness": "fitness workout gym exercise",
        "entrepreneur": "startup entrepreneur working laptop"
    }

    tone_query = tone_map.get(tone.lower(), tone)

    return {
        "hook": f"{tone_query} inspiration motivation",
        "body": f"{product} {tone_query}",
        "cta": f"{tone_query} success achievement"
    }