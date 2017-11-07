import cv2

from PosePoly import *
from PosePoint import *



class PoseFull:

    def __init__(self, point_pose_data):
        self.point_pose_data = point_pose_data

        # Head data contains all the points needed
        self.full_point_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        self.point_full_data = []

        self.full_poly = None
        self.full_rect = None

        # Score based on the points
        self.score = 0.0
        self.max_score = 0.0

        # Variables concerning the head calculation
        self.margin = 1.2

        # Calculate the torso points
        self.fetch_full_data()
        self.calc_full_score()

        self.calc_full_rect()

    def draw(self, frame, bb=False):

        if bb is False:
            pts = self.full_poly.get_cv2_poly()
        elif bb is True:
            pts = self.full_poly.get_bb_cv2_poly()

        cv2.polylines(frame, [pts], True,  (255, 127, 255), 2)

    def fetch_full_data(self):
        self.full_poly = PosePoly()

        for i in self.full_point_index:
            if i in self.point_pose_data:
                self.point_full_data.append(self.point_pose_data[i])
                self.full_poly.add_point(self.point_pose_data[i].pt)

    def calc_full_score(self):
        cum_score = 0.0
        cnt_points = 0

        if self.point_full_data is not None:
            for point in self.point_full_data:
                if not point.empty_point():
                    cum_score += point.score
                    cnt_points += 1

                    if self.max_score < point.score:
                        self.max_score = point.score

        if cnt_points > 0:
            self.score = cum_score / cnt_points

    def calc_full_rect(self):
        if self.full_poly.get_bb() is not None:
            bb_full_poly, bb_full_poly_shape = self.full_poly.get_bb()

            left = bb_full_poly[0][0]
            top = bb_full_poly[0][1]

            width = bb_full_poly_shape[0]
            height = bb_full_poly_shape[1]

            #Calculate the center point of this rect
            center = (width/2.0 + left, height/2.0 + top)
            self.center = center

            #Apply margin
            width *= self.margin
            height *= self.margin

            tl = (int(round(center[0] - width/2, 0)), int(round(center[1] - height/2, 0)))
            br = (int(round(center[0] + width/2, 0)), int(round(center[1] + height/2, 0)))

            self.full_rect = (tl, br)

        else:
            self.full_rect = None