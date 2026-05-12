import os

import torch

from cross_efficient_vit_model import CrossEfficientViT
from npr_model import NPRModel

IMAGE_MODEL_PATH = os.path.join("pretrained_model", "NPR.pth")
VIDEO_MODEL_PATH = os.path.join("pretrained_model", "cross_efficient_vit.pth")
device = torch.device("cpu")

_image_model = None
_video_model = None


def get_image_model():
    global _image_model

    if _image_model is None:
        _image_model = NPRModel()
        _image_model.load_state_dict(torch.load(IMAGE_MODEL_PATH, map_location=device))
        _image_model.eval()

    return _image_model


def get_video_model():
    global _video_model

    if _video_model is None:
        _video_model = CrossEfficientViT()
        _video_model.load_state_dict(torch.load(VIDEO_MODEL_PATH, map_location=device))
        _video_model.eval()

    return _video_model
