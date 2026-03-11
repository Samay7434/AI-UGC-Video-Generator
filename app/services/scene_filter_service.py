import clip
import torch
from PIL import Image
import requests
from io import BytesIO

device = "cpu"

model, preprocess = clip.load("ViT-B/32", device=device)


def score_scene(image_url, text_query):

    try:
        image = Image.open(
            BytesIO(requests.get(image_url).content)
        ).convert("RGB")

        image_input = preprocess(image).unsqueeze(0).to(device)
        text_input = clip.tokenize([text_query]).to(device)

        with torch.no_grad():

            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_input)

            similarity = (image_features @ text_features.T).item()

        return similarity

    except:
        return -999
    
def filter_best_videos(videos, query, top_k=6):

    scored = []

    for v in videos:

        image_url = v["image"]

        score = score_scene(image_url, query)

        scored.append((score, v))

    scored.sort(reverse=True)

    best = [v for score, v in scored[:top_k]]

    return best

