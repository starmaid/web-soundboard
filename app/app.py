# app.py
# This file runs the flask webserver

import json
import os
import subprocess
import uuid as uuidlib
import time
import sys

from flask import Flask, render_template, request, make_response, redirect, url_for, send_file, send_from_directory, abort
from waitress import serve
from pydub import AudioSegment
from pydub.playback import play
from mutagen.wave import WAVE


from audiotools import *

app = Flask(__name__)

# PAGES: endpoints that return webpages =======================================

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
def index():
    """
    The homepage.
    """

    return render_template('index.html')


@app.route('/info')
def info():
    """
    Version, your own pubkey, and other info
    """
    global version

    return render_template('info.html',
        version=version,
        hostname=config['hostname'],
        )

@app.route('/board')
def board():
    directory = './app/static/sounds'  # Change to your directory
    files = [[f,WAVE(os.path.join(directory, f)).tags['TIT2'].text] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    print(files)
    return render_template('board.html', files=files)


@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        print(request.form)
        try:
            r = request.form.to_dict()
        except:
            data = request.form
            r = str(request.values)

        videolink = r['videolink'].split('&')[0]

        with open("./links.txt",'a') as f:
            f.write(f'{videolink}\n')

        return render_template('upload.html')

@app.route('/play', methods=['GET'])
def play_sound():
    filename = request.args.get('filename')
    if not filename:
        abort(400, "Missing filename parameter")
    sounds_dir = os.path.join(app.static_folder, 'sounds')
    file_path = os.path.join(sounds_dir, filename)
    if not os.path.isfile(file_path):
        abort(404, "File not found")
    try:
        audio = AudioSegment.from_file(file_path)
        play(audio)
        return f"Playing {filename}", 200
    except Exception as e:
        abort(500, f"Error playing file: {str(e)}")

download_inprogress = False

@app.route('/downloadall', methods=['GET'])
def downloadall():
    global download_inprogress
    if download_inprogress:
        return render_template('index.html', status="already downloading")
    
    download_inprogress = True
    with open("links.txt",'r') as f:
        links = [x.strip() for x in f.readlines()]

    download_youtube_wavs(links,'app/static/sounds')
    download_inprogress = False
    return render_template('index.html', status="completed new download.")


@app.route('/logs')
def logs():
    logs_text = log_buffer.get_logs()
    return render_template('logs.html', logs=logs_text)


# NON-PAGE HELPERS: do other tasks in the program =============================

def loadConfig():
    with open('./app/data/config.json', 'r') as c:
        try:
            config = json.load(c)
        except:
            print('unable to load config. Exiting')
            config = None
    print('loaded config')
    return config

class LogBuffer:
    def __init__(self, max_lines=100):
        self.max_lines = max_lines
        self.lines = []
        self._stdout = sys.__stdout__  # Save original stdout

    def write(self, msg):
        self._stdout.write(msg)        # Print to normal stdout
        for line in msg.splitlines():
            self.lines.append(line)
            if len(self.lines) > self.max_lines:
                self.lines.pop(0)

    def flush(self):
        self._stdout.flush()

    def get_logs(self):
        return "\n".join(self.lines)

log_buffer = LogBuffer(100)
sys.stdout = log_buffer
sys.stderr = log_buffer




if __name__ == '__main__':
    # Load config

    config = loadConfig()
    if config['usegit']:
        version = subprocess.check_output("git describe --tags", shell=True).decode().strip().split('-')[0]
    else:
        version = '0.1.0'
    
    # start web server
    if config is not None:
        if config['debug']:
            app.run(debug=True, host='0.0.0.0', port=config['flaskport'])
        else:
            # This is the 'production' WSGI server
            serve(app, host='0.0.0.0', port=config['flaskport'])
