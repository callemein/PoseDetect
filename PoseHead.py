from enum import Enum

import cv2

from .PosePoly import *
from .PosePoint import *


class HeadOrientation(Enum):
    UNKNOWN = 0
    FRONTAL = 1
    LEFT_SIDE = 2
    RIGHT_SIDE = 3

class PoseHead:

    def __init__(self, point_pose_data):
        self.point_pose_data = point_pose_data

        # Head data contains all the points needed
        self.head_point_index = [0, 16, 14, 15, 17]
        self.point_head_data = []
        self.head_poly = None
        self.head_rect = None

        # Score based on the points
        self.score = 0.0
        self.max_score = 0.0

        # Variables concerning the head orientation
        self.head_orientation = HeadOrientation.UNKNOWN

        # Variables concerning the head calculation
        self.margin = 1.7
        self.margin_profile = 2.2

        self.aspect_ratio = 0.9
        self.aspect_ratio_profile = 1.2


        # Calculate the head points
        self.fetch_head_data()
        self.calc_head_score()

        # Determine Head orientation
        self.orientation_center = 0.1
        self.calc_head_orientation()

        # Calculate Head rect based on head points + orientation + margin
        self.calc_head_rect()

    def draw(self, frame, bb = False):
        if self.head_poly is not None and self.head_rect is not None:
            if bb is False:
                pts = self.head_poly.get_cv2_poly()
                cv2.polylines(frame, [pts], True, (255, 255, 0), 2)
            else:
                cv2.rectangle(frame, self.head_rect[0], self.head_rect[1], (255, 255, 0), 2)


    def draw_score(self, frame):
        if self.head_rect is not None:

            text = str(round(100*self.score, 2))+'%'

            fontFace = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
            fontScale = 1
            thickness = 2

            textSize, baseline = cv2.getTextSize(text, fontFace, fontScale, thickness)
            baseline += thickness


            # Right-Top Corner
            textOrg = (int(self.head_rect[1][0] - textSize[0] - 5 ),
                    int(self.head_rect[0][1] + textSize[1] + 10))

            box_tl = (textOrg[0] - 5, self.head_rect[0][1])
            box_br = (self.head_rect[1][0], textOrg[1] + 5)

            cv2.rectangle(frame, box_tl, box_br, (255, 255, 0), -1)

            cv2.putText(frame, text, textOrg, fontFace, fontScale,
                    (0, 0, 0), thickness, 8)

    def fetch_head_data(self):
        self.head_poly = PosePoly()

        for i in self.head_point_index:
            if i in self.point_pose_data:
                self.point_head_data.append(self.point_pose_data[i])
                self.head_poly.add_point(self.point_pose_data[i].pt)

    def calc_head_orientation(self):
        self.head_orientation = HeadOrientation.UNKNOWN
        center_index = 0
        left_side_index  = [14, 16]
        right_side_index = [15, 17]

        if len(self.point_pose_data) > 0 and center_index in self.point_pose_data :
            #calc the distances between left side and right side
            center_point = self.point_pose_data[center_index]


            left_dist  = 0.0
            right_dist = 0.0

            if center_point.empty_point():
                self.head_orientation = HeadOrientation.UNKNOWN
            else:

                for i in left_side_index:
                    if i in self.point_pose_data and not self.point_pose_data[i].empty_point():
                        left_dist += center_point.euclidean_distance_points(self.point_pose_data[i])

                for i in right_side_index:
                    if i in self.point_pose_data and not self.point_pose_data[i].empty_point():
                        right_dist += center_point.euclidean_distance_points(self.point_pose_data[i])

                if left_dist == 0.0:
                    left_dist = 0.0000001

                if right_dist == 0.0:
                    right_dist = 0.0000001

                ratio = left_dist / right_dist

                if ratio > 1.0 + self.orientation_center:
                    self.head_orientation = HeadOrientation.LEFT_SIDE
                elif ratio < 1.0 - self.orientation_center:
                    self.head_orientation = HeadOrientation.RIGHT_SIDE
                else:
                    self.head_orientation = HeadOrientation.FRONTAL

    def calc_head_rect_margins(self, margins):

        if 'margin' in margins:
            self.margin = margins['margin']

        if 'aspect_ratio' in margins:
            self.aspect_ratio = margins['aspect_ratio']


        if 'margin_profile' in margins:
            self.margin_profile = margins['margin_profile']

        if 'aspect_ratio_profile' in margins:
            self.aspect_ratio_profile = margins['aspect_ratio_profile']

        self.calc_head_rect()

    def calc_head_rect(self):

        if self.head_poly.get_bb() is not None:
            bb_head_poly, bb_head_poly_shape = self.head_poly.get_bb()

            left = bb_head_poly[0][0]
            top = bb_head_poly[0][1]

            width = bb_head_poly_shape[0]
            height = bb_head_poly_shape[1]

            #Calculate the center point of this rect
            center = (width/2.0 + left, height/2.0 + top)

            #Correct width or height based on the other

            if self.head_orientation == HeadOrientation.FRONTAL:
                ratio = self.aspect_ratio
                margin = self.margin
            else:
                ratio = self.aspect_ratio_profile
                margin = self.margin_profile

            if width > height:
                #use width to calc height
                height = width / ratio
            else:
                width = height * ratio

            #Apply margin
            width *= margin
            height *= margin

            tl = (int(round(center[0] - width/2, 0)), int(round(center[1] - height/2, 0)))
            br = (int(round(center[0] + width/2, 0)), int(round(center[1] + height/2, 0)))

            self.head_rect = (tl, br)

        else:
            self.head_rect = None

    def calc_head_score(self):
        cum_score = 0.0
        cnt_points = 0

        if self.point_head_data is not None:
            for point in self.point_head_data:
                if not point.empty_point():
                    cum_score += point.score
                    cnt_points += 1

                    if point.score > self.max_score:
                        self.max_score = point.score

        if cnt_points > 0:
            self.score = cum_score / cnt_points
