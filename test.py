from flask import Flask, request, render_template, redirect, url_for
import boto3
import os
from werkzeug.middleware.proxy_fix import ProxyFix   # ✅ NEW

app = Flask(__name__)

# ✅ Fix for ALB / Reverse Proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

# ✅ Using IAM Role (no keys needed)
s3 = boto3.client("s3")

BUCKET = os.environ.get("AWS_BUCKET_NAME")


# ✅ Health Check (for ALB)
@app.route("/health")
def health():
    return "OK", 200


@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("gallery"))


@app.route("/gallery", methods=["GET", "POST"])
def gallery():
    # ---------- Upload ----------
    if request.method == "POST":
        file = request.files.get("photo")

        if file and file.filename:
            try:
                s3.upload_fileobj(
                    file,
                    BUCKET,
                    file.filename,
                    ExtraArgs={
                        "ContentType": file.content_type
                    }
                )
            except Exception as e:
                return f"Upload Error: {str(e)}", 500

            return redirect(url_for("gallery"))

    # ---------- Fetch Images ----------
    photos = []
    try:
        response = s3.list_objects_v2(Bucket=BUCKET)

        if "Contents" in response:
            for obj in response["Contents"]:
                # ✅ Secure temporary URL
                url = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": BUCKET, "Key": obj["Key"]},
                    ExpiresIn=3600
                )

                photos.append({
                    "name": obj["Key"],
                    "url": url
                })

    except Exception as e:
        return f"S3 Error: {str(e)}", 500

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
