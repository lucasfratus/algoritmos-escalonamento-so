import socket

class Emissor:
    def __init__(self, caminho_arquivo, porta_clock=4000, porta_emissor=4001, porta_escalonador=4002):
        self.clock_atual = 0
        self.indice_tarefa = 0 # Indice da tarefa que será emitida
        self.emissao_finalizada = False
        self.tarefas = self.carregar_tarefas(caminho_arquivo)
        self.total_tarefas = len(self.tarefas)
        self.porta_clock = porta_clock
        self.porta_emissor = porta_emissor
        self.porta_escalonador = porta_escalonador
        self.endereco_clock = ('localhost', porta_clock)
        self.endereco_escalonador = ('localhost', porta_escalonador)

    def carregar_tarefas(self, caminho_arquivo):
        tarefas = []
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                if linha.strip():
                    id, tempo_ingresso, duracao_prevista, prioridade = linha.strip().split(';')
                    # Utiliza um dicionário para cada tarefa na lista de tarefas 
                    tarefa = {
                        'id': id,
                        'ingresso': int(tempo_ingresso),
                        'duracao_prevista': int(duracao_prevista),
                        'prioridade': int(prioridade)
                    }
                    tarefas.append(tarefa)
        return tarefas
    

    def emitir_tarefa(self, tarefa):
        # Forma a mensagem com as informações da tarefa para enviá-la ao Escalonador
        mensagem = f"{tarefa['id']};{tarefa['ingresso']};{tarefa['duracao_prevista']};{tarefa['prioridade']}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.endereco_escalonador)
                s.sendall(mensagem.encode())
                print(f"[T{self.clock_atual} - Emissor]: Enviou a tarefa {tarefa['id']} ao Escalonador.")
        except ConnectionRefusedError:
            print(f"[T{self.clock_atual} - Emissor]: Não conseguiu conectar ao Escalonador.")
    

    def emissor_main(self):
        # Envia sinal de início ao Clock
        print(f"[T{self.clock_atual} - Emissor]: Tarefas carregadas. Enviando sinal de início para o Clock...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.endereco_clock)
                s.sendall("START CLOCK".encode())
        except ConnectionRefusedError:
            print(f"[T{self.clock_atual} - Emissor]: Falha de conexão com Clock para enviar o sinal de início.")
            return

        # Inicia operação de emissão
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', self.porta_emissor))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                msg = conn.recv(1024).decode()
                # Recebe sinal de Clock
                if msg.startswith("CLOCK"):
                    self.clock_atual = int(msg.split()[1])
                    print(f"[T{self.clock_atual} - Emissor] Recebeu Clock {self.clock_atual}.")

                    if not self.emissao_finalizada:
                        # Verifica quais tarefas devem ser emitidas no Clock atual
                        while self.indice_tarefa < self.total_tarefas and self.tarefas[self.indice_tarefa]['ingresso'] == self.clock_atual:
                            tarefa = self.tarefas[self.indice_tarefa]
                            self.emitir_tarefa(tarefa)
                            self.indice_tarefa += 1
                        
                        # Caso tenha emitido todas as tarefas, envia um sinal de término de emissão ao Escalonador
                        if self.indice_tarefa == self.total_tarefas:
                            try:
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
                                    s1.connect(self.endereco_escalonador)
                                    s1.sendall("-1".encode())
                                    print(f"[T{self.clock_atual} - Emissor]: Sinal de término de emissão enviado ao Escalonador.")
                            except ConnectionRefusedError:
                                print(f"[T{self.clock_atual} - Emissor]: Não foi possível enviar o sinal de término de emissão ao Escalonador.")
                            self.emissao_finalizada = True
                # Recebeu sinal de encerramento do Escalonador
                elif msg == "FIM":
                    print(f"[T{self.clock_atual} - Emissor]: Sinal de encerramento recebido. Encerrando Emissor...")
                    break

        s.close() # Fecha a conexão do Socket
        print(f"[T{self.clock_atual} - Emissor]: Emissor encerrado.")
