from tinytag import TinyTag
from pymediainfo import MediaInfo

def extrair_metadados_audio(self, caminho):
    metadados = {}

    try:
        tag = TinyTag.get(caminho)

        if tag.duration:
            duracao = int(tag.duration)
            metadados['duracao'] = f"{duracao//3600:02d}:{(duracao%3600)//60:02d}:{duracao%60:02d}"

        if tag.bitrate:
            metadados['taxa_bits'] = f"{tag.bitrate} kbps"

        if tag.artist:
            metadados['artist'] = tag.artist

        if tag.album:
            metadados['album'] = tag.album

        if tag.title:
            metadados['title'] = tag.title

    except Exception as e:
        print(f"Erro ao extrair metadados do áudio {caminho}: {e}")

        try:
            media_info = MediaInfo.parse(caminho)
            for track in media_info.tracks:
                if track.track_type == "Audio":
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

                    break

        except Exception as me:
            print(f"Fallback para MediaInfo também falhou: {me}")

    return metadados
