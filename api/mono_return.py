from fastapi import FastAPI, File, UploadFile
import cv2, tempfile
from os import remove, path
from uvicorn import run

app = FastAPI(
    title='API de Teste Algorítmo Físico',
    description='API criada para testar o frontend do App Algorítmo Físico',
    version='1.0.0'
)


@app.post(
        '/convert',
        summary='Converter imagem para código',
        description='Recebe uma imagem e retorna o código correspondente em pseudocódigo e Python.')
async def convert(file: UploadFile = File(...)):
    ext = path.splitext(file.filename)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_img:
        temp_path = temp_img.name
        temp_img.write(await file.read())

    img = cv2.imread(temp_path)

    remove(temp_path)
    if img is None:
        return {'error': 'Imagem inválida ou corrompida.'}
    
    return {
        'output': '0',
        'pseudocode': 'inicio\n  se 4 > 2\n    mostre 0\n  fim se\nfim',
        'python': 'if 4 > 2:\n    print(0)'
    }


run(app, host='0.0.0.0')