import os
from pymediainfo import MediaInfo
from PIL import Image

def extrair_metadados(caminho, loc):
    try:
        stats = os.stat(caminho)
        metadados = {
            "tamanho": stats.st_size,
            "data_acesso": stats.st_atime,
            "data_modificacao": stats.st_mtime,
            "data_criacao": stats.st_ctime
        }

        ext = os.path.splitext(caminho)[1].lower()
        if ext in ['.jpg', '.png', '.mp3', '.mp4', '.pdf']:
            try:
                media_info = MediaInfo.parse(caminho)
                for track in media_info.tracks:
                    if track.track_type == "Image":
                        if hasattr(track, 'width') and hasattr(track, 'height'):
                            metadados['dimensoes'] = f"{track.width}x{track.height}"

                    elif track.track_type in ["Audio", "Video"]:
                        if hasattr(track, 'duration'):
                            duracao_ms = float(track.duration)
                            duracao_s = duracao_ms / 1000.0
                            horas = int(duracao_s // 3600)
                            minutos = int((duracao_s % 3600) // 60)
                            segundos = int(duracao_s % 60)
                            metadados['duracao'] = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

                        if hasattr(track, 'bit_rate'):
                            bit_rate = int(track.bit_rate)
                            metadados['taxa_bits'] = f"{bit_rate//1000} kbps"

            except Exception as e:
                print(f"Erro ao usar MediaInfo: {e}")

                if ext in ['.jpg', '.png']:
                    try:
                        with Image.open(caminho) as img:
                            metadados['dimensoes'] = f"{img.width}x{img.height}"

                    except Exception as ie:
                        print(f"Erro ao abrir imagem: {ie}")

                elif ext == '.pdf':
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(caminho)
                        pages = len(reader.pages)

                    except Exception as pe:
                        print(f"Erro ao ler PDF: {pe}")

        return caminho, metadados

    except Exception as e:
        print(f"Erro extraindo metadados: {e}")
        return caminho, {}
