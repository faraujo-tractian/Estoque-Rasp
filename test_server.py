"""
Servidor de teste simples
"""
import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"🚀 Servidor rodando em http://localhost:{PORT}")
    print(f"📁 Servindo arquivos de: {os.path.abspath(DIRECTORY)}")
    print("Pressione Ctrl+C para parar")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor parado")

