import Downloader
import Compare
from pytube import Playlist
import os
import warnings

warnings.filterwarnings("ignore")

playlist_url = "https://www.youtube.com/playlist?list=PLaAVDbMg_XArcet5lwcRo12Fh9JrGKydh"

old_dir = r"G:\\Etho Best 105-605"
new_dir = r"G:\\Etho New Clips"

old_files = [fname.path for fname in os.scandir(old_dir) if fname.is_file()]
new_files = [fname.path for fname in os.scandir(new_dir) if fname.is_file()]

p = Playlist(playlist_url)
videos = [video for video in p.videos[:150]]


def get_next_ep_num():
    for ep in old_files:
        if ep not in new_files:
            return ep.split("Ep ")[1].split(" -")[0]


def get_old_clips_urls(num):
    return [path for path in old_files if str(num) in path]


def main():
    ep_num = get_next_ep_num()
    ep_clips = get_old_clips_urls(ep_num)
    video = videos[int(ep_num)-105]

    downloader_out = Downloader.download(url=video.watch_url, save_dir=new_dir)

    start_frame = 0
    for clip in ep_clips:
        compare_out = Compare.main(main_dir=new_dir+'\\Video'+downloader_out[1], clip_dir=clip, start_frame=start_frame)
        start_frame = compare_out[1]
        start_time = start_frame / 30  # at 30fps
        if compare_out[0] < 0.05:
            Downloader.join(directory=new_dir, output_dir=new_dir, vid_name=clip.replace(old_dir+'\\', '')
                            .replace('.mp4', ''), start_time=start_time, duration=compare_out[2])


if __name__ == "__main__":
    while True:
        main()
