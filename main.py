from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import yt_dlp
import os

app = FastAPI()

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.get("/download_audio")
async def download_audio(youtube_url: str = Query(..., title="Youtube URL", description="Insira o link do vídeo do Youtube")):
    try:
        # Usando yt-dlp para baixar o áudio diretamente sem FFmpeg
        ydl_opts = {
            'format': 'bestaudio/best',  # Melhor áudio disponível
            'extractaudio': True,  # Extrair apenas o áudio
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Caminho do arquivo
            # Não vamos usar o FFmpeg aqui
        }

        # Usando yt-dlp para baixar o áudio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            file_path = f"{DOWNLOAD_FOLDER}/{info_dict['title']}.{info_dict['ext']}"

        # Retornar o arquivo de áudio para o usuário
        return FileResponse(file_path, media_type="audio/mpeg", filename=f"{info_dict['title']}.{info_dict['ext']}")
    
    except Exception as e:
        return {"error": str(e)}
