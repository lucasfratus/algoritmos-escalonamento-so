import socket
import sys
import math


class Escalonador:
    def __init__(self, algoritmo, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002):
        self.clock_atual = 0
        self.quantum = 3
        self.quantum_restante = 0
        self.dinamica_restante = True
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
            'rr': self._escalonar_rr,
            'sjf': self._escalonar_sjf,
            'srtf': self._escalonar_srtf,
            'prioc': self._escalonar_prioc,
            'priop': self._escalonar_priop,
            'priod': self._escalonar_priod
        }

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Escalonador]: Falha ao conectar {destino}")
    
    def converter_tarefa(self, msg):
        id, duracao, prioridade = msg.split(";")
        return {
            'id': id,
            'duracao': int(duracao),
            'tempo_restante': int(duracao),
            'prioridade_estatica': int(prioridade),
            'prioridade': int(prioridade)
        }
    
    def encerramento(self):
        print("[Escalonador]: Todas as tarefas finalizadas. Enviando sinal de fim ao Clock e ao Emissor...")
        # Envio de sinal de fim para Clock e Emissor
        self.enviar_mensagem(self.endereco_clock, "FIM")
        self.enviar_mensagem(self.endereco_emissor, "FIM")

        self.gerar_arquivo_saida()
        print(self.lista_tarefas_escalonadas)
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
                    if self.algoritmo == 'priod':
                        # Aplica prioridade dinâmica
                        for tarefa in self.fila_tarefas_prontas:
                            if tarefa['prioridade'] > 0 and self.registro_tarefas[tarefa['id']]['ingresso'] != self.clock_atual:
                                tarefa['prioridade'] -= 1
                                self.dinamica_restante = False

    def executar_escalonamento(self):
        # Atualiza informações
        for tarefa in self.fila_tarefas_prontas:
            self.registro_tarefas[tarefa['id']]['waiting_time'] += 1

        if self.tarefa_em_execucao:
            self.tarefa_em_execucao['tempo_restante'] -= 1
            if self.algoritmo == 'rr':
                self.quantum_restante -= 1

        # Verifica término da tarefa no processador
        if self.tarefa_em_execucao and self.tarefa_em_execucao['tempo_restante'] == 0:
            id_tarefa = self.tarefa_em_execucao['id']
            print(f"[Escalonador]: Tarefa {id_tarefa} terminou no Clock {self.clock_atual}.")
            if self.algoritmo == 'priod':
                # Aplica prioridade dinâmica
                for tarefa in self.fila_tarefas_prontas:
                    if tarefa['prioridade'] > 0 and self.registro_tarefas[tarefa['id']]['ingresso'] != self.clock_atual and self.dinamica_restante:
                        tarefa['prioridade'] -= 1
            
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
        
        self.dinamica_restante = True

    def gerar_arquivo_saida(self):
        with open("saida.txt", "w") as f:
            linha_execucao = ";".join(self.lista_tarefas_escalonadas)
            f.write(linha_execucao + "\n")

            soma_turnaround = 0
            soma_waiting = 0
            total_tarefas = len(self.registro_tarefas)

            for id_tarefa in sorted(self.registro_tarefas.keys()):
                dados = self.registro_tarefas[id_tarefa]
                ingresso = dados['ingresso']
                fim = dados['fim']
                turnaround = dados['turnaround']
                waiting = dados['waiting_time']
                soma_turnaround += turnaround
                soma_waiting += waiting
                f.write(f"{id_tarefa};{ingresso};{fim};{turnaround};{waiting}\n")

            # 3. Médias com 1 casa decimal, arredondadas para cima
            media_turnaround = math.ceil((soma_turnaround / total_tarefas) * 10) / 10
            media_waiting = math.ceil((soma_waiting / total_tarefas) * 10) / 10
            f.write(f"{media_turnaround:.1f};{media_waiting:.1f}\n")


    def _escalonar_fcfs(self):
        # First-Come, First Served
        if self.tarefa_em_execucao is not None or not self.fila_tarefas_prontas:
            return

        self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
        print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {self.tarefa_em_execucao['id']} iniciou sua execução. (FCFS)")

    def _escalonar_rr(self):
        # Roud-Robin
        if self.tarefa_em_execucao and self.quantum_restante == 0:
            print(f"[Escalonador CLOCK {self.clock_atual}]: Quantum da tarefa {self.tarefa_em_execucao['id']} expirou. Ocorrendo preempção.")
            self.fila_tarefas_prontas.append(self.tarefa_em_execucao)
            self.tarefa_em_execucao = None
        
        if self.tarefa_em_execucao is None and self.fila_tarefas_prontas:
            self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
            self.quantum_restante = self.quantum
            print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {self.tarefa_em_execucao['id']} iniciou sua execução (RR).")

    def _escalonar_sjf(self):
        # Shortest Job First
        if self.tarefa_em_execucao or not self.fila_tarefas_prontas:
            return

        self.fila_tarefas_prontas.sort(key=lambda t: (t['duracao'], self.registro_tarefas[t['id']]['ingresso'], t['id']))
        self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
        print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {self.tarefa_em_execucao['id']} iniciou sua execução. (SJF)")

    def _escalonar_srtf(self):
        # Shortest Remaining Time First
        if not self.fila_tarefas_prontas:
            return
        
        self.fila_tarefas_prontas.sort(key=lambda t: (t['tempo_restante'], self.registro_tarefas[t['id']]['ingresso'], t['id']))
        candidata = self.fila_tarefas_prontas[0]
        
        if self.tarefa_em_execucao and candidata['tempo_restante'] < self.tarefa_em_execucao['tempo_restante']:
                self.fila_tarefas_prontas.append(self.tarefa_em_execucao)
                self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
                print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {candidata['id']} é melhor que {self.tarefa_em_execucao['id']}.")
        elif self.tarefa_em_execucao is None:
            self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
            print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {self.tarefa_em_execucao['id']} iniciou (SRTF).")

    def _escalonar_prioc(self):
        # Escalonamento por Prioridades Fixas Cooperativo
        if self.tarefa_em_execucao is not None or not self.fila_tarefas_prontas:
            return

        self.fila_tarefas_prontas.sort(key=lambda t: t['prioridade_estatica'])
        self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
        print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {self.tarefa_em_execucao['id']} iniciou sua execução (PRIOc).")

    def _escalonar_priop(self):
        # Escalonamento por Prioridades Preemptivo
        if not self.fila_tarefas_prontas:
            return

        self.fila_tarefas_prontas.sort(key=lambda t: (t['prioridade_estatica'], self.registro_tarefas[t['id']]['ingresso'], t['id']))
        candidata = self.fila_tarefas_prontas[0]

        if self.tarefa_em_execucao and candidata['prioridade_estatica'] < self.tarefa_em_execucao['prioridade_estatica']:
                self.fila_tarefas_prontas.append(self.tarefa_em_execucao)
                self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
                print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {candidata['id']} (P{candidata['prioridade_estatica']}) é melhor que {self.tarefa_em_execucao['id']} (P{self.tarefa_em_execucao['prioridade_estatica']}).")
        elif self.tarefa_em_execucao is None:
            self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
            id_tarefa = self.tarefa_em_execucao['id']
            print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {id_tarefa} iniciou (PRIOp).")

    def _escalonar_priod(self):
        print(self.fila_tarefas_prontas)
        # Escalonamento por Prioridades Dinâmicas
        if not self.fila_tarefas_prontas:
            return

        self.fila_tarefas_prontas.sort(key=lambda t: (t['prioridade'], self.registro_tarefas[t['id']]['ingresso'], t['id']))
        candidata = self.fila_tarefas_prontas[0]

        if self.tarefa_em_execucao and candidata['prioridade'] < self.tarefa_em_execucao['prioridade']:
                print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {candidata['id']} (P{candidata['prioridade']}) é melhor que {self.tarefa_em_execucao['id']} (P{self.tarefa_em_execucao['prioridade']}).")
                self.fila_tarefas_prontas.append(self.tarefa_em_execucao)
                self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
                prioridade_estatica = self.tarefa_em_execucao['prioridade_estatica']
                self.tarefa_em_execucao['prioridade'] = prioridade_estatica
                print(f"[Escalonador]: Prioridade da tarefa {self.tarefa_em_execucao['id']} resetada para {self.tarefa_em_execucao['prioridade_estatica']}.")
        elif self.tarefa_em_execucao is None:
            self.tarefa_em_execucao = self.fila_tarefas_prontas.pop(0)
            prioridade_estatica = self.tarefa_em_execucao['prioridade_estatica']
            self.tarefa_em_execucao['prioridade'] = prioridade_estatica
            print(f"[Escalonador CLOCK {self.clock_atual}]: Tarefa {self.tarefa_em_execucao['id']} iniciou (PRIOD). Prioridade resetada para {self.tarefa_em_execucao['prioridade_estatica']}.")
