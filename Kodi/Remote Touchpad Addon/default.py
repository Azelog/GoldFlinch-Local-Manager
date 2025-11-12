import xbmc
import xbmcgui
import os

QR_IMAGE_PATH = "/tmp/remote_touchpad_qr.png"

class QRDisplay:
    def __init__(self, image_path):
        self.image_path = image_path
        self.window = xbmcgui.Window(10000)
        # esquina superior derecha, tamaño 200x200
        self.control = xbmcgui.ControlImage(1200, 50, 200, 200, self.image_path)
        self.window.addControl(self.control)

    def refresh_loop(self):
        while True:
            if os.path.exists(self.image_path):
                self.control.setImage(self.image_path)
            xbmc.sleep(5000)  # evita bloquear la GUI

# Instanciación
qr_display = QRDisplay(QR_IMAGE_PATH)
qr_display.refresh_loop()
