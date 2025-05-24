from model import build_model  # Ensure this import is correct
import numpy as np
from tensorflow.keras.callbacks import ModelCheckpoint
import os

# Load data
X_train = np.load("X_train.npy")
y_train = np.load("y_train.npy")
X_test = np.load("X_test.npy")
y_test = np.load("y_test.npy")

# Build model
model = build_model()

# Define checkpoint to save best model
checkpoint = ModelCheckpoint("best_model.h5", monitor="val_loss", save_best_only=True)

# Train model
model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test), callbacks=[checkpoint])

# Save the architecture to a JSON file
model_json = model.to_json()
with open("model_architecture.json", "w") as json_file:
    json_file.write(model_json)

# Save model weights
model.save_weights("model.weights.h5")

print("✅ Model training complete, architecture and weights saved successfully.")
