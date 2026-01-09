from flask import Flask, request, render_template
import os
import boto3
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Read S3 credentials from environment variables
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
REGION = os.environ.get("AWS_REGION")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["photo"]
        if file:
            filename = secure_filename(file.filename)
            
            # Save locally first (optional)
            local_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(local_path)
            
            # Upload to S3
            s3.upload_file(local_path, BUCKET_NAME, filename)
            
            return "✅ Photo uploaded successfully to S3!"
    
    # List photos in S3 bucket
    try:
        objects = s3.list_objects_v2(Bucket=BUCKET_NAME)
        files = [obj['Key'] for obj in objects.get('Contents', [])]
    except:
        files = []
    
    # Show simple gallery
    gallery_html = ""
    for f in files:
        url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{f}"
        gallery_html += f'<img src="{url}" width="200" style="margin:5px;">'
    
    return f'''
    <h2>📸 Trip Photo Upload</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="photo" required>
        <br><br>
        <button type="submit">Upload</button>
    </form>
    <h3>Gallery</h3>
    {gallery_html}
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
