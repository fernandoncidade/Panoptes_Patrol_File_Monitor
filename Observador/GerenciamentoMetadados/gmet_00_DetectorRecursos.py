import os
import sys
import logging

logger = logging.getLogger('FileManager')

class DetectorRecursosWindows:
    """Classe para detectar a disponibilidade de recursos Windows e fornecer alternativas."""
    
    # Variáveis de classe para armazenar informações de disponibilidade
    win32api_disponivel = False
    win32security_disponivel = False
    file_version_disponivel = False
    crypt_query_disponivel = False
    pefile_disponivel = False
    
    @classmethod
    def inicializar(cls):
        """Verifica a disponibilidade de recursos e inicializa as flags."""
        try:
            # Verificar win32api
            try:
                import win32api
                cls.win32api_disponivel = True
                
                # Verificar se GetFileVersionInfoSize está disponível
                if hasattr(win32api, 'GetFileVersionInfoSize'):
                    cls.file_version_disponivel = True
                else:
                    logger.warning("Função GetFileVersionInfoSize não disponível no win32api")
            except ImportError:
                logger.warning("Módulo win32api não disponível")
            
            # Verificar win32security
            try:
                import win32security
                cls.win32security_disponivel = True
                
                # Verificar se CryptQueryObject está disponível
                if hasattr(win32security, 'CryptQueryObject'):
                    cls.crypt_query_disponivel = True
                else:
                    logger.warning("Função CryptQueryObject não disponível no win32security")
            except ImportError:
                logger.warning("Módulo win32security não disponível")
            
            # Verificar pefile
            try:
                import pefile
                cls.pefile_disponivel = True
            except ImportError:
                logger.warning("Módulo pefile não disponível")
            
            # Log da detecção
            recursos = []
            if cls.win32api_disponivel:
                recursos.append("win32api")
            if cls.file_version_disponivel:
                recursos.append("GetFileVersionInfo")
            if cls.win32security_disponivel:
                recursos.append("win32security")
            if cls.crypt_query_disponivel:
                recursos.append("CryptQueryObject")
            if cls.pefile_disponivel:
                recursos.append("pefile")
            
            logger.info(f"Recursos disponíveis: {', '.join(recursos)}")
            
        except Exception as e:
            logger.error(f"Erro ao verificar recursos disponíveis: {e}")

    @classmethod
    def obter_metadados_basicos_de_executavel(cls, caminho):
        """Obtém metadados básicos de um executável sem usar win32api."""
        metadados = {}
        
        try:
            if os.path.exists(caminho):
                stats = os.stat(caminho)
                tamanho = stats.st_size
                metadados['tamanho'] = tamanho
                
                # Usar heurística baseada no arquivo
                with open(caminho, 'rb') as f:
                    header = f.read(2)
                    if header == b'MZ':
                        metadados['tipo'] = 'Executável Windows'
                    else:
                        metadados['tipo'] = 'Arquivo binário'
                
                # Verificar se tem extensão conhecida
                ext = os.path.splitext(caminho)[1].lower()
                if ext == '.exe':
                    metadados['tipo'] = 'Executável Windows'
                elif ext == '.dll':
                    metadados['tipo'] = 'Biblioteca dinâmica Windows'
                elif ext == '.sys':
                    metadados['tipo'] = 'Driver de dispositivo Windows'
                
                # Se disponível, usar o módulo pefile
                if cls.pefile_disponivel:
                    try:
                        import pefile
                        pe = pefile.PE(caminho, fast_load=True)
                        
                        if hasattr(pe, 'FILE_HEADER'):
                            if pe.FILE_HEADER.Machine == 0x014c:
                                metadados['arquitetura'] = 'x86 (32 bits)'
                            elif pe.FILE_HEADER.Machine == 0x8664:
                                metadados['arquitetura'] = 'x64 (64 bits)'
                            
                            if pe.FILE_HEADER.Characteristics & 0x2000:
                                metadados['tipo'] = 'Biblioteca dinâmica Windows'
                            
                        pe.close()
                    except Exception as pe_error:
                        logger.debug(f"Erro ao usar pefile: {pe_error}")
        
        except Exception as e:
            logger.error(f"Erro ao obter metadados básicos: {e}")
        
        return metadados

# Inicializar o detector ao importar o módulo
DetectorRecursosWindows.inicializar()