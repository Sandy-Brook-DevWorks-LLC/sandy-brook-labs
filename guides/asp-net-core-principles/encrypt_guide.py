#!/usr/bin/env python3
"""
Encrypt the <main> content of each ASP.NET Core study guide HTML page.

For each file:
  1. Extract everything between <main...> and </main>
  2. Encrypt it with AES-256-GCM, key derived from password via PBKDF2
  3. Replace the <main> body with:
     - A <script> tag loading crypto.js
     - A <script id="rv-encrypted-data"> element holding salt, iv, ciphertext
  4. Write the file back in place

Usage:
    python encrypt_guide.py <password>
"""

import sys, os, re, hashlib, secrets, base64
from pathlib import Path

# --- AES-GCM via cryptography library ---
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

# Files to encrypt (all chapter pages + index + capstone, but NOT the PDF)
TARGET_FILES = sorted(GUIDE_DIR.glob("chapter*.html")) + [
    GUIDE_DIR / "index.html",
    GUIDE_DIR / "capstone.html",
]


def derive_key(password: str, salt: bytes) -> bytes:
    """PBKDF2-SHA256 → 256-bit key (matches the JS side)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt(plaintext: str, password: str) -> tuple[str, str, str]:
    """Encrypt plaintext → (salt_b64, iv_b64, ciphertext_b64)."""
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)  # AES-GCM standard nonce
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
    return (
        base64.b64encode(salt).decode(),
        base64.b64encode(iv).decode(),
        base64.b64encode(ct).decode(),
    )


# Regex to capture <main ...> ... </main>  (DOTALL so . matches newlines)
MAIN_RE = re.compile(
    r"(<main[^>]*>)(.*?)(</main>)",
    re.DOTALL,
)


def process_file(filepath: Path, password: str) -> bool:
    """Encrypt the <main> content of a single HTML file in-place."""
    html = filepath.read_text(encoding="utf-8")

    m = MAIN_RE.search(html)
    if not m:
        print(f"  SKIP  {filepath.name} — no <main> found")
        return False

    open_tag = m.group(1)   # e.g. <main> or <main style="...">
    content  = m.group(2)   # the inner HTML
    close_tag = m.group(3)  # </main>

    # Don't re-encrypt if already encrypted
    if "rv-encrypted-data" in content:
        print(f"  SKIP  {filepath.name} — already encrypted")
        return False

    salt_b64, iv_b64, ct_b64 = encrypt(content, password)

    # Build the replacement <main> body
    replacement_body = f"""
<script id="rv-encrypted-data" type="application/octet-stream"
        data-salt="{salt_b64}"
        data-iv="{iv_b64}">{ct_b64}</script>
"""

    new_main = open_tag + replacement_body + close_tag

    # Inject crypto.js script right before </body> if not already present
    if "crypto.js" not in html:
        html = html.replace("</body>", '    <script src="crypto.js"></script>\n</body>')

    # Replace the <main> block
    html = html[:m.start()] + new_main + html[m.end():]

    filepath.write_text(html, encoding="utf-8")
    ct_kb = len(ct_b64) / 1024
    print(f"  OK    {filepath.name} — encrypted ({ct_kb:.0f} KB payload)")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python encrypt_guide.py <password>")
        sys.exit(1)

    password = sys.argv[1]
    print(f"\nEncrypting {len(TARGET_FILES)} files in {GUIDE_DIR.name}/")
    print(f"PBKDF2 iterations: {ITERATIONS:,}")
    print(f"Cipher: AES-256-GCM\n")

    encrypted = 0
    for fp in TARGET_FILES:
        if fp.exists():
            if process_file(fp, password):
                encrypted += 1
        else:
            print(f"  MISS  {fp.name} — file not found")

    print(f"\nDone. {encrypted} files encrypted.")


if __name__ == "__main__":
    main()
