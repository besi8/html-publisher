from flask import Flask, request, jsonify
import zipfile
import io
import requests
import os  # Shtuar për env vars

app = Flask(__name__)

# Përdor env vars për siguri (vendos në Render Settings > Environment)
NETLIFY_SITE_ID = os.getenv('NETLIFY_SITE_ID', 'ea2c01c6-c2b6-46e3-ab7a-135b45af3838')
NETLIFY_API_TOKEN = os.getenv('NETLIFY_API_TOKEN', 'nfp_G1fwnnWwkQPTB9xrFZ8QWXVdYxgYbxmW6f11')

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "✅ App is running", "message": "Use POST /publish to deploy HTML to Netlify"})

@app.route("/publish", methods=["POST"])
def publish():
    html_content = request.form.get("html")
    if not html_content:
        return jsonify({"error": "No HTML provided"}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        zipf.writestr("index.html", html_content)
    zip_buffer.seek(0)

    headers = {
        "Authorization": f"Bearer {NETLIFY_API_TOKEN}",
        "Content-Type": "application/zip"  # Korrigjuar: Nevojshëm për raw ZIP
    }

    url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"
    response = requests.post(url, headers=headers, data=zip_buffer.getvalue())  # Korrigjuar: data= në vend të files=

    if response.status_code in [200, 201]:
        return jsonify({"message": "✅ Deployment successful!", "url": response.json().get('deploy_ssl_url')})
    elif response.status_code == 429:
        return jsonify({"error": "Rate limit exceeded", "details": response.text}), 429
    else:
        return jsonify({"error": "Deployment failed", "details": response.text}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)  # Vetëm për test lokal
