from cv2 import imread
from os import path

from aruco_reader import read_arucos
from conversor import indentPseudo, toPython
from executor import safe_exec


def read_img(file):
    img = imread(file)
    if img is None:
        return {'error': 'Imagem inválida ou corrompida.'}
    try:
        pseudocode = read_arucos(img)
        if pseudocode is None or pseudocode.strip() == '':
            return {'error': 'Nenhum código detectado na imagem.'}
    except Exception as e:
        return {'error': f'Erro ao processar a imagem: {str(e)}'}

    python = toPython(pseudocode)
    pseudocode = indentPseudo(pseudocode)

    try:
        output = safe_exec(python)
    except Exception as e:
        return {'error': f'Erro ao executar o código: {e}'}

    return {
        'output': output,
        'pseudocode': indentPseudo(pseudocode),
        'python': python
    }