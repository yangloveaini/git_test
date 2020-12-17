import os
import json
import glob

from munch import Munch
from moviepy.editor import *
import pandas as pd


if __name__ == '__main__':

    # load configure file
    cur_filepath = os.path.abspath(__file__)
    cur_folder = os.path.split(cur_filepath)[0]
    cfg_path = os.path.join(cur_folder, 'CutParams.json')
    with open(cfg_path, 'r', encoding='utf8') as f:
        cfg = json.load(f)
        cfg = Munch.fromDict(cfg)

    print(cfg.ShotSequence)

    # read from troop infos file
    troops = ["步兵-1", "步兵-2", "步兵-3", "步兵-4", "步兵-5", "步兵-6", "步兵-7", "步兵-8", "步兵-9", "步兵-10",
              "机械-1", "机械-2", "机械-3", "机械-4"]

    # read clip info file for every channel
    channel_clip_infos = {}
    for shot in cfg.ShotSequence:
        c_clip_info_path = os.path.join(cfg.Channels[shot].Path, 'clip.json')
        print(c_clip_info_path)
        try:
            with open(c_clip_info_path, 'r') as f:
                clip_info = Munch().fromDict(json.load(f))
                channel_clip_infos[shot] = clip_info
        except:
            print(f"open file {c_clip_info_path} failed")


    # read from db or read from data file
    data_path = r'I:\阅兵剪辑\两分钟剪辑视频'
    markpoint_df = pd.read_csv(os.path.join(data_path, 'markpoints.csv')).apply(pd.to_numeric, errors='ignore')

    for idx, markpoint in markpoint_df.iterrows():
        clips = []
        troop_filepath = os.path.join(data_path, troops[idx] + '.mp4')
        if os.path.exists(troop_filepath):
            continue
        print(troop_filepath)
        try:
            clip_info = channel_clip_infos['A1']
            for shot in cfg.ShotSequence:
                print(shot)

                # get markpoint clippos
                for seg in clip_info.sequence:
                    if markpoint.FileName in seg.filepath:
                        markpoint_clippos = seg.clipin + markpoint.FilePos - seg.filein
                        break

                shot_clipin = markpoint_clippos + cfg.Channels[shot].Range[0] * 10000000
                shot_clipout = markpoint_clippos + cfg.Channels[shot].Range[1] * 10000000

                for i in range(0, len(clip_info.sequence)):
                    seg = clip_info.sequence[i]
                    seg_file_name = os.path.split(seg.filepath)[1]
                    next_seg = clip_info.sequence[i + 1]
                    next_seg_file_name = os.path.split(next_seg.filepath)[1]
                    if (seg.clipin <= shot_clipin < seg.clipout) and (seg.clipin < shot_clipout < seg.clipout):
                        sub_clip = VideoFileClip(os.path.join(cfg.Channels[shot].Path, seg_file_name))\
                            .subclip(markpoint.FilePos / 10000000 + cfg.Channels[shot].Range[0],
                                     markpoint.FilePos / 10000000 + cfg.Channels[shot].Range[1])
                        clips.append(sub_clip)
                        break
                    elif (seg.clipin <= shot_clipin < seg.clipout) and (shot_clipout > seg.clipout):
                        sub_clip_part_1 = VideoFileClip(os.path.join(cfg.Channels[shot].Path, seg_file_name))\
                            .subclip((seg.filein + shot_clipin - seg.clipin) / 10000000,
                                     seg.fileout / 10000000)
                        clips.append(sub_clip_part_1)

                        remain_len_secs = cfg.Channels[shot].Range[1] - \
                                          (seg.fileout / 10000000 - markpoint.FilePos / 10000000)

                        #
                        sub_clip_part_2 = VideoFileClip(os.path.join(cfg.Channels[shot].Path, next_seg_file_name))\
                            .subclip(next_seg.filein / 10000000,
                                     next_seg.filein / 10000000 + remain_len_secs)
                        clips.append(sub_clip_part_2)
                        break

            troop_clip = concatenate_videoclips(clips)
            troop_clip.write_videofile(troop_filepath)
            troop_clip.close()
            [clip.close() for clip in clips]
        except:
            print(f"generate {troop_filepath} failed")
    print(markpoint_df)