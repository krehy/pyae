from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from supabase import create_client
from dotenv import load_dotenv
import os, uuid, glob

load_dotenv()

app = Flask(__name__)

SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not SUPA_URL or not SUPA_KEY:
    raise RuntimeError("Env variables SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")

supabase = create_client(SUPA_URL, SUPA_KEY)

@app.route("/extract-audio", methods=["POST"])
def extract_audio():
    url = request.json.get("videoUrl")
    if not url:
        return jsonify({"error": "Missing videoUrl"}), 400

    uid = uuid.uuid4().hex
    tmpl = f"temp_{uid}.%(ext)s"
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': tmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '5',
        }],
        'quiet': True,
    }

    with YoutubeDL(opts) as ydl:
        ydl.download([url])

    files = glob.glob(f"temp_{uid}*.mp3")
    if not files:
        return jsonify({"error": "No mp3 found"}), 500
    fname = files[0]

    bucket = supabase.storage.from_("youtube-audio")
    path = f"audio/{uid}.mp3"

    try:
        with open(fname, "rb") as f:
            res = bucket.upload(path, f)  # upload do Supabase :contentReference[oaicite:4]{index=4}

        public_url = bucket.get_public_url(path)
    except Exception as e:
        return jsonify({"error": f"Upload failed: {e}"}), 500
    finally:
        try:
            os.remove(fname)
        except Exception as e:
            print("Warning: failed to remove temp file:", e)

    return jsonify({"audioUrl": public_url, "path": path})

if __name__ == "__main__":
    app.run()
