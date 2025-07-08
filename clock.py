import socket
import time

class Clock():
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