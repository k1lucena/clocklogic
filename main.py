import random

class Cliente:
    def __init__(self, id, hora, envio, clock=0):
        self.id = id
        self.hora = hora
        self.envio = envio
        self.clock = clock

    def enviar(self):
        self.clock += 1
        print(f"[{self.id}] Pedi acesso! (Hora fisica: {self.hora:.1f}, Clock logico: {self.clock})")
        return {
            "id": self.id,
            "hora": self.hora,
            "envio": self.envio,
            "clock": self.clock
        }

    def conceder(self, clock_servidor):
        self.clock = max(self.clock, clock_servidor) + 1
        print(f"[{self.id}] Consegui entrar na regiao critica! Clock: {self.clock}")

    def liberar(self):
        self.clock += 1
        print(f"[{self.id}] Terminei e desocupei a regiao critica. Clock: {self.clock}")
        return {
            "id": self.id,
            "clock": self.clock
        }

    def ajustar(self, val):
        self.hora += val

class Servidor:
    def __init__(self, hora):
        self.hora = hora
        self.clock = 0
        self.pedidos = []

    def receber(self, msg):
        self.clock = max(self.clock, msg["clock"]) + 1
        self.pedidos.append({
            "id": msg["id"],
            "hora": msg["hora"],
            "envio": msg["envio"],
            "clock": msg["clock"],
        })
        print(f"[Servidor] Pedido de {msg['id']} recebido. Clock: {self.clock}")

    def sincronizar(self, limite=15.0):
        validas = [0.0]
        outliers = []
        for p in self.pedidos:
            dif = p["hora"] - self.hora
            if abs(dif) <= limite:
                validas.append(dif)
            else:
                outliers.append(p["id"])

        media = sum(validas) / len(validas)
        self.hora += media
        
        ajustes = {"Servidor": media}
        for p in self.pedidos:
            ajustes[p["id"]] = self.hora - p["hora"]

        print(f"\n[Berkeley] Sincronizando relogios:")
        print(f"  Diferenca media: {media:+.1f} | Novo horario: {self.hora:.1f}")
        if outliers:
            print(f"  Ignorados (fora do limite): {outliers}")
        for dest, v in ajustes.items():
            print(f"  Ajuste de {dest}: {v:+.1f}")
        return ajustes

    def processar(self, clientes):
        fila = sorted(self.pedidos, key=lambda e: (e["clock"], e["id"]))
        
        print("\n[Lamport] Fila de prioridade:")
        for pos, p in enumerate(fila, 1):
            print(f"  {pos}o: {p['id']} (Clock: {p['clock']}, Envio: {p['envio']})")

        print("\n[Regiao Critica] Simulando acessos:")
        acessos = []
        for p in fila:
            pid = p["id"]
            cli = clientes[pid]
            
            self.clock += 1
            print(f"[Servidor] Liberando {pid}. Clock: {self.clock}")
            cli.conceder(self.clock)
            
            retorno = cli.liberar()
            self.clock = max(self.clock, retorno["clock"]) + 1
            print(f"[Servidor] {pid} liberou. Clock: {self.clock}")
            print("-" * 40)
            acessos.append(pid)

        print("Ordem de acesso final:", " -> ".join(acessos))

def simular(titulo, configs):
    print("\n" + "=" * 50)
    print(f" {titulo.upper()} ")
    print("=" * 50)

    server = Servidor(100.0)
    clientes = {c["id"]: Cliente(c["id"], c["hora"], c["envio"], c.get("clock", 0)) for c in configs}
    
    fila_envio = list(clientes.values())
    random.shuffle(fila_envio)
    
    print("Enviando pedidos em ordem aleatoria:")
    for cli in fila_envio:
        msg = cli.enviar()
        server.receber(msg)

    print(f"\nHorarios antes da sincronizacao:")
    print(f"  Servidor: {server.hora:.1f}")
    for cli in clientes.values():
        print(f"  {cli.id}: {cli.hora:.1f}")

    ajustes = server.sincronizar()
    
    for pid, val in ajustes.items():
        if pid != "Servidor":
            clientes[pid].ajustar(val)

    print(f"\nHorarios apos a sincronizacao:")
    print(f"  Servidor: {server.hora:.1f}")
    for cli in clientes.values():
        print(f"  {cli.id}: {cli.hora:.1f}")

    server.processar(clientes)

def main():
    cenarios = [
        (
            "Cenario 1 - Clocks logicos iguais (desempate por ID)",
            [
                {"id": "P1", "hora": 95, "envio": 5},
                {"id": "P2", "hora": 102, "envio": 2},
                {"id": "P3", "hora": 98, "envio": 8},
            ]
        ),
        (
            "Cenario 2 - Clocks logicos diferentes",
            [
                {"id": "P1", "hora": 95, "envio": 5, "clock": 4},
                {"id": "P2", "hora": 102, "envio": 2, "clock": 0},
                {"id": "P3", "hora": 98, "envio": 8, "clock": 2},
            ]
        ),
        (
            "Cenario 3 - Envio fisico anterior com prioridade logica posterior",
            [
                {"id": "P1", "hora": 95, "envio": 9, "clock": 0},
                {"id": "P2", "hora": 102, "envio": 1, "clock": 5},
                {"id": "P3", "hora": 98, "envio": 3, "clock": 2},
            ]
        ),
        (
            "Cenario 4 - Empate de clock entre dois nos",
            [
                {"id": "P1", "hora": 95, "envio": 7, "clock": 2},
                {"id": "P2", "hora": 102, "envio": 4, "clock": 0},
                {"id": "P3", "hora": 98, "envio": 1, "clock": 2},
            ]
        ),
        (
            "Cenario 5 - Correcao de relogio desregulado (Outlier)",
            [
                {"id": "P1", "hora": 95, "envio": 5},
                {"id": "P2", "hora": 102, "envio": 2},
                {"id": "P3", "hora": 150, "envio": 8},
            ]
        )
    ]

    for tit, cfg in cenarios:
        simular(tit, cfg)

if __name__ == "__main__":
    main()
