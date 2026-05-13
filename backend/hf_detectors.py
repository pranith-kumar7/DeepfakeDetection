from functools import lru_cache

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    VideoMAEForVideoClassification,
    VideoMAEImageProcessor,
)

from detector_config import DEVICE, IMAGE_HF_MODEL_IDS, VIDEO_HF_MODEL_ID, VIDEO_NUM_FRAMES


FAKE_LABEL_KEYWORDS = ("fake", "ai", "synthetic", "generated", "deepfake", "manipulated")
REAL_LABEL_KEYWORDS = ("real", "human", "authentic", "original")
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def _label_text(label):
    return str(label).replace("_", " ").replace("-", " ").lower()


def _scores_from_probs(probs, id2label, default_fake_index=0):
    fake_score = 0.0
    real_score = 0.0

    for index, prob in enumerate(probs):
        label = _label_text(id2label.get(index, id2label.get(str(index), index)))
        if any(keyword in label for keyword in FAKE_LABEL_KEYWORDS):
            fake_score += float(prob)
        elif any(keyword in label for keyword in REAL_LABEL_KEYWORDS):
            real_score += float(prob)

    if fake_score == 0.0 and real_score == 0.0 and len(probs) == 2:
        fake_score = float(probs[default_fake_index])
        real_score = float(probs[1 - default_fake_index])
    elif real_score == 0.0:
        real_score = max(0.0, 1.0 - fake_score)
    elif fake_score == 0.0:
        fake_score = max(0.0, 1.0 - real_score)

    total = fake_score + real_score
    if total > 0:
        fake_score /= total
        real_score /= total

    return fake_score, real_score


def _prediction(fake_score, real_score, threshold, uncertain_margin):
    margin = abs(fake_score - real_score)
    if margin < uncertain_margin:
        result = "Uncertain"
        confidence = max(fake_score, real_score)
    elif fake_score >= threshold and fake_score > real_score:
        result = "Fake"
        confidence = fake_score
    else:
        result = "Real"
        confidence = real_score

    return result, confidence


class HFImageDetector:
    def __init__(self, model_ids):
        self.models = []
        for model_id in model_ids:
            model = AutoModelForImageClassification.from_pretrained(model_id).to(DEVICE)
            processor = load_image_processor(model_id)
            model.eval()
            self.models.append((model_id, processor, model))

    @torch.no_grad()
    def predict(self, image, threshold, uncertain_margin):
        model_results = []
        fake_scores = []
        real_scores = []

        for model_id, processor, model in self.models:
            inputs = processor(images=image, return_tensors="pt")
            inputs = {name: value.to(DEVICE) for name, value in inputs.items()}
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)[0].detach().cpu().tolist()
            default_fake_index = 1 if "CommunityForensics" in str(model_id) else 0
            fake_score, real_score = _scores_from_probs(
                probs,
                model.config.id2label,
                default_fake_index=default_fake_index,
            )
            fake_scores.append(fake_score)
            real_scores.append(real_score)
            model_results.append({
                "model": model_id,
                "fake_score": round(fake_score * 100, 2),
                "real_score": round(real_score * 100, 2),
            })

        fake_score = float(np.mean(fake_scores))
        real_score = float(np.mean(real_scores))
        result, confidence = _prediction(fake_score, real_score, threshold, uncertain_margin)

        return {
            "result": result,
            "confidence": round(confidence * 100, 2),
            "fake_score": round(fake_score * 100, 2),
            "real_score": round(real_score * 100, 2),
            "raw_probability": round(fake_score, 6),
            "model": "huggingface_image_ensemble",
            "model_results": model_results,
        }


class HFVideoDetector:
    def __init__(self, model_id):
        self.model_id = model_id
        self.processor = VideoMAEImageProcessor.from_pretrained(model_id)
        self.model = VideoMAEForVideoClassification.from_pretrained(model_id).to(DEVICE)
        self.model.eval()

    @torch.no_grad()
    def predict(self, video_path, threshold, uncertain_margin):
        frames = load_video_frames(video_path, VIDEO_NUM_FRAMES)
        if not frames:
            return {"error": "No frames processed"}

        inputs = self.processor(frames, return_tensors="pt")
        inputs = {name: value.to(DEVICE) for name, value in inputs.items()}
        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0].detach().cpu().tolist()
        fake_score, real_score = _scores_from_probs(
            probs,
            self.model.config.id2label,
            default_fake_index=1,
        )
        result, confidence = _prediction(fake_score, real_score, threshold, uncertain_margin)

        return {
            "result": result,
            "confidence": round(confidence * 100, 2),
            "fake_score": round(fake_score * 100, 2),
            "real_score": round(real_score * 100, 2),
            "raw_probability": round(fake_score, 6),
            "frames_analyzed": len(frames),
            "performance": [round(confidence * 100, 2)],
            "frame_scores": [],
            "model": self.model_id,
        }


def load_video_frames(video_path, num_frames):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total_frames <= 0:
        cap.release()
        return []

    indices = set(np.linspace(0, total_frames - 1, num_frames).astype(int).tolist())
    frames = []
    frame_index = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index in indices:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame))
        frame_index += 1
        if len(frames) >= num_frames:
            break

    cap.release()
    return frames


def load_image_processor(model_id):
    model_id_text = str(model_id)
    if "CommunityForensics" in model_id_text:
        return default_image_processor(384)

    try:
        return AutoImageProcessor.from_pretrained(model_id)
    except Exception:
        return default_image_processor(224)


def default_image_processor(image_size):
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])

    class DefaultImageProcessor:
        def __call__(self, images, return_tensors="pt"):
            return {"pixel_values": transform(images).unsqueeze(0)}

    return DefaultImageProcessor()


@lru_cache(maxsize=1)
def get_hf_image_detector():
    return HFImageDetector(tuple(IMAGE_HF_MODEL_IDS))


@lru_cache(maxsize=1)
def get_hf_video_detector():
    return HFVideoDetector(VIDEO_HF_MODEL_ID)
