"""
Rede de Acesso SP - Módulo de Grafo
==========================
Classe principal para construção e manipulação do grafo
das UBSs de São Paulo usando NetworkX.

Integrantes:
- Lucas Fernandes de Camargo — RA 10419400
- Lendy Naiara Carpio Pacheco — RA 10428525
- Anna Luiza Stella Santos — RA 10417401

Histórico de alterações:
- 2026-02-12: Grupa Rede de Acesso SP - implementação do grafo de UBSs.
- 2026-05-19: Codex - revisão do cabeçalho para o padrão da Parte 3.

Implementa:
- Construção do grafo a partir de dados JSON
- Algoritmo de Dijkstra (menor caminho)
- BFS (busca em largura)
- Cálculo de centralidade
- Busca da referência de serviço de saúde mais próxima
"""

import json
import math
from pathlib import Path
from collections import deque

import networkx as nx


class GrafoSP:
    """
    Grafo das UBSs de São Paulo.

    Modela UBSs reais como vértices e utiliza conexões por proximidade
    geográfica como arestas ponderadas pela distância em km.
    """

    def __init__(self, data_dir: str | Path = "data"):
        """
        Inicializa o grafo carregando dados do diretório especificado.

        Args:
            data_dir: Caminho para o diretório com os arquivos JSON.
        """
        self.data_dir = Path(data_dir)
        self.G = nx.Graph()
        self.ubs: dict[int, dict] = {}
        self.distritos: dict[int, dict] = {}
        self.distritos_base: dict[int, dict] = {}
        self.servicos: list[dict] = []
        self.servicos_por_distrito: dict[int, list[dict]] = {}
        self.servicos_por_tipo: dict[str, list[dict]] = {}
        self.vertices_por_distrito: dict[int, list[int]] = {}

        self._carregar_dados()
        self._construir_grafo()

    # ================================================================
    # Carregamento e Construção
    # ================================================================

    def _carregar_dados(self):
        """Carrega os dados dos arquivos JSON."""
        vertices_path = self.data_dir / "ubs_vertices.json"
        if not vertices_path.exists():
            vertices_path = self.data_dir / "distritos.json"

        with open(vertices_path, "r", encoding="utf-8") as f:
            lista_ubs = json.load(f)
        self.ubs = {int(d["id"]): d for d in lista_ubs}

        # Alias de compatibilidade: várias telas/métricas ainda iteram por
        # grafo.distritos, mas o conteúdo agora são UBSs.
        self.distritos = self.ubs

        distritos_path = self.data_dir / "distritos.json"
        if distritos_path.exists():
            with open(distritos_path, "r", encoding="utf-8") as f:
                lista_distritos_base = json.load(f)
            self.distritos_base = {
                int(d["id"]): d
                for d in lista_distritos_base
            }

        # Adjacências
        with open(self.data_dir / "adjacencias.json", "r", encoding="utf-8") as f:
            self.adjacencias = json.load(f)

        # Serviços
        with open(self.data_dir / "servicos.json", "r", encoding="utf-8") as f:
            servicos_brutos = json.load(f)

        # Normalização e filtro de tipos permitidos
        # Regra do projeto: apenas UBS, UPA e Hospital SUS
        tipos_permitidos = {"ubs", "upa", "hospital_sus"}
        self.servicos = []
        for s in servicos_brutos:
            tipo = str(s.get("tipo", "")).strip().lower()

            # Compatibilidade com datasets legados
            if tipo == "hospital":
                tipo = "hospital_sus"

            if tipo not in tipos_permitidos:
                continue

            s_norm = dict(s)
            s_norm["tipo"] = tipo
            if "distrito_id" in s_norm:
                s_norm["distrito_id"] = int(s_norm["distrito_id"])
            if s_norm.get("vertex_id") is not None:
                s_norm["vertex_id"] = int(s_norm["vertex_id"])
            self.servicos.append(s_norm)

        # Indexar UBSs por distrito real
        self.vertices_por_distrito = {}
        for vid, ubs in self.ubs.items():
            did = int(ubs.get("distrito_id", vid))
            self.vertices_por_distrito.setdefault(did, []).append(vid)

        # Indexar serviços por distrito
        self.servicos_por_distrito = {}
        for s in self.servicos:
            did = int(s["distrito_id"])
            self.servicos_por_distrito.setdefault(did, []).append(s)

        # Indexar serviços por tipo
        self.servicos_por_tipo = {}
        for s in self.servicos:
            tipo = s["tipo"]
            if tipo not in self.servicos_por_tipo:
                self.servicos_por_tipo[tipo] = []
            self.servicos_por_tipo[tipo].append(s)

    def _construir_grafo(self):
        """Constrói o grafo NetworkX a partir dos dados carregados."""
        # Adicionar vértices (UBSs)
        for did, d in self.ubs.items():
            self.G.add_node(
                did,
                **d,
            )

        # Adicionar arestas (adjacências)
        for adj in self.adjacencias:
            origem = int(adj.get("origem_id", adj.get("distrito1_id")))
            destino = int(adj.get("destino_id", adj.get("distrito2_id")))
            if origem not in self.ubs or destino not in self.ubs:
                continue
            self.G.add_edge(
                origem,
                destino,
                weight=float(adj["distancia_km"])
            )

    # ================================================================
    # Algoritmos de Grafos
    # ================================================================

    def dijkstra(self, origem_id: int, destino_id: int) -> tuple[float, list[int]]:
        """
        Calcula o menor caminho entre duas UBSs usando Dijkstra.

        Args:
            origem_id: ID da UBS de origem.
            destino_id: ID da UBS de destino.

        Returns:
            Tupla (distância_total_km, lista_de_ids_no_caminho).
            Retorna (inf, []) se não houver caminho.
        """
        try:
            distancia = nx.dijkstra_path_length(
                self.G, origem_id, destino_id, weight="weight"
            )
            caminho = nx.dijkstra_path(
                self.G, origem_id, destino_id, weight="weight"
            )
            return round(distancia, 2), caminho
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return float("inf"), []

    def dijkstra_todos(self, origem_id: int) -> dict[int, float]:
        """
        Calcula a distância mínima de uma UBS para todas as outras.

        Args:
            origem_id: ID da UBS de origem.

        Returns:
            Dicionário {ubs_id: distância_km}.
        """
        try:
            return dict(nx.single_source_dijkstra_path_length(
                self.G, origem_id, weight="weight"
            ))
        except nx.NodeNotFound:
            return {}

    def bfs(self, origem_id: int, max_profundidade: int | None = None) -> dict[int, int]:
        """
        Executa BFS a partir de uma UBS, retornando a profundidade de cada nó.

        Args:
            origem_id: ID da UBS de origem.
            max_profundidade: Profundidade máxima (None = sem limite).

        Returns:
            Dicionário {ubs_id: profundidade (nº de saltos)}.
        """
        visitados = {origem_id: 0}
        fila = deque([origem_id])

        while fila:
            atual = fila.popleft()
            profundidade_atual = visitados[atual]

            if max_profundidade is not None and profundidade_atual >= max_profundidade:
                continue

            for vizinho in self.G.neighbors(atual):
                if vizinho not in visitados:
                    visitados[vizinho] = profundidade_atual + 1
                    fila.append(vizinho)

        return visitados

    @staticmethod
    def distancia_geografica_km(a: dict, b: dict) -> float:
        """Distância geográfica aproximada entre duas entidades com lat/lon."""
        raio_terra_km = 6371.0
        lat1, lon1 = float(a["lat"]), float(a["lon"])
        lat2, lon2 = float(b["lat"]), float(b["lon"])
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        h = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        return 2 * raio_terra_km * math.atan2(math.sqrt(h), math.sqrt(1 - h))

    def _servico_da_ubs(self, ubs_id: int) -> dict:
        """Monta uma referência de serviço para a própria UBS selecionada."""
        ubs = self.ubs[ubs_id]
        return {
            "id": ubs.get("servico_id", ubs_id),
            "nome": ubs["nome"],
            "tipo": "ubs",
            "vertex_id": ubs_id,
            "distrito_id": int(ubs.get("distrito_id", ubs_id)),
            "distrito": ubs.get("distrito", ""),
            "zona": ubs.get("zona", ""),
            "lat": ubs.get("lat"),
            "lon": ubs.get("lon"),
        }

    def _ancora_servico(self, servico: dict) -> tuple[int | None, float]:
        """
        Retorna a UBS da rede que representa o serviço e o deslocamento extra.

        Hospital/UPA não são vértices do grafo. Para comparar acesso no grafo
        de UBSs, cada serviço é ancorado na UBS mais próxima de sua coordenada.
        """
        vertex_id = servico.get("vertex_id")
        if vertex_id is not None and int(vertex_id) in self.ubs:
            return int(vertex_id), 0.0

        if "lat" not in servico or "lon" not in servico:
            candidatos = self.vertices_por_distrito.get(int(servico["distrito_id"]), [])
            if candidatos:
                return candidatos[0], 0.0
            return None, float("inf")

        melhor_id: int | None = None
        menor_dist = float("inf")
        for vid, ubs in self.ubs.items():
            dist = self.distancia_geografica_km(ubs, servico)
            if dist < menor_dist:
                menor_dist = dist
                melhor_id = vid

        return melhor_id, menor_dist

    def servico_mais_proximo(
        self, distrito_id: int, tipo_servico: str
    ) -> tuple[dict | None, float, list[int]]:
        """
        Encontra a referência de serviço de saúde mais próxima de uma UBS.

        Args:
            distrito_id: ID da UBS de origem.
            tipo_servico: Tipo de serviço ('ubs', 'upa' ou 'hospital_sus').

        Returns:
            Tupla (servico, distância_km, caminho).
            Retorna (None, inf, []) se não houver serviço acessível.
        """
        if distrito_id not in self.ubs:
            return None, float("inf"), []

        if tipo_servico == "ubs":
            return self._servico_da_ubs(distrito_id), 0.0, [distrito_id]

        servicos_tipo = self.servicos_por_tipo.get(tipo_servico, [])
        if not servicos_tipo:
            return None, float("inf"), []

        distancias = self.dijkstra_todos(distrito_id)

        menor_dist = float("inf")
        melhor_servico: dict | None = None
        melhor_vertice: int | None = None

        for servico in servicos_tipo:
            vertice_ancora, deslocamento_extra = self._ancora_servico(servico)
            if vertice_ancora is None or vertice_ancora not in distancias:
                continue

            distancia_total = distancias[vertice_ancora] + deslocamento_extra
            if distancia_total < menor_dist:
                menor_dist = distancia_total
                melhor_servico = servico
                melhor_vertice = vertice_ancora

        if melhor_servico is None or melhor_vertice is None:
            return None, float("inf"), []

        if melhor_vertice == distrito_id:
            caminho = [distrito_id]
        else:
            _, caminho = self.dijkstra(distrito_id, melhor_vertice)

        return melhor_servico, round(menor_dist, 2), caminho

    # ================================================================
    # Métricas de Centralidade e Grau
    # ================================================================

    def grau_vertices(self) -> dict[int, int]:
        """Retorna o grau de cada vértice (número de conexões)."""
        return dict(self.G.degree())

    def centralidade_grau(self) -> dict[int, float]:
        """Calcula a centralidade de grau de cada vértice."""
        return nx.degree_centrality(self.G)

    def centralidade_proximidade(self) -> dict[int, float]:
        """Calcula a centralidade de proximidade (closeness) de cada vértice."""
        return nx.closeness_centrality(self.G, distance="weight")

    def centralidade_intermediacao(self) -> dict[int, float]:
        """Calcula a centralidade de intermediação (betweenness) de cada vértice."""
        return nx.betweenness_centrality(self.G, weight="weight")

    # ================================================================
    # Estatísticas do Grafo
    # ================================================================

    def estatisticas(self) -> dict:
        """Retorna estatísticas gerais do grafo."""
        graus = [d for _, d in self.G.degree()]
        return {
            "num_vertices": self.G.number_of_nodes(),
            "num_arestas": self.G.number_of_edges(),
            "grau_medio": round(sum(graus) / len(graus), 2) if graus else 0,
            "grau_maximo": max(graus) if graus else 0,
            "grau_minimo": min(graus) if graus else 0,
            "eh_conexo": nx.is_connected(self.G) if self.G.number_of_nodes() else False,
            "num_componentes": nx.number_connected_components(self.G) if self.G.number_of_nodes() else 0,
            "densidade": round(nx.density(self.G), 4),
        }

    # ================================================================
    # Utilidades
    # ================================================================

    def get_posicoes(self) -> dict[int, tuple[float, float]]:
        """Retorna posições (lon, lat) para visualização do grafo."""
        return {
            did: (d["lon"], d["lat"])
            for did, d in self.distritos.items()
        }

    def get_nome(self, distrito_id: int) -> str:
        """Retorna o nome de uma UBS pelo ID."""
        return self.distritos.get(distrito_id, {}).get("nome", "Desconhecido")

    def get_nomes_ordenados(self) -> list[tuple[int, str]]:
        """Retorna lista de (id, nome) de UBSs ordenada por nome."""
        return sorted(
            [(did, d["nome"]) for did, d in self.distritos.items()],
            key=lambda x: x[1]
        )

    def get_tipos_servico(self) -> list[str]:
        """Retorna os tipos de serviço disponíveis."""
        return sorted(self.servicos_por_tipo.keys())

    def contar_servicos_distrito(self, distrito_id: int) -> dict[str, int]:
        """Conta os serviços por tipo no distrito real da UBS informada."""
        distrito_real_id = int(
            self.ubs.get(distrito_id, {}).get("distrito_id", distrito_id)
        )
        contagem = {}
        for s in self.servicos_por_distrito.get(distrito_real_id, []):
            contagem[s["tipo"]] = contagem.get(s["tipo"], 0) + 1
        return contagem

    def get_distrito_base(self, distrito_id: int) -> dict:
        """Retorna metadados do distrito real, quando disponíveis."""
        return self.distritos_base.get(distrito_id, {})
