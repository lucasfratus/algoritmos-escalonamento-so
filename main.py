import sys
import multiprocessing
from clock import Clock
from emissor import Emissor
from escalonador import Escalonador

if __name__ == "__main__":
    #  Verifica quantidade de argumentos
    if len(sys.argv) != 3:
        print("Erro: Quantidade inválida de argumentos.")
        print("Uso: python main.py <caminho_do_arquivo> <algoritmo>")
    
    else:
        caminho_tarefas = sys.argv[1]
        algoritmo = sys.argv[2]

        # Constrói os componentes
        clock = Clock()
        emissor = Emissor(caminho_tarefas)
        escalonador = Escalonador(algoritmo)

        # Cria os processos
        processo_clock = multiprocessing.Process(target=clock.iniciar_clock)
        processo_emissor = multiprocessing.Process(target=emissor.iniciar)
        processo_escalonador = multiprocessing.Process(target=escalonador.receber_conexoes)

        # Inicia e executa os processos
        print("[Main]: Iniciando a simulação...")
        processo_clock.start()
        processo_emissor.start()
        processo_escalonador.start()

        # Espera os processos terminarem
        processo_escalonador.join()
        processo_clock.join(timeout=2)
        processo_emissor.join(timeout=2)

        # Força parada caso não terminem
        if processo_clock.is_alive():
            processo_clock.terminate()
        if processo_emissor.is_alive():
            processo_emissor.terminate()
        
        print("[Main]: Simulação finalizada.")