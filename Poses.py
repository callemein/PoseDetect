from Pose import *


class Poses:

    def __init__(self, raw_pose_data, hand_threshold = 0.0, head_threshold=0.0):
        self.raw_pose_data = raw_pose_data

        self.hand_threshold = hand_threshold
        self.head_threshold = head_threshold

        self.poses = []

        self.fetch_poses(raw_pose_data, hand_threshold, head_threshold)

    def draw_all_poses(self, frame, bb=False):
        for p in self.poses:
            p.draw_pose(frame, bb=bb)

    def fetch_poses(self, raw_pose_data, hand_threshold, head_threshold):

        for p in raw_pose_data['people']:
            self.poses.append(Pose(p, hand_threshold, head_threshold))