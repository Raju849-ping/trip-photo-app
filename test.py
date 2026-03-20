from flask import Flask, request, render_template, redirect, url_for
import boto3
import os
import uuid

app = Flask(__name__)

# AWS S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_REGION")
)

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
            # ✅ Create unique filename
            unique_filename = str(uuid.uuid4()) + "_" + file.filename

            # ✅ Upload with public access
            s3.upload_fileobj(
                file,
                BUCKET,
                unique_filename,
                ExtraArgs={
                    "ContentType": file.content_type,
                    "ACL": "public-read"   # 🔥 IMPORTANT CHANGE
                }
            )

            return redirect(url_for("gallery"))

    # ---------- Load Images ----------
    response = s3.list_objects_v2(Bucket=BUCKET)

    photos = []
    if "Contents" in response:
        for obj in response["Contents"]:
            # ✅ Direct public URL (no expiry needed)
            url = f"https://{BUCKET}.s3.amazonaws.com/{obj['Key']}"

            photos.append({
                "name": obj["Key"],
                "url": url
            })

    return render_template("gallery.html", photos=photos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
