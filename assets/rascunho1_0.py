from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.serialization import pkcs12

def gerar_certificado_pfx(nome, organizacao, email, site, cidade, estado, pais, senha, arquivo_saida="certificado.pfx"):
    """Gera um certificado digital PFX (PKCS#12) com os dados fornecidos."""

    # Geração da chave privada
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Informações do sujeito do certificado
    nome_sujeito = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, nome),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organizacao),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
        x509.NameAttribute(NameOID.LOCALITY_NAME, cidade),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, estado),
        x509.NameAttribute(NameOID.COUNTRY_NAME, pais),
    ])

    # Construção do certificado
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome_sujeito)
        .issuer_name(nome_sujeito)  # Autoassinado
        .public_key(chave_privada.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=1825))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(site)]),
            critical=False,
        )
        # Adicionar esta extensão para assinatura de código
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CODE_SIGNING]),
            critical=False
        )
        .sign(chave_privada, hashes.SHA256())
    )

    # Serialização do certificado e da chave privada para o formato PFX (PKCS#12)
    pfx = pkcs12.serialize_key_and_certificates(
        name=organizacao.encode(),
        key=chave_privada,
        cert=certificado,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )

    # Salvando o arquivo PFX
    with open(arquivo_saida, "wb") as arquivo_pfx:
        arquivo_pfx.write(pfx)

    print(f"Certificado PFX gerado com sucesso: {arquivo_saida}")


if __name__ == "__main__": 
    gerar_certificado_pfx(
        nome="Fernando Nillsson Cidade",
        organizacao="fernandoncidade",
        email="fernando.n.cidade@outlook.com",
        site="https://github.com/fernandoncidade",
        cidade="São José dos Pinhais",
        estado="Paraná",
        pais="BR",
        senha="fernando1603nillsson1986cidade",
    )
