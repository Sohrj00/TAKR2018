from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
#generate our key
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
# Write our key to disk for safe keeping
with open("client2-key.pem", "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
    ))
#various details about who we are. For a self-signed certificate the
# subject and issuer are always the same.
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"CZ"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"MS"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Brno"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Client 2 bueno projekt"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"client2-buenoprojekt.com"),
])
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    # Our certificate will be valid for 10 days
    datetime.datetime.utcnow() + datetime.timedelta(days=10)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"127.0.0.1")]),
    critical=False,
# Sign our certificate with our private key
).sign(key, hashes.SHA256(), default_backend())
# Write our certificate out to disk.
with open("client2-cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
print(cert)