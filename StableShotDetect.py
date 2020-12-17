import cv2
import os
import threading
import queue

import requests


class StableShotDetector(threading.Thread):

    def __init__(self, img_queue, db_params):
        super(StableShotDetector, self).__init__()
        self.img_queue = img_queue
        self.db_params = db_params

    def run(self):
        print(self.db_params)
        while True:
            img_with_metadata = self.img_queue.get()

            # analyze img then return result
            ret = "Stable result protocol"

            # img_with_metadata = Munch()
            # img_with_metadata.img = img
            # img_with_metadata.file_path = file_path
            # img_with_metadata.file_pos = file_pos
            # img_with_metadata.clip_folder = os.path.split(file_path)[0]
            # img_with_metadata.clip_pos = segment.clipin + file_pos - segment.filein

            print(f"write db "
                  f"{img_with_metadata.file_path}, "
                  f"{img_with_metadata.file_pos}, "
                  f"{img_with_metadata.clip_folder}, "
                  f"{img_with_metadata.clip_pos},"
                  f"{ret}")


if __name__ == '__main__':

    segment = Munch().fromDict(
        {
            "filepath": "I:\\阅兵剪辑\\两分钟剪辑视频\\A1\\095950000.mp4",
            "filein": 0,
            "fileout": 1200000000,
            "clipin": 0,
            "clipout": 1200000000
        }
    )

    img_queue = queue.Queue(100)

    db_params = Munch()
    db_params.host = 'localhost'
    db_params.user = 'user'
    db_params.password = 'passwd'
    db_params.db = 'db'

    detector = FaceDetector(img_queue, db_params)
    detector.start()

    cap = cv2.VideoCapture(segment.filepath)
    file_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    file_frame_offset = 0
    while file_frame_offset < file_frame_count:
        ret = cap.set(cv2.CAP_PROP_POS_FRAMES, file_frame_offset)
        ret, img = cap.read()
        if ret:
            img_with_metadata = Munch()
            img_with_metadata.img = img
            img_with_metadata.file_path = segment.filepath
            img_with_metadata.file_pos = file_frame_offset * 400000
            img_with_metadata.clip_folder = os.path.split(segment.filepath)[0]
            img_with_metadata.clip_pos = segment.clipin + img_with_metadata.file_pos - segment.filein

            img_queue.put(img_with_metadata)
        file_frame_offset += 25

    print("Quit")