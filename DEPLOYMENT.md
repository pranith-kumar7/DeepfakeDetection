# Vercel + Hugging Face Spaces Deployment

This project is split into:

- `backend`: Flask API deployed on Hugging Face Spaces
- `frontend`: React app deployed on Vercel

## 1. Prepare MongoDB

Use MongoDB Atlas or another hosted MongoDB instance. Hosted deployment will not be able to use `mongodb://localhost:27017/`.

Create a database user, allow network access, and copy the connection string.

## 2. Deploy Backend To Hugging Face Spaces

1. Create a Hugging Face account.
2. Create a new Space.
3. Choose Docker as the Space SDK.
4. Upload or push the contents of the `backend` folder to the Space repository.
5. Make sure these Python files are present:
   - `app.py`
   - `detection.py`
   - `video_detection.py`
   - `model_loader.py`
   - `cross_efficient_vit_model.py`
   - `npr_model.py`
   - `requirements.txt`
   - `Dockerfile`
6. Make sure the `.pth` model files are uploaded with Git LFS. They can be inside `pretrained_model/` or directly in the Space root:
   - `pretrained_model/NPR.pth`
   - `pretrained_model/cross_efficient_vit.pth`
   - `pretrained_model/efficientnet.pth`
7. In the Space settings, add these secrets:
   - `MONGO_URI`: your hosted MongoDB connection string
   - `MONGO_DB_NAME`: `deepfake_detection`
8. Wait for the Space to build.
9. Check:
   - `https://YOUR-USERNAME-YOUR-SPACE.hf.space/health`
   - `https://YOUR-USERNAME-YOUR-SPACE.hf.space/health/models`

The backend Docker startup is configured in `backend/Dockerfile`.

## 3. Deploy Frontend To Vercel

1. In Vercel, import the same GitHub repo.
2. Set the project root directory to `frontend`.
3. Add this Vercel environment variable:
   - `REACT_APP_API_BASE_URL`: your Hugging Face Space URL, with no trailing slash
4. Deploy.

The frontend build and SPA route fallback are configured in `frontend/vercel.json`.

## 4. Important Notes

- The `.pth` files are large and tracked with Git LFS. If `/health/models` reports `git_lfs_pointer`, Hugging Face received pointer files instead of real model weights.
- The video model is around 400 MB. Free CPU Spaces are better suited for this than many free web backends, but prediction can still be slow.
- After changing `REACT_APP_API_BASE_URL` in Vercel, redeploy the frontend because Create React App embeds environment variables at build time.
