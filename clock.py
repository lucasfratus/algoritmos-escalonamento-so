import socket
import time

class Clock:
    # delay foi convertido de 100 ms para 0.1 s
    def __init__(self, porta_emissor=4001, porta_escalonador=4002, delay=0.1):
        self.valor_clock = 0
        self.endereco_emissor = ('localhost', porta_emissor)
        self.endereco_escalonador = ('localhost', porta_escalonador)
        self.delay_por_incremento = delay # 100 ms = 0.1s
        self.delay_escalonador = 0.005 # 5 ms
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("[Clock]: Socket inicializado.")

    def enviar_mensagem(self, destino, mensagem):
        self.socket.sendto(mensagem.encode(), destino)
    
    def iniciar_clock(self):
        print("[Clock]: Iniciando...")
        while True:
            mensagem = f"CLOCK {self.valor_clock}"

            # Envio da mensagem para o emissor de tarefas
            self.enviar_mensagem(self.endereco_emissor, mensagem)
            print(f"[Clock {self.valor_clock}]: Mensagem enviada ao emissor de tarefas ")

            time.sleep(self.delay_escalonador) # Delay de 5ms

            # Envio da mensagem para o escalonador de tarefas
            self.enviar_mensagem(self.endereco_escalonador, mensagem)
            print(f"[Clock {self.valor_clock}]: Mensagem enviada ao escalonador de tarefas ")

            # Tempo do incremento (Subtrair o número 5 de 100?) - Não
            time.sleep(self.delay_por_incremento)

            self.valor_clock += 1
