import socket
import sys

class Emissor:
    def __init__(self, caminho_arquivo, porta_escuta=4001, porta_escalonador=4002):
        self.tarefas = self.carregar_tarefas(caminho_arquivo)
        self.porta_escuta = porta_escuta
        self.escalonador_endereco = ('localhost', porta_escalonador)
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
                    tarefas.append(id)
                    tarefas.append(int(tempo_ingresso))
                    tarefas.append(int(duracao_prevista))
                    tarefas.append(int(prioridade))
        return tarefas
    
    def emitir_tarefa(self, tarefa):
        pass
    
    def carregar_tarefas(self, caminho_arquivo):
        pass