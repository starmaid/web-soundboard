# You need to install pydub and ffmpeg: pip install pydub
# ffmpeg: sudo apt install ffmpeg

from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import yt_dlp
from mutagen.wave import WAVE
import taglib

#import openai

PTOKEN = "MlJ7HpTfrz-6XHsl2muP_k1XeFod-40Q9KAomC17Bes2YQ2IalIsqJDc9XBz6kKW2vQcPaTTLoJwWAh0_WXqkn6Zy7UrUqjinl51I-LVNo18HuV5"

def trim_leading_silence(input_path, output_path, silence_thresh=-40, chunk_size=10):
    audio = AudioSegment.from_wav(input_path)
    nonsilent = detect_nonsilent(audio, min_silence_len=chunk_size, silence_thresh=silence_thresh)
    if nonsilent:
        start_trim = nonsilent[0][0]
        trimmed_audio = audio[start_trim:]
    else:
        trimmed_audio = audio
    
    # trim to 6 seconds
    trimmed_audio2 = trimmed_audio[:6000]

    trimmed_audio2.export(output_path, format="wav")
    tags = taglib.File(output_path)
    tags.tags["TITLE"] = WAVE(input_path).tags['TIT2'].text
    tags.save()
    return


def download_youtube_wavs(links, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'worstaudio',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '1',  # lowest quality
        }],
        'quiet': True,
    }
    for link in links:
        # Get YouTube video ID
        video_id = link.split('v=')[-1].split('&')[0]
        wav_path = os.path.join(output_dir, f"{video_id}.wav")
        if os.path.exists(wav_path):
            print(f"Already downloaded: {wav_path}")
            continue
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

def download_youtube_wavs_V2(links, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts1 = {
        'format': 'worstaudio',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '1',  # lowest quality
        }],
        'quiet': True,
        'skip_download': True,  # We'll download manually after extracting info
        'extractor_args': {"youtube":{"player-client":["default","mweb"],"po_token":[f"mweb.player+{PTOKEN}"]}}
    }

    ydl_opts2 = {
        'format': 'worstaudio',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '1',  # lowest quality
        }],
        'quiet': True,
        'extractor_args': {"youtube":{"player-client":["default","mweb"],"po_token":[f"mweb.player+{PTOKEN}"]}}
    }
    for link in links:
        with yt_dlp.YoutubeDL(ydl_opts1) as ydl:
            info = ydl.extract_info(link, download=False)            
            video_id = info['id']
            title = info.get('title', '')
            
            #print(f'{video_id} {title}')
            
            wav_path = os.path.join(output_dir, f"{video_id}.wav")
            if os.path.exists(wav_path):
                print(f"Already downloaded: {wav_path}")
                tags = taglib.File(wav_path)
                tags.tags["TITLE"] = title
                tags.save()
                continue
            # Download audio
            

        with yt_dlp.YoutubeDL(ydl_opts2) as ydl:
            ydl.download([link])
            # Add metadata (title) using pydub
            audio = AudioSegment.from_file(wav_path)
            audio.export(wav_path, format="wav", tags={"title": title})
            tags = taglib.File(wav_path)
            tags.tags["TITLE"] = title
            tags.save()
            print(f"saved metadata on {title}")

def extract_sound_name(title, api_key=None):
    """
    Extracts the identifying name of a sound effect from a long title using OpenAI's GPT.
    Example: "Bonk Sound Effect (High Quality) (420kbps)" -> "Bonk"
    """
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not provided")
    openai.api_key = api_key
    prompt = (
        f'Extract only the short identifying name of the sound effect from this title: "{title}". '
        'Return only the name, no extra words or punctuation.'
    )
    response = openai.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.choices[0].message.content.strip()
    """
    print("that costs money lol")
    return

if __name__ == "__main__":
    with open("links.txt",'r') as f:
        links = [x.strip() for x in f.readlines()]

    #print(links)

    #download_youtube_wavs_V2(links,'app/static/sounds')
    rootname = "./app/static/sounds"
    for path in os.listdir(f"{rootname}/orig"):
        trim_leading_silence(f"{rootname}/orig/{path}",f"{rootname}/{path}")