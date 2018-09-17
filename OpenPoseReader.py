import json
import os
import zipfile

__all__ = ["OpenPoseReader"]


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


        if path.endswith('.zip'):
            try:
                self.zfile = zipfile.ZipFile(path, 'r')
                ret = self.zfile.testzip()
                if ret is not None:
                    print ("%s bad zip file, error: %s" % file, ret)
            except zipfile.BadZipfile as ex:
                print ("%s no a zip file" % path)

    def load_file_by_frame_from_zip(self, frame):
        self.load_zfile(self.prefix + str(frame).zfill(self.frame_zfill) + self.suffix + ".json")

    def load_file_by_frame(self, frame):
        self.load_file(self.openpose_path + self.prefix + str(frame).zfill(self.frame_zfill) + self.suffix + ".json")

    def load_file_by_name(self, filename):
        self.load_file(self.openpose_path + str(os.path.splitext(filename)[0]) + self.suffix + ".json")

    def load_file(self, path):
        with open(path) as json_data:
            self.current_file = path
            self.raw_data = json.load(json_data)
            json_data.close()

    def load_zfile(self, path):
        json_data = self.zfile.read(path) 
        self.raw_data = json.loads(json_data)
