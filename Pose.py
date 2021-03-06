from .PoseHead import *
from .PoseHand import *
from .PoseHandEstimate import *
from .PoseTorso import *

from .PosePoint import *
from .PoseFull import *

class Pose:

    def __init__(self, raw_pose_data, hand_threshold, head_threshold):
        self.raw_pose_data = raw_pose_data

        self.hand_threshold = hand_threshold
        self.head_threshold = head_threshold

        self.pose = self.load_pose(raw_pose_data['pose_keypoints_2d'])
        self.pose_lh = self.load_pose(raw_pose_data['hand_left_keypoints_2d'])
        self.pose_rh = self.load_pose(raw_pose_data['hand_right_keypoints_2d'])

        self.head = PoseHead(self.pose)
        self.torso = PoseTorso(self.pose)

        self.full = PoseFull(self.pose)

        self.full_head_rect = None
        self.full_head_desc = []

        self.hands = [
            PoseHand(self.pose_lh,  side=HandSide.LEFT),
            PoseHand(self.pose_rh, side=HandSide.RIGHT)
        ]

        self.hands_e = [
            PoseHandEstimate(self.pose,  side=HandSide.LEFT),
            PoseHandEstimate(self.pose, side=HandSide.RIGHT)
        ]

        self.calc_full_head_rect()

    def calc_full_head_rect(self):
        head = self.head.head_rect
        full = self.full.full_rect
        
        if head is not None:
            tl = (min(head[0][0], full[0][0]), min(head[0][1], full[0][1]) )
            br = (max(head[1][0], full[1][0]), max(head[1][1], full[1][1]) )
            self.full_head_rect = (tl, br)
        else:
            self.full_head_rect = full

    def draw_pose(self, frame, bb=False):
        if self.head.score > self.head_threshold:
            self.head.draw(frame, bb=bb)

        self.torso.draw(frame)
        self.full.draw(frame, bb=bb)

        if self.hands[0].score > self.hand_threshold:
            self.hands[0].draw(frame)

        if self.hands[1].score > self.hand_threshold:
            self.hands[1].draw(frame)

    def load_pose(self, raw_pose, ignore_check_empty=True):
        tmp_pose = {}
        cnt_points = len(raw_pose)

        if cnt_points % 3 == 0:
            for i in range(int(cnt_points/3)):
               pt = PosePoint(  x=raw_pose[(3 * i) + 0],
                                y=raw_pose[(3 * i) + 1],
                                score=raw_pose[(3 * i) + 2])

               if not (pt.empty_point() and ignore_check_empty):
                   tmp_pose[i] = pt

        return tmp_pose
