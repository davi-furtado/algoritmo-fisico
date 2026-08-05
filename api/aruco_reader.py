from json import load
from os import path

from cv2 import COLOR_BGR2GRAY, cvtColor
from cv2.aruco import (
    DICT_5X5_100,
    ArucoDetector,
    DetectorParameters,
    getPredefinedDictionary,
)

# Carrega o mapeamento dos marcadores ArUco para texto a partir de um arquivo JSON
# localizado no mesmo diretório do script atual.
JSON_PATH = path.join(path.dirname(path.abspath(__file__)), "blocks.json")
with open(JSON_PATH) as f:
    blocks = load(f)

# Configura o dicionário e os parâmetros do detector ArUco
dictionary = getPredefinedDictionary(DICT_5X5_100)

parameters = DetectorParameters()
parameters.adaptiveThreshWinSizeMin = 3
parameters.adaptiveThreshWinSizeMax = 23
parameters.adaptiveThreshWinSizeStep = 10
parameters.adaptiveThreshConstant = 7

# Instância do detector de marcadores ArUco do OpenCV
detector = ArucoDetector(dictionary, parameters)


def read_arucos(img) -> str | None:
    """Detecta marcadores ArUco em uma imagem e os traduz em texto estruturado por linhas.

    A função converte a imagem para escala de cinza, detecta os marcadores ArUco presentes,
    calcula as coordenadas do centro de cada marcador e agrupa os IDs correspondentes
    em linhas baseadas na proximidade vertical (coordenada Y). Em seguida, ordena os itens
    horizontalmente (coordenada X) e substitui cada ID pelo seu valor correspondente
    no dicionário `blocks`.

    Args:
        img (numpy.ndarray): Imagem BGR carregada via OpenCV na qual os marcadores
            ArUco serão detectados.

    Returns:
        str | None: Retorna uma string com o texto resultante ordenado por linhas
            e separado por quebras de linha (`\\n`), ou `None` caso nenhum marcador
            seja identificado na imagem.
    """
    gray = cvtColor(img, COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        return None

    data = []
    for i, marker_id in enumerate(ids):
        c = corners[i][0]
        x = int(c[:, 0].mean())
        y = int(c[:, 1].mean())
        data.append((x, y, marker_id[0]))

    # Ordena os marcadores inicialmente por Y (posição vertical) e X (posição horizontal)
    data.sort(key=lambda t: (t[1], t[0]))

    lines = []
    y_threshold = 40  # Tolerância em pixels para considerar marcadores na mesma linha

    # Agrupa os marcadores em "linhas" com base no limite de tolerância Y
    for x, y, marker_id in data:
        for line in lines:
            if abs(line["y"] - y) < y_threshold:
                line["items"].append((x, marker_id))
                break
        else:
            lines.append({"y": y, "items": [(x, marker_id)]})

    # Ordena as linhas verticalmente
    lines.sort(key=lambda l: l["y"])

    final_text = []

    # Processa cada linha para ordenar os itens da esquerda para a direita (X)
    # e mapear os IDs para o texto correspondente
    for line in lines:
        line["items"].sort(key=lambda t: t[0])
        words = []

        for x, marker_id in line["items"]:
            key = str(marker_id)
            if key in blocks:
                words.append(blocks[key])

        final_text.append(" ".join(words))

    return "\n".join(final_text)
