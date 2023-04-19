from pytube import YouTube
yt = YouTube('https://youtu.be/NUdu1n-ML98')
yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
