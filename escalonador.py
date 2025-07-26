import socket
import threading
import sys
import math 


class Escalonador:
    def __init__(self, algoritmo, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002):
        self.algoritmo = algoritmo
        self.fila_tarefas_prontas = []
        self.todas_tarefas_recebidas = False
        self.clock_atual = 0

        self.tempo_restante = {} # algoritmo preemptivo

        self.lista_saida = []
        self.registro_tarefas = {} # id ->  [ingresso, fim, turnaround, waiting]

        self.endereco_clock = ('localhost', porta_clock)
        self.endereco_emissor = ('localhost', porta_emissor)

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Escalonador]: Falha ao conectar {destino}")


    def receber_conexoes(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', self.porta_escalonador))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()

                if msg.startswith("CLOCK"):
                    self.clcok_atual = int(msg.split()[1])
                    print(f"[Escalonador]: Recebeu CLOCK {self.clock_atual}")
                    self.executar_escalonamento()

                elif msg == "-1":
                    print("[Escalonador]: Recebeu sinal de término do Emissor")
                    self.todas_tarefas_recebidas = True
                    self.verificar_encerramento()

                else:
                    tarefa = self.converter_tarefa(msg)
                    print(f"[Escalonador]: Tarefa recebida {tarefa}")
                    self.fila_tarefas_prontas.append(tarefa)
                    self.registro_tarefas[tarefa['id']] = [self.clock_atual] # salva ingresso
                    self.tempo_restante[tarefa['id']] = tarefa['duracao']

    def converter_tarefa(self, msg):
        id, duracao, prioridade = msg.split(";")
        return {'id': id, 'duracao': int(duracao), 'prioridade': int(prioridade)}

    def executar_escalonamento(self):
        pass


    def verificar_encerramento(self):
        if self.todas_tarefas_recebidas and not self.fila_tarefas_prontas:
            print("[Escalonador]: Todas as tarefas finalizadas. Encerrando.")

            ## Envio de mensagem de fim para clock e Emissor
            self.enviar_mensagem(self.endereco_clock, "FIM")
            self.enviar_mensagem(self.endereco_emissor, "FIM")

            self.gerar_arquivo_saida()
            sys.exit(0)

    def gerar_arquivo_saida(self):
        pass