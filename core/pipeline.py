"""
pipeline.py — ponto de entrada único do núcleo.

Este é o arquivo que a API, a interface desktop e o app Flet devem chamar.
Nenhum deles precisa saber como o leitor, o conversor ou o interpretador
funcionam por dentro. Se um dia a leitura mudar, muda aqui e as três frentes
mudam juntas.
"""

import cv2
import numpy as np

from . import converter, interpreter, reader


def process_image(image) -> dict[str, str | None]:
    """
    Recebe uma imagem do OpenCV e devolve um dicionário com:
      pseudocode, python, output, error
    """
    result = {"pseudocode": "", "python": "", "output": "", "error": None}

    try:
        raw = reader.read_blocks(image)
    except Exception as error:
        result["error"] = f"Não consegui analisar a foto. ({error})"
        return result

    if not raw or not raw.strip():
        result["error"] = (
            "Nenhum bloco foi encontrado na foto. Tente de novo com mais luz "
            "e enquadrando o algoritmo inteiro."
        )
        return result

    clean = converter.clean(raw)

    if not clean.strip():
        result["error"] = (
            "Encontrei blocos na foto, mas eles não formam um algoritmo. "
            "Verifique se o 'inicio' e o 'fim' estão na foto."
        )
        return result

    result["pseudocode"] = converter.indent_pseudocode(clean)
    result["python"] = converter.to_python(clean)

    output, error = interpreter.execute(clean)
    result["output"] = output
    result["error"] = error

    # Algoritmo que roda mas não mostra nada quase sempre é foto incompleta ou
    # bloco "mostre" faltando. Silenciar isso confunde mais do que ajuda.
    if not error and not output.strip():
        result["error"] = (
            "O algoritmo rodou, mas não mostrou nada. "
            'Faltou o bloco "mostre" ou algum bloco ficou fora da foto?'
        )

    return result


def process_file(path) -> dict[str, str | None]:
    """Mesma coisa, a partir de um caminho de arquivo."""
    image = cv2.imread(path)
    if image is None:
        return {
            "pseudocode": "",
            "python": "",
            "output": "",
            "error": "Não consegui abrir essa imagem.",
        }
    return process_image(image)


def process_bytes(data):
    """Mesma coisa, a partir dos bytes da imagem (útil no app e na API)."""
    array = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        return {
            "pseudocode": "",
            "python": "",
            "output": "",
            "error": "Não consegui abrir essa imagem.",
        }
    return process_image(image)
