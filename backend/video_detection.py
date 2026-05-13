import torch
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np

from detector_config import (
    ALLOW_LOCAL_MODEL_FALLBACK,
    VIDEO_DETECTOR_BACKEND,
    VIDEO_FAKE_THRESHOLD,
    VIDEO_UNCERTAIN_MARGIN,
)
from model_loader import get_video_model


def build_video_insight(result, confidence, fake_score, real_score, probs):
    if len(probs) == 0:
        probs = np.array([real_score])

    real_frames = int(np.sum(probs >= 0.5))
    fake_frames = int(len(probs) - real_frames)
    frame_confidences = np.maximum(probs, 1 - probs) * 100
    winning_frames = max(real_frames, fake_frames)
    consistency = (winning_frames / len(probs)) * 100
    score_gap = abs(real_score - fake_score) * 100

    if confidence >= 85:
        certainty = "High"
    elif confidence >= 65:
        certainty = "Moderate"
    else:
        certainty = "Low"

    if result == "Uncertain":
        summary = "The detector did not find a large enough gap between fake and real video evidence."
    elif certainty == "Low":
        summary = "Frame-level predictions are close together, so the video result is uncertain."
    elif result == "Fake":
        summary = "More sampled evidence leaned toward manipulated or synthetic content."
    else:
        summary = "More sampled evidence leaned toward authentic content."

    return {
        "certainty": certainty,
        "summary": summary,
        "scores": {
            "fake": round(fake_score * 100, 2),
            "real": round(real_score * 100, 2),
        },
        "frames": {
            "analyzed": len(probs),
            "fake_leaning": fake_frames,
            "real_leaning": real_frames,
            "min_confidence": round(float(np.min(frame_confidences)), 2),
            "max_confidence": round(float(np.max(frame_confidences)), 2),
            "avg_confidence": round(float(np.mean(frame_confidences)), 2),
        },
        "metrics": {
            "confidence": round(confidence, 2),
            "score_gap": round(score_gap, 2),
            "uncertainty": round(100 - confidence, 2),
            "consistency": round(consistency, 2),
            "avg_frame_confidence": round(float(np.mean(frame_confidences)), 2),
        },
        "risk_level": "High" if result == "Fake" and confidence >= 70 else "Medium" if result == "Fake" else "Low",
    }


# -------------------------------
# Preprocessing (FIXED)
# -------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # ✅ FIXED
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# -------------------------------
# Video Prediction
# -------------------------------
def predict_video(video_path):
    if VIDEO_DETECTOR_BACKEND == "huggingface":
        try:
            from hf_detectors import get_hf_video_detector

            result = get_hf_video_detector().predict(
                video_path,
                threshold=VIDEO_FAKE_THRESHOLD,
                uncertain_margin=VIDEO_UNCERTAIN_MARGIN,
            )
            if "error" in result:
                return result
            probs = np.array([result["real_score"] / 100], dtype=float)
            result["insight"] = build_video_insight(
                result["result"],
                result["confidence"],
                result["fake_score"] / 100,
                result["real_score"] / 100,
                probs,
            )
            return result
        except Exception as error:
            if not ALLOW_LOCAL_MODEL_FALLBACK:
                return {"error": f"Hugging Face video detector failed: {error}"}

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    frames = []
    max_frames = 8
    frame_skip = max(1, total_frames // max_frames) if total_frames else 15
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % frame_skip != 0:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        frames.append(transform(image))

        if len(frames) >= max_frames:
            break

    cap.release()

    if not frames:
        return {"error": "No frames processed"}

    batch = torch.stack(frames)

    with torch.no_grad():
        output = get_video_model()(batch)
        probs = torch.sigmoid(output).detach().cpu().numpy().reshape(-1)

    real_score = float(np.mean(probs))
    fake_score = 1 - real_score

    if real_score >= fake_score:
        result = "Real"
        confidence = real_score
    else:
        result = "Fake"
        confidence = fake_score

    frame_scores = []
    for index, prob in enumerate(probs, start=1):
        frame_real_score = float(prob)
        frame_fake_score = 1 - frame_real_score
        frame_result = "Real" if frame_real_score >= frame_fake_score else "Fake"
        frame_scores.append({
            "frame": index,
            "result": frame_result,
            "confidence": round(max(frame_real_score, frame_fake_score) * 100, 2),
            "fake_score": round(frame_fake_score * 100, 2),
            "real_score": round(frame_real_score * 100, 2),
        })

    return {
        "result": result,
        "confidence": round(confidence * 100, 2),
        "fake_score": round(fake_score * 100, 2),
        "real_score": round(real_score * 100, 2),
        "raw_probability": round(real_score, 6),
        "frames_analyzed": len(frames),
        "performance": [round(float(max(prob, 1 - prob)) * 100, 2) for prob in probs],
        "frame_scores": frame_scores,
        "insight": build_video_insight(result, confidence * 100, fake_score, real_score, probs),
    }
