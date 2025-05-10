from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption

def extrair_chave_privada(caminho_pfx, senha, arquivo_saida="chave_privada.key"):
    with open(caminho_pfx, "rb") as arquivo:
        pfx_data = arquivo.read()

    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
        pfx_data, 
        senha.encode()
    )

    pem_key = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )

    with open(arquivo_saida, "wb") as key_file:
        key_file.write(pem_key)

    print(f"Chave privada extraída e salva em {arquivo_saida}")
    return pem_key

if __name__ == "__main__":
    extrair_chave_privada("certificado.pfx", "#@Brahe@#16&03#@Kepler@#19&86#@Higgs@#")


from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PrivateFormat, NoEncryption

def extrair_chave_privada(caminho_pfx, senha, arquivo_saida="chave_privada.pem"):
    with open(caminho_pfx, "rb") as arquivo:
        pfx_data = arquivo.read()

    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
        pfx_data, 
        senha.encode()
    )

    pem_key = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )

    with open(arquivo_saida, "wb") as key_file:
        key_file.write(pem_key)

    print(f"Chave privada extraída e salva em {arquivo_saida}")
    return pem_key

if __name__ == "__main__":
    extrair_chave_privada("certificado.pfx", "#@Brahe@#16&03#@Kepler@#19&86#@Higgs@#")
