import pytube

url = 'https://www.youtube.com/watch?v=sPL46v7xrMY'

save_dir = r'G:\Recording'

yt = pytube.YouTube(url)

yt.streams.filter(only_audio=True).first().download(save_dir, filename='Audio.mp4')
