import os
import yt_dlp
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

OUTPUT_DIR = '/tmp/downloads'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/convertir', methods=['GET'])
def convertir_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Falta la URL del video"}), 400

    # Buscamos el archivo cookies.txt en la raiz del servidor
    cookies_path = os.path.join(os.getcwd(), 'cookies.txt')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(OUTPUT_DIR, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    # Si el archivo existe, se lo inyectamos de prepo a yt-dlp
    if os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_id = info['id']
            archivo_mp3 = os.path.join(OUTPUT_DIR, f"{video_id}.mp3")

            if os.path.exists(archivo_mp3):
                return send_file(
                    archivo_mp3,
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name=f"{info.get('title', 'audio')}.mp3"
                )
            else:
                return jsonify({"error": "No se pudo generar el archivo MP3"}), 500

    except Exception as e:
        error_msg = str(e).split('\n')[0]
        return jsonify({"error": f"Error: {error_msg}"}), 500

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=puerto)
