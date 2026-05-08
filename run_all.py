from subprocess import Popen
import socket as sc

try:
    Popen('uvicorn main:app --host 0.0.0.0', cwd='api')
    if sc.socket().connect_ex(('localhost', 8000)) is None: raise
except:
    Popen(
        'pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0',
        cwd='api',
        shell=True
    )

try:
    Popen('npx expo start --port 6000', cwd='mobile')
    if sc.socket().connect_ex(('localhost', 6000)) is None: raise
except:
    Popen(
        'npm install && npx expo start --port 6000',
        cwd='mobile',
        shell=True
    )