# Deepfake Detection System

A full-stack deepfake detection project with a Flask API backend and a React frontend. The app supports user authentication, image deepfake prediction, video deepfake prediction, and model health checks.

## Project Structure

```text
.
+-- backend/                 # Flask API, ML model loading, detection routes
+-- frontend/                # React app
+-- deepfake_detection/      # Project assets/files
+-- DEPLOYMENT.md            # Vercel + Hugging Face deployment guide
`-- run-project.ps1          # Local startup helper for Windows
```

## Features

- Image deepfake detection through `/predict`
- Video deepfake detection through `/predict-video`
- Signup and signin API routes
- MongoDB user storage
- Model and API health checks
- React frontend for uploading media and viewing prediction results

## Tech Stack

- Frontend: React, Bootstrap, Axios, Chart.js
- Backend: Flask, PyMongo, PyTorch/TensorFlow model utilities
- Database: MongoDB
- Deployment: Vercel for frontend, Hugging Face Spaces for backend

## Local Setup

### 1. Backend

```powershell
cd backend
pip install -r requirements.txt
python app.py
```

The backend starts at:

```text
http://localhost:5000
```

Optional environment variables:

```text
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=deepfake_detection
DETECTOR_DEVICE=cpu
```

### 2. Frontend

```powershell
cd frontend
npm install
npm start
```

The frontend starts at:

```text
http://localhost:3000
```

### 3. Windows Helper Script

From the project root, you can also run:

```powershell
.\run-project.ps1
```

This script starts both the backend and frontend.

## API Routes

```text
GET  /health
GET  /health/models
POST /auth/signup
POST /auth/signin
POST /predict
POST /predict-video
```

## Model Files

The backend expects model checkpoint files such as:

```text
backend/pretrained_model/NPR.pth
backend/pretrained_model/cross_efficient_vit.pth
backend/pretrained_model/efficientnet.pth
```

Large `.pth` files should be tracked with Git LFS when pushing to GitHub or Hugging Face Spaces.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for the complete deployment steps.

In short:

- Deploy `backend/` to Hugging Face Spaces using Docker.
- Deploy `frontend/` to Vercel.
- Set `REACT_APP_API_BASE_URL` in Vercel to your Hugging Face Space URL.
- Set `MONGO_URI` and `MONGO_DB_NAME` as backend secrets.

## Health Checks

After the backend is running, check:

```text
http://localhost:5000/health
http://localhost:5000/health/models
```
