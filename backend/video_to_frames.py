import cv2
import os

def extract_frames_from_video(video_path, output_dir):
    # Read the video file
    cap = cv2.VideoCapture(video_path)

    # Get frame rate of the video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize to 224x224
        frame = cv2.resize(frame, (224, 224))

        # Save the frame as an image
        frame_filename = os.path.join(output_dir, f"frame_{frame_count}.jpg")
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    # Release the video capture object
    cap.release()
    print(f"Extracted {frame_count} frames from {video_path}")

# Example usage: extract frames for all real and fake videos
videos_dir = "dataset_frames"  # Root directory where real/fake videos are stored
for category in ['real', 'fake']:
    video_dir = os.path.join(videos_dir, category)
    for video_name in os.listdir(video_dir):
        if video_name.endswith('.mp4'):
            video_path = os.path.join(video_dir, video_name)
            output_dir = os.path.join(videos_dir, category, video_name.split('.')[0])  # Create a folder for each video
            extract_frames_from_video(video_path, output_dir)
 