import random
import tkinter as tk
import os
import pickle
from abc import ABC, abstractmethod

class Circuito(ABC):
    def __init__(self, resistores, corrente):
        self.resistores = resistores
        self.corrente = round(corrente, 2)
        self.tensao = round(self.calcular_tensao_total(), 2)

    @abstractmethod
    def calcular_resistencia_eq(self):
        pass

    def calcular_tensao_total(self):
        return round(self.corrente * self.calcular_resistencia_eq(), 2)

ARQUIVO_RECORDE = "recorde.pkl"
ARQUIVO_PROGRESSO = "progresso.pkl"

def salvar_dados(arquivo, dados):
    with open(arquivo, "wb") as f:
        pickle.dump(dados, f)

def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "rb") as f:
            return pickle.load(f)
    return None

def carregar_recorde():
    recorde = carregar_dados(ARQUIVO_RECORDE)
    return recorde if recorde is not None else 0

def salvar_recorde(novo_recorde):
    salvar_dados(ARQUIVO_RECORDE, novo_recorde)

def salvar_progresso(pontuacao):
    salvar_dados(ARQUIVO_PROGRESSO, pontuacao)

def carregar_progresso():
    progresso = carregar_dados(ARQUIVO_PROGRESSO)
    return progresso if progresso is not None else 0

class CircuitoSerie(Circuito):
    def calcular_resistencia_eq(self):
        return round(sum(self.resistores), 2)

class CircuitoParalelo(Circuito):
    def calcular_resistencia_eq(self):
        return round(1 / sum(1 / r for r in self.resistores), 2)

class GerenciadorPerguntas: #estrutura de dados para gerenciar repetitividade das perguntas
    def __init__(self):
        self.tipos_perguntas = ["tensao_total", "corrente_total", "resistencia_eq"]
        self.perguntas_disponiveis = self.tipos_perguntas.copy()

    def obter_proxima_pergunta(self):
        if not self.perguntas_disponiveis:
            self.perguntas_disponiveis = self.tipos_perguntas.copy() 
        pergunta = random.choice(self.perguntas_disponiveis)
        self.perguntas_disponiveis.remove(pergunta) 
        return pergunta

def gerar_circuito(gerenciador_perguntas):
    num_resistores = random.randint(1, 4)
    resistores = [round(random.randint(1, 100), 2) for _ in range(num_resistores)]
    corrente = round(random.uniform(0.1, 5.0), 2)

    tipo_circuito = random.choice(["série", "paralelo"])
    circuito = CircuitoSerie(resistores, corrente) if tipo_circuito == "série" else CircuitoParalelo(resistores, corrente)

    parametro_faltante = gerenciador_perguntas.obter_proxima_pergunta()

    return circuito, parametro_faltante, tipo_circuito

