from pathlib import Path

import torch

from cross_efficient_vit_model import CrossEfficientViT
from npr_model import NPRModel

BASE_DIR = Path(__file__).resolve().parent


def _find_model_file(file_name):
    for model_path in (
        BASE_DIR / "pretrained_model" / file_name,
        BASE_DIR / file_name,
    ):
        if model_path.exists():
            return model_path

    return BASE_DIR / "pretrained_model" / file_name


IMAGE_MODEL_PATH = _find_model_file("NPR.pth")
VIDEO_MODEL_PATH = _find_model_file("cross_efficient_vit.pth")
device = torch.device("cpu")

_image_model = None
_video_model = None


def _load_state_dict(model_path):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model weights not found at {model_path}. "
            "Make sure Git LFS files are available in the deployed backend."
        )

    with model_path.open("rb") as model_file:
        header = model_file.read(64)

    if header.startswith(b"version https://git-lfs.github.com/spec"):
        raise RuntimeError(
            f"{model_path.name} is a Git LFS pointer, not the real model file. "
            "Enable Git LFS for the Hugging Face Space or upload the real weights to the backend."
        )

    return torch.load(model_path, map_location=device)


def get_image_model():
    global _image_model

    if _image_model is None:
        _image_model = NPRModel()
        _image_model.load_state_dict(_load_state_dict(IMAGE_MODEL_PATH))
        _image_model.eval()

    return _image_model


def get_video_model():
    global _video_model

    if _video_model is None:
        _video_model = CrossEfficientViT()
        _video_model.load_state_dict(_load_state_dict(VIDEO_MODEL_PATH))
        _video_model.eval()

    return _video_model
