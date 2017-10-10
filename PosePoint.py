import math

## POSE POINT ##
# This class will contain a single pose point from the pose data


class PosePoint:

    def __init__(self, x=None, y=None, score=None):
        if x is None or y is None or score is None:
            self.pt = None
            self.score = None
        else:
            self.set_point(x, y, score)

    def set_point(self, x, y, score):
        self.pt = (int(round(float(x), 0)),
                   int(round(float(y), 0)))

        self.score = float(score)

    def empty_point(self):
        if self.pt[0] == 0 and self.pt[1] == 0:
            return True
        else:
            return False

    def euclidean_distance_points(self, pointB):
        return math.sqrt((self.pt[0] - pointB.pt[0])
                  * (self.pt[0] - pointB.pt[0])
                  + (self.pt[1] - pointB.pt[1])
                  * (self.pt[1] - pointB.pt[1]))

    def vector(self, pointB):
        return (pointB.pt[0] - self.pt[0]) , (pointB.pt[1] - self.pt[1])