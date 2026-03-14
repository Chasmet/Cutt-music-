import os
import io
import zipfile
import tempfile
from math import ceil
from flask import Flask, request, send_file, render_template_string
from werkzeug.utils import secure_filename
from pydub import AudioSegment

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "flac", "ogg", "aac", "wma"}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Cutter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            margin: 0;
            padding: 30px;
        }
        .box {
            max-width: 650px;
            margin: auto;
            background: #1e1e1e;
            padding: 25px;
            border-radius: 14px;
        }
        h1 {
            margin-top: 0;
            text-align: center;
        }
        p {
            color: #ccc;
            text-align: center;
        }
        label {
            display: block;
            margin-top: 16px;
            margin-bottom: 6px;
            font-weight: bold;
        }
        input, select, button {
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: none;
            box-sizing: border-box;
            font-size: 16px;
        }
        input, select {
            background: #2d2d2d;
            color: white;
        }
        button {
            margin-top: 20px;
            background: #00b894;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background: #00a383;
        }
        .error {
            background: #b33939;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>Découpe Audio</h1>
        <p>Charge un audio, choisis une durée, récupère un ZIP avec tous les morceaux.</p>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST" enctype="multipart/form-data">
            <label>Fichier audio</label>
            <input type="file" name="audio_file" accept=".mp3,.wav,.m4a,.flac,.ogg,.aac,.wma" required>

            <label>Durée de découpe</label>
            <select name="segment_length">
                <option value="10">10 secondes</option>
                <option value="15">15 secondes</option>
                <option value="30">30 secondes</option>
                <option value="custom">Personnalisée</option>
            </select>

            <label>Durée personnalisée (si besoin)</label>
            <input type="number" name="custom_length" min="1" placeholder="Ex : 12">

            <button type="submit">Découper et télécharger</button>
        </form>
    </div>
</body>
</html>
"""

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_PAGE, error=None)

    file = request.files.get("audio_file")
    segment_choice = request.form.get("segment_length", "10")
    custom_length = request.form.get("custom_length", "").strip()

    if not file or file.filename == "":
        return render_template_string(HTML_PAGE, error="Aucun fichier sélectionné.")

    if not allowed_file(file.filename):
        return render_template_string(HTML_PAGE, error="Format non supporté.")

    try:
        if segment_choice == "custom":
            if not custom_length.isdigit():
                return render_template_string(HTML_PAGE, error="La durée personnalisée doit être un nombre entier.")
            segment_seconds = int(custom_length)
        else:
            segment_seconds = int(segment_choice)

        if segment_seconds <= 0:
            return render_template_string(HTML_PAGE, error="La durée doit être supérieure à 0.")
    except ValueError:
        return render_template_string(HTML_PAGE, error="Valeur de durée invalide.")

    original_filename = secure_filename(file.filename)
    base_name, ext = os.path.splitext(original_filename)
    ext = ext.lower().replace(".", "")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, original_filename)
        file.save(input_path)

        try:
            audio = AudioSegment.from_file(input_path)
        except Exception as e:
            return render_template_string(HTML_PAGE, error=f"Erreur lecture audio : {e}")

        audio_length_ms = len(audio)
        segment_length_ms = segment_seconds * 1000

        if segment_length_ms > audio_length_ms:
            return render_template_string(HTML_PAGE, error="La durée choisie est plus longue que le fichier audio.")

        total_parts = ceil(audio_length_ms / segment_length_ms)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i in range(total_parts):
                start_ms = i * segment_length_ms
                end_ms = min((i + 1) * segment_length_ms, audio_length_ms)
                chunk = audio[start_ms:end_ms]

                chunk_name = f"{base_name}_{i+1:03d}.{ext}"
                chunk_path = os.path.join(temp_dir, chunk_name)

                try:
                    chunk.export(chunk_path, format=ext)
                    zipf.write(chunk_path, arcname=chunk_name)
                except Exception as e:
                    return render_template_string(HTML_PAGE, error=f"Erreur export morceau {i+1} : {e}")

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"{base_name}_decoupe.zip",
            mimetype="application/zip"
        )

if __name__ == "__main__":
    app.run(debug=True)
