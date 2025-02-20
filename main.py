from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import re
import logging
import os
from io import BytesIO
from tempfile import NamedTemporaryFile

app = FastAPI()

# Configuração do logging para registrar erros
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Expressão regular para validar URLs do YouTube
YOUTUBE_REGEX = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com|youtu\.be)/"
)

@app.get("/download_audio")
async def download_audio(youtube_url: str = Query(..., title="Youtube URL", description="Insira o link do vídeo do Youtube")):
    try:
        # Validação do URL
        if not YOUTUBE_REGEX.match(youtube_url):
            raise HTTPException(status_code=400, detail="URL inválida. Insira um link válido do YouTube.")

        # Opções de download sem usar o ffmpeg
        ydl_opts = {
            'format': 'bestaudio/best',  # Pegando o melhor áudio disponível
            'outtmpl': '-',  # Saída para stdout
            'quiet': True,  # Silenciar a saída do yt-dlp
        }

        # Usando NamedTemporaryFile para criar um arquivo temporário
        with NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
            tmp_filename = tmp_file.name

        # Função de download e salvamento no arquivo temporário
        def download_audio_data():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                ydl.process_info(info_dict)
                filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
                
                # Salvando o áudio no arquivo temporário
                with open(filename, "rb") as f:
                    with open(tmp_filename, "wb") as tmp_file:
                        tmp_file.write(f.read())
                
                os.remove(filename)  # Apagar o arquivo original

                return info_dict['title']
        
        title = download_audio_data()

        # Enviar a resposta com o áudio
        return StreamingResponse(open(tmp_filename, "rb"), media_type="audio/webm", headers={"Content-Disposition": f"attachment; filename={title}.webm"})
    
    except yt_dlp.DownloadError:
        logging.error(f"Erro ao baixar o áudio do link: {youtube_url}")
        raise HTTPException(status_code=500, detail="Erro ao baixar o áudio. Verifique se o link está correto e tente novamente.")
    
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno. Tente novamente mais tarde.")
