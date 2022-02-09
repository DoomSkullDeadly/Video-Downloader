import cv2
import numpy as np
import warnings
from PIL import Image

warnings.filterwarnings("ignore")


def get_frame(cap, frame, size):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    ret, cv2_im = cap.read()
    if ret:
        converted = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(converted)
        pil_im_resize = pil_im.resize(size)
        return np.array(pil_im_resize, dtype='int64')


def get_clip_frames(cap, clip_frame_num, size, num=7):
    frame_pos_list = np.linspace(0, clip_frame_num-1, num=num, dtype='int')
    clip_frames = []
    for frame_pos in frame_pos_list:
        clip_frames.append(get_frame(cap, frame_pos, size))

    return clip_frames, frame_pos_list


def get_size(cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return width, height


def iter_all(main_dir, clip_dir, start_frame):
    cap_main = cv2.VideoCapture(main_dir)
    cap_clip = cv2.VideoCapture(clip_dir)

    main_frame_num = int(cap_main.get(cv2.CAP_PROP_FRAME_COUNT))
    clip_frame_num = int(cap_clip.get(cv2.CAP_PROP_FRAME_COUNT))

    main_width, main_height = get_size(cap_main)
    clip_width, clip_height = get_size(cap_clip)

    size = (min([main_width, clip_width]), min([main_height, clip_height]))

    clip_frames, clip_frame_pos = get_clip_frames(cap_clip, clip_frame_num, size)

    comparisons = {}

    for i in range(start_frame, main_frame_num):
        if i + clip_frame_pos[len(clip_frame_pos)-1] > main_frame_num:
            return comparisons
        frame_diff = []

        for j in range(len(clip_frame_pos)):
            main_frame = get_frame(cap_main, i+clip_frame_pos[j], size)
            clip_frame = clip_frames[j]
            this_diff = compare(main_frame, clip_frame)

            if this_diff < 0.005:
                frame_diff.append(this_diff)
            else:
                frame_diff = [1]
                break

        comparisons[i] = frame_diff
        if i != start_frame and 1 not in comparisons[i-1] and 1 in comparisons[i]:
            return comparisons, clip_frame_num


def compare(vid, clip, num=64):
    percent = 0
    for a, b in zip(np.array_split(vid, num), np.array_split(clip, num)):
        percent += abs(np.sum(a) - np.sum(b)) / ((len(a)) * (len(a[0])) * 3 * 256)  # DO FIX on 256???
    return percent/num


def main(main_dir, clip_dir, start_frame=0):

    comparisons, clip_duration = iter_all(main_dir, clip_dir, start_frame)
    all_together = [sum(comparisons[i])/len(comparisons[i]) for i in comparisons]

    return min(all_together), all_together.index(min(all_together))+start_frame, clip_duration


if __name__ == '__main__':
    main(main_dir=r"G:\Recording\Video.mp4", clip_dir=r"G:\Etho Best 105-605\Ep 106 - 1.mp4")
