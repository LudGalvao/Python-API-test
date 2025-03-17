import os
import re
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import logging

app = FastAPI()

@app.get("/download_audio")
async def download_audio(youtube_url: str = Query(..., title="Youtube URL", description="Insira o link do vídeo do Youtube")):
    try:
        
        if not re.match(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+', youtube_url):
            raise HTTPException(status_code=400, detail="URL do YouTube inválida")

        
        ydl_opts = {
            'format': 'bestaudio/best',  
            'extractaudio': True,  
            'outtmpl': '%(title)s.%(ext)s',  
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            file_path = f"{info_dict['title']}.{info_dict['ext']}"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Erro ao baixar o áudio")

        return FileResponse(file_path, media_type="audio/mpeg", filename=f"{info_dict['title']}.{info_dict['ext']}")

    except Exception as e:
        logging.error(f"Erro ao tentar baixar o áudio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
