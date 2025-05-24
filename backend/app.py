from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os
import tempfile
import cv2

app = Flask(__name__)
CORS(app)

MODEL_PATH = "best_model.h5"
IMG_SIZE = 128
THRESHOLD = 0.5
model = load_model(MODEL_PATH)

@app.route('/predict', methods=['POST'])
def predict_image():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
            file.save(temp.name)
            image_path = temp.name

        img = load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array)[0][0]
        result = "FAKE" if prediction < THRESHOLD else "REAL"
        confidence = round(float(prediction) * 100, 2)

        return jsonify({'result': result, 'confidence': confidence})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


@app.route('/predict-video', methods=['POST'])
def predict_video():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No video file uploaded'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            file.save(temp.name)
            video_path = temp.name

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return jsonify({'error': 'Could not open video.'})

        predictions = []
        frame_count = 0
        frame_skip = 10

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_skip == 0:
                resized_frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
                normalized_frame = resized_frame / 255.0
                input_frame = np.expand_dims(normalized_frame, axis=0)
                pred = model.predict(input_frame)[0][0]
                predictions.append(pred)

            frame_count += 1

        cap.release()

        if predictions:
            avg_pred = np.mean(predictions)
            result = "FAKE" if avg_pred < THRESHOLD else "REAL"
            confidence = round(float(avg_pred) * 100, 2)
            return jsonify({
                "result": result,
                "confidence": confidence,
                "frames_processed": len(predictions),
                "performance": [round(float(p) * 100, 2) for p in predictions]
            })
        else:
            return jsonify({'error': 'No frames processed.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


if __name__ == '__main__':
    app.run(debug=True)
