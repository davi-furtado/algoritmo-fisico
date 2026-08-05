import json
import os

import cv2
import cv2.aruco as aruco


def sanitize_filename(text: str) -> str:
    """Sanitiza o texto de um bloco substituindo operadores e caracteres especiais por nomes seguros.

    Garante que os nomes dos arquivos salvos em disco não contenham caracteres
    inválidos ou problemáticos em sistemas de arquivos (como '/', '*', '>', etc.).

    Args:
        text (str): Texto ou símbolo associado ao marcador ArUco.

    Returns:
        str: Nome sanitizado apropriado para uso como nome de arquivo.
    """
    name = text.replace(" ", "_")
    match name:
        case "+":
            return "mais"
        case "-":
            return "menos"
        case "*":
            return "vezes"
        case "/":
            return "dividido"
        case "//":
            return "divisao_inteira"
        case "%":
            return "resto"
        case "==":
            return "igual"
        case "!=":
            return "diferente"
        case "<":
            return "menor"
        case ">":
            return "maior"
        case "<=":
            return "menor_igual"
        case ">=":
            return "maior_igual"
        case _:
            return name


def generate_aruco_markers(
    config_file: str = "blocks.json", output_dir: str = "arucos"
) -> None:
    """Lê o mapeamento do arquivo JSON e gera as imagens dos marcadores ArUco com borda branca.

    Para cada ID definido no arquivo de configuração, gera a imagem do marcador correspondente
    utilizando o dicionário `DICT_5X5_100`, adiciona uma borda de segurança branca (quiet zone)
    e salva a imagem no diretório de saída com um nome descritivo.

    Args:
        config_file (str, optional): Caminho do arquivo JSON de entrada contendo os marcadores.
            Defaults to 'blocks.json'.
        output_dir (str, optional): Diretório onde as imagens PNG serão salvas.
            Defaults to 'arucos'.
    """
    # Carrega os mapeamentos dos marcadores a partir do arquivo JSON
    with open(config_file, "r", encoding="utf-8") as f:
        blocks: dict[str, str] = json.load(f)

    # Cria a pasta de destino caso ela não exista
    os.makedirs(output_dir, exist_ok=True)

    # Inicializa o dicionário de marcadores ArUco 5x5 (100 variações)
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)

    for id_str, text in blocks.items():
        marker_id = int(id_str)

        # Gera a imagem base do marcador ArUco (tamanho de 300x300 pixels)
        marker = aruco.generateImageMarker(dictionary, marker_id, 300)

        # Adiciona uma borda branca de 30px ao redor do marcador (Quiet Zone)
        marker = cv2.copyMakeBorder(
            marker,
            30,
            30,
            30,
            30,
            cv2.BORDER_CONSTANT,
            value=255,
        )

        name = sanitize_filename(text)
        filename = f"{marker_id}_{name}.png"
        filepath = os.path.join(output_dir, filename)

        # Salva a imagem final gerada
        cv2.imwrite(filepath, marker)


if __name__ == "__main__":
    generate_aruco_markers()
