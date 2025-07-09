import socket
import sys

class Emissor:
    def __init__(self, caminho_arquivo, porta_escuta=4001, porta_escalonador=4002):
        self.tarefas = self.carregar_tarefas(caminho_arquivo)
        self.porta_escuta = porta_escuta
        self.endereco_escalonador = ('localhost', porta_escalonador)
        self.socket = socket.socket(soclket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', porta_Escuta))
        print(f"[Emissor] Escutando a porta {porta_escuta}")

        # Indice da tarefa que será emitida
        self.indice_tarefa = 0
        self.total_tarefas = len(self.tarefas)

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
        mensagem = f"{tarefa['id']};{tarefa['duracao']};{tarefa['prioridade']}"
        self.socket.sendto(mensagem.encode(), self.endereco_escalonador)
        print(f"[Emissor] Enviou a tarefa {mensagem}")
    
    def iniciar(self):
        print("[Emissor] Aguardando clock...")

        while self.indice_tarefa < self.total_tarefas:
            dados, x = self.socket.recvfrom(256) # Talvez tenha que mudar isso aqui para 1024
            msg = dados.decode()

            if msg.starswith("CLOCK"):
                clock = int(msg.split()[1])
                print(f"[Emissor] Recebeu Clock {clock}")

                # Verifica quais tarefas devem ser emitidas no clock atual
                while self.indice_tarefa < self.total_tarefas and self.tarefas[self.indice_tarefa]['tempo_ingresso'] == clock:
                    tarefa = self.tarefas[self.indice_tarefa]
                    self.emitir_tarefa(tarefa)
                    self.indice_tarefa += 1

            # Envia um sinal que indica o FIM ao escalonador
            self.socket.sendto("-1".encode(), self.endereco_escalonador)
            print(f"[Emissor] Todas as tarefas foram emitidas ao escalonador. Enviando sinal de fim (-1)")

            self.socket.close() # "Fecha" o sinal do socket
            print(f"[Emissor] Encerrado.")

