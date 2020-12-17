import os
import threading
import cv2


class VideoDecoder(threading.Thread):

    def __init__(self, file_path, start_frame_pos, decode_callback_fun, user_data):
        super(VideoDecoder, self).__init__()
        self.file_path = file_path
        self.start_frame_pos = start_frame_pos
        self.decode_callback_fun = decode_callback_fun
        self.user_data = user_data

    def run(self):

        cap = cv2.VideoCapture(self.file_path)
        file_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.start_frame_pos:
            ret = cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame_pos)
        file_frame_pos = self.start_frame_pos
        while file_frame_pos < file_frame_count:
            ret, img = cap.read()
            self.decode_callback_fun(img, self.file_path, file_frame_pos * 400000, self.user_data)
            file_frame_pos += 1

        print(f"decode {self.file_path} finish")


if __name__ == '__main__':

    video_path = r'I:\阅兵剪辑\两分钟剪辑视频\A1\095950000.mp4'

    # for test
    def decocde_CB(img, file_path, file_frame_offset, user_data):
        print(f"{file_path}, {file_frame_offset}, {len(img)}, {user_data}")

    decoder = VideoDecoder(video_path, 0, decocde_CB, video_path)
    decoder.start()
