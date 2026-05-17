from typing import Dict, List


Evento = Dict[str, int | str]
ClienteConfig = Dict[str, int | str]


class Cliente:
    """Representa um processo cliente no sistema distribuido."""

    def __init__(
        self,
        processo_id: str,
        hora_local: int,
        instante_envio: int,
        clock_inicial: int = 0,
    ) -> None:
        self.processo_id = processo_id
        self.hora_local = hora_local
        self.instante_envio = instante_envio
        self.clock_logico = clock_inicial
        self.ajuste = 0.0

    def enviar_requisicao(self) -> Evento:
        """
        Simula a emissao de uma requisicao de acesso ao recurso.
        O cliente incrementa seu clock antes de gerar o evento local.
        """
        self.clock_logico += 1
        mensagem: Evento = {
            "processo_id": self.processo_id,
            "hora_local": self.hora_local,
            "hora_envio": self.instante_envio,
            "clock_requisicao": self.clock_logico,
        }

        print(f"{self.processo_id} preparando requisicao de acesso...")
        print(f"Hora local do {self.processo_id}: {self.hora_local}")
        print(f"Instante fisico informado por {self.processo_id}: {self.instante_envio}")
        print(f"Clock logico inicial do {self.processo_id}: {self.clock_logico - 1}")
        print(f"Clock logico do {self.processo_id} na requisicao: {self.clock_logico}")
        print("-" * 70)
        return mensagem

    def receber_concessao(self, clock_servidor: int) -> None:
        """Atualiza o clock do cliente ao receber a concessao do servidor."""
        self.clock_logico = max(self.clock_logico, clock_servidor) + 1
        print(f"{self.processo_id} recebeu concessao do servidor.")
        print(f"Clock logico do {self.processo_id} apos concessao: {self.clock_logico}")

    def liberar_recurso(self) -> Evento:
        """Registra o evento local de saida da regiao critica."""
        self.clock_logico += 1
        mensagem: Evento = {
            "processo_id": self.processo_id,
            "clock_liberacao": self.clock_logico,
        }
        print(f"{self.processo_id} liberando o recurso compartilhado.")
        print(f"Clock logico do {self.processo_id} na liberacao: {self.clock_logico}")
        return mensagem


