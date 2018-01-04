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
        self.hand_rect = None


        self.margin_x = 1.0
        self.margin_y = 1.0

        # variables
        self.score = 0.0
        self.max_score = 0.0

        if len(point_hand_data) > 0:

            # Fetch hand_data from raw_data
            self.fetch_hand_data()

            # Calculate the global score of non empty points
            self.calc_hand_score()
            self.calc_hand_rect()


    def draw(self, frame, rect = False):
        if self.hand_poly is not None:
            if rect is False:
                pts = self.hand_poly.get_cv2_poly()
            else:
                pts = self.hand_poly.get_bb_cv2_poly()

            cv2.polylines(frame, [pts], True, (127, 255, 127), 2)


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

            cv2.rectangle(frame, box_tl, box_br, (127, 255, 127), -1)

            cv2.putText(frame, text, textOrg, fontFace, fontScale,
                    (0, 0, 0), thickness, 8)

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