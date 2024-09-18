class Fila:
    def __init__(self, servidores, capacidade, min_chegada, max_chegada, min_atendimento, max_atendimento):
        self.servidores = servidores
        self.capacidade = capacidade
        self.min_chegada = min_chegada
        self.max_chegada = max_chegada
        self.min_atendimento = min_atendimento
        self.max_atendimento = max_atendimento
        self.clientes = 0
        self.perdidos = 0
        self.tempos_estados = [0.0] * (capacidade + 1)
        self.servidores_ocupados = 0

    def status(self):
        return self.clientes

    def capacidade_total(self):
        return self.capacidade

    def servidores_total(self):
        return self.servidores

    def perda(self):
        self.perdidos += 1

    def entrada(self):
        self.clientes += 1

    def saida(self):
        self.clientes -= 1

class Evento:
    def __init__(self, tipo, tempo, fila):
        self.tipo = tipo
        self.tempo = tempo
        self.fila = fila

class Simulador:
    def __init__(self, filas):
        self.filas = filas
        self.tempo_global = 0.0
        self.eventos = []
        
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32
        self.previous = 12345

    def next_random(self):
        self.previous = (self.a * self.previous + self.c) % self.m
        return self.previous / self.m

    def agendar_evento(self, tipo, tempo, fila):
        self.eventos.append(Evento(tipo, tempo, fila))
        self.eventos.sort(key=lambda x: x.tempo)

    def next_event(self):
        return self.eventos.pop(0)

    def acumula_tempo(self, tempo):
        for i, fila in enumerate(self.filas):
            fila.tempos_estados[fila.status()] += tempo - self.tempo_global
        self.tempo_global = tempo

    def chegada(self, evento):
        fila = self.filas[evento.fila]
        self.acumula_tempo(evento.tempo)

        if fila.status() < fila.capacidade_total():
            fila.entrada()
            if fila.servidores_ocupados < fila.servidores_total():
                fila.servidores_ocupados += 1
                tempo_atendimento = fila.min_atendimento + (fila.max_atendimento - fila.min_atendimento) * self.next_random()
                self.agendar_evento("saida", self.tempo_global + tempo_atendimento, evento.fila)
        else:
            fila.perda()

        if evento.fila == 0:
            tempo_chegada = fila.min_chegada + (fila.max_chegada - fila.min_chegada) * self.next_random()
            self.agendar_evento("chegada", self.tempo_global + tempo_chegada, 0)

    def saida(self, evento):
        fila_atual = self.filas[evento.fila]
        self.acumula_tempo(evento.tempo)

        fila_atual.saida()
        if fila_atual.status() >= fila_atual.servidores_total():
            tempo_atendimento = fila_atual.min_atendimento + (fila_atual.max_atendimento - fila_atual.min_atendimento) * self.next_random()
            self.agendar_evento("saida", self.tempo_global + tempo_atendimento, evento.fila)
        else:
            fila_atual.servidores_ocupados -= 1

        if evento.fila < len(self.filas) - 1:
            self.agendar_evento("passagem", self.tempo_global, evento.fila)

    def passagem(self, evento):
        fila_atual = self.filas[evento.fila]
        proxima_fila = self.filas[evento.fila + 1]
        self.acumula_tempo(evento.tempo)

        if proxima_fila.status() < proxima_fila.capacidade_total():
            proxima_fila.entrada()
            if proxima_fila.servidores_ocupados < proxima_fila.servidores_total():
                proxima_fila.servidores_ocupados += 1
                tempo_atendimento = proxima_fila.min_atendimento + (proxima_fila.max_atendimento - proxima_fila.min_atendimento) * self.next_random()
                self.agendar_evento("saida", self.tempo_global + tempo_atendimento, evento.fila + 1)
        else:
            proxima_fila.perda()

    def simular(self, num_aleatorios):
        self.agendar_evento("chegada", 1.5, 0)

        count = num_aleatorios
        while count > 0:
            evento = self.next_event()
            if evento.tipo == "chegada":
                self.chegada(evento)
            elif evento.tipo == "saida":
                self.saida(evento)
            elif evento.tipo == "passagem":
                self.passagem(evento)
            count -= 1

        for fila in self.filas:
            fila.tempos_estados[fila.status()] += self.tempo_global - self.tempo_global

    def imprimir_resultados(self):
        print(f"Tempo global de simulação: {self.tempo_global:.2f}")
        for i, fila in enumerate(self.filas):
            print(f"\nFila {i+1}:")
            print(f"Clientes perdidos: {fila.perdidos}")
            print("Distribuição de probabilidades dos estados:")
            for j in range(fila.capacidade_total() + 1):
                prob = fila.tempos_estados[j] / self.tempo_global
                print(f"{j}: {fila.tempos_estados[j]:.2f} ({prob:.2%})")

# Configuração das filas
fila1 = Fila(2, 3, 1, 4, 3, 4)
fila2 = Fila(1, 5, float('inf'), float('inf'), 2, 3)

sim = Simulador([fila1, fila2])

sim.simular(100000)

sim.imprimir_resultados()