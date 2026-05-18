import os
import yt_dlp
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Carpeta temporal dentro del servidor en la nube para procesar el audio
OUTPUT_DIR = '/tmp/downloads'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/convertir', methods=['GET'])
def convertir_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Falta la URL del video"}), 400

    # Configuración de yt-dlp optimizada para la nube
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(OUTPUT_DIR, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraemos la información para saber el ID del video
            info = ydl.extract_info(video_url, download=True)
            video_id = info['id']
            # Ruta del archivo MP3 generado en el servidor
            archivo_mp3 = os.path.join(OUTPUT_DIR, f"{video_id}.mp3")

            if os.path.exists(archivo_mp3):
                # Enviamos el archivo final directo al teléfono de quien lo pidió
                return send_file(
                    archivo_mp3,
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name=f"{info.get('title', 'audio')}.mp3"
                )
            else:
                return jsonify({"error": "No se pudo generar el archivo MP3"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render u otras nubes te asignan el puerto automáticamente mediante una variable de entorno
    puerto = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=puerto)
