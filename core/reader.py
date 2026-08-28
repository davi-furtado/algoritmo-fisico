"""
reader.py — reconstrói o pseudocódigo a partir de uma foto dos blocos físicos.

Diferenças em relação ao reader.py original:

1. CORREÇÃO AUTOMÁTICA DE ORIENTAÇÃO
   O leitor antigo ordenava os blocos pelo eixo Y e X *da foto*. Se a foto
   estivesse girada (celular deitado, foto de cabeça para baixo), a ordem de
   leitura saía errada mesmo com o algoritmo montado corretamente na mesa.
   Cada marcador ArUco devolve seus 4 cantos sempre na mesma ordem, então o
   vetor canto0 -> canto1 aponta para a "direita" do marcador. Tirando a média
   desse vetor entre todos os marcadores, descobrimos a inclinação da foto e
   giramos as coordenadas antes de ordenar.

2. AGRUPAMENTO DE LINHAS PROPORCIONAL AO TAMANHO DO BLOCO
   O limiar antigo era fixo em 40 pixels, o que só funciona a uma distância
   específica da câmera. Agora ele é proporcional ao tamanho medido dos
   marcadores na imagem, então funciona perto e longe.

3. CENTRO DA LINHA ATUALIZADO A CADA BLOCO
   O agrupamento antigo comparava com o Y do primeiro bloco da linha. Agora usa
   a média corrente, o que tolera linhas levemente inclinadas.
"""

import json
import math
import os

import cv2
import numpy as np

# --------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------

# Multiplicador do tamanho do marcador usado para decidir se dois blocos estão
# na mesma linha. Calibrado sobre as 25 fotos de teste do repositório:
# 1.2 -> 15 acertos | 1.6 -> 17 acertos | 2.0 -> 11 acertos
TOLERANCIA_LINHA = 1.6


def _caminho_blocos():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocks.json")


with open(_caminho_blocos(), encoding="utf-8") as _f:
    BLOCOS = json.load(_f)


_parametros = cv2.aruco.DetectorParameters()
_parametros.adaptiveThreshWinSizeMin = 3
_parametros.adaptiveThreshWinSizeMax = 23
_parametros.adaptiveThreshWinSizeStep = 10
_parametros.adaptiveThreshConstant = 7

_detector = cv2.aruco.ArucoDetector(
    cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100),
    _parametros,
)


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------

def _orientacao_media(cantos):
    """Ângulo (radianos) da direção 'direita' média dos marcadores."""
    soma_x = soma_y = 0.0
    for c in cantos:
        q = c[0]
        dx = q[1][0] - q[0][0]
        dy = q[1][1] - q[0][1]
        norma = math.hypot(dx, dy)
        if norma:
            soma_x += dx / norma
            soma_y += dy / norma
    return math.atan2(soma_y, soma_x)


def _tamanho_medio(cantos):
    """Lado médio dos marcadores em pixels (mediana, resistente a outliers)."""
    lados = []
    for c in cantos:
        q = c[0]
        lados.append(math.hypot(q[1][0] - q[0][0], q[1][1] - q[0][1]))
    return float(np.median(lados)) if lados else 1.0


def read_blocks(image):
    """
    Recebe uma imagem (array do OpenCV) e devolve o pseudocódigo lido.

    Retorna None se nenhum marcador for encontrado.
    """
    cinza = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cantos, ids, _ = _detector.detectMarkers(cinza)

    if ids is None or len(ids) == 0:
        return None

    angulo = _orientacao_media(cantos)
    cos_a = math.cos(-angulo)
    sen_a = math.sin(-angulo)
    limiar = _tamanho_medio(cantos) * TOLERANCIA_LINHA

    # Coordenadas de cada marcador já giradas para o "endireitado"
    pontos = []
    for i, marcador in enumerate(ids):
        q = cantos[i][0]
        x = float(q[:, 0].mean())
        y = float(q[:, 1].mean())
        # Compatibilidade com diferentes formatos de `ids` retornados pelo OpenCV:
        # pode ser um array de shape (n,) ou (n,1). Normalizar para um inteiro.
        mid = int(np.array(marcador).ravel()[0])
        pontos.append((x * cos_a - y * sen_a, x * sen_a + y * cos_a, mid))

    pontos.sort(key=lambda p: (p[1], p[0]))

    linhas = []
    for x, y, marcador in pontos:
        for linha in linhas:
            if abs(linha["soma"] / linha["qtd"] - y) < limiar:
                linha["itens"].append((x, marcador))
                linha["soma"] += y
                linha["qtd"] += 1
                break
        else:
            linhas.append({"soma": y, "qtd": 1, "itens": [(x, marcador)]})

    linhas.sort(key=lambda l: l["soma"] / l["qtd"])

    texto = []
    for linha in linhas:
        linha["itens"].sort(key=lambda item: item[0])
        palavras = [
            BLOCOS[str(m)] for _, m in linha["itens"] if str(m) in BLOCOS
        ]
        if palavras:
            texto.append(" ".join(palavras))

    return "\n".join(texto)


def read_file(path):
    """Lê uma imagem do disco e devolve o pseudocódigo. None se não abrir."""
    imagem = cv2.imread(path)
    if imagem is None:
        return None
    return read_blocks(imagem)
