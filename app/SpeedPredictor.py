import numpy as np

class SpeedPredictor:
    @staticmethod
    def predict_speed(speeds, change_detection_window):
        estimate = SpeedPredictor.__weighted_robust_mean_with_change_detection(speeds, change_detection_window)
        return estimate

    @staticmethod
    def __weighted_robust_mean(speeds):
        """Calculates weighted average based on distance from median"""
       
        median = np.median(speeds)
        mad = np.median([abs(x - median) for x in speeds])
        
        if mad == 0:  # all values are equal
            return median
        
        weights = [1 / (1 + abs(x - median) / mad) for x in speeds]
        weighted_sum = sum(w * x for w, x in zip(weights, speeds))
        
        estimate = weighted_sum / sum(weights)
        return estimate
    
    @staticmethod    
    def __weighted_robust_mean_with_change_detection(speeds, change_detection_window):
        """Calculates weighted average based on distance from median with change detection. 
        If pattern change is detected in recent data calculates result only for recent data discarding historical values"""
       
        wr_mean = SpeedPredictor.__weighted_robust_mean(speeds)
        wr_mean_recent = SpeedPredictor.__weighted_robust_mean(speeds[-change_detection_window:])

        large_diff = SpeedPredictor.__is_large_diff(wr_mean, wr_mean_recent)

        if (large_diff):
            estimate = wr_mean_recent
        else:
            estimate = wr_mean            

        return estimate
    
    @staticmethod  
    def __is_large_diff(a, b):
        if a == 0 and b == 0:
            return False
        
        vmin = min(a, b)
        vmax = max(a, b)
        ratio =  vmax / max(vmin, 1)

        return ratio >= 2