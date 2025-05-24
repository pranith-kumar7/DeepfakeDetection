import numpy as np
import cv2
import os
import tempfile
from tensorflow.keras.models import load_model

IMG_SIZE = 128
THRESHOLD = 0.6  # stricter threshold to catch fakes
FRAME_SKIP = 10

model = load_model("best_model.h5")

def detect_deepfake_video(file):
    # Save the uploaded video file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
        file.save(temp.name)
        path = temp.name

    predictions = []
    frame_count = 0

    try:
        cap = cv2.VideoCapture(path)

        if not cap.isOpened():
            return {"error": "Could not open video."}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % FRAME_SKIP == 0:
                try:
                    resized_frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
                    normalized_frame = resized_frame.astype("float32") / 255.0
                    input_frame = np.expand_dims(normalized_frame, axis=0)

                    score = model.predict(input_frame, verbose=0).item()
                    predictions.append(score)

                except Exception as e:
                    print(f"Error processing frame {frame_count}: {e}")

            frame_count += 1

        cap.release()

        if predictions:
            avg_pred = np.mean(predictions)
            result = "FAKE" if avg_pred < THRESHOLD else "REAL"
            return {
                "result": result,
                "confidence": round(avg_pred * 100, 2),
                "frames_processed": len(predictions),
                "processing_time": "N/A",  # Add timing if you want
                "analyzed_frames": len(predictions),
                "performance": [round(p * 100, 2) for p in predictions],  # confidence % per frame
            }
        else:
            return {"error": "No frames processed from the video."}

    finally:
        if os.path.exists(path):
            os.remove(path)