class JogoEletronica:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo de Eletrônica - Lei de Ohm")
        self.pontuacao = carregar_progresso()
        self.recorde = carregar_recorde()
        self.jogo_terminado = False
        self.root.geometry("600x600")
        self.gerenciador_perguntas = GerenciadorPerguntas() 

        tk.Label(root, text="Bem-vindo ao Jogo de Eletrônica!", font=("Arial", 14)).pack(pady=10)

        self.label_recorde = tk.Label(root, text=f"Recorde: {self.recorde} pontos", font=("Arial", 12), fg="blue")
        self.label_recorde.pack(pady=5)

        self.botao_iniciar = tk.Button(root, text="Iniciar", command=self.iniciar_jogo)
        self.botao_iniciar.pack(pady=5)
        self.botao_sair = tk.Button(root, text="Sair", command=self.sair)
        self.botao_sair.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.sair)

        if self.pontuacao > 0:
            self.iniciar_jogo()

    def sair(self):
        if self.jogo_terminado:
            salvar_progresso(0)
        else:
            salvar_progresso(self.pontuacao)
        self.root.quit()

    def iniciar_jogo(self):
        self.botao_iniciar.pack_forget()
        self.botao_sair.pack_forget()
        self.nova_rodada()

    def nova_rodada(self):
        self.circuito, self.parametro_faltante, self.tipo_circuito = gerar_circuito(self.gerenciador_perguntas)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.label_pontuacao = tk.Label(self.root, text=f"Pontuação: {self.pontuacao}", font=("Arial", 12))
        self.label_pontuacao.pack(pady=5)

        descricao = f"Circuito {self.tipo_circuito.upper()} com {len(self.circuito.resistores)} resistores:\n"
        for i, r in enumerate(self.circuito.resistores, 1):
            descricao += f"Resistor {i}: {r if self.parametro_faltante != f'resistor_{i}' else '?'}Ω\n"

        if self.parametro_faltante != "resistencia_eq":
            descricao += f"Corrente: {self.circuito.corrente if self.parametro_faltante != 'corrente_total' else '?'}A\n"
            descricao += f"Tensão Total: {self.circuito.tensao if self.parametro_faltante != 'tensao_total' else '?'}V\n"
        else:
            descricao += "Resistência Equivalente: ?Ω"

        tk.Label(self.root, text=descricao, font=("Arial", 12), justify="left").pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=400, height=200, bg="white")
        self.canvas.pack(pady=10)
        self.desenhar_circuito()

        self.entry_resposta = tk.Entry(self.root)
        self.entry_resposta.pack(pady=5)

        self.label_erro = tk.Label(self.root, text="", fg="red", font=("Arial", 10))
        self.label_erro.pack(pady=2)

        self.entry_resposta.bind("<KeyRelease>", self.ocultar_erro)

        tk.Button(self.root, text="Verificar", command=self.verificar_resposta).pack(pady=10)

    def desenhar_circuito(self):
        self.canvas.delete("all")
        x_start, y_start = 50, 50

        if self.tipo_circuito == "série":
            for i, r in enumerate(self.circuito.resistores):
                self.canvas.create_line(x_start, y_start, x_start + 40, y_start, width=3)
                self.canvas.create_rectangle(x_start + 40, y_start - 10, x_start + 70, y_start + 10, fill="black")

                valor_exibido = "?Ω" if self.parametro_faltante == f"resistor_{i+1}" else f"{r}Ω"

                self.canvas.create_text(x_start + 55, y_start, text=valor_exibido, fill="white", font=("Arial", 10, "bold"))

                x_start += 70
            self.canvas.create_line(x_start, y_start, x_start + 40, y_start, width=3)

        else:
            mid_x = 200 #paralelo
            num_resistores = len(self.circuito.resistores)

            for i, r in enumerate(self.circuito.resistores):
                y_offset = y_start + (i + 1) * 30

                self.canvas.create_line(mid_x - 50, y_start, mid_x - 50, y_offset, width=3)
                self.canvas.create_line(mid_x + 50, y_start, mid_x + 50, y_offset, width=3)

                self.canvas.create_rectangle(mid_x - 20, y_offset - 5, mid_x + 20, y_offset + 5, fill="black")

                valor_exibido = "?" if self.parametro_faltante == f"resistor_{i+1}" else f"{r}Ω"

                self.canvas.create_text(mid_x, y_offset, text=valor_exibido, fill="white", font=("Arial", 10, "bold"))

                self.canvas.create_line(mid_x - 50, y_offset, mid_x - 20, y_offset, width=3)
                self.canvas.create_line(mid_x + 20, y_offset, mid_x + 50, y_offset, width=3)

    def verificar_resposta(self):
        try:
            resposta = int(float(self.entry_resposta.get()))
            if self.parametro_faltante == "tensao_total":
                valor_correto = int(self.circuito.calcular_tensao_total())
            elif self.parametro_faltante == "corrente_total":
                valor_correto = int(self.circuito.corrente)
            elif self.parametro_faltante == "resistencia_eq":
                valor_correto = int(self.circuito.calcular_resistencia_eq())
            else:
                indice = int(self.parametro_faltante.split("_")[1]) - 1
                valor_correto = int(self.circuito.resistores[indice])

            if valor_correto - 1 <= resposta <= valor_correto + 1:
                self.pontuacao += 1
                self.nova_rodada()
            else:
                self.exibir_fim_de_jogo()
        except ValueError:
            self.label_erro.config(text="Digite um valor numérico válido.")

    def ocultar_erro(self, event=None):
        self.label_erro.config(text="")

    def exibir_fim_de_jogo(self):
        if self.pontuacao > self.recorde:
            self.recorde = self.pontuacao
            salvar_recorde(self.recorde)

        self.jogo_terminado = True

        salvar_progresso(0)

        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Fim de Jogo!", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Você conseguiu {self.pontuacao} pontos!", font=("Arial", 14)).pack(pady=10)

        tk.Button(self.root, text="Reiniciar Jogo", command=self.reiniciar_jogo, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.root, text="Sair", command=lambda: [salvar_progresso(0), self.root.quit()], font=("Arial", 12)).pack(pady=5)

    def reiniciar_jogo(self):
        self.pontuacao = 0
        self.jogo_terminado = False
        self.gerenciador_perguntas = GerenciadorPerguntas() 
        if os.path.exists(ARQUIVO_PROGRESSO):
            os.remove(ARQUIVO_PROGRESSO)
        self.iniciar_jogo()

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoEletronica(root)
    root.mainloop()