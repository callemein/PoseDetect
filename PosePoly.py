import cv2
import numpy as np

## POSE POLY/RECT ##
# This class will contain a methods to calculate overlap inbetween rects/polys etc

class PosePoly:

    def __init__(self):
        self.poly_points = []

    def add_point(self, pt):
        self.poly_points.append(pt)

    def get_cv2_poly(self):
        if len(self.poly_points) > 0:
            pts = np.array(self.poly_points, np.int32)
            pts = cv2.convexHull(pts)
            return pts.reshape((-1, 1, 2))
        else:
            return None

    def get_bb_cv2_poly(self):
        bb_poly_points = []

        (tl, br), (width, height) = self.get_bb()

        bb_poly_points.append(tl)
        bb_poly_points.append((br[0], tl[1]))
        bb_poly_points.append(br)
        bb_poly_points.append((tl[0], br[1]))

        if len(bb_poly_points) > 0:
            pts = np.array(bb_poly_points, np.int32)
            pts = cv2.convexHull(pts)
            return pts.reshape((-1, 1, 2))
        else:
            return None


    def get_bb_polys(self, polyB):
        # Calculate Head based on
        x_positions = []
        y_positions = []

        for point in self.poly_points:
            x_positions.append(point[0])
            y_positions.append(point[1])

        for point in polyB.poly_points:
            x_positions.append(point[0])
            y_positions.append(point[1])

        return self._get_bb_around_xy(x_positions, y_positions)

    def get_bb(self):
        # Calculate Head based on
        x_positions = []
        y_positions = []

        for point in self.poly_points:
            x_positions.append(point[0])
            y_positions.append(point[1])

        return self._get_bb_around_xy(x_positions, y_positions)


    def _get_bb_around_xy(self, x_positions, y_positions):

        left = None
        right = None
        top = None
        bot = None

        if len(x_positions) > 0:
            left = min(x_positions)
            right = max(x_positions)

        if len(y_positions) > 0:
            top = min(y_positions)
            bot = max(y_positions)

        if (bot is not None and top is not None and left is not None and right is not None):

            width = right - left
            height = bot - top

            # Calculate the center point of this rect
            center = (width / 2.0 + left, height / 2.0 + top)

            tl = (int(round(center[0] - width / 2, 0)), int(round(center[1] - height / 2, 0)))
            br = (int(round(center[0] + width / 2, 0)), int(round(center[1] + height / 2, 0)))

            return ((tl, br), (width, height))
        else:
            return None

    def IoU(self, posePolyB):
        # Create an image mask for both poly's
        ((tl, br), (w, h)) = self.get_bb_polys(posePolyB)

        polyA_conv = []
        polyB_conv = []

        for p in self.poly_points:
            polyA_conv.append((p[0] - tl[0], p[1] - tl[1]))

        for p in posePolyB.poly_points:
            polyB_conv.append((p[0] - tl[0], p[1] - tl[1]))

        ptsA = np.array(polyA_conv, np.int32)
        ptsA = ptsA.reshape((-1, 1, 2))

        ptsB = np.array(polyB_conv, np.int32)
        ptsB = ptsB.reshape((-1, 1, 2))

        maskA = np.zeros((w, h), dtype=np.uint8)
        maskB = np.zeros((w, h), dtype=np.uint8)

        cv2.fillConvexPoly(maskA, ptsA, 255)
        cv2.fillConvexPoly(maskB, ptsB, 255)

        areaA = cv2.countNonZero(maskA)
        areaB = cv2.countNonZero(maskB)

        ret, maskA = cv2.threshold(maskA, 127, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_and(maskB, maskB, mask=maskA)

        intersect = cv2.countNonZero(mask)

        union = areaA + areaB - intersect

        if union != 0.0:
            iou = float(intersect) / float(union)
        else:
            iou = 0.0

        # return the intersection over union value
        return iou