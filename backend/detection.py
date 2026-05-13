import torch
from torchvision import transforms
from PIL import Image, ImageOps
import tempfile
import os

from detector_config import (
    ALLOW_LOCAL_MODEL_FALLBACK,
    IMAGE_DETECTOR_BACKEND,
    IMAGE_FAKE_THRESHOLD,
    IMAGE_UNCERTAIN_MARGIN,
)
from model_loader import get_image_model


def build_image_insight(result, confidence, fake_score, real_score):
    margin = abs(fake_score - real_score) * 100

    if confidence >= 90:
        certainty = "High"
    elif confidence >= 70:
        certainty = "Moderate"
    else:
        certainty = "Low"

    if result == "Uncertain":
        summary = "The detector did not find a large enough gap between fake and real evidence."
    elif certainty == "Low":
        summary = "The model is not strongly confident. Treat this as a signal, not a final judgement."
    elif result == "Fake":
        summary = "The image contains patterns the model associates with manipulated or synthetic content."
    else:
        summary = "The image looks closer to authentic content based on the model's learned patterns."

    return {
        "certainty": certainty,
        "summary": summary,
        "scores": {
            "fake": round(fake_score * 100, 2),
            "real": round(real_score * 100, 2),
        },
        "metrics": {
            "confidence": round(confidence, 2),
            "score_gap": round(margin, 2),
            "uncertainty": round(100 - confidence, 2),
            "consistency": 100,
        },
        "risk_level": "High" if result == "Fake" and confidence >= 80 else "Medium" if result == "Fake" else "Low",
    }


transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

def detect_deepfake(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        file.save(temp.name)
        path = temp.name

    try:
        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")

        if IMAGE_DETECTOR_BACKEND == "huggingface":
            try:
                from hf_detectors import get_hf_image_detector

                result = get_hf_image_detector().predict(
                    image,
                    threshold=IMAGE_FAKE_THRESHOLD,
                    uncertain_margin=IMAGE_UNCERTAIN_MARGIN,
                )
                result["insight"] = build_image_insight(
                    result["result"],
                    result["confidence"],
                    result["fake_score"] / 100,
                    result["real_score"] / 100,
                )
                return result
            except Exception as error:
                if not ALLOW_LOCAL_MODEL_FALLBACK:
                    return {"error": f"Hugging Face image detector failed: {error}"}

        img = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = get_image_model()(img)
            fake_score = torch.sigmoid(output).item()
            real_score = 1 - fake_score

        THRESHOLD = IMAGE_FAKE_THRESHOLD

        if fake_score > THRESHOLD:
            result = "Fake"
            confidence = fake_score
        else:
            result = "Real"
            confidence = real_score

        return {
            "result": result,
            "confidence": round(confidence * 100, 2),
            "fake_score": round(fake_score * 100, 2),
            "real_score": round(real_score * 100, 2),
            "raw_probability": round(fake_score, 6),
            "insight": build_image_insight(result, confidence * 100, fake_score, real_score),
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(path):
            os.remove(path)
