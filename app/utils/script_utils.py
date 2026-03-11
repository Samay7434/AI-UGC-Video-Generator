def parse_script(script_text):
    hook = ""
    body = ""
    cta = ""

    # Match HOOK section
    hook_match = re.search(r"HOOK:(.*?)(BODY:|CTA:)", script_text, re.S)

    # Match BODY section
    body_match = re.search(r"BODY:(.*?)(CTA:)", script_text, re.S)

    # Match CTA section
    cta_match = re.search(r"CTA:(.*)", script_text, re.S)

    if hook_match:
        hook = hook_match.group(1).strip()

    if body_match:
        body = body_match.group(1).strip()

    if cta_match:
        cta = cta_match.group(1).strip()

    return {
        "hook": hook,
        "body": body,
        "cta": cta
    }


import re

def clean_for_voice(text):
    # remove stage directions (anything in brackets)
    text = re.sub(r"\(.*?\)", "", text)

    # remove narrator labels
    text = re.sub(r"(?i)narrator:?", "", text)

    # remove extra labels
    text = re.sub(r"(?i)here is.*?:", "", text)

    # collapse spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def build_voice_text(parsed):
    combined = f"{parsed['hook']} {parsed['body']} {parsed['cta']}"
    return clean_for_voice(combined)