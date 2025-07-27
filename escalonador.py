import socket
import threading
import sys
import math 


class Escalonador:
    def __init__(self, algoritmo, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002):
        self.clock_atual = 0
        self.fila_tarefas_prontas = []
        self.tarefa_em_execucao = None
        self.todas_tarefas_emitidas = False
        self.lista_tarefas_escalonadas = []
        self.registro_tarefas = {} # id: {ingresso, fim, turnaround, waiting}
        self.porta_clock = porta_clock
        self.porta_emissor = porta_emissor
        self.porta_escalonador = porta_escalonador
        self.algoritmo = algoritmo
        self.endereco_clock = ('localhost', porta_clock)
        self.endereco_emissor = ('localhost', porta_emissor)
        self.selecionador_de_algoritmo = {
            'fcfs': self._escalonar_fcfs,
            'sjf': self._escalonar_sjf,
            'srtf': self._escalonar_srtf,
            'rr': self._escalonar_rr,
            'prioc': self._escalonar_prioc,
            'priop': self._escalonar_priop,
            'priod': self._escalonar_priod
        }

    def converter_tarefa(self, msg):
        id, duracao, prioridade = msg.split(";")
        return {
            'id': id,
            'duracao': int(duracao),
            'prioridade': int(prioridade),
            'tempo_restante': int(duracao)
        }

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Escalonador]: Falha ao conectar {destino}")
    
    def encerramento(self):
        print("[Escalonador]: Todas as tarefas finalizadas. Enviando sinal de fim ao Clock e ao Emissor...")
        # Envio de sinal de fim para Clock e Emissor
        self.enviar_mensagem(self.endereco_clock, "FIM")
        self.enviar_mensagem(self.endereco_emissor, "FIM")

        self.gerar_arquivo_saida()
        sys.exit(0)

    def escalonamento_main(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', self.porta_escalonador))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()

                # Recebeu Clock
                if msg.startswith("CLOCK"):
                    self.clock_atual = int(msg.split()[1])
                    print(f"[Escalonador]: Recebeu CLOCK {self.clock_atual}")
                    self.executar_escalonamento()
                # Recebeu sinal de término de emissão
                elif msg == "-1":
                    print("[Escalonador]: Recebeu sinal de término do Emissor")
                    self.todas_tarefas_emitidas = True
                # Recebeu tarefa
                else:
                    tarefa = self.converter_tarefa(msg)
                    print(f"[Escalonador]: Tarefa recebida {tarefa}")
                    self.fila_tarefas_prontas.append(tarefa)
                    self.registro_tarefas[tarefa['id']] = {
                        'ingresso': self.clock_atual,
                        'fim': -1, # Ainda não finalizou
                        'turnaround': -1, # Ainda não finalizou
                        'waiting_time': 0 # Começa com 0
                    }

    def executar_escalonamento(self):
        # Atualiza informações
        for tarefa in self.fila_tarefas_prontas:
            self.registro_tarefas[tarefa['id']]['waiting_time'] += 1

        if self.tarefa_em_execucao:
            self.tarefa_em_execucao['tempo_restante'] -= 1

        # Verifica término da tarefa no processador
        if self.tarefa_em_execucao and self.tarefa_em_execucao['tempo_restante'] == 0:
            id_tarefa = self.tarefa_em_execucao['id']
            print(f"[Escalonador]: Tarefa {id_tarefa} terminou no Clock {self.clock_atual}.")
            
            # Registra métricas
            self.registro_tarefas[id_tarefa]['fim'] = self.clock_atual
            self.registro_tarefas[id_tarefa]['turnaround'] = self.clock_atual - self.registro_tarefas[id_tarefa]['ingresso']
    
            self.tarefa_em_execucao = None # Libera a CPU
        
        # Verifica fim da simulação
        if self.todas_tarefas_emitidas and not self.fila_tarefas_prontas and self.tarefa_em_execucao is None:
            self.encerramento()
        
        # Chama método de escalonamento
        try:
            funcao_escalonadora = self.selecionador_de_algoritmo[self.algoritmo]
            funcao_escalonadora()
        except KeyError:
            print(f"ERRO: Algoritmo '{self.algoritmo}' não reconhecido.")
            print("Algoritmos possíveis: fcfs, sjf, srtf, rr, prioc, priop, priod")
            return

        # Atualiza linha de tarefas escalonadas
        if self.tarefa_em_execucao:
            self.lista_tarefas_escalonadas.append(self.tarefa_em_execucao['id'])
        else:
            self.lista_tarefas_escalonadas.append('idle')

    def gerar_arquivo_saida(self):
        pass

    def _escalonar_fcfs(self): pass
    def _escalonar_sjf(self): pass
    def _escalonar_srtf(self): pass
    def _escalonar_rr(self): pass
    def _escalonar_prioc(self): pass
    def _escalonar_priop(self): pass
    def _escalonar_priod(self): pass