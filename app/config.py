import yaml
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class Point:
    x: float
    y: float
    
    def to_tuple(self):
        return (self.x, self.y)
    
    def to_array(self):
        return np.array([self.x, self.y], dtype=np.float32)
    
@dataclass
class HomographyConfig:
    video_pts: List[Point]
    world_pts: List[Point]

@dataclass
class VideoConfig:
    file: str
    camera_fov_deg: Optional[float] = None
    camera_height_m: Optional[float] = None
    homography: Optional[HomographyConfig] = None

    def find_video_by_filename(config, filename):
        for video in config.videos:
            if video.file == filename:
                return video
        return None

@dataclass
class Config:
    videos: List[VideoConfig]

    def find_by_filename(self, filename):
        for video in self.videos:
            if video.file == filename:
                return video
        return None
    
def load_config(path: str) -> Config:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    videos = []
    for v in data['videos']:
        homography_data = v.get('homography')
        homography = None
        if homography_data:
            video_pts = []
            world_pts = []
            
            # Process video_pts
            for pt in homography_data.get('video_pts', []):
                if isinstance(pt, str):  # if coordinates specified as string "180, 109"
                    x_str, y_str = pt.split(',')
                    video_pts.append(Point(x=float(x_str.strip()), y=float(y_str.strip())))
                elif isinstance(pt, (list, tuple)) and len(pt) == 2:  # if coordinates specified as list [180, 109]
                    video_pts.append(Point(x=float(pt[0]), y=float(pt[1])))
                elif isinstance(pt, dict):  # if coordinates specified as dictionary {x: 180, y: 109}
                    video_pts.append(Point(x=float(pt['x']), y=float(pt['y'])))
            
            # Process world_pts
            for pt in homography_data.get('world_pts', []):
                if isinstance(pt, str):   # if coordinates specified as string "180, 109"
                    x_str, y_str = pt.split(',')
                    world_pts.append(Point(x=float(x_str.strip()), y=float(y_str.strip())))
                elif isinstance(pt, (list, tuple)) and len(pt) == 2:  # if coordinates specified as list [180, 109]
                    world_pts.append(Point(x=float(pt[0]), y=float(pt[1])))
                elif isinstance(pt, dict):  # if coordinates specified as dictionary {x: 180, y: 109}
                    world_pts.append(Point(x=float(pt['x']), y=float(pt['y'])))
            
            homography = HomographyConfig(video_pts=video_pts, world_pts=world_pts)
        
        video_config = VideoConfig(
            file=v['file'],
            camera_fov_deg=v.get('camera_fov_deg'),
            camera_height_m=v.get('camera_height_m'),
            homography=homography
        )
        videos.append(video_config)
    
    return Config(videos=videos)