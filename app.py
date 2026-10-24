import os
import time
import requests
import asyncio
from google import genai
import edge_tts

# FIX ERROR MOVIEPY V2+: Impor langsung dari module moviepy (tanpa .editor)
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. SETUP API KEYS & CONFIG
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")

client = genai.Client(api_key=GEMINI_API_KEY)

print("🚀 Memulai Pipeline Otomasi YouTube Gratis...")

# 2. GENERATE NASKAH VIA GEMINI API
prompt = "Buat naskah video pendek YouTube Short (maksimal 20 detik) tentang fakta sains unik dalam bahasa Indonesia. Format response langsung naskah narasi tanpa intro/outro."
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
script_text = response.text.strip()
print(f"📝 Naskah Dihasilkan:\n{script_text}\n")

# 3. GENERATE VOICEOVER GRATIS (Edge-TTS)
async def generate_audio(text, output_file):
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
    await communicate.save(output_file)

audio_file = "voiceover.mp3"
asyncio.run(generate_audio(script_text, audio_file))
print("🎙️ Audio Voiceover Berhasil Dibuat!")

# 4. DOWNLOAD GAMBAR VISUAL GRATIS (Pollinations.ai)
img_prompt = "aesthetic space galaxy ultra detailed 8k cinematic"
img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(img_prompt)}?width=1080&height=1920&nologo=true"
img_data = requests.get(img_url).content
image_file = "background.jpg"
with open(image_file, 'wb') as f:
    f.write(img_data)
print("🖼️ Gambar Background Berhasil Diunduh!")

# 5. RENDER VIDEO MP4 (Kompatibel MoviePy v2)
audio_clip = AudioFileClip(audio_file)
# Di MoviePy v2, penentuan durasi menggunakan method with_duration() atau set_duration()
image_clip = ImageClip(image_file).with_duration(audio_clip.duration)
video_clip = image_clip.with_audio(audio_clip)

output_video = "final_output.mp4"
video_clip.write_videofile(
    output_video, 
    fps=24, 
    codec="libx264", 
    audio_codec="aac",
    preset="ultrafast",
    threads=4
)
print("🎬 Video Berhasil Dirender!")

# 6. UPLOAD & SCHEDULE KE YOUTUBE
def upload_to_youtube(video_path):
    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET
    )
    youtube = build('youtube', 'v3', credentials=creds)

    # Menentukan Jadwal Publish (2 jam dari sekarang)
    publish_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 7200))

    body = {
        'snippet': {
            'title': 'Fakta Unik Sains Hari Ini #Shorts',
            'description': f'{script_text}\n\n#shorts #sains #faktaunik',
            'tags': ['shorts', 'sains', 'faktaunik'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': publish_time
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = request.execute()
    print(f"🎉 Sukses Ter-upload & Terjadwal! Video ID: {response['id']} (Tayang pada {publish_time})")

upload_to_youtube(output_video)import os
import time
import requests
import asyncio
from google import genai
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. SETUP API KEYS & CONFIG
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")

client = genai.Client(api_key=GEMINI_API_KEY)

print("🚀 Memulai Pipeline Otomasi YouTube Gratis...")

# 2. GENERATE NASKAH VIA GEMINI API
prompt = "Buat naskah video pendek YouTube Short (maksimal 20 detik) tentang fakta sains unik dalam bahasa Indonesia. Format response langsung naskah narasi tanpa intro/outro."
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
script_text = response.text.strip()
print(f"📝 Naskah Dihasilkan:\n{script_text}\n")

# 3. GENERATE VOICEOVER GRATIS (Edge-TTS)
async def generate_audio(text, output_file):
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
    await communicate.save(output_file)

audio_file = "voiceover.mp3"
asyncio.run(generate_audio(script_text, audio_file))
print("🎙️ Audio Voiceover Berhasil Dibuat!")

# 4. DOWNLOAD GAMBAR VISUAL GRATIS (Pollinations.ai)
img_prompt = "aesthetic space galaxy ultra detailed 8k cinematic"
img_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(img_prompt)}?width=1080&height=1920&nologo=true"
img_data = requests.get(img_url).content
image_file = "background.jpg"
with open(image_file, 'wb') as f:
    f.write(img_data)
print("🖼️ Gambar Background Berhasil Diunduh!")

# 5. RENDER VIDEO MP4 (Sederhana tanpa ImageMagick dependency)
audio_clip = AudioFileClip(audio_file)
image_clip = ImageClip(image_file).set_duration(audio_clip.duration)
video_clip = image_clip.set_audio(audio_clip)

output_video = "final_output.mp4"
# Menggunakan preset ultrafast agar proses render di GitHub Actions sangat cepat
video_clip.write_videofile(
    output_video, 
    fps=24, 
    codec="libx264", 
    audio_codec="aac",
    preset="ultrafast",
    threads=4
)
print("🎬 Video Berhasil Dirender!")

# 6. UPLOAD & SCHEDULE KE YOUTUBE
def upload_to_youtube(video_path):
    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET
    )
    youtube = build('youtube', 'v3', credentials=creds)

    # Menentukan Jadwal Publish (2 jam dari sekarang)
    publish_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 7200))

    body = {
        'snippet': {
            'title': 'Fakta Unik Sains Hari Ini #Shorts',
            'description': f'{script_text}\n\n#shorts #sains #faktaunik',
            'tags': ['shorts', 'sains', 'faktaunik'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': publish_time
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = request.execute()
    print(f"🎉 Sukses Ter-upload & Terjadwal! Video ID: {response['id']} (Tayang pada {publish_time})")

upload_to_youtube(output_video)
