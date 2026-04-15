#!/usr/bin/env python3
"""
Decrypt the <main> content of each ASP.NET Core study guide HTML page.

Reverses encrypt_guide.py so you can edit the cleartext content, then
re-encrypt with encrypt_guide.py when you're ready to publish.

Usage:
    python decrypt_guide.py <password>

Workflow:
    1. python decrypt_guide.py SandyBrook     # unlock for editing
    2. ... make your changes ...
    3. python encrypt_guide.py SandyBrook      # lock for publishing
"""

import sys, os, re, base64
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("Installing cryptography package...")
    os.system(f"{sys.executable} -m pip install cryptography --break-system-packages -q")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes

ITERATIONS = 100_000
GUIDE_DIR = Path(__file__).parent


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def decrypt(password: str, salt_b64: str, iv_b64: str, ct_b64: str) -> str:
    salt = base64.b64decode(salt_b64)
    iv = base64.b64decode(iv_b64)
    ct = base64.b64decode(ct_b64)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ct, None).decode("utf-8")


# Regex to match the encrypted <main> block
MAIN_RE = re.compile(
    r"(<main[^>]*>)\s*"
    r'<script id="rv-encrypted-data" type="application/octet-stream"\s+'
    r'data-salt="([^"]+)"\s+'
    r'data-iv="([^"]+)">'
    r"([^<]+)"
    r"</script>\s*"
    r"(</main>)",
    re.DOTALL,
)


def process_file(filepath: Path, password: str) -> bool:
    html = filepath.read_text(encoding="utf-8")

    m = MAIN_RE.search(html)
    if not m:
        print(f"  SKIP  {filepath.name} — not encrypted")
        return False

    open_tag   = m.group(1)
    salt_b64   = m.group(2)
    iv_b64     = m.group(3)
    ct_b64     = m.group(4).strip()
    close_tag  = m.group(5)

    try:
        plaintext = decrypt(password, salt_b64, iv_b64, ct_b64)
    except Exception:
        print(f"  FAIL  {filepath.name} — wrong password or corrupted data")
        return False

    # Restore the original <main> content
    new_main = open_tag + plaintext + close_tag
    html = html[:m.start()] + new_main + html[m.end():]

    # Remove the crypto.js script tag (keep the file, just unlink it)
    html = html.replace('    <script src="crypto.js"></script>\n', '')

    filepath.write_text(html, encoding="utf-8")
    print(f"  OK    {filepath.name} — decrypted ({len(plaintext):,} chars)")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python decrypt_guide.py <password>")
        sys.exit(1)

    password = sys.argv[1]

    target_files = sorted(GUIDE_DIR.glob("chapter*.html")) + [
        GUIDE_DIR / "index.html",
        GUIDE_DIR / "capstone.html",
    ]

    print(f"\nDecrypting {len(target_files)} files in {GUIDE_DIR.name}/\n")

    decrypted = 0
    failed = 0
    for fp in target_files:
        if fp.exists():
            result = process_file(fp, password)
            if result:
                decrypted += 1
            elif "FAIL" in open(os.devnull).read() if False else "":
                failed += 1

    print(f"\nDone. {decrypted} files decrypted.")
    if decrypted > 0:
        print("\nYou can now edit the HTML files freely.")
        print("When done, re-encrypt with:  python encrypt_guide.py <password>")


if __name__ == "__main__":
    main()
