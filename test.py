from flask import Flask, request, render_template, redirect, url_for
import boto3
import os

app = Flask(__name__)

# ✅ Using IAM Role (no keys needed)
s3 = boto3.client("s3")

BUCKET = os.environ.get("AWS_BUCKET_NAME")


@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("gallery"))


@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    # ---------- Upload ----------
    if request.method == "POST":
        file = request.files.get("photo")

        if file and file.filename:
            s3.upload_fileobj(
                file,
                BUCKET,
                file.filename,
                ExtraArgs={
                    "ContentType": file.content_type,
                    "ACL": "public-read"   # ✅ allow public access
                }
            )
            return redirect(url_for("gallery"))

    # ---------- Fetch Images ----------
    response = s3.list_objects_v2(Bucket=BUCKET)

    photos = []
    if "Contents" in response:
        for obj in response["Contents"]:
            url = f"https://{BUCKET}.s3.eu-north-1.amazonaws.com/{obj['Key']}"
            photos.append({
                "name": obj["Key"],
                "url": url
            })

    return render_template("gallery.html", photos=photos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


# ---------------- Telegram Script ----------------
import requests
from datetime import datetime

def send_telegram(msg):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={
        "chat_id": chat_id,
        "text": msg
    }, timeout=5)


send_telegram(f"""
🚀 App Started

⏰ Time: {datetime.utcnow()}
📦 Service: Trip Photo App
""")
