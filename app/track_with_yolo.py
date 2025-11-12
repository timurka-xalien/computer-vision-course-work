from app.SpeedCalculator import SpeedCalculator
import cv2
from ultralytics import YOLO

from app.models import TrackedObject

def track_with_yolo(video, fps, pixels_per_meter):
    model = YOLO("yolov8n.pt")  

    speed_calc = SpeedCalculator(fps, pixels_per_meter)

    frame_no = 1

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame_no = frame_no + 1

        objects = detect_objects(model, frame);

        for obj in objects:
            speed_calc.update_position(obj.id, obj.bbox)
            speed = speed_calc.calculate_speed_kmh(obj.id, frame_no)
            x1, y1, x2, y2 = obj.bbox
            render_annotation(frame, x1, y1, x2, y2, obj.id, speed, frame_no)

        cv2.imshow("Tracking + Speed", cv2.resize(frame, (758, 476)))

        if cv2.waitKey(500) & 0xFF == 27:
            break

def detect_objects(model, frame):
    results = model.track(frame, persist=True, tracker="data/botsort.yaml", conf=0.3, iou=0.3, verbose=False)[0]

    if results.boxes.id is None:
        return (None, None)

    boxes = results.boxes.xyxy.cpu().numpy()
    ids = results.boxes.id.cpu().numpy().astype(int)
    classes = results.boxes.cls.cpu().numpy().astype(int)
    names = results.names

    # classes we interested in
    allowed_classes = ["car", "truck", "bus", "bicycle", "motorbike"]  

    objects = []

    for i, c in enumerate(classes):
        name = names[c]
        if name in allowed_classes:
            objects.append(TrackedObject(boxes[i], c, name, ids[i]))

    return objects

def render_annotation(frame, x1, y1, x2, y2, id, speed, frame_no):
    color = (0, 255, 0)
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 1)

    if (speed == None):
        speed = "..."
    else:
        speed = f"{speed:.0f} kmh"
    
    # full info
    #text = f"{cls} ID:{obj_id} {speed}"
    # just speed
    text = f"ID:{id} {speed}"

    # render objects
    cv2.putText(frame, text, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1, cv2.LINE_AA)

    # render frame number
    cv2.putText(frame, str(frame_no), (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)