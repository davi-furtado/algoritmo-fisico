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
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from aruco_reader import read_arucos
from conversor import indentPseudo, toPython
from executor import safe_exec

app = FastAPI(
    title='API Algorítmo Físico',
    description='API responsável por converter imagens de pseudocódigo em código Python e executá-lo.',
    version='1.0.0' # ,
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Limite de requisições excedido: {exc.detail}"}
    )

@app.post(
    '/',
    summary='Converte imagem para código',
    description='Recebe uma imagem e retorna o código correspondente em pseudocódigo e Python.'
)
@limiter.limit('0.5/minute')
async def convert(request: Request, file: UploadFile = File(...)):
    ext = Path(str(file.filename)).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.bmp']:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Formato de arquivo não suportado. Use JPG, PNG ou BMP.'
        )
        
    filepath = Path(f'/tmp/{uuid.uuid4()}{ext}')

    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail='Arquivo muito grande. O limite é de 10 MB.'
            )

        with open(filepath, 'wb') as f:
            f.write(content)

        img = imread(str(filepath))

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
            detail=f'Falha inesperada:\n{e}'
        )

    finally:
        if filepath.exists():
            filepath.unlink()


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0')