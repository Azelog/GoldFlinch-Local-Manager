#!/usr/bin/env python3
# server.py  -- servidor HTTP mínimo que sirve index.html y guarda selecciones en wishlist.txt
import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, unquote

PORT = 8000
WISHLIST = "wishlist.txt"
WEBROOT = "."  # carpeta donde está index.html

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/save':
            # leer body
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode('utf-8')
            try:
                payload = json.loads(data)
                line = payload.get('line', '').strip()
                if not line:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'No line provided')
                    return
                # Sanitize newline characters to avoid injection of extra lines
                safe_line = line.replace('\r', '').replace('\n', ' ')
                # Append to wishlist file
                with open(WISHLIST, 'a', encoding='utf-8') as f:
                    f.write(safe_line + '\n')
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
                print("Saved:", safe_line)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                msg = ('Error: ' + str(e)).encode('utf-8')
                self.wfile.write(msg)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    # Añadimos cabeceras CORS para que la página pueda hacer fetch desde el navegador local
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    # para soporte OPTIONS (preflight)
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    os.chdir(WEBROOT)
    print("Serving on port", PORT)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Stopping server")
            httpd.server_close()