class Servidor:
    """Controla a sincronizacao dos clocks e o acesso ao recurso compartilhado."""

    def __init__(self, hora_local: int) -> None:
        self.hora_local = hora_local
        self.clock_logico = 0
        self.mensagens_recebidas: List[Evento] = []
        self.clock_sincronizado = 0.0

    def receber_requisicao(self, mensagem: Evento) -> None:
        """
        Recebe a requisicao do cliente e atualiza o clock do servidor
        seguindo a regra de Lamport.
        """
        processo_id = str(mensagem["processo_id"])
        print(f"Servidor recebendo requisicao de {processo_id}...")
        print(f"Hora local do servidor no recebimento: {self.hora_local}")

        clock_recebido = int(mensagem["clock_requisicao"])
        self.clock_logico = max(self.clock_logico, clock_recebido) + 1

        evento: Evento = {
            "processo_id": processo_id,
            "hora_local_cliente": int(mensagem["hora_local"]),
            "hora_envio": int(mensagem["hora_envio"]),
            "clock_requisicao": clock_recebido,
            "clock_servidor_recebimento": self.clock_logico,
        }
        self.mensagens_recebidas.append(evento)

        print(f"Clock logico recebido do cliente: {clock_recebido}")
        print(f"Clock logico do servidor apos recebimento: {self.clock_logico}")
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
        Cria um clock sincronizado usando a media entre a hora do servidor e
        as horas locais dos clientes.
        """
        soma_horarios = self.hora_local
        for evento in self.mensagens_recebidas:
            soma_horarios += int(evento["hora_local_cliente"])

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
            ajuste = self.clock_sincronizado - int(evento["hora_local_cliente"])
            ajustes[str(evento["processo_id"])] = ajuste
            print(
                f"Ajuste necessario para {evento['processo_id']}: "
                f"{ajuste:+.2f}"
            )

        print("-" * 70)
        return ajustes

    def ordenar_eventos_lamport(self) -> List[Evento]:
        """
        Ordena as requisicoes pelo timestamp logico de Lamport.
        Em caso de empate, usa apenas o identificador do processo.
        """
        print("=" * 70)
        print("ORDENACAO DAS REQUISICOES PELO CLOCK LOGICO DE LAMPORT")
        print("=" * 70)

        eventos_ordenados = sorted(
            self.mensagens_recebidas,
            key=lambda evento: (
                int(evento["clock_requisicao"]),
                str(evento["processo_id"]),
            ),
        )

        for posicao, evento in enumerate(eventos_ordenados, start=1):
            print(
                f"{posicao}o lugar -> {evento['processo_id']} | "
                f"C(req) = {evento['clock_requisicao']} | "
                f"Hora fisica observada = {evento['hora_envio']}"
            )

        print("-" * 70)
        return eventos_ordenados

    def controlar_recurso_compartilhado(
        self, eventos_ordenados: List[Evento], clientes: Dict[str, Cliente]
    ) -> None:
        """
        Concede acesso ao recurso compartilhado respeitando a fila de Lamport.
        O tempo fisico eh apenas ilustrativo; a decisao usa clock logico.
        """
        print("=" * 70)
        print("ACESSO AO RECURSO COMPARTILHADO")
        print("=" * 70)
        print("Fila ordenada por (clock logico, processo_id).")
        print("Cada concessao e liberacao atualiza os clocks conforme Lamport.")
        print("-" * 70)

        ordem_final: List[str] = []

        for evento in eventos_ordenados:
            processo_id = str(evento["processo_id"])
            cliente = clientes[processo_id]

            print(f"{processo_id} aguardando liberacao do recurso compartilhado...")
            self.clock_logico += 1
            print(
                f"Servidor concede acesso a {processo_id} "
                f"com clock logico {self.clock_logico}."
            )
            cliente.receber_concessao(self.clock_logico)
            print(f"{processo_id} entrou na regiao critica.")
            print(f"{processo_id} esta utilizando o recurso compartilhado.")

            liberacao = cliente.liberar_recurso()
            self.receber_liberacao(liberacao)

            print(f"{processo_id} saiu da regiao critica.")
            print("-" * 70)
            ordem_final.append(processo_id)

        print("Ordem final de acesso ao recurso compartilhado:")
        print(" -> ".join(ordem_final))
        print("=" * 70)

    def receber_liberacao(self, mensagem: Evento) -> None:
        """Atualiza o clock do servidor ao receber a liberacao do cliente."""
        processo_id = str(mensagem["processo_id"])
        clock_recebido = int(mensagem["clock_liberacao"])
        self.clock_logico = max(self.clock_logico, clock_recebido) + 1
        print(f"Servidor registrou a liberacao de {processo_id}.")
        print(f"Clock logico do servidor apos liberacao: {self.clock_logico}")


def criar_clientes(configuracoes: List[ClienteConfig]) -> List[Cliente]:
    """Monta os clientes a partir da configuracao do cenario."""
    return [
        Cliente(
            processo_id=str(config["processo_id"]),
            hora_local=int(config["hora_local"]),
            instante_envio=int(config["instante_envio"]),
            clock_inicial=int(config.get("clock_inicial", 0)),
        )
        for config in configuracoes
    ]


def exibir_resumo_cenario(titulo: str, descricao: str) -> None:
    """Apresenta o que o cenario quer demonstrar."""
    print()
    print("#" * 70)
    print(titulo)
    print(descricao)
    print("#" * 70)


def simular_cenario(
    titulo: str, descricao: str, configuracoes_clientes: List[ClienteConfig]
) -> None:
    """Executa um cenario isolado de ordenacao de Lamport."""
    exibir_resumo_cenario(titulo, descricao)

    servidor = Servidor(hora_local=100)
    clientes_lista = criar_clientes(configuracoes_clientes)
    clientes = {cliente.processo_id: cliente for cliente in clientes_lista}

    print("Clientes criados com horarios locais, tempos fisicos e clocks iniciais.")
    print("Servidor pronto para receber as requisicoes.")
    print("-" * 70)

    for cliente in clientes_lista:
        mensagem = cliente.enviar_requisicao()
        servidor.receber_requisicao(mensagem)

    servidor.exibir_horarios()
    servidor.sincronizar_clocks()
    eventos_ordenados = servidor.ordenar_eventos_lamport()
    servidor.controlar_recurso_compartilhado(eventos_ordenados, clientes)


def simular_sistema_distribuido() -> None:
    """Executa varios cenarios para mostrar todos os casos principais."""
    print("=" * 70)
    print("SIMULACAO DE ORDENACAO DE LAMPORT EM VARIOS CENARIOS")
    print("=" * 70)

    cenarios = [
        (
            "CENARIO 1 - EMPATE TOTAL NO CLOCK LOGICO",
            "Todos pedem com o mesmo clock. A ordem usa apenas processo_id.",
            [
                {"processo_id": "P1", "hora_local": 95, "instante_envio": 5},
                {"processo_id": "P2", "hora_local": 102, "instante_envio": 2},
                {"processo_id": "P3", "hora_local": 98, "instante_envio": 8},
            ],
        ),
        (
            "CENARIO 2 - CLOCKS LOGICOS DIFERENTES",
            "A ordem muda porque os clocks das requisicoes sao diferentes.",
            [
                {
                    "processo_id": "P1",
                    "hora_local": 95,
                    "instante_envio": 5,
                    "clock_inicial": 4,
                },
                {
                    "processo_id": "P2",
                    "hora_local": 102,
                    "instante_envio": 2,
                    "clock_inicial": 0,
                },
                {
                    "processo_id": "P3",
                    "hora_local": 98,
                    "instante_envio": 8,
                    "clock_inicial": 2,
                },
            ],
        ),
        (
            "CENARIO 3 - TEMPO FISICO ANTECIPADO, MAS ORDEM LOGICA DEPOIS",
            "P2 envia antes no tempo fisico, mas P1 tem clock logico menor e entra antes.",
            [
                {
                    "processo_id": "P1",
                    "hora_local": 95,
                    "instante_envio": 9,
                    "clock_inicial": 0,
                },
                {
                    "processo_id": "P2",
                    "hora_local": 102,
                    "instante_envio": 1,
                    "clock_inicial": 5,
                },
                {
                    "processo_id": "P3",
                    "hora_local": 98,
                    "instante_envio": 3,
                    "clock_inicial": 2,
                },
            ],
        ),
        (
            "CENARIO 4 - EMPATE PARCIAL ENTRE DOIS PROCESSOS",
            "P1 e P3 empatam no clock e o desempate entre eles usa processo_id.",
            [
                {
                    "processo_id": "P1",
                    "hora_local": 95,
                    "instante_envio": 7,
                    "clock_inicial": 2,
                },
                {
                    "processo_id": "P2",
                    "hora_local": 102,
                    "instante_envio": 4,
                    "clock_inicial": 0,
                },
                {
                    "processo_id": "P3",
                    "hora_local": 98,
                    "instante_envio": 1,
                    "clock_inicial": 2,
                },
            ],
        ),
    ]

    for titulo, descricao, configuracoes_clientes in cenarios:
        simular_cenario(titulo, descricao, configuracoes_clientes)


if __name__ == "__main__":
    simular_sistema_distribuido()
