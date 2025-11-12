import numpy as np
import cv2

def find_homography(image_pts, world_pts):
    image_pts = np.array([pt.to_array() for pt in image_pts])
    world_pts = np.array([pt.to_array() for pt in world_pts])    

    homography, mask = cv2.findHomography(image_pts, world_pts, cv2.RANSAC)
    print("Homography matrix:\n", homography)

    return homography

def pixels_per_meter(H, image_pts):
    # take 2 arbitrary image pixels
    p1 = np.array([image_pts[0].to_array()[0], image_pts[0].to_array()[1], 1.0])
    p2 = np.array([image_pts[1].to_array()[0], image_pts[1].to_array()[1], 1.0])

    # convert them to world coordinates using homography
    world_p1 = H @ p1
    world_p2 = H @ p2

    # normalize 
    world_p1 /= world_p1[2]
    world_p2 /= world_p2[2]

    dist_m = np.linalg.norm(world_p1[:2] - world_p2[:2])
    dist_px = np.linalg.norm(p1[:2] - p2[:2])

    # pixel to meter ratio
    px_per_m = dist_px / dist_m
    return px_per_m