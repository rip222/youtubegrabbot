import os
import requests
import subprocess
from threading import Thread
from youtube_dl import YoutubeDL
from tempfile import TemporaryFile


output = 'output.mp4'


def handleMessage(message):
    try:
        if message.get('message') != None:
            user = message['message']['from']['id']
            received = message['message']['text']
            if 'https://www.youtube.com/watch?v=' in received\
            or 'https://youtu.be/' in received:
                sent = formats(received)
                with open('url', 'w') as f:
                    f.write(received)
            else:
                sent = commands(received, message)
        elif message.get('callback_query') != None:
                f = open('url', 'r')
                url = f.read()
                user = message['callback_query']['from']['id']
                received = message['callback_query']['data']
                sent = get(url, received)
    except:
        sent = "Can't process that. Sorry..."
    return user, sent


def formats(url):
    """Returns a list of available resolutions of a Youtube video.
    Some results are intentionally omitted"""
    result = []
    info = YoutubeDL().extract_info(url, download=False)
    for i in info['formats']: # the list of dicts containing info about all formats
        resolution = i['format_note']
        extension = i['ext']

        if extension == 'mp4' \
        and resolution not in ['hd720', 'medium', 'small', 'DASH audio']:
            result.append(resolution)
            result.sort()
    return result


def get(url, format):
    """Downloads audio and the video in the chosen format, combines them"""
    video = TemporaryFile(prefix='.video_'+format, delete=False, dir='')
    audio = TemporaryFile(prefix='.audio_', delete=False, dir='')
    size_limit = 50000000 # size limit for telegram bots in bytes
    urls = []
    total_size = 0
    info = YoutubeDL().extract_info(url, download=False)
    for i in info['formats']:
        resolution = i['format_note']
        url = i['url']
        extension = i['ext']
        if extension == 'mp4' or extension == 'm4a':
            if resolution == format or resolution == 'DASH audio':
                urls.append(url)
                r = requests.head(url, stream=True, allow_redirects=True)
                r_size = int(r.headers['content-length'])
                total_size += r_size
    if total_size <= size_limit:
        t1 = Thread(target=download, args=(urls[0], audio))
        t2 = Thread(target=download, args=(urls[1], video))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        mux(audio.name, video.name)
        return open('output.mp4', 'rb')
    else:
        return "The video is too big to upload :  {}mb.\n\
Here is the download link: \n\
{}".format(int(total_size/1000000), url)


def download(url, file, size_limit=50000000):
    with requests.get(url, stream=True, allow_redirects=True) as r:
            for chunk in r.iter_content(chunk_size=100*4086):
                if chunk:
                    file.write(chunk)


def mux(audio, video):
    mux = subprocess.call(f'ffmpeg -i {audio} -i {video} -c:v copy -c:a copy {output}')


def temp_delete():
    for file in os.listdir('.'):
        if file.startswith('.audio') or file.startswith('.video'):
            os.remove(file)
        if file.endswith('.mp4'):
            os.remove(file)


def commands(text, message):
    name = message['message']['chat']['first_name']
    username = message['message']['chat']['username']
    if text == '/start':
        response = """
        Hi there, {}. I can download Youtube videos for you!
        Type /help if you need assistance!
        Type /about to visit my github page.""".format(name if name else username)
    elif text == '/help':
        response = """
1. Send a youtube video link
2. Choose a suitable format to download the video
3. Enjoy:)"""
    elif text == '/about':
        response = 'https://github.com/dmzmk/youtubegrabbot'
    else:
        response = "Sorry. I don't understand that:("
    return response
