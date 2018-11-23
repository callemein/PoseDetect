import cv2

from .PosePoly import *
from .PosePoint import *



class PoseTorso:

    def __init__(self, point_pose_data):
        self.point_pose_data = point_pose_data

        # Head data contains all the points needed
        self.torso_point_index = [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 14, 15, 16, 17]
        self.point_torso_data = []

        self.torso_poly = None
        self.torso_rect = None

        # Score based on the points
        self.score = 0.0
        self.max_score = 0.0

        # Variables concerning the head calculation
        self.margin_x = 1.35
        self.margin_y = 10

        # Calculate the torso points
        self.fetch_torso_data()
        self.calc_torso_score()

        self.calc_torso_rect()

    def draw(self, frame, rect=False):
        if self.torso_poly is not None:
            if rect is False:
                pts = self.torso_poly.get_cv2_poly()
                cv2.polylines(frame, [pts], True,  (127, 127, 255), 2)
            else:
                cv2.rectangle(frame, self.torso_rect[0], self.torso_rect[1], (127, 127, 255), 2)

    def draw_score(self, frame):
        text = str(round(100*self.score, 2))+'%'

        fontFace = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        fontScale = 1
        thickness = 2

        textSize, baseline = cv2.getTextSize(text, fontFace, fontScale, thickness)
        baseline += thickness


        # Right-Top Corner
        textOrg = (int(self.torso_rect[1][0] - textSize[0] - 5 ),
                int(self.torso_rect[0][1] + textSize[1] + 10))

        box_tl = (textOrg[0] - 5, self.torso_rect[0][1])
        box_br = (self.torso_rect[1][0], textOrg[1] + 5)

        cv2.rectangle(frame, box_tl, box_br, (127, 127, 255), -1)

        cv2.putText(frame, text, textOrg, fontFace, fontScale,
                (0, 0, 0), thickness, 8)

    def fetch_torso_data(self):
        self.torso_poly = PosePoly()

        for i in self.torso_point_index:
            if i in self.point_pose_data:
                self.point_torso_data.append(self.point_pose_data[i])
                self.torso_poly.add_point(self.point_pose_data[i].pt)

    def calc_torso_score(self):
        cum_score = 0.0
        cnt_points = 0

        if self.point_torso_data is not None:
            for point in self.point_torso_data:
                if not point.empty_point():
                    cum_score += point.score
                    cnt_points += 1

                    if self.max_score < point.score:
                        self.max_score = point.score

        if cnt_points > 0:
            self.score = cum_score / cnt_points



    def calc_torso_rect(self):
        if self.torso_poly.get_bb() is not None:
            bb_torso_poly, bb_torso_poly_shape = self.torso_poly.get_bb()

            left = bb_torso_poly[0][0]
            top = bb_torso_poly[0][1]

            width = bb_torso_poly_shape[0]
            height = bb_torso_poly_shape[1]

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

            self.torso_rect = (tl, br)

        else:
            self.torso_rect = None
