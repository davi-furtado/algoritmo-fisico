from multiprocessing import Process, Pipe
import sys

def run_code(code, conn):
    class Writer:
        def __init__(self):
            self.buffer = ''

        def write(self, data):
            self.buffer += data
            while '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                try:
                    conn.send(line + '\n')
                except:
                    pass

        def flush(self):
            if self.buffer:
                try:
                    conn.send(self.buffer)
                except:
                    pass
                self.buffer = ''

    writer = Writer()
    sys.stdout = writer

    try:
        exec(code, {})
    except Exception as e:
        try:
            conn.send(f'Erro: {e}')
        except:
            pass

    writer.flush()
    conn.close()


def format_output(output, infinite=False):
    lines = output.strip().split('\n')

    if infinite and len(lines) > 7:
        return '\n'.join(lines[:7]) + '\n...'

    return output.strip()


def safe_exec(code, timeout=2):
    parent_conn, child_conn = Pipe()
    p = Process(target=run_code, args=(code, child_conn))
    p.start()

    output = ''

    try:
        p.join(timeout)

        while parent_conn.poll():
            output += parent_conn.recv()

        if p.is_alive():
            p.terminate()
            p.join()
            return format_output(output, infinite=True)

        return format_output(output, infinite=False)

    finally:
        parent_conn.close()