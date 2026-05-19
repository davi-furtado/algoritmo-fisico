from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from cv2 import imread
from pathlib import Path

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
    '/',
    summary='Converte imagem para código',
    description='Recebe uma imagem e retorna o código correspondente em pseudocódigo e Python.'
)
async def convert(file: UploadFile = File(...)):
    filepath = Path(f'/tmp/{file.filename}')

    try:
        with open(filepath, 'wb') as f:
            f.write(await file.read())

        img = imread(str(filepath))

        if img is None:
            return {'error': 'Imagem inválida ou corrompida.'}

        try:
            pseudocode = read_arucos(img)

            if pseudocode is None or pseudocode.strip() == '':
                return {'error': 'Nenhum código detectado na imagem.'}

        except Exception as e:
            return {'error': f'Erro ao processar a imagem:\n{e}'}

        python_code = toPython(pseudocode)

        try:
            output = safe_exec(python_code)

        except Exception as e:
            return {'error': f'Erro ao executar o código:\n{e}'}

        return {
            'output': output,
            'pseudocode': indentPseudo(pseudocode),
            'python': python_code
        }

    except Exception as e:
        return {'error': f'Falha inesperada:\n{e}'}

    finally:
        if filepath.exists():
            filepath.unlink()


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0')