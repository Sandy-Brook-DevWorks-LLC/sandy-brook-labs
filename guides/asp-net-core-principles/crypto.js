/**
 * RecipeVault Study Guide — Client-Side Content Protection
 *
 * Encrypts guide content with AES-256-GCM derived from a password via PBKDF2.
 * The encrypted payload is stored inline in each HTML page; the cleartext
 * content never appears in the page source.
 *
 * Flow:
 *  1. Page loads → <main> contains only a password prompt + encrypted blob.
 *  2. User enters password (or it's read from sessionStorage).
 *  3. Password → PBKDF2 (100 000 iterations, SHA-256) → AES-GCM key.
 *  4. Decrypt the blob → inject decrypted HTML into <main>.
 *  5. Store password in sessionStorage so subsequent pages don't re-prompt.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'rv_guide_pwd';
  const ITERATIONS  = 100000;

  // ── Helpers ──────────────────────────────────────────────

  function b64ToBuffer(b64) {
    const bin = atob(b64);
    const buf = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    return buf;
  }

  function bufferToB64(buf) {
    let bin = '';
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin);
  }

  async function deriveKey(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']
    );
    return crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt: salt, iterations: ITERATIONS, hash: 'SHA-256' },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    );
  }

  async function decryptContent(password, saltB64, ivB64, ciphertextB64) {
    const salt       = b64ToBuffer(saltB64);
    const iv         = b64ToBuffer(ivB64);
    const ciphertext = b64ToBuffer(ciphertextB64);
    const key        = await deriveKey(password, salt);
    const plainBuf   = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: iv },
      key,
      ciphertext
    );
    return new TextDecoder().decode(plainBuf);
  }

  // ── UI ───────────────────────────────────────────────────

  function buildPromptUI() {
    return `
      <div id="rv-lock" style="
        max-width: 420px;
        margin: 80px auto;
        padding: 2.5rem 2rem;
        text-align: center;
        border-radius: 1rem;
        border: 1px solid var(--border, #e2e8f0);
        background: var(--surface, #f8fafc);
      ">
        <div style="margin-bottom:1.25rem;">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
               style="display:inline-block;color:var(--brand-teal,#1a5f6b);">
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <h2 style="font-size:1.25rem;font-weight:700;margin-bottom:.5rem;">Protected Content</h2>
        <p style="color:var(--text-dim,#64748b);font-size:.9rem;margin-bottom:1.5rem;line-height:1.5;">
          This study guide is password-protected out of respect for the original author.<br>
          Enter the access password to continue.
        </p>
        <form id="rv-form" autocomplete="off" style="display:flex;flex-direction:column;gap:.75rem;">
          <input id="rv-pwd" type="password" placeholder="Password" autocomplete="off"
            style="
              width:100%;
              padding:.65rem 1rem;
              border-radius:.5rem;
              border:1px solid var(--border,#e2e8f0);
              font-size:.95rem;
              background:white;
              color:#1e293b;
              outline:none;
              transition:border-color .2s;
              box-sizing:border-box;
            "
          />
          <button type="submit" style="
            padding:.65rem 1rem;
            border-radius:.5rem;
            border:none;
            background:var(--brand-teal,#1a5f6b);
            color:white;
            font-weight:600;
            font-size:.95rem;
            cursor:pointer;
            transition:opacity .2s;
          ">Unlock</button>
          <p id="rv-error" style="color:#ef4444;font-size:.85rem;display:none;margin:0;">
            Incorrect password. Please try again.
          </p>
        </form>
      </div>
    `;
  }

  // ── Main ─────────────────────────────────────────────────

  async function tryDecrypt(password) {
    const dataEl = document.getElementById('rv-encrypted-data');
    if (!dataEl) return false;

    const salt       = dataEl.getAttribute('data-salt');
    const iv         = dataEl.getAttribute('data-iv');
    const ciphertext = dataEl.textContent.trim();

    try {
      const html = await decryptContent(password, salt, iv, ciphertext);
      // Replace the <main> contents with decrypted HTML
      const main = document.querySelector('main');
      main.innerHTML = html;
      // Persist password for this session
      try { sessionStorage.setItem(STORAGE_KEY, password); } catch (_) {}
      return true;
    } catch (_) {
      return false;
    }
  }

  function showPrompt() {
    const main = document.querySelector('main');
    // Keep the encrypted data element, prepend the prompt
    const dataEl = document.getElementById('rv-encrypted-data');
    const dataHTML = dataEl ? dataEl.outerHTML : '';
    main.innerHTML = buildPromptUI() + dataHTML;

    const form  = document.getElementById('rv-form');
    const input = document.getElementById('rv-pwd');
    const error = document.getElementById('rv-error');

    input.focus();

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      error.style.display = 'none';
      const pwd = input.value;
      if (!pwd) return;

      const ok = await tryDecrypt(pwd);
      if (!ok) {
        error.style.display = 'block';
        input.value = '';
        input.focus();
      }
    });
  }

  async function init() {
    // Only run on pages that have encrypted content
    const dataEl = document.getElementById('rv-encrypted-data');
    if (!dataEl) return;

    // Try session password first
    let stored = null;
    try { stored = sessionStorage.getItem(STORAGE_KEY); } catch (_) {}

    if (stored) {
      const ok = await tryDecrypt(stored);
      if (ok) return;
      // Bad stored password — clear and show prompt
      try { sessionStorage.removeItem(STORAGE_KEY); } catch (_) {}
    }

    showPrompt();
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
