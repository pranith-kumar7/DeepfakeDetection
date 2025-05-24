import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import tempfile
import os

IMG_SIZE = 128
MODEL_PATH = "best_model.h5"
model = load_model(MODEL_PATH)

def detect_deepfake(file):
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        file.save(temp.name)
        path = temp.name

    try:
        img = load_img(path, target_size=(IMG_SIZE, IMG_SIZE))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0

        prediction = model.predict(img_array)[0]  # first batch prediction

        # Check if sigmoid output or softmax output
        if len(prediction) == 1:
            confidence = float(prediction[0])  # probability of "Fake"
            if confidence > 0.5:
                result = "Fake"
                confidence_display = confidence
            else:
                result = "Real"
                confidence_display = 1 - confidence
        else:
            # Softmax with 2 neurons [Real, Fake]
            confidence_fake = float(prediction[1])
            confidence_real = float(prediction[0])
            if confidence_fake > confidence_real:
                result = "Fake"
                confidence_display = confidence_fake
            else:
                result = "Real"
                confidence_display = confidence_real

        return {
            "result": result,
            "confidence": round(confidence_display * 100, 2)  # percentage
        }
    finally:
        os.remove(path)
