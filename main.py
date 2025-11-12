from app.config import load_config
from app.calc import find_homography, pixels_per_meter
import cv2

from app.track_with_yolo import track_with_yolo

config = load_config('data/config.yaml')

config_for_demo = config.find_by_filename("data/speed camera 1.mp4")

# Open video file
video = cv2.VideoCapture(config_for_demo.file)

fps = int(video.get(cv2.CAP_PROP_FPS))

# Take first frame 
ret, frame = video.read()
if not ret:
    print("Error: Could not read video")
    video.release()
    exit()

homography = find_homography(config_for_demo.homography.video_pts, config_for_demo.homography.world_pts)
pixels_per_meter = pixels_per_meter(homography, config_for_demo.homography.video_pts)

track_with_yolo(video, fps, pixels_per_meter)

video.release()
cv2.destroyAllWindows()