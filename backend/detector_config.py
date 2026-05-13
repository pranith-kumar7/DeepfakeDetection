import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PRETRAINED_MODEL_DIR = BASE_DIR / "pretrained_model"
LOCAL_HF_MODEL_DIR = PRETRAINED_MODEL_DIR / "huggingface"
DEFAULT_IMAGE_MODEL_DIR = LOCAL_HF_MODEL_DIR / "buildborderless__CommunityForensics-DeepfakeDet-ViT"
DEFAULT_VIDEO_MODEL_DIR = LOCAL_HF_MODEL_DIR / "Vansh180__VideoMae-ffc23-deepfake-detector"


def get_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_float(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def get_int(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_csv(name, default):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


DEVICE = os.environ.get("DETECTOR_DEVICE", "cpu")

IMAGE_DETECTOR_BACKEND = os.environ.get("IMAGE_DETECTOR_BACKEND", "huggingface").strip().lower()
IMAGE_HF_MODEL_IDS = get_csv(
    "IMAGE_HF_MODEL_IDS",
    str(DEFAULT_IMAGE_MODEL_DIR if DEFAULT_IMAGE_MODEL_DIR.exists() else "buildborderless/CommunityForensics-DeepfakeDet-ViT"),
)
IMAGE_FAKE_THRESHOLD = get_float("IMAGE_FAKE_THRESHOLD", 0.5)
IMAGE_UNCERTAIN_MARGIN = get_float("IMAGE_UNCERTAIN_MARGIN", 0.12)

VIDEO_DETECTOR_BACKEND = os.environ.get("VIDEO_DETECTOR_BACKEND", "huggingface").strip().lower()
VIDEO_HF_MODEL_ID = os.environ.get(
    "VIDEO_HF_MODEL_ID",
    str(DEFAULT_VIDEO_MODEL_DIR if DEFAULT_VIDEO_MODEL_DIR.exists() else "Vansh180/VideoMae-ffc23-deepfake-detector"),
).strip()
VIDEO_NUM_FRAMES = get_int("VIDEO_NUM_FRAMES", 16)
VIDEO_FAKE_THRESHOLD = get_float("VIDEO_FAKE_THRESHOLD", 0.5)
VIDEO_UNCERTAIN_MARGIN = get_float("VIDEO_UNCERTAIN_MARGIN", 0.12)
ALLOW_LOCAL_MODEL_FALLBACK = get_bool("ALLOW_LOCAL_MODEL_FALLBACK", True)
