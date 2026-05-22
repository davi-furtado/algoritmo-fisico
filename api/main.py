from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Request,
    HTTPException,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from cv2 import imread
from pathlib import Path
import uuid

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
async def convert(request: Request, file: UploadFile = File(...)):
    content_type = (file.content_type or '').lower()
    supported_types = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/bmp': '.bmp',
        'image/webp': '.webp'
    }

    ext = Path(str(file.filename)).suffix.lower()
    if ext not in supported_types.values():
        ext = supported_types.get(content_type, ext)

    if ext not in supported_types.values():
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Formato de arquivo não suportado. Use JPG, PNG, BMP ou WEBP.'
        )
        
    filepath = Path(f'/tmp/{uuid.uuid4()}{ext}')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    try:
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)

        img = imread(filepath)

        if img is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Imagem inválida ou corrompida.'
            )

        try:
            pseudocode = read_arucos(img)

            if pseudocode is None or pseudocode.strip() == '':
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='Nenhum código detectado na imagem.'
                )

        except HTTPException: raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Erro ao processar a imagem:\n{e}'
            )

        python = toPython(pseudocode)
        pseudocode = indentPseudo(pseudocode)

        try:
            output = safe_exec(python)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Erro ao executar o código:\n{e}'
            )

        return {
            'output': output,
            'pseudocode': pseudocode,
            'python': python
        }

    except HTTPException: raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e
        )

    finally:
        if filepath.exists():
            filepath.unlink()


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0')