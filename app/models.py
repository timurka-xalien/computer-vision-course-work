from dataclasses import dataclass
import numpy as np

@dataclass
class TrackedObject:
    bbox: np.ndarray
    class_id: int
    class_name: str
    id: int