from pathlib import Path
from shutil import copytree, rmtree

from huggingface_hub import snapshot_download


BASE_DIR = Path(__file__).resolve().parent
TARGET_ROOT = BASE_DIR / "pretrained_model" / "huggingface"

MODELS = {
    "buildborderless/CommunityForensics-DeepfakeDet-ViT": "buildborderless__CommunityForensics-DeepfakeDet-ViT",
    "Vansh180/VideoMae-ffc23-deepfake-detector": "Vansh180__VideoMae-ffc23-deepfake-detector",
}


def download_model(repo_id, folder_name):
    target_dir = TARGET_ROOT / folder_name
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    snapshot_path = Path(
        snapshot_download(
            repo_id=repo_id,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )
    )

    if snapshot_path.resolve() != target_dir.resolve():
        if target_dir.exists():
            rmtree(target_dir)
        copytree(snapshot_path, target_dir)

    return target_dir


def main():
    for repo_id, folder_name in MODELS.items():
        target_dir = download_model(repo_id, folder_name)
        print(f"{repo_id} -> {target_dir}")


if __name__ == "__main__":
    main()
