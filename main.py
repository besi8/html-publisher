# ✅ main.py - version e përmirësuar me variabla të lexueshëm nga ambienti
import os
import zipfile
import io
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lexim i kredencialeve nga environment variables
NETLIFY_SITE_ID = os.environ.get("NETLIFY_SITE_ID")
NETLIFY_API_TOKEN = os.environ.get("NETLIFY_API_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "✅ Aplikacioni është gjallë!",
        "message": "Flask serveri pret POST në /publish."
    })

@app.route("/publish", methods=["POST"])
def publish():
    html_content = request.form.get("html")
    if not html_content:
        return jsonify({"error": "Asnjë HTML nuk u dërgua."}), 400

    # Krijo ZIP me index.html
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        zipf.writestr("index.html", html_content)
    zip_buffer.seek(0)

    # Konfigurimi për Netlify
    headers = {
        "Authorization": f"Bearer {NETLIFY_API_TOKEN}"
    }
    files = {
        'file': ('site.zip', zip_buffer, 'application/zip')
    }
    url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"

    # Dërgo kërkesën
    response = requests.post(url, headers=headers, files=files)

    if response.status_code in [200, 201]:
        deploy_url = response.json().get('deploy_ssl_url')
        return jsonify({
            "message": "Publikimi u krye me sukses në Netlify!",
            "url": deploy_url
        })
    else:
        return jsonify({
            "error": "Dështoi publikimi",
            "details": response.text
        }), 500
