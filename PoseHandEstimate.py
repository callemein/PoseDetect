from enum import Enum

import math
import cv2

from .PosePoly import *


class HandSide(Enum):
    UNKNOWN = 0
    LEFT = 1
    RIGHT = 2

class PoseHandEstimate:
    def __init__(self, point_pose_data, side=HandSide.LEFT):
        self.point_pose_data = point_pose_data
        self.hand_orientation = side

        if side is HandSide.RIGHT:
            self.hand_point_index = [3, 4]

        elif side is HandSide.LEFT:
            self.hand_point_index = [6, 7]

        # Hand data contains all the points needed (This case all)
        self.hand_data = []
        self.hand_poly = None
        self.hand_rect = None

        self.margin_x = 1.0
        self.margin_y = 1.0

        self.elbow = None
        self.wrist = None

        self.arm_angle = None
        self.arm_length = None

        self.hand_arm_ratio = 0.6
        self.hand_ratio = 0.5

        # variables
        self.score = 0.0
        self.max_score = 0.0

        if len(point_pose_data) > 0:

            # Fetch hand_data from raw_data
            self.fetch_hand_data()

            self.calc_hand_rect()


    def draw(self, frame, rect = False):
        if self.hand_poly is not None:
            if rect is False:
                pts = self.hand_poly.get_cv2_poly()
            else:
                pts = self.hand_poly.get_bb_cv2_poly()

            cv2.polylines(frame, [pts], True, (0, 255, 127), 2)


    def draw_score(self, frame):
        if self.hand_rect is not None:
            text = str(round(100*self.score, 2))+'%'

            fontFace = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
            fontScale = 1
            thickness = 2

            textSize, baseline = cv2.getTextSize(text, fontFace, fontScale, thickness)
            baseline += thickness


            # Right-Top Corner
            textOrg = (int(self.hand_rect[1][0] - textSize[0] - 5 ),
                    int(self.hand_rect[0][1] + textSize[1] + 10))

            box_tl = (textOrg[0] - 5, self.hand_rect[0][1])
            box_br = (self.hand_rect[1][0], textOrg[1] + 5)

            cv2.rectangle(frame, box_tl, box_br, (0, 255, 127), -1)

            cv2.putText(frame, text, textOrg, fontFace, fontScale,
                    (0, 0, 0), thickness, 8)

    def fetch_hand_data(self):
        self.hand_poly = PosePoly()

        if len(self.hand_point_index) == 2:
            # Elbow and Wrist

            if self.hand_point_index[0] in self.point_pose_data and self.hand_point_index[1] in self.point_pose_data:
                self.elbow = self.point_pose_data[self.hand_point_index[0]]

                self.wrist = self.point_pose_data[self.hand_point_index[1]]
                self.score = self.point_pose_data[self.hand_point_index[1]].score

                arm_vector = self.elbow.vector(self.wrist)

                self.arm_angle = math.atan2(arm_vector[1], arm_vector[0])
                self.arm_length = self.wrist.euclidean_distance_points(self.elbow)


                if self.wrist is not None and self.elbow is not None:
                    self.calc_hand_poly()



    def calc_hand_poly(self):
        # Use the vector and arm length to determine the hand rect
        hand_length = self.arm_length * self.hand_arm_ratio
        hand_width = self.arm_length * self.hand_ratio

        angle_perpendicular = self.arm_angle + math.pi/2

        pt = self.wrist.pt

        pt_a = (pt[0] + math.cos(angle_perpendicular) * hand_width /2,
                pt[1] + math.sin(angle_perpendicular) * hand_width / 2)

        pt_b = (pt[0] + math.cos(angle_perpendicular + math.pi) * hand_width /2,
                pt[1] + math.sin(angle_perpendicular + math.pi) * hand_width / 2)

        pt_2 = (pt[0] + math.cos(self.arm_angle) * hand_length,
                pt[1] + math.sin(self.arm_angle) * hand_length)

        pt_c = (pt_2[0] + math.cos(angle_perpendicular) * hand_width /2,
                pt_2[1] + math.sin(angle_perpendicular) * hand_width / 2)

        pt_d = (pt_2[0] + math.cos(angle_perpendicular + math.pi) * hand_width /2,
                pt_2[1] + math.sin(angle_perpendicular + math.pi) * hand_width / 2)


        self.hand_poly.add_point(pt_a)
        self.hand_poly.add_point(pt_b)
        self.hand_poly.add_point(pt_d)
        self.hand_poly.add_point(pt_c)


    def calc_hand_rect(self):
        if self.hand_poly.get_bb() is not None:
            bb_hand_poly, bb_hand_poly_shape = self.hand_poly.get_bb()

            left = bb_hand_poly[0][0]
            top = bb_hand_poly[0][1]

            width = bb_hand_poly_shape[0]
            height = bb_hand_poly_shape[1]

            #Calculate the center point of this rect
            center = (width/2.0 + left, height/2.0 + top)
            self.center = center

            #Apply margin
            width *= self.margin_x
            height *= self.margin_y

            tl = (int(round(center[0] - width/2, 0)), int(round(center[1] - height/2, 0)))
            br = (int(round(center[0] + width/2, 0)), int(round(center[1] + height/2, 0)))

            # Add 10% space for head
            head_offset = 0.1 * height

            tl = (tl[0], int(round(max(tl[1] - head_offset, 0),0)))

            self.hand_rect = (tl, br)

        else:
            self.hand_rect = None
