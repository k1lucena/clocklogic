from typing import Dict, List


class Cliente:
    """Representa um processo cliente no sistema distribuído."""

    def __init__(self, processo_id: str, hora_local: int, instante_envio: int) -> None:
        self.processo_id = processo_id
        self.hora_local = hora_local
        self.instante_envio = instante_envio
        self.clock_logico = 0
        self.ajuste = 0.0

    def enviar_mensagem(self) -> Dict[str, int]:
        """
        Simula o envio de uma mensagem ao servidor.
        Antes do envio, o cliente incrementa seu clock lógico.
        """
        self.clock_logico += 1
        mensagem = {
            "processo_id": self.processo_id,
            "hora_local": self.hora_local,
            "hora_envio": self.instante_envio,
            "clock_logico": self.clock_logico,
        }

        print(f"{self.processo_id} preparando envio da mensagem...")
        print(f"Hora local do {self.processo_id}: {self.hora_local}")
        print(f"Hora de envio informada pelo {self.processo_id}: {self.instante_envio}")
        print(f"Clock lógico do {self.processo_id} no envio: {self.clock_logico}")
        print("-" * 70)
        return mensagem


class Servidor:
    """Controla a sincronização dos clocks e o acesso ao recurso compartilhado."""

    def __init__(self, hora_local: int) -> None:
        self.hora_local = hora_local
        self.clock_logico = 0
        self.mensagens_recebidas: List[Dict[str, int]] = []
        self.clock_sincronizado = 0.0

    def receber_mensagem(self, mensagem: Dict[str, int]) -> None:
        """
        Recebe uma mensagem do cliente e atualiza o clock lógico do servidor
        seguindo a regra de Lamport.
        """
        print(f"Servidor recebendo mensagem de {mensagem['processo_id']}...")
        print(f"Hora local do servidor no recebimento: {self.hora_local}")

        clock_recebido = mensagem["clock_logico"]
        self.clock_logico = max(self.clock_logico, clock_recebido) + 1

        evento = {
            "processo_id": mensagem["processo_id"],
            "hora_local_cliente": mensagem["hora_local"],
            "hora_envio": mensagem["hora_envio"],
            "clock_cliente": mensagem["clock_logico"],
            "clock_servidor_recebimento": self.clock_logico,
        }
        self.mensagens_recebidas.append(evento)

        print(f"Clock lógico recebido do cliente: {clock_recebido}")
        print(f"Clock lógico do servidor após recebimento: {self.clock_logico}")
        print("-" * 70)

    def exibir_horarios(self) -> None:
        """Mostra a hora local do servidor e de cada cliente."""
        print("=" * 70)
        print("HORARIOS LOCAIS DO SISTEMA")
        print("=" * 70)
        print(f"Hora local do servidor: {self.hora_local}")
        for evento in self.mensagens_recebidas:
            print(
                f"Hora local do {evento['processo_id']}: "
                f"{evento['hora_local_cliente']}"
            )
        print("-" * 70)

    def sincronizar_clocks(self) -> Dict[str, float]:
        """
        Cria um clock sincronizado usando a média entre a hora do servidor e
        as horas locais dos clientes.
        """
        soma_horarios = self.hora_local
        for evento in self.mensagens_recebidas:
            soma_horarios += evento["hora_local_cliente"]

        quantidade_relogios = len(self.mensagens_recebidas) + 1
        self.clock_sincronizado = soma_horarios / quantidade_relogios

        ajustes = {"Servidor": self.clock_sincronizado - self.hora_local}

        print("=" * 70)
        print("SINCRONIZACAO DOS CLOCKS")
        print("=" * 70)
        print(f"Media calculada entre servidor e clientes: {self.clock_sincronizado:.2f}")
        print(
            f"Ajuste necessario para o Servidor: "
            f"{ajustes['Servidor']:+.2f}"
        )

        for evento in self.mensagens_recebidas:
            ajuste = self.clock_sincronizado - evento["hora_local_cliente"]
            ajustes[evento["processo_id"]] = ajuste
            print(
                f"Ajuste necessario para {evento['processo_id']}: "
                f"{ajuste:+.2f}"
            )

        print("-" * 70)
        return ajustes

    def ordenar_eventos_lamport(self) -> List[Dict[str, int]]:
        """
        Ordena os eventos pelo timestamp lógico de Lamport.
        Em caso de empate, usa a hora de envio e o identificador do processo.
        """
        print("=" * 70)
        print("ORDENACAO DOS EVENTOS PELO CLOCK LOGICO DE LAMPORT")
        print("=" * 70)

        eventos_ordenados = sorted(
            self.mensagens_recebidas,
            key=lambda evento: (
                evento["clock_cliente"],
                evento["hora_envio"],
                evento["processo_id"],
            ),
        )

        for posicao, evento in enumerate(eventos_ordenados, start=1):
            print(
                f"{posicao}o lugar -> {evento['processo_id']} | "
                f"C(a) = {evento['clock_cliente']} | "
                f"Hora de envio = {evento['hora_envio']}"
            )

        print("-" * 70)
        return eventos_ordenados

    def controlar_recurso_compartilhado(
        self, eventos_ordenados: List[Dict[str, int]]
    ) -> None:
        """
        Simula exclusão mútua, região crítica e acesso sequencial ao recurso.
        Apenas um processo entra por vez, respeitando a ordem de Lamport.
        """
        print("=" * 70)
        print("ACESSO AO RECURSO COMPARTILHADO")
        print("=" * 70)
        print("Exclusao mutua ativada: somente um processo acessa o recurso por vez.")
        print("Regiao critica protegida pelo clock logico de Lamport.")
        print("-" * 70)

        for evento in eventos_ordenados:
            processo_id = evento["processo_id"]
            print(f"{processo_id} aguardando liberacao do recurso compartilhado...")
            print(f"{processo_id} entrou na regiao critica.")
            print(f"{processo_id} esta utilizando o recurso compartilhado.")
            print(f"{processo_id} saiu da regiao critica.")
            print("-" * 70)

        print("Ordem final de acesso ao recurso compartilhado:")
        ordem_final = [evento["processo_id"] for evento in eventos_ordenados]
        print(" -> ".join(ordem_final))
        print("=" * 70)


def simular_sistema_distribuido() -> None:
    """Executa a simulacao completa do sistema distribuido."""
    print("=" * 70)
    print("SIMULACAO DE SINCRONIZACAO DISTRIBUIDA COM CLOCK LOGICO DE LAMPORT")
    print("=" * 70)

    servidor = Servidor(hora_local=100)

    clientes = [
        Cliente(processo_id="P1", hora_local=95, instante_envio=5),
        Cliente(processo_id="P2", hora_local=102, instante_envio=2),
        Cliente(processo_id="P3", hora_local=98, instante_envio=8),
    ]

    print("Clientes criados com horarios locais e instantes de envio.")
    print("Servidor pronto para receber as mensagens.")
    print("-" * 70)

    for cliente in clientes:
        mensagem = cliente.enviar_mensagem()
        servidor.receber_mensagem(mensagem)

    servidor.exibir_horarios()
    servidor.sincronizar_clocks()
    eventos_ordenados = servidor.ordenar_eventos_lamport()
    servidor.controlar_recurso_compartilhado(eventos_ordenados)


if __name__ == "__main__":
    simular_sistema_distribuido()
