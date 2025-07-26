import socket
import time

class Clock:
    def __init__(self, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002, delay=0.1):
        self.valor_clock = 0
        self.delay_escalonador = 0.005 # 5 ms
        self.delay_por_incremento = delay # 100 ms = 0.1s
        self.endereco_emissor = ('localhost', porta_emissor)
        self.endereco_escalonador = ('localhost', porta_escalonador)
        

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Clock]: Falha ao conectar em {destino}")

    def iniciar_clock(self):
        print("[Clock] Aguardando sinal do emissor para iniciar...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.porta_clock))
            s.listen()
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()
                if msg != "START CLOCK":
                    print(f"[Clock]: Sinal inválido '{msg}' recebido. Encerrando.")
                    return
                print("[Clock]: Sinal de início recebido do Emissor.")

        print("[Clock]: Iniciando contagem...")
        while True:
            mensagem = f"CLOCK {self.valor_clock}"

            # Envio da mensagem para o Emissor
            self.enviar_mensagem(self.endereco_emissor, mensagem)
            print(f"[Clock {self.valor_clock}]: Mensagem enviada ao emissor de tarefas ")

            time.sleep(self.delay_escalonador) # Delay de 5ms

            # Envio da mensagem para o Escalonador
            self.enviar_mensagem(self.endereco_escalonador, mensagem)
            print(f"[Clock {self.valor_clock}]: Mensagem enviada ao escalonador de tarefas ")

            # Incrementa Clock
            time.sleep(self.delay_por_incremento)
            self.valor_clock += 1
