import socket
import sys
import threading
from clock import Clock


class Emissor:
    def __init__(self, caminho_arquivo, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002):
        self.indice_tarefa = 0 # Indice da tarefa que será emitida
        self.tarefas = self.carregar_tarefas(caminho_arquivo)
        self.total_tarefas = len(self.tarefas)
        self.endereco_clock = ('localhost', porta_clock)
        self.endereco_escalonador = ('localhost', porta_escalonador)

    def carregar_tarefas(self, caminho_arquivo):
        tarefas = []
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                if linha.strip():
                    id, tempo_ingresso, duracao_prevista, prioridade = linha.strip().split(';')
                    # Utiliza um dicionário para cada tarefa na lista de tarefas 
                    tarefa = {'id': id, 'ingresso': int(tempo_ingresso), 'duracao_prevista': int(duracao_prevista), 'prioridade': int(prioridade) }
                    tarefas.append(tarefa)
        return tarefas
    

    def emitir_tarefa(self, tarefa):
        mensagem = f"{tarefa['id']};{tarefa['duracao_prevista']};{tarefa['prioridade']}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.endereco_escalonador)
                s.sendall(mensagem.encode())
                print(f"[Emissor]: Enviou a tarefa {mensagem} ao Escalonador.")
        except ConnectionRefusedError:
            print("[Emissor]: Não conseguiu conectar ao Escalonador.")
    

    def iniciar(self):
        # Envia sinal de início ao Clock
        print("[Emissor]: Tarefas carregadas. Enviando sinal de início para o Clock...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(endereco_clock)
                s.sendall("START CLOCK".encode())
        except ConnectionRefusedError:
            print("[Emissor]: Falha de conexão com Clock para enviar o sinal de início.")
            return

        # Inicia operação de emissão
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', self.porta_escuta))
        s.listen()

        while self.indice_tarefa < self.total_tarefas:
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()
                if msg.startswith("CLOCK"):
                    clock = int(msg.split()[1])
                    print(f"[Emissor] Recebeu Clock {clock}.")

                    # Verifica quais tarefas devem ser emitidas no Clock atual
                    while self.indice_tarefa < self.total_tarefas and self.tarefas[self.indice_tarefa]['ingresso'] == clock:
                        tarefa = self.tarefas[self.indice_tarefa]
                        self.emitir_tarefa(tarefa)
                        self.indice_tarefa += 1

        # Envia um sinal de término de emissão ao Escalonador
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
                s1.connect(self.endereco_escalonador)
                s1.sendall("-1".encode())
                print(f"[Emissor]: Sinal de término de emissão enviado ao Escalonador.")
        except ConnectionRefusedError:
            print(f"[Emissor]: Não foi possível enviar o sinal de término de emissão ao Escalonador.")

        s.close() # Fecha a conexão do Socket
        print(f"[Emissor]: Encerrado.")