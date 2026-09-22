import asyncio
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from core import pipeline


class ConversionResponse(BaseModel):
    """Resultado do reconhecimento, conversão e execução do algoritmo."""

    pseudocode: str | None = Field(
        description="Pseudocódigo reconhecido e formatado a partir da imagem.",
        examples=["inicio\n  mostre 1\nfim"],
    )
    python: str | None = Field(
        description="Código Python gerado a partir do pseudocódigo reconhecido.",
        examples=["print(1)"],
    )
    output: str | None = Field(
        description="Saída produzida pela execução do código Python.",
        examples=["1"],
    )
    error: str | None = Field(
        default=None,
        description=(
            "Mensagem de erro do processamento. É nulo quando o algoritmo "
            "é processado com sucesso."
        ),
        examples=[None, "O algoritmo rodou, mas não mostrou nada."],
    )


class ErrorResponse(BaseModel):
    """Formato das respostas de erro geradas pela API."""

    detail: str = Field(
        description="Descrição do erro ocorrido.",
        examples=["Formato de arquivo não suportado."],
    )


class ValidationErrorItem(BaseModel):
    """Detalhe de um erro de validação do FastAPI."""

    loc: list[str | int] = Field(
        description="Local do campo inválido na requisição.",
        examples=[["body", "file"]],
    )
    msg: str = Field(
        description="Mensagem explicando o erro de validação.",
        examples=["Field required"],
    )
    type: str = Field(
        description="Código do tipo de erro de validação.",
        examples=["missing"],
    )


class ValidationErrorResponse(BaseModel):
    """Formato da resposta para requisições que não passam na validação."""

    detail: list[ValidationErrorItem] = Field(
        description="Lista de erros encontrados na requisição."
    )


# Instância principal da aplicação FastAPI
app = FastAPI(
    title="API Algoritmo Físico",
    description="API responsável por converter imagens de pseudocódigo em código Python e executá-lo.",
    version="1.0.0",
)


@app.post(
    "/",
    summary="Converte imagem para código",
    description="Recebe uma imagem e retorna o código correspondente em pseudocódigo e Python.",
    response_description="Objeto JSON contendo a saída da execução, o pseudocódigo e o código Python traduzido.",
    response_model=ConversionResponse,
    responses={
        415: {
            "model": ErrorResponse,
            "description": "O arquivo enviado não possui um formato de imagem suportado.",
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "A requisição não contém o campo de upload obrigatório.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Ocorreu um erro interno ao processar a imagem.",
        },
    },
)
async def convert(
    file: Annotated[
        UploadFile,
        File(
            description=(
                "Imagem contendo os blocos físicos do algoritmo. "
                "Formatos aceitos: JPG, JPEG, PNG, BMP ou WEBP."
            )
        ),
    ],
) -> ConversionResponse:
    """Processa o upload de uma imagem contendo marcadores ArUco de pseudocódigo.

    A função valida o tipo do arquivo, salva-o temporariamente em disco, lê os marcadores
    ArUco para gerar o pseudocódigo, converte-o para Python, executa o código com
    segurança e retorna o resultado. O arquivo temporário é garantidamente removido
    ao final.

    Args:
        file (UploadFile): O arquivo de imagem enviado via formulário (`multipart/form-data`).

    Raises:
        HTTPException [415]: Se a extensão ou MIME type do arquivo não for suportado.
        HTTPException [500]: Se ocorrer um erro interno inesperado no servidor.

    Returns:
        ConversionResponse: Objeto contendo:
            - `output`: Saída de texto gerada pela execução do código Python.
            - `pseudocode`: Pseudocódigo formatado e indentado.
            - `python`: Código-fonte traduzido em Python.
            - `error`: Mensagem de erro do processamento, quando aplicável.
    """
    content_type = (file.content_type or "").lower()
    supported_types = {
        "image/jpeg": ".jpeg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
    }

    ext = Path(str(file.filename)).suffix.lower()
    if ext not in supported_types.values():
        ext = supported_types.get(content_type, ext)

    if ext not in supported_types.values():
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato de arquivo não suportado. Use JPG, JPEG, PNG, BMP ou WEBP.",
        )

    # Criação do arquivo temporário com identificador único
    filepath = Path(f"/tmp/{uuid.uuid4()}{ext}")
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = await file.read()
        await asyncio.to_thread(filepath.write_bytes, content)

        return ConversionResponse(**pipeline.process_file(filepath))
    except HTTPException:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error

    finally:
        # Garante a limpeza do arquivo de imagem do disco
        if filepath.exists():
            filepath.unlink()


if __name__ == "__main__":
    from uvicorn import run

    run("api:app", host="0.0.0.0")
