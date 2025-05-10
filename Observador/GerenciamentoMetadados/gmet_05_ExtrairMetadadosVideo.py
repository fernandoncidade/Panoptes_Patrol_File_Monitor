import os
import time
import win32api
from pymediainfo import MediaInfo

def extrair_metadados_video(self, caminho):
    metadados = {}

    caminho = os.path.normpath(caminho).replace('/', '\\')
    if not os.path.exists(caminho):
        return metadados

    try:
        import win32security
        import ntsecuritycon as con

        sd = win32security.GetFileSecurity(caminho, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32security.TOKEN_QUERY)
        sid = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
        dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, sid)
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        win32security.SetFileSecurity(caminho, win32security.DACL_SECURITY_INFORMATION, sd)

    except Exception as e:
        print(f"Erro ao ajustar permissões: {e}")

    max_tentativas = 5
    delays = [0.5, 1.0, 2.0, 3.0, 5.0]

    for tentativa in range(max_tentativas):
        try:
            media_info = MediaInfo.parse(caminho)
            for track in media_info.tracks:
                if track.track_type == "Video":
                    if hasattr(track, 'width') and hasattr(track, 'height'):
                        metadados['dimensoes'] = f"{track.width}x{track.height}"

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

            if metadados:
                return metadados

        except Exception as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            time.sleep(delays[tentativa])

            if tentativa == max_tentativas - 1:
                try:
                    media_info = MediaInfo.parse(caminho, full=True)
                    for track in media_info.tracks:
                        if track.track_type == "Video":
                            if hasattr(track, 'width') and hasattr(track, 'height'):
                                metadados['dimensoes'] = f"{track.width}x{track.height}"

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
                    print(f"Fallback também falhou: {me}")

    return metadados
