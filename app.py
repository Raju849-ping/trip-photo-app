from flask import Flask, request, render_template
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["photo"]
        if file:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            return "✅ Photo uploaded successfully!"
    return '''
    <h2>📸 Trip Photo Upload</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="photo" required>
        <br><br>
        <button type="submit">Upload</button>
    </form>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
