import cv2
import numpy as np
import warnings
from PIL import Image

warnings.filterwarnings("ignore")


def get_frame(cap, frame, size):  # gets a frame from specified position, returns at specified size
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    ret, cv2_im = cap.read()
    if ret:
        converted = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(converted)
        pil_im_resize = pil_im.resize(size)
        return np.array(pil_im_resize, dtype='int64')


def get_clip_frames(cap, clip_frame_num, size, num=8):  # get frames from the clip to compare
    frame_pos_list = np.linspace(0, clip_frame_num-1, num=num, dtype='int')
    clip_frames = []
    for frame_pos in frame_pos_list:
        clip_frames.append(get_frame(cap, frame_pos, size))

    return clip_frames, frame_pos_list


def get_size(cap):  # get resolution of video
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

    clip_frames, clip_frame_pos = get_clip_frames(cap=cap_clip, clip_frame_num=clip_frame_num, size=size,
                                                  num=max(int(clip_frame_num / (30 * 1.2)), 8))

    comparisons = {}

    for i in range(start_frame, main_frame_num):
        if i + clip_frame_pos[len(clip_frame_pos)-1] > main_frame_num:
            return comparisons, clip_frame_num
        frame_diff = []

        for j in range(len(clip_frame_pos)):
            main_frame = get_frame(cap_main, i+clip_frame_pos[j], size)
            clip_frame = clip_frames[j]
            this_diff = compare(vid=main_frame, clip=clip_frame, num=size[1])

            if this_diff != 1:
                frame_diff.append(this_diff)
            else:
                frame_diff = [1]
                break

        comparisons[i] = frame_diff
        if i != start_frame and 1 not in comparisons[i-1] and 1 in comparisons[i]:
            return comparisons, clip_frame_num


def compare(vid, clip, num=64):  # compare clip frame to main video frame
    percent = 0
    for a, b in zip(np.array_split(vid, num), np.array_split(clip, num)):
        diff = abs(np.sum(a) - np.sum(b)) / ((len(a)) * (len(a[0])) * 3 * 256)  # divides by resolution, number of
        # individual pixels (3), number of possible pixel values (256)
        if diff < 0.5:
            percent += diff
        else:
            return 1
        percent += diff
    return percent/num  # divides by number of sectors that were compared


def main(main_dir, clip_dir, start_frame=0):

    iter_all_out = iter_all(main_dir, clip_dir, start_frame)
    print(iter_all_out)
    if iter_all_out is not None:
        comparisons = iter_all_out[0]
        clip_duration = iter_all_out[1]
        all_together = [sum(comparisons[i])/len(comparisons[i]) for i in comparisons]

        print(min(all_together), all_together.index(min(all_together))+start_frame, clip_duration)
        return min(all_together), all_together.index(min(all_together))+start_frame, clip_duration

    else:
        return None


if __name__ == '__main__':
    main(main_dir=r"G:\Etho New Clips\test.mp4", clip_dir=r"G:\Etho Best 105-605\Ep 107.mp4", start_frame=300)
