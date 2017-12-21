from enum import Enum

import cv2

from PosePoly import *


class HandSide(Enum):
    UNKNOWN = 0
    LEFT = 1
    RIGHT = 2

class PoseHand:
    def __init__(self, point_hand_data, side=HandSide.UNKNOWN):
        self.point_hand_data = point_hand_data
        self.hand_orientation = side

        # Hand data contains all the points needed (This case all)
        self.hand_point_index = []
        self.hand_data = []
        self.hand_poly = None

        # variables
        self.score = 0.0
        self.max_score = 0.0

        if len(point_hand_data) > 0:

            # Fetch hand_data from raw_data
            self.fetch_hand_data()

            # Calculate the global score of non empty points
            self.calc_hand_score()


    def draw(self, frame, rect = False):
        if self.hand_poly is not None:
            if rect is False:
                pts = self.hand_poly.get_cv2_poly()
            else:
                pts = self.hand_poly.get_bb_cv2_poly()

            cv2.polylines(frame, [pts], True, (255, 255, 0), 2)

    def fetch_hand_data(self):
        self.hand_poly = PosePoly()

        if len(self.hand_point_index) == 0:
            # All points
            self.hand_data = self.point_hand_data
            for i in self.point_hand_data:
                self.hand_poly.add_point(self.point_hand_data[i].pt)
        else:
            for i in self.hand_point_index:
                self.hand_data.append(self.point_hand_data[i])
                self.hand_poly.add_point(self.point_hand_data[i].pt)

    def calc_hand_score(self):
        cum_score = 0.0
        cnt_points = 0

        tmp_max_score = 0.0

        if self.point_hand_data is not None:
            for i in self.point_hand_data:
                if not self.point_hand_data[i].empty_point():
                    cum_score += self.point_hand_data[i].score
                    cnt_points += 1

                    if tmp_max_score < self.point_hand_data[i].score:
                        tmp_max_score = self.point_hand_data[i].score

        if cnt_points > 0:
            self.score = cum_score / cnt_points

        self.max_score = tmp_max_score