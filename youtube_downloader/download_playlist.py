from pytube import Playlist

playlist = Playlist('https://youtu.be/qQvEV2dTTW8')
cur_dir = "./ict_2022_mentorship"
print(f"downloading to {cur_dir}")
for video in playlist.videos:
    print('downloading : {} with url : {}'.format(video.title, video.watch_url))
    video.streams.\
        filter(type='video', progressive=True, file_extension='mp4').\
        order_by('resolution').\
        desc().\
        first().\
        download(cur_dir)

#yt = YouTube('https://youtu.be/tmeCWULSTHc')
#
#from pytube import YouTube
#import json
#yt = YouTube('https://youtu.be/tmeCWULSTHc')
#output = yt.streams.order_by('resolution').desc()
