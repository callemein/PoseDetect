import json
import os

class OpenPoseReader:

    def __init__(self, path=None, prefix=None, suffix="_keypoints", z_fill=12):
        self.openpose_path = path

        if prefix is not None:
            self.prefix = prefix
        else:
            self.prefix = ""

        self.suffix = suffix
        self.frame_zfill = z_fill

        self.current_file = None
        self.raw_data = {}

    def load_file_by_frame(self, frame):
        self.load_file(self.openpose_path + self.prefix + str(frame).zfill(self.frame_zfill) + self.suffix + ".json")

    def load_file_by_name(self, filename):
        self.load_file(self.openpose_path + str(os.path.splitext(filename)[0]) + self.suffix + ".json")

    def load_file(self, path):
        with open(path) as json_data:
            self.current_file = path
            self.raw_data = json.load(json_data)
            json_data.close()