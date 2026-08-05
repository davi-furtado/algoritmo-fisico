from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import sys


class Writer:
    """Bufferizador de saída para interceptar e redirecionar o `sys.stdout`.

    Acumula caracteres enviados para a saída padrão e os transmite em tempo
    real por meio de uma conexão de IPC (`Pipe`), enviando linha por linha
    conforme são formadas.

    Attributes:
        conn (Connection): Extremidade do Pipe IPC para envio das mensagens.
        buffer (str): Buffer interno para armazenar dados parciais.
    """

    def __init__(self, conn: Connection) -> None:
        """Inicializa o manipulador do buffer de saída.

        Args:
            conn (Connection): A extremidade da conexão do `Pipe` para envio.
        """
        self.conn = conn
        self.buffer = ""

    def write(self, data: str) -> None:
        """Processa os dados recebidos do `sys.stdout`.

        Adiciona os dados ao buffer local e envia linhas completas através do Pipe
        à medida que encontra caracteres de quebra de linha (`\\n`).

        Args:
            data (str): Texto enviado para impressão.
        """
        self.buffer += data
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            try:
                self.conn.send(line + "\n")
            except Exception:
                pass

    def flush(self) -> None:
        """Força o envio de qualquer conteúdo remanescente no buffer.

        Limpando o buffer ao final do processamento ou término da execução.
        """
        if self.buffer:
            try:
                self.conn.send(self.buffer)
            except Exception:
                pass
            self.buffer = ""


def run_code(code: str, conn: Connection) -> None:
    """Executa dinamicamente uma string de código Python isolada em um processo filho.

    Redireciona o `sys.stdout` para capturar impressões em tempo real, executa o
    código com a função `exec` em um escopo global limpo e envia erros capturados
    através da conexão do Pipe.

    Args:
        code (str): O código Python em string a ser executado.
        conn (Connection): A extremidade do Pipe para enviar os dados de saída
            ao processo pai.
    """
    writer = Writer(conn)
    sys.stdout = writer

    try:
        exec(code, {})
    except Exception as e:
        try:
            conn.send(f"Erro:\n{e}")
        except Exception:
            pass

    writer.flush()
    conn.close()


def format_output(output: str, infinite: bool = False) -> str:
    """Formata a string de saída final produzida pela execução do código.

    Remove espaços/quebras de linha sobressalentes e, caso a execução tenha
    excedido o tempo limite (loop infinito/timeout), limita a exibição às primeiras
    linhas com uma indicação de reticências.

    Args:
        output (str): A saída bruta acumulada da execução.
        infinite (bool, optional): Indica se a execução sofreu timeout/loop infinito.
            Se True, trunca o resultado caso exceda 4 linhas. Defaults to False.

    Returns:
        str: A string de saída formatada e limpa.
    """
    if infinite and len(lines := output.strip().split("\n")) > 4:
        return "\n".join(lines[:4]) + "\n..."

    return output.strip()


def safe_exec(code: str, timeout: int = 3) -> str:
    """Executa um código Python com segurança e limite de tempo (timeout).

    Utiliza um processo separado (`multiprocessing.Process`) para evitar travamentos
    e captura a saída gerada por um Pipe de comunicação IPC. Se a execução ultrapassar
    o limite em segundos estipulado em `timeout`, o processo é encerrado.

    Args:
        code (str): Código Python em formato string que será executado.
        timeout (int, optional): Tempo limite de execução em segundos. Defaults to 3.

    Returns:
        str: O resultado da impressão gerado pelo código ou mensagem de erro formatada.
    """
    parent_conn, child_conn = Pipe()
    p = Process(target=run_code, args=(code, child_conn))
    p.start()

    output = ""

    try:
        p.join(timeout)

        # Esvazia os dados restantes na fila da comunicação IPC
        while parent_conn.poll():
            output += parent_conn.recv()

        if p.is_alive():
            p.terminate()
            p.join()
            return format_output(output, infinite=True)

        return format_output(output, infinite=False)

    finally:
        parent_conn.close()
