import select
import socket
import time

class Clock:
    def __init__(self, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002, delay=0.1):
        self.valor_clock = 0
        self.delay_escalonador = 0.005 # 5 ms
        self.delay_por_incremento = delay # 100 ms = 0.1s
        self.porta_clock = porta_clock
        self.porta_emissor = porta_emissor
        self.porta_escalonador = porta_escalonador
        self.endereco_emissor = ('localhost', porta_emissor)
        self.endereco_escalonador = ('localhost', porta_escalonador)
        

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[T{self.valor_clock} - Clock]: Falha ao conectar em {destino}.")
            return

    def clock_main(self):
        # Aguarda o sinal do emissor para iniciar a contagem
        print(f"[T{self.valor_clock} - Clock] Aguardando sinal do emissor para iniciar...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.porta_clock))
            s.listen()
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()
                if msg != "START CLOCK":
                    print(f"[T{self.valor_clock} - Clock]: Sinal inválido '{msg}' recebido. Encerrando...")
                    return
                print(f"[T{self.valor_clock} - Clock]: Sinal de início recebido do Emissor.")

        # Abertura do Socket para receber sinal do Escalonador ao final da simulação
        se = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        se.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        se.bind(('localhost', self.porta_clock))
        se.listen()
        se.setblocking(False)  # Não-bloqueante

        print(f"[T{self.valor_clock} - Clock]: Iniciando contagem...")
        try:
            while True:
                mensagem = f"CLOCK {self.valor_clock}"

                # Envio da mensagem para o Emissor
                self.enviar_mensagem(self.endereco_emissor, mensagem)
                print(f"[T{self.valor_clock} - Clock]: Mensagem enviada ao emissor de tarefas.")

                time.sleep(self.delay_escalonador) # Delay de 5ms

                # Envio da mensagem para o Escalonador
                self.enviar_mensagem(self.endereco_escalonador, mensagem)
                print(f"[T{self.valor_clock} - Clock]: Mensagem enviada ao escalonador de tarefas.")

                # Incrementa Clock
                time.sleep(self.delay_por_incremento)
                self.valor_clock += 1

                # Verifica sinal de parada do Escalonador
                ready, _, _ = select.select([se], [], [], 0)
                if ready:
                    conn, addr = se.accept()
                    with conn:
                        msg = conn.recv(1024).decode()
                        if msg == "FIM":
                            print(f"[T{self.valor_clock} - Clock]: Sinal de encerramento recebido. Encerrando Clock...")
                            break
        finally:
            # Fecha o Socket
            se.close()
            print(f"[T{self.valor_clock} - Clock]: Clock encerrado.")