from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from cv2 import imread
from tempfile import NamedTemporaryFile
from os import remove, path

from aruco_reader import read_arucos
from conversor import indentPseudo, toPython
from executor import safe_exec

app = FastAPI(
    title='API Algorítmo Físico',
    description='API responsável por converter imagens de pseudocódigo em código Python e executá-lo.',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.post(
    '/convert',
    summary='Converter imagem para código',
    description='Recebe uma imagem e retorna o código correspondente em pseudocódigo e Python.'
)
async def convert(file: UploadFile = File(...)):
    ext = path.splitext(file.filename)[1].lower()

    with NamedTemporaryFile(delete=False, suffix=ext) as temp_img:
        temp_path = temp_img.name
        temp_img.write(await file.read())

    img = imread(temp_path)
    if img is None:
        remove(temp_path)
        return {'error': 'Imagem inválida ou corrompida.'}

    try:
        pseudocode = read_arucos(img)
        if pseudocode is None or pseudocode.strip() == '':
            remove(temp_path)
            return {'error': 'Nenhum código detectado na imagem.'}
    except Exception as e:
        remove(temp_path)
        return {'error': f'Erro ao processar a imagem: {str(e)}'}

    python_code = toPython(pseudocode)

    try:
        output = safe_exec(python_code)
    except Exception as e:
        remove(temp_path)
        return {'error': f'Erro ao executar o código: {e}'}

    remove(temp_path)

    return {
        'output': output,
        'pseudocode': indentPseudo(pseudocode),
        'python': python_code
    }


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0')