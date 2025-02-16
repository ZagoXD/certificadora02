import random
import tkinter as tk
import os
import pickle
from abc import ABC, abstractmethod
from PIL import Image, ImageTk  # Importando Pillow para manipulação de imagens

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

class CircuitoSerie(Circuito):
    def calcular_resistencia_eq(self):
        return round(sum(self.resistores), 2)

class CircuitoParalelo(Circuito):
    def calcular_resistencia_eq(self):
        return round(1 / sum(1 / r for r in self.resistores), 2)

ARQUIVO_RECORDE = "recorde.pkl"

def carregar_recorde():
    if os.path.exists(ARQUIVO_RECORDE):
        with open(ARQUIVO_RECORDE, "rb") as f:
            return pickle.load(f)
    return 0

def salvar_recorde(novo_recorde):
    with open(ARQUIVO_RECORDE, "wb") as f:
        pickle.dump(novo_recorde, f)

class JogoEletronica:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo de Eletrônica - Lei de Ohm")
        self.root.geometry("600x500")
        self.pontuacao = 0
        self.recorde = carregar_recorde()
        
        # Carregar a imagem da interface
        try:
            self.imagem_interface = Image.open("interface.png")
            self.imagem_interface = self.imagem_interface.resize((300, 300), Image.Resampling.LANCZOS)
            self.imagem_interface = ImageTk.PhotoImage(self.imagem_interface)
        except FileNotFoundError:
            self.imagem_interface = None  # Caso a imagem não seja encontrada

        # Tela inicial
        self.label_titulo = tk.Label(root, text="Bem-vindo ao Jogo de Eletrônica!", font=("Arial", 14, "bold"))
        self.label_titulo.pack(pady=10)
        
        # Exibir a imagem, se carregada
        if self.imagem_interface:
            self.label_imagem = tk.Label(root, image=self.imagem_interface)
            self.label_imagem.pack(pady=10)
        
        self.label_recorde = tk.Label(root, text=f"Recorde: {self.recorde} pontos", font=("Arial", 12), fg="blue")
        self.label_recorde.pack(pady=5)
        
        self.botao_iniciar = tk.Button(root, text="Iniciar", command=self.iniciar_jogo, font=("Arial", 12))
        self.botao_iniciar.pack(pady=5)

    def iniciar_jogo(self):
        self.botao_iniciar.pack_forget()
        if hasattr(self, 'label_imagem'):
            self.label_imagem.pack_forget()  # Remover a imagem ao iniciar o jogo
        self.nova_rodada()

    def nova_rodada(self):
        self.tipo_circuito = random.choice([CircuitoSerie, CircuitoParalelo])
        num_resistores = random.randint(2, 4)
        resistores = [random.randint(1, 100) for _ in range(num_resistores)]
        corrente = random.randint(1, 10)
        self.circuito = self.tipo_circuito(resistores, corrente)
        
        parametros = ["tensao", "resistencia", "corrente"]
        self.parametro_faltante = random.choice(parametros)
        
        if self.parametro_faltante == "tensao":
            self.valor_correto = int(self.circuito.calcular_tensao_total())
            enunciado = f"Corrente: {int(self.circuito.corrente)} A\nCalcule a tensão total do circuito."
        elif self.parametro_faltante == "resistencia":
            self.valor_correto = int(self.circuito.calcular_resistencia_eq())
            enunciado = "Calcule a resistência equivalente do circuito."
        else:
            self.valor_correto = int(self.circuito.corrente)
            enunciado = f"Tensão: {int(self.circuito.tensao)} V\nCalcule a corrente total do circuito."
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.label_pontuacao = tk.Label(self.root, text=f"Pontuação: {self.pontuacao}", font=("Arial", 12))
        self.label_pontuacao.pack(pady=5)
        
        self.label_pergunta = tk.Label(self.root, text=enunciado, font=("Arial", 12))
        self.label_pergunta.pack(pady=10)
        
        self.canvas = tk.Canvas(self.root, width=400, height=200, bg="white")
        self.canvas.pack(pady=10)
        self.desenhar_circuito()
        
        self.entry_resposta = tk.Entry(self.root, font=("Arial", 12))
        self.entry_resposta.pack(pady=5)
        
        self.label_feedback = tk.Label(self.root, text="", font=("Arial", 10), fg="red")
        self.label_feedback.pack()
        
        self.botao_verificar = tk.Button(self.root, text="Verificar", command=self.verificar_resposta, font=("Arial", 12))
        self.botao_verificar.pack(pady=5)
        
        self.botao_finalizar = tk.Button(self.root, text="Finalizar Jogo", command=self.finalizar_jogo, font=("Arial", 12))
        self.botao_finalizar.pack(pady=5)
    
    def desenhar_circuito(self):
        self.canvas.delete("all")
        x_start, y_start = 50, 100
        if isinstance(self.circuito, CircuitoSerie):
            for r in self.circuito.resistores:
                self.canvas.create_line(x_start, y_start, x_start + 40, y_start, width=3)
                self.canvas.create_rectangle(x_start + 40, y_start - 10, x_start + 70, y_start + 10, fill="black")
                self.canvas.create_text(x_start + 55, y_start, text=f"{r}Ω", fill="white", font=("Arial", 10, "bold"))
                x_start += 70
            self.canvas.create_line(x_start, y_start, x_start + 40, y_start, width=3)
        else:
            mid_x = 200
            y_offset = y_start - 30 * (len(self.circuito.resistores) - 1) // 2
            for r in self.circuito.resistores:
                self.canvas.create_line(mid_x - 50, y_offset, mid_x + 50, y_offset, width=3)
                self.canvas.create_rectangle(mid_x - 20, y_offset - 5, mid_x + 20, y_offset + 5, fill="black")
                self.canvas.create_text(mid_x, y_offset, text=f"{r}Ω", fill="white", font=("Arial", 10, "bold"))
                y_offset += 30
                
            self.canvas.create_line(mid_x - 50, y_start - 30 * (len(self.circuito.resistores) - 1) // 2, mid_x - 50, y_offset - 30, width=3)
            self.canvas.create_line(mid_x + 50, y_start - 30 * (len(self.circuito.resistores) - 1) // 2, mid_x + 50, y_offset - 30, width=3)
    
    def verificar_resposta(self):
        try:
            resposta = int(self.entry_resposta.get())
            if resposta == self.valor_correto:
                self.label_feedback.config(text="Correto! Próxima rodada.", fg="green")
                self.pontuacao += 1
                if self.pontuacao > self.recorde:
                    self.recorde = self.pontuacao
                    salvar_recorde(self.recorde)
                self.nova_rodada()
            elif resposta < self.valor_correto:
                self.label_feedback.config(text="Muito baixo. Tente novamente.", fg="red")
            else:
                self.label_feedback.config(text="Muito alto. Tente novamente.", fg="red")
        except ValueError:
            self.label_feedback.config(text="Digite um número inteiro válido.", fg="red")
    
    def finalizar_jogo(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = JogoEletronica(root)
    root.mainloop()