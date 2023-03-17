# This is a sample Python script.
from typing import Union

from fastapi import FastAPI
# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
from starlette.responses import StreamingResponse
import pytube
import requests
import shutil
import music_tag
import os

def download_image(url, path):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(f"{path}/artwork.jpg", 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        f.close()
    else:
        return False
    return True

def download(url: str, download_format: str, name_of_playlist: str, track_number: str):
    if not name_of_playlist == "Unbekannt":
        is_playlist = True
    else:
        is_playlist = False
    i = 0
    path = "/main/youtubeDownload/download"
    yt = pytube.YouTube(url)
    if download_format.lower() in ["mp3", "aac", "aiff", "ogg", "wav"]:
        try:
            author, topic = yt.author.split("-")
        except ValueError:
            author = yt.author
        stream = yt.streams.get_audio_only()
        file = f"{author}- {stream.title}"
        filename = f"{file}.mp3"
    else:
        author = yt.author
        stream = yt.streams.get_highest_resolution()
        filename = f"{author}- {stream.title}.mp4"
    if os.path.exists(path+"/"+filename):
        set_tags(yt, filename, author, name_of_playlist, path, is_playlist, track_number)
        return path+"/"+filename
    stream.download(output_path=path, filename=filename)
    set_tags(yt, filename, author, name_of_playlist, path, is_playlist, track_number)
    return path+"/"+filename


def set_tags(yt, file, author, name_of_playlist, path, is_playlist=False, track_number=0):

    if "Album" in name_of_playlist:
        album, name_of_playlist = name_of_playlist.split("- ")
    if is_playlist:
        song = music_tag.load_file(f"{path}/{file}")
        song.append_tag('album', name_of_playlist)
        song['tracknumber'] = track_number
    else:
        song = music_tag.load_file(f"{path}/{file}")
    song.append_tag('title', yt.title)
    song.append_tag('artist', author)
    while not download_image(yt.thumbnail_url, path):
        continue
    with open(path + "/artwork.jpg", 'rb') as img_in:
       song['artwork'] = img_in.read()
    os.remove(path + "/artwork.jpg")
    song.save()

app = FastAPI()


#127.0.0.1:8000/youtubeDownload?url=https://www.youtube.com/watch?v=tas0O586t80&download_format=mp4&name_of_playlist=Unbekannt&track_number=0
@app.get("/youtubeDownload/version")
def youtubeDownloadVersion():
    with open("/main/youtubeDownload/version") as f:
        return {"version": f.read()}

@app.get("/youtubeDownload")
def youtubeDownload(url: str, download_format: str, name_of_playlist: str, track_number: str):
    filename = download(url, download_format, name_of_playlist, track_number)
    if "mp3" in filename:
        return StreamingResponse(open(filename, "rb"), media_type="audio/mp3")
    else:
        return StreamingResponse(open(filename, "rb"), media_type="video/mp4")

#alle Armin Geräte
@app.get("/devices")
def devices():
    with open("/main/armin_devices/devices") as f:
        return {"devices": f.read()}