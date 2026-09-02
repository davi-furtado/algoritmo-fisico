"""
main.py - aplicativo Flet do Algoritmo Físico.

Roda inteiramente dentro do celular: não existe API, não existe rede, não
existe servidor para cair no meio da apresentação.
"""

import asyncio
import json
from pathlib import Path
import sys
from typing import Any

import flet as ft

# Permite importar o pacote `core` que está na raiz do projeto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import pipeline

FUNDO = "#000000"
CARTAO = "#222528"
BORDA = "#303438"
TEXTO = "#dcdcdc"
APAGADO = "#bfbfbf"
DESCRICAO = "#8b909a"
DESTAQUE = "#1760ff"
SUCESSO = "#00ff00"
ERRO = "#ff5c61"
SOMBRA = "#00000055"

JETBRAINS_MONO = "JetBrains Mono"


def main(pagina: ft.Page):
    pagina.title = "Algoritmo Físico"
    pagina.bgcolor = FUNDO
    pagina.padding = 0
    pagina.theme_mode = ft.ThemeMode.DARK
    pagina.fonts = {JETBRAINS_MONO: "JetBrainsMonoNL-Bold.ttf"}

    seletor = ft.FilePicker()
    pagina.services.append(seletor)
    compartilhamento = ft.Share()
    pagina.services.append(compartilhamento)

    estado = {"aba": "pseudo", "resultado": None, "foto": None}

    # ---------------------------------------------------------------- widgets

    previa = ft.Image(
        src="",
        fit=ft.BoxFit.CONTAIN,
        height=200,
        visible=False,
        semantics_label="Pré-visualização da foto do algoritmo",
    )

    def fechar_imagem(_: Any = None) -> None:
        pagina.pop_dialog()

    def abrir_imagem(_: Any) -> None:
        if not previa.src:
            return

        imagem_tela_cheia = ft.Image(
            src=previa.src,
            fit=ft.BoxFit.CONTAIN,
            width=pagina.width or 800,
            height=max((pagina.height or 600) - 170, 220),
            semantics_label="Imagem do algoritmo em tela cheia",
        )

        async def fechar_com_opacidade(evento: Any) -> None:
            evento.control.opacity = 0.62
            evento.control.update()
            await asyncio.sleep(0.12)
            fechar_imagem(evento)

        async def compartilhar_imagem(evento: Any) -> None:
            evento.control.opacity = 0.62
            evento.control.update()
            try:
                origem = previa.src
                arquivo_jpg = (
                    ft.ShareFile(
                        data=origem,
                        name="algoritmo.jpg",
                        mime_type="image/jpeg",
                    )
                    if isinstance(origem, bytes)
                    else ft.ShareFile(path=origem, name="algoritmo.jpg")
                )
                await compartilhamento.share_files(
                    [arquivo_jpg],
                    title="Compartilhar imagem",
                )
            finally:
                evento.control.opacity = 1
                evento.control.update()

        dialogo = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column(
                    [
                        imagem_tela_cheia,
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.TextButton(
                                        "Compartilhar",
                                        on_click=compartilhar_imagem,
                                        style=ft.ButtonStyle(
                                            color="#ffffff",
                                            bgcolor=DESTAQUE,
                                            shape=ft.RoundedRectangleBorder(radius=999),
                                            padding=ft.Padding(24, 12, 24, 12),
                                        ),
                                    ),
                                    ft.TextButton(
                                        "Fechar",
                                        on_click=fechar_com_opacidade,
                                        style=ft.ButtonStyle(
                                            color="#ffffff",
                                            bgcolor=ERRO,
                                            shape=ft.RoundedRectangleBorder(radius=999),
                                            padding=ft.Padding(24, 12, 24, 12),
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            alignment=ft.Alignment(0, 0),
                            margin=ft.Margin(0, 0, 0, 4),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                width=pagina.width,
                height=pagina.height,
                alignment=ft.Alignment(0, 0),
            ),
            bgcolor=FUNDO,
            barrier_color="#CC000000",
            inset_padding=0,
            content_padding=0,
        )
        pagina.show_dialog(dialogo)

    carregando = ft.Row(
        [
            ft.ProgressRing(width=18, height=18, color=DESTAQUE),
            ft.Text("Lendo os blocos...", color=APAGADO),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False,
    )

    titulo_saida = ft.Text(
        "Saída",
        size=13,
        weight=ft.FontWeight.BOLD,
        color=APAGADO,
    )
    caixa_saida = ft.Text(
        "",
        font_family=JETBRAINS_MONO,
        size=14,
        color=SUCESSO,
        selectable=True,
    )

    caixa_codigo = ft.Text(
        "",
        font_family=JETBRAINS_MONO,
        size=13,
        color=TEXTO,
        selectable=True,
    )

    async def copiar(texto: str) -> None:
        if texto:
            await pagina.clipboard.set(texto)

    async def copiar_saida(_: Any) -> None:
        await copiar(caixa_saida.value)

    async def copiar_codigo(_: Any) -> None:
        await copiar(caixa_codigo.value)

    async def compartilhar_resultados(_: Any) -> None:
        resultado = estado["resultado"]
        if not resultado:
            return
        conteudo = json.dumps(resultado, ensure_ascii=False, indent=2).encode("utf-8")
        arquivo_json = ft.ShareFile(
            data=conteudo, name="resultados.json", mime_type="application/json"
        )
        await compartilhamento.share_files(
            [arquivo_json], title="Compartilhar resultados"
        )

    botao_copiar_saida = ft.IconButton(
        icon=ft.Icons.CONTENT_COPY,
        icon_color=APAGADO,
        tooltip="Copiar saída",
        on_click=copiar_saida,
    )

    botao_copiar_codigo = ft.IconButton(
        icon=ft.Icons.CONTENT_COPY,
        icon_color=APAGADO,
        tooltip="Copiar código",
        on_click=copiar_codigo,
    )

    def botao_toggle(rotulo: str, chave: str) -> ft.Container:
        ativo = estado["aba"] == chave
        return ft.Container(
            content=ft.Text(
                rotulo,
                color="#ffffff" if ativo else APAGADO,
                size=13,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=DESTAQUE if ativo else "transparent",
            border_radius=10,
            padding=ft.Padding(8, 4, 8, 4),
            ink=True,
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
            shadow=(
                ft.BoxShadow(blur_radius=10, color="#1760ff66", offset=ft.Offset(0, 3))
                if ativo
                else None
            ),
            on_click=lambda _, selecionada=chave: trocar_aba(selecionada),
        )

    toggle_botoes: list[ft.Control] = []
    toggle = ft.Row(spacing=0)
    toggle_fundo = ft.Container(
        content=toggle,
        bgcolor=CARTAO,
        border=ft.Border.all(0, BORDA),
        border_radius=14,
    )

    painel_saida = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [titulo_saida, botao_copiar_saida],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                caixa_saida,
            ],
            spacing=6,
        ),
        bgcolor=CARTAO,
        border=ft.Border.all(1, BORDA),
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=18, color=SOMBRA, offset=ft.Offset(0, 6)),
        padding=ft.Padding(14, 22, 14, 22),
        visible=False,
    )

    painel_codigo = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        toggle_fundo,
                        ft.Container(
                            content=botao_copiar_codigo,
                            alignment=ft.Alignment(1, 0),
                            padding=ft.Padding(0, 0, 0, 0),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
                caixa_codigo,
            ],
            spacing=10,
        ),
        bgcolor=CARTAO,
        border=ft.Border.all(1, BORDA),
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=18, color=SOMBRA, offset=ft.Offset(0, 6)),
        padding=ft.Padding(14, 22, 14, 22),
        visible=False,
    )

    # ---------------------------------------------------------------- lógica

    def trocar_aba(chave):
        estado["aba"] = chave
        desenhar_abas()
        result = estado["resultado"]
        if result:
            caixa_codigo.value = result["pseudocode" if chave == "pseudo" else "python"]
        pagina.update()

    def desenhar_abas():
        toggle_botoes.clear()
        toggle_botoes.extend(
            [
                botao_toggle("Pseudocódigo", "pseudo"),
                botao_toggle("Python", "python"),
            ]
        )
        toggle.controls = toggle_botoes

    def mostrar(resultado):
        estado["resultado"] = resultado
        carregando.visible = False

        tem_codigo = bool(resultado["pseudocode"])
        painel_codigo.visible = tem_codigo
        painel_saida.visible = True
        area_compartilhar.visible = True

        if resultado["error"]:
            titulo_saida.value = "Erro"
            titulo_saida.color = ERRO
            caixa_saida.color = ERRO
            caixa_saida.value = resultado["error"]
            if resultado["output"]:
                caixa_saida.value = f"{resultado['output']}\n\n{resultado['error']}"
        else:
            titulo_saida.value = "Saída"
            titulo_saida.color = APAGADO
            caixa_saida.color = SUCESSO
            caixa_saida.value = resultado["output"]

        if tem_codigo:
            caixa_codigo.value = resultado[
                "pseudocode" if estado["aba"] == "pseudo" else "python"
            ]

        pagina.update()

    def preparar_leitura(imagem: bytes | str) -> None:
        previa.src = imagem
        previa.visible = True
        carregando.visible = True
        painel_saida.visible = False
        painel_codigo.visible = False
        area_compartilhar.visible = False
        pagina.update()

    async def processar_imagem(imagem: bytes | str) -> dict[str, Any]:
        preparar_leitura(imagem)
        resultado = (
            pipeline.process_bytes(imagem)
            if isinstance(imagem, bytes)
            else pipeline.process_file(imagem)
        )
        mostrar(resultado)
        return resultado

    async def escolher_foto(_: Any):
        arquivos = await seletor.pick_files(
            dialog_title="Escolha a foto do algoritmo",
            file_type=ft.FilePickerFileType.IMAGE,
            with_data=True,
        )
        if not arquivos:
            return

        arquivo = arquivos[0]
        caminho = arquivo.path

        # No iOS, o caminho retornado pelo FilePicker pode apontar para um
        # sandbox temporário que não é legível pelo processo do app. Os bytes
        # são a representação portátil e devem ser usados quando disponíveis.
        imagem = arquivo.bytes or caminho
        if not imagem:
            mostrar(
                {
                    "pseudocode": "",
                    "python": "",
                    "output": "",
                    "error": "Não consegui ler os dados dessa foto.",
                }
            )
            return
        await processar_imagem(imagem)

    async def abrir_seletor(e: Any) -> None:
        await escolher_foto(e)

    # ---------------------------------------------------------------- layout

    desenhar_abas()

    cabecalho = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Algoritmo Físico", size=22, weight=ft.FontWeight.BOLD, color=TEXTO
                ),
                ft.Text(
                    "Fotografe o algoritmo montado com os blocos",
                    size=13,
                    color=DESCRICAO,
                ),
            ],
            spacing=2,
        ),
        padding=ft.Padding(0, 0, 0, 16),
    )

    # Texto do botão: preferir termo "Carregar" quando estiver no modo web
    # (usando atributos de Page se existirem; getattr com default evita erros).
    def criar_botao_acao(icone, texto, on_click, bgcolor=DESTAQUE):
        botao = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icone, color="#ffffff", size=20),
                    ft.Text(
                        texto,
                        color="#ffffff",
                        weight=ft.FontWeight.BOLD,
                        size=15,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=bgcolor,
            border_radius=12,
            padding=ft.Padding(18, 14, 18, 14),
            expand=1,
            shadow=ft.BoxShadow(blur_radius=12, color=SOMBRA, offset=ft.Offset(0, 4)),
            ink=True,
        )

        async def clicar(evento: Any) -> None:
            botao.opacity = 0.62
            botao.update()
            await asyncio.sleep(0.12)
            botao.opacity = 1
            botao.update()
            await on_click(evento)

        botao.on_click = clicar
        return botao

    botao_selecionar = criar_botao_acao(
        ft.Icons.IMAGE,
        "Selecionar foto",
        abrir_seletor,
    )

    botoes_foto = ft.Row(
        [botao_selecionar],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    botao_compartilhar_resultados = criar_botao_acao(
        ft.Icons.SHARE,
        "Compartilhar resultados",
        compartilhar_resultados,
        bgcolor=CARTAO,
    )

    area_compartilhar = ft.Container(
        content=ft.Row(
            [botao_compartilhar_resultados],
            spacing=10,
        ),
        padding=ft.Padding(0, 14, 0, 0),
        visible=False,
    )

    pagina.add(
        ft.SafeArea(
            ft.Container(
                content=ft.Column(
                    [
                        cabecalho,
                        botoes_foto,
                        ft.Container(
                            content=ft.Container(
                                content=previa,
                                alignment=ft.Alignment(0, 0),
                                on_click=abrir_imagem,
                                tooltip="Abrir imagem em tela cheia",
                            ),
                            padding=ft.Padding(0, 14, 0, 0),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(carregando, padding=ft.Padding(0, 14, 0, 0)),
                        ft.Container(painel_saida, padding=ft.Padding(0, 14, 0, 0)),
                        ft.Container(painel_codigo, padding=ft.Padding(0, 12, 0, 0)),
                        area_compartilhar,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                ),
                padding=20,
                expand=True,
            ),
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.run(main)
