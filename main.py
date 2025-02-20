from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import re
import logging
from io import BytesIO

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

        # Opções de download para armazenar em memória
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '-',  # Saída para stdout
            'quiet': True,
        }

        # Buffer para armazenar o áudio baixado
        audio_buffer = BytesIO()

        # Função de download e escrita no buffer
        def download_audio_data():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                ydl.process_info(info_dict)
                filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
                with open(filename, "rb") as f:
                    audio_buffer.write(f.read())
                audio_buffer.seek(0)
                os.remove(filename)  # Remove o arquivo temporário
                return info_dict['title']
        
        title = download_audio_data()
        return StreamingResponse(audio_buffer, media_type="audio/mpeg", headers={"Content-Disposition": f"attachment; filename={title}.mp3"})

    except yt_dlp.DownloadError:
        logging.error(f"Erro ao baixar o áudio do link: {youtube_url}")
        raise HTTPException(status_code=500, detail="Erro ao baixar o áudio. Verifique se o link está correto e tente novamente.")

    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno. Tente novamente mais tarde.")