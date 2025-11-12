from collections import defaultdict
import numpy as np

from app.SpeedPredictor import SpeedPredictor

class SpeedCalculator:
    def __init__(self, fps, pixels_per_meter):
        self.position_history = defaultdict(list)
        self.speed_history = defaultdict(list)
        self.bbox_history = defaultdict(list)

        self.fps = fps
        self.smoothing_frames = fps * 2
        self.min_smoothing_frames = int(fps / 4)
        self.pixels_per_meter = pixels_per_meter
        self.min_speed_kmh = 1
    
    def update_position(self, track_id, bbox):
        """Save new position, bbox and instant speed. 
        Try to detect bbox jitter and discard such bboxes reusing previous ones"""

        position_history = self.position_history[track_id]
        speed_history = self.speed_history[track_id]
        bbox_history = self.bbox_history[track_id]
        
        instant_speed_kmh = 0

        if len(position_history) > 0:
            # We will compare current bbox with bbox several frames back in order not to miss 
            # slow object movement and not to confuse it with jitter
            last_x, last_y = position_history[-1]

            if (len(bbox_history) > 3):
                prev_bbox = bbox_history[-3]
            else:
                if (len(bbox_history) > 2):
                    prev_bbox = bbox_history[-2]          
                else:
                    prev_bbox = bbox_history[-1]   

            x, y = self.__get_stable_bbox_center(bbox, prev_bbox, (last_x, last_y))

            instant_speed_kmh = self.__calculate_instant_speed_kmh(last_x, last_y, x, y)

            if (instant_speed_kmh == 0):
                x = last_x
                y = last_y
        else:
            # just take bbox center if we hove not enough historical data
            x, y = self.__get_bbox_center(bbox)

        if (len(position_history) > 0):
            speed_history.append(instant_speed_kmh)  

        position_history.append((x, y))
        bbox_history.append(bbox)

        # limit history to smoothing_frames
        if len(position_history) > self.smoothing_frames:
            position_history.pop(0)
            bbox_history.pop(0)
            speed_history.pop(0)
        
    def __get_stable_bbox_center(self, bbox, prev_bbox, last_center):
        x1, y1, x2, y2 = bbox
        x1_prev, y1_prev, x2_prev, y2_prev = prev_bbox

        dx1 = abs(x1 - x1_prev)
        dx2 = abs(x2 - x2_prev)
        dy1 = abs(y1 - y1_prev)
        dy2 = abs(y2 - y2_prev)

        # try to discard jitter
        if (dx1 < 0.5 and dy1 < 0.5 or dx2 < 0.5 and dy2 < 0.5):
            return last_center
        
        return self.__get_bbox_center(bbox)
    
    def __get_bbox_center(elf, bbox):
        x1, y1, x2, y2 = bbox      
        return int((x1 + x2) / 2), int((y1 + y2) / 2)   
    
    def calculate_speed_kmh(self, track_id, frame_no):
        """Calculate average speed"""

        speed_history = self.speed_history[track_id]
        
        # do not try to calculate until we get some historical data
        if len(speed_history) < self.min_smoothing_frames:
            return None

        speed_kmh = SpeedPredictor.predict_speed(speed_history, self.min_smoothing_frames)

        if (speed_kmh < 1):
            speed_kmh = 0

        print(f'FR {frame_no} predicted {speed_kmh:.1f}')
        print([f"{num:.1f}" for num in speed_history]) 

        return speed_kmh
    
    def __calculate_instant_speed_kmh(self, x1, y1, x2, y2):
        dt = 1 / self.fps
        distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        speed_pxs = distance / dt
        speed_kmh = self.__speed_pxs_to_kmh(speed_pxs)

        return speed_kmh

    def __speed_pxs_to_kmh(self, speed_pxs):
        speed_mps = speed_pxs / self.pixels_per_meter  # m/sec
        speed_kmh = speed_mps * 3.6  # km/h

        if (speed_kmh < 1):
            speed_kmh = 0

        return speed_kmh











        
    #     # Разделяем на первую и вторую половину
    #     half = len(points) // 2
    #     first_half = points[:half]
    #     second_half = points[half:]
        
    #     # Находим средние координаты для каждой половины
    #     first_avg = np.mean(first_half, axis=0)  # [avg_x, avg_y]
    #     second_avg = np.mean(second_half, axis=0)  # [avg_x, avg_y]
        
    #     # Вычисляем расстояние между средними точками
    #     distance_pixels = np.linalg.norm(second_avg - first_avg)
        
    #     # Время между половинами (в секундах)
    #     time_seconds = half / self.fps  # половина кадров / FPS
        
    #     # Скорость в пикселях/секунду
    #     speed_pixels_per_second = distance_pixels / time_seconds if time_seconds > 0 else 0
        
    #     return speed_pixels_per_second