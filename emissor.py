import socket
import sys
import threading
from clock import Clock


class Emissor:
    def __init__(self, caminho_arquivo, porta_escuta=4001, porta_escalonador=4002, porta_emissor=4000):
        self.tarefas = self.carregar_tarefas(caminho_arquivo)
        self.porta_escuta = porta_escuta
        self.endereco_escalonador = ('localhost', porta_escalonador)

        # Indice da tarefa que será emitida
        self.indice_tarefa = 0
        self.total_tarefas = len(self.tarefas)

        # Cria um clock
        self.clock = Clock(porta_emissor=porta_escuta, porta_escalonador=porta_escalonador)


    def carregar_tarefas(self, caminho_arquivo):
        tarefas = []
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                if linha.strip():
                    id, tempo_ingresso, duracao_prevista, prioridade = linha.strip().split(';')
                    # Utiliza um dicionario para cada tarefa na lista de tarefas 
                    tarefa = {'id': id, 'ingresso': int(tempo_ingresso), 'duracao_prevista': int(duracao_prevista), 'prioridade': int(prioridade) }
                    tarefas.append(tarefa)
        return tarefas
    

    def emitir_tarefa(self, tarefa):
        mensagem = f"{tarefa['id']};{tarefa['duracao_prevista']};{tarefa['prioridade']}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.endereco_escalonador)
                s.sendall(mensagem.encode())
                print(f"[Emissor]: Enviou a tarefa {mensagem}")
        except ConnectionRefusedError:
            print("[Emissor]: Não conseguiu conectar ao escalonador")
    

    def iniciar(self):

        threading.Thread(target=self.clock.iniciar_clock, daemon=True).start()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', self.porta_escuta))
        s.listen()

        while self.indice_tarefa < self.total_tarefas:
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()

                if msg.startswith("CLOCK"):
                    clock = int(msg.split()[1])
                    print(f"[Emissor] Recebeu Clock {clock}")

                    # Verifica quais tarefas devem ser emitidas no clock atual
                    while self.indice_tarefa < self.total_tarefas and self.tarefas[self.indice_tarefa]['ingresso'] == clock:
                        tarefa = self.tarefas[self.indice_tarefa]
                        self.emitir_tarefa(tarefa)
                        self.indice_tarefa += 1

        # Envia um sinal que indica o FIM ao escalonador
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
                s1.connect(self.endereco_escalonador)
                s1.sendall("-1".encode())
                print(f"[Emissor]: Enviou sinal de fim (-1)")
        except ConnectionRefusedError:
            print(f"[Emissor]: Não conseguiu enviar sinal de fim ao escalonador")

        s.close() # "Fecha" o sinal do socket
        print(f"[Emissor]: Encerrado.")

if __name__ == "__main__":
    emissor = Emissor("tarefas.txt")
    emissor.iniciar()
    print(emissor.tarefas)
