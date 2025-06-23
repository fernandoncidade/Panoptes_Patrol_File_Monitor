def extrair_metadados_executavel(self, caminho):
    metadados = {}

    try:
        import pefile
        import win32api

        try:
            info = win32api.GetFileVersionInfo(caminho, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            versao = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"

            try:
                lang, codepage = win32api.GetFileVersionInfo(caminho, '\\VarFileInfo\\Translation')[0]
                str_info = {}
                for entry in ['CompanyName', 'FileDescription', 'InternalName', 'LegalCopyright', 'OriginalFilename', 'ProductName', 'ProductVersion', 'FileVersion']:
                    try:
                        str_path = f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\{entry}'
                        str_info[entry] = win32api.GetFileVersionInfo(caminho, str_path)

                    except:
                        pass

                if 'FileVersion' in str_info:
                    metadados['versao'] = str_info['FileVersion']

                else:
                    metadados['versao'] = versao

                if 'CompanyName' in str_info:
                    metadados['empresa'] = str_info['CompanyName']

                if 'FileDescription' in str_info:
                    metadados['descricao'] = str_info['FileDescription']

                if 'ProductName' in str_info:
                    metadados['produto'] = str_info['ProductName']

                if 'LegalCopyright' in str_info:
                    metadados['copyright'] = str_info['LegalCopyright']

            except Exception as e:
                print(f"Erro ao extrair strings de versão: {e}")
                metadados['versao'] = versao

        except Exception as e:
            print(f"Erro com win32api: {e}")
            try:
                pe = pefile.PE(caminho)
                if hasattr(pe, 'VS_FIXEDFILEINFO'):
                    info = pe.VS_FIXEDFILEINFO
                    versao = f"{info.FileVersionMS >> 16}.{info.FileVersionMS & 0xFFFF}.{info.FileVersionLS >> 16}.{info.FileVersionLS & 0xFFFF}"
                    metadados['versao'] = versao

                if hasattr(pe, 'FileInfo'):
                    for fileinfo in pe.FileInfo:
                        for entry in fileinfo:
                            if hasattr(entry, 'StringTable'):
                                for st in entry.StringTable:
                                    for key, value in st.entries.items():
                                        key_str = key.decode('utf-8', errors='ignore')
                                        val_str = value.decode('utf-8', errors='ignore')
                                        if key_str == 'FileVersion':
                                            metadados['versao'] = val_str

                                        elif key_str == 'CompanyName':
                                            metadados['empresa'] = val_str

                                        elif key_str == 'FileDescription':
                                            metadados['descricao'] = val_str

                                        elif key_str == 'ProductName':
                                            metadados['produto'] = val_str

                pe.close()

            except Exception as pe_error:
                print(f"Erro com pefile: {pe_error}")

        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.x509.oid import NameOID
            import win32security

            signatures = win32security.CryptQueryObject(
                win32security.CERT_QUERY_OBJECT_FILE,
                caminho,
                win32security.CERT_QUERY_CONTENT_FLAG_PKCS7_SIGNED_EMBED,
                win32security.CERT_QUERY_FORMAT_FLAG_BINARY,
                0,
                0,
                0,
                None,
                None,
                None,
                None
            )

            if signatures:
                metadados['assinado'] = 'Sim'

            else:
                metadados['assinado'] = 'Não'

        except Exception as sig_error:
            print(f"Erro ao verificar assinatura: {sig_error}")

    except ImportError as imp_err:
        print(f"Bibliotecas para executáveis não disponíveis: {imp_err}")

    except Exception as e:
        print(f"Erro geral ao extrair metadados do executável {caminho}: {e}")

    return metadados
