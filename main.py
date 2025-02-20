import os
import re
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import logging

app = FastAPI()

DOWNLOAD_FOLDER = "downloads"

@app.get("/download_audio")
async def download_audio(youtube_url: str = Query(..., title="Youtube URL", description="Insira o link do vídeo do Youtube")):
    try:
        # Verificar se a URL fornecida é válida
        if not re.match(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+', youtube_url):
            raise HTTPException(status_code=400, detail="URL do YouTube inválida")

        # Usando yt-dlp para baixar o áudio diretamente sem FFmpeg
        ydl_opts = {
            'format': 'bestaudio/best',  # Melhor áudio disponível
            'extractaudio': True,  # Extrair apenas o áudio
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',  # Caminho do arquivo
        }

        # Usando yt-dlp para baixar o áudio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            file_path = f"{DOWNLOAD_FOLDER}/{info_dict['title']}.{info_dict['ext']}"

        # Verificar se o arquivo foi baixado corretamente
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Erro ao baixar o áudio")

        # Retornar o arquivo de áudio para o usuário
        return FileResponse(file_path, media_type="audio/mpeg", filename=f"{info_dict['title']}.{info_dict['ext']}")

    except Exception as e:
        # Logar o erro para análise posterior
        logging.error(f"Erro ao tentar baixar o áudio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
