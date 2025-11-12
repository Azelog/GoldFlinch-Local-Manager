import xbmc
import xbmcgui
import time
import os

# Ruta de la imagen (puede ser el QR de Remote Touchpad)
QR_IMAGE_PATH = "/tmp/remote_touchpad_qr.png"

# Crear un Window overlay
window = xbmcgui.Window(10000)  # Window ID genérico para overlays

# Posición de la esquina superior derecha
pos_x = 1200  # ajusta según tu resolución
pos_y = 50
width = 200
height = 200

# Crear el control de imagen
qr_control = xbmcgui.ControlImage(pos_x, pos_y, width, height, QR_IMAGE_PATH)
window.addControl(qr_control)

# Bucle para refrescar la imagen cada 5 segundos
try:
    while True:
        if os.path.exists(QR_IMAGE_PATH):
            qr_control.setImage(QR_IMAGE_PATH)  # recarga la imagen
        time.sleep(5)
except KeyboardInterrupt:
    window.removeControl(qr_control)
    del qr_control
