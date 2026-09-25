from pydantic import BaseModel, Field


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
