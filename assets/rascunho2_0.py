from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.serialization import pkcs12

def gerar_certificado_teste():
    # Geração da chave privada
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Informações do sujeito do certificado (simplificadas)
    nome_sujeito = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "Test Cert"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    ])

    # Construção do certificado
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome_sujeito)
        .issuer_name(nome_sujeito)
        .public_key(chave_privada.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=1825))
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CODE_SIGNING]),
            critical=False
        )
        .sign(chave_privada, hashes.SHA256())
    )

    # Serialização para PFX
    pfx = pkcs12.serialize_key_and_certificates(
        name=b"TestCert",
        key=chave_privada,
        cert=certificado,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(b"Senha123"),
    )

    # Salvando o arquivo PFX
    with open("test_cert.pfx", "wb") as arquivo_pfx:
        arquivo_pfx.write(pfx)

    print("Certificado de teste gerado com sucesso: test_cert.pfx")
    print("Senha: Senha123")

if __name__ == "__main__":
    gerar_certificado_teste()