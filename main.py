from flask import Flask, request, jsonify
import zipfile
import io
import requests

app = Flask(__name__)

NETLIFY_API_TOKEN = "nfp_G1fwnnWwkQPTB9xrFZ8QWXVdYxgYbxmW6f11"
NETLIFY_SITE_ID = "ea2c01c6-c2b6-46e3-ab7a-135b45af3838"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ Serveri është aktiv.",
        "usage": "POST HTML to /publish to deploy."
    })

@app.route("/publish", methods=["POST"])
def publish():
    html_content = request.form.get("html")
    if not html_content:
        return jsonify({"error": "Missing HTML content in form-data."}), 400

    # Krijimi i një ZIP-i me index.html
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("index.html", html_content)
    zip_buffer.seek(0)

    # Dërgimi i kërkesës në Netlify
    headers = {
        "Authorization": f"Bearer {NETLIFY_API_TOKEN}"
    }

    files = {
        'file': ('site.zip', zip_buffer, 'application/zip')
    }

    netlify_url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"
    response = requests.post(netlify_url, headers=headers, files=files)

    if response.status_code in [200, 201]:
        return jsonify({
            "message": "✅ Publikimi u krye me sukses!",
            "deploy_url": response.json().get("deploy_ssl_url")
        })
    else:
        return jsonify({
            "error": "Deployment failed.",
            "details": response.text
        }), 500

if __name__ == "__main__":
    app.run()
