#!/usr/bin/env python3
import subprocess
import re
import qrcode
import signal

QR_IMAGE_PATH = "/tmp/remote_touchpad_qr.png"
REMOTE_CMD = ["flatpak", "run", "com.github.unrud.RemoteTouchpad"]

def run_remote_touchpad():
    # Ejecutar Remote Touchpad y capturar stdout
    proc = subprocess.Popen(
        REMOTE_CMD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    url_pattern = re.compile(r'https?://[^\s]+')
    url = None

    try:
        for line in proc.stdout:
            match = url_pattern.search(line)
            if match:
                url = match.group(0)
                print(f"URL detectada: {url}")
                break
    finally:
        proc.terminate()
        proc.wait()

    if url:
        # Generar QR
        img = qrcode.make(url)
        img.save(QR_IMAGE_PATH)
        print(f"QR guardado en {QR_IMAGE_PATH}")
    else:
        print("No se detectó ninguna URL.")

if __name__ == "__main__":
    run_remote_touchpad()
