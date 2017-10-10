import json
import math
import numpy as np
from enum import Enum
import os
import cv2

class HeadOrientation(Enum):
    UNKNOWN = 0
    FRONTAL = 1
    LEFT_SIDE = 2
    RIGHT_SIDE = 3
    BACK_SIDE = 4

class HeadType(Enum):
    POSE_BOUNDING_BOX = 1
    POSE_EUCLIDIAN = 2

class PoseTorso:

    def __init__(self, pose_data):
        self.raw_points = pose_data["raw_data"]
        self.pose_data = pose_data

        self.torso_margin = 1.2

        self.torso_data = []
        self.torso_score = 0.0

        self.get_rect_torso()

    def empty_point(self, point):
        if point[0] == 0 and point[1] == 0:
            return True
        else:
            return False

    def euclidean_distance_points(self, pt_a, pt_b):
        return math.sqrt((pt_a[0] - pt_b[0])
                  * (pt_a[0] - pt_b[0])
                  + (pt_a[1] - pt_b[1])
                  * (pt_a[1] - pt_b[1]))

    def draw_torso_pose(self, frame):
        cv2.rectangle(frame, self.torso_data[0], self.torso_data[1], (127, 127, 255))

    def get_rect_torso(self):
        #Calculate Torso
        x_positions = []
        y_positions = []

        use_points = [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 14, 15, 16, 17]

        cum_score = 0.0
        cnt_score = 0

        for up in use_points:
            p = (int(self.raw_points[up*3]), int(self.raw_points[up*3 + 1]))

            if not self.empty_point(p):
                cum_score += self.raw_points[up*3 +2]
                cnt_score +=1

                x_positions.append(p[0])
                y_positions.append(p[1])

        self.torso_score = float(cum_score)/float(cnt_score)

        if len(x_positions) > 0:
            left = min(x_positions)
            right = max(x_positions)
        else:
            left = None
            right = None

        if len(y_positions) > 0:
            top = min(y_positions)
            bot = max(y_positions)
        else:
            top = None
            bot = None

        if (bot is not None and top is not None and left is not None and right is not None):

            width = right - left
            height = bot  - top

            #Calculate the center point of this rect
            center = (width/2.0 + left, height/2.0 + top)

            #Apply margin
            width *= self.torso_margin
            height *= self.torso_margin

            tl = (int(round(center[0] - width/2, 0)), int(round(center[1] - height/2*1.1, 0)))
            br = (int(round(center[0] + width/2, 0)), int(round(center[1] + height/2, 0)))

            self.torso_data = (tl, br)
        else:
            self.torso_data = None