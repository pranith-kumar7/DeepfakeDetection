---
title: Deepfake Detection API
emoji: D
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
---

# Deepfake Detection API

Flask API for the deepfake detection frontend.

Health checks:

- `/health`
- `/health/models`

Detector configuration:

- `IMAGE_DETECTOR_BACKEND=huggingface` uses `IMAGE_HF_MODEL_IDS`.
- `IMAGE_HF_MODEL_IDS=pretrained_model/huggingface/buildborderless__CommunityForensics-DeepfakeDet-ViT` is the default local broad AI-image detector after running `python download_hf_models.py`.
- `VIDEO_DETECTOR_BACKEND=huggingface` uses `VIDEO_HF_MODEL_ID`.
- `VIDEO_HF_MODEL_ID=pretrained_model/huggingface/Vansh180__VideoMae-ffc23-deepfake-detector` is the default local temporal video detector after running `python download_hf_models.py`.
- `DETECTOR_DEVICE=cpu` can be changed to `cuda` on GPU hosts.
- `ALLOW_LOCAL_MODEL_FALLBACK=true` falls back to the bundled `.pth` checkpoints if Hugging Face models are unavailable.
- `IMAGE_FAKE_THRESHOLD`, `VIDEO_FAKE_THRESHOLD`, `IMAGE_UNCERTAIN_MARGIN`, and `VIDEO_UNCERTAIN_MARGIN` tune classification strictness.

Download the stronger Hugging Face model files into `pretrained_model/huggingface/`:

```bash
python download_hf_models.py
```

Required files in this Space:

- `app.py`
- `detection.py`
- `video_detection.py`
- `model_loader.py`
- `detector_config.py`
- `hf_detectors.py`
- `cross_efficient_vit_model.py`
- `npr_model.py`
- `requirements.txt`
- `Dockerfile`
- `NPR.pth` or `pretrained_model/NPR.pth`
- `cross_efficient_vit.pth` or `pretrained_model/cross_efficient_vit.pth`
- `efficientnet.pth` or `pretrained_model/efficientnet.pth`
