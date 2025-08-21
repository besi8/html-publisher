from flask import Flask, request, jsonify
import zipfile
import io
import requests

app = Flask(__name__)

NETLIFY_API_TOKEN = "nfp_G1fwnnWwkQPTB9xrFZ8QWXVdYxgYbxmW6f11"  # ← zëvendëso nëse ndryshon
NETLIFY_SITE_ID = "ea2c01c6-c2b6-46e3-ab7a-135b45af3838"       # ← zëvendëso nëse ndryshon

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "✅ Aplikacioni është gjallë!",
        "message": "Flask serveri është ngritur me sukses dhe pret kërkesa në /publish."
    })

@app.route("/publish", methods=["POST"])
def publish():
    html_content = request.form.get("html")
    if not html_content:
        return jsonify({"error": "No HTML provided"}), 400

    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr("index.html", html_content)
    zip_buffer.seek(0)

    headers = {
        "Authorization": f"Bearer {NETLIFY_API_TOKEN}"
    }
    files = {
        "file": ("site.zip", zip_buffer, "application/zip")
    }
    url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"
    response = requests.post(url, headers=headers, files=files)

    if response.status_code in [200, 201]:
        return jsonify({
            "message": "✅ Deploy me sukses!",
            "url": response.json().get("deploy_ssl_url")
        })
    else:
        return jsonify({
            "error": "❌ Deploy dështoi!",
            "details": response.text
        }), 500
