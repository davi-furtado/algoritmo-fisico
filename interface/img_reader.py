from os import path
from cv2 import imread

from aruco_reader import read_arucos
from conversor import indentPseudo, toPython
from executor import safe_exec


def read_img(file: str) -> dict[str, str]:
    """Lê uma imagem local contendo marcadores ArUco, extrai o pseudocódigo e executa a tradução Python.

    A função carrega o arquivo de imagem via OpenCV, detecta e transcreve os
    marcadores para pseudocódigo, realiza a formatação da indentação e tradução
    para Python, e por fim executa o código resultante retornando as saídas obtidas.

    Args:
        file (str): Caminho local do arquivo de imagem a ser processado.

    Returns:
        dict[str, str]: Dicionário contendo os resultados da operação:
            - Se bem-sucedido, contém as chaves 'output', 'pseudocode' e 'python'.
            - Em caso de falha, retorna um dicionário com a chave 'error' e a mensagem correspondente.
    """
    img = imread(file)
    if img is None:
        return {"error": "Imagem inválida ou corrompida."}

    try:
        pseudocode = read_arucos(img)
        if pseudocode is None or pseudocode.strip() == "":
            return {"error": "Nenhum código detectado na imagem."}
    except Exception as e:
        return {"error": f"Erro ao processar a imagem: {str(e)}"}

    python = toPython(pseudocode)
    pseudocode = indentPseudo(pseudocode)

    try:
        output = safe_exec(python)
    except Exception as e:
        return {"error": f"Erro ao executar o código: {e}"}

    return {
        "output": output,
        "pseudocode": pseudocode,
        "python": python,
    }
