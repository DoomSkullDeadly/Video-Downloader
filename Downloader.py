import pytube
import os
import shutil
from ffmpy import FFmpeg

link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

video_res = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
video_codec = ["avc1", "vp9"]
video_fps = ["60", "50", "48", "30", "25", "24"]


def download(url, save_dir, target_res='2160p', target_fps='60'):
    global vid_name
    yt = pytube.YouTube(url)
    vid_name = char_check(yt.title)
    print('title downloaded:', vid_name)

    global bestcodec

    stream = None
    bestres = None
    bestfps = None
    bestcodec = None

    for vres in video_res:
        for stream in yt.streams.filter(res=vres):
            if stream and not bestres:
                bestres = vres
            if stream and vres == target_res:
                bestres = vres
                break

    print(bestres)

    for vfps in video_fps:
        for stream in yt.streams.filter(res=bestres):
            # print(stream)
            if vfps == stream.fps and not bestfps:
                bestfps = vfps
            if stream.fps == target_fps:
                bestfps = target_fps
                break

    print(bestfps)

    for codec in video_codec:
        for stream in yt.streams.filter(res=bestres, fps=bestfps):
            if codec in stream.video_codec and not bestcodec:
                bestcodec = stream.video_codec
    print('Stream found')
    print(yt.streams.filter(res=bestres, fps=bestfps, video_codec=bestcodec).first())

    if bestcodec == 'vp9':
        yt.streams.filter(res=bestres, fps=bestfps, video_codec=bestcodec).first().download(save_dir,
                                                                                            filename='Video.webm')
        ret = '.webm'
    else:
        yt.streams.filter(res=bestres, fps=bestfps, video_codec=bestcodec).first().download(save_dir,
                                                                                            filename='Video.mp4')
        ret = '.mp4'
    print('Video downloaded')

    if not yt.streams.filter(res=bestres, fps=bestfps, video_codec=bestcodec).first().is_progressive:
        bestrate = 0
        for stream in yt.streams.filter(only_audio=True):
            if bestrate < int(stream.abr[:-4]):
                bestrate = int(stream.abr[:-4])
        bestrate = str(bestrate)+'kbps'
        yt.streams.filter(only_audio=True, abr=bestrate).first().download(save_dir, filename='Audio.mp4')
        print('Audio downloaded')
        return 'audio', ret
    else:
        return 'video', ret


def join(directory, output_dir, vid_name, start_time=0.0, duration=0):
    global bestcodec

    if bestcodec == 'vp9':
        fext = '.webm'
    else:
        fext = '.mp4'

    if start_time or duration:
        ff = FFmpeg(
            inputs={directory + '\\Video' + fext: f'-ss {start_time}', directory + '\\Audio.mp4': f'-ss {start_time}'},
            outputs={output_dir + '\\' + vid_name + '.mp4': f'-c:v libx264 -crf 10 -preset slow -t {duration/30} -c:a aac -t {duration/30}'}
        )
        """
        ffmpeg -i "G:\Recording\Video.mp4" -ss 17:00 -to 17:10 -force_key_frames "expr:eq(n,n)" -c:v libx264 -crf 10 -preset slow -c:a copy G:\Recording\test.mp4
        try this first:
        ffmpeg -ss 1020.000 -i "G:\Recording\Video.mp4" -c:a copy -c:v libx264 -crf 10 -preset slow -frames:v 300 "G:\Recording\test2.mp4"
        use that to cut video, after analysing it, before adding audio to it
        """
        #ff.cmd = f'ffmpeg -ss {start_time} -i "G:\Recording\Video.mp4" -c:v libx264 -crf 10 -preset slow -frames:v {duration} "G:\Recording\test2.mp4"'
    else:
        ff = FFmpeg(
            inputs={directory + '\\Video' + fext: None, directory + '\\Audio.mp4': None},
            outputs={output_dir + '\\' + vid_name + '.mp4': '-c:v copy -c:a copy'}
        )
    print(ff.cmd)
    ff.run()


def char_check(string):
    special_chars = '<>:"/\|?*'
    for i in range(len(string)):
        if string[i] in special_chars:
            string = string.replace(string[i], '-')
    return string


def main():
    url = input("Enter youtube URL: ")
    directory = 'G:\\Recording'
    target_res = '2160p'
    target_fps = '60'
    output_dir = 'G:\\Recording'

    if 'audio' in download(url, directory, target_res, target_fps):
        join(directory=directory, output_dir=output_dir, vid_name=vid_name, start_time=1023.7666666666667, duration=86)
        #os.remove(directory+'\\Video.mp4')
        #os.remove(directory+'\\Audio.mp4')
    else:
        shutil.move(directory+'\\Video.mp4', output_dir+'\\Video.mp4')
        os.rename(directory+'\\Video.mp4', output_dir+'\\'+vid_name+'.mp4')


if __name__ == '__main__':
    main()
