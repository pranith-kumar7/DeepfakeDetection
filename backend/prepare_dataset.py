import os
import cv2
import numpy as np
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 128  # Reduced from 224 to 128
MAX_FRAMES_PER_VIDEO = 10  # Limit number of frames per video
dataset_dir = "dataset_frames"

def load_data():
    X, y = [], []
    for category in ['real', 'fake']:
        category_path = os.path.join(dataset_dir, category)
        label = 0 if category == 'real' else 1  # 0 for real, 1 for fake
        for video_folder in os.listdir(category_path):
            folder_path = os.path.join(category_path, video_folder)
            if not os.path.isdir(folder_path):
                continue

            frame_files = sorted(os.listdir(folder_path))[:MAX_FRAMES_PER_VIDEO]  # Limit frames
            for img_file in frame_files:
                img_path = os.path.join(folder_path, img_file)
                try:
                    img = cv2.imread(img_path)
                    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                    X.append(img)
                    y.append(label)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")

    X = np.array(X, dtype="float32") / 255.0
    y = to_categorical(y, 2)
    return train_test_split(X, y, test_size=0.2, random_state=42)

def augment_data(X_train):
    # Augmenting the data using ImageDataGenerator
    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    datagen.fit(X_train)
    return datagen

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data()
    np.save("X_train.npy", X_train)
    np.save("X_test.npy", X_test)
    np.save("y_train.npy", y_train)
    np.save("y_test.npy", y_test)
    print("✅ Dataset prepared and saved successfully.")

    # Data Augmentation
    augment_data(X_train)
