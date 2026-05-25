"""
Rede de Acesso SP - Módulo de Métricas de Cobertura Territorial
======================================================
Calcula métricas de cobertura territorial em saúde baseadas
na estrutura de grafos de UBSs de São Paulo.

Integrantes:
- Lucas Fernandes de Camargo — RA 10419400
- Lendy Naiara Carpio Pacheco — RA 10428525
- Anna Luiza Stella Santos — RA 10417401

Histórico de alterações:
- 2026-02-12: Grupa Rede de Acesso SP - implementação das métricas.
- 2026-05-19: Codex - revisão do cabeçalho para o padrão da Parte 3.

Métricas disponíveis:
- Score de cobertura por distrito
- Ranking de cobertura
- Média da cidade
- Identificação de distritos com menor cobertura
"""

from __future__ import annotations

import pandas as pd
from src.grafo import GrafoSP


class MetricasAcessibilidade:
    """
    Calcula métricas de cobertura territorial para UBSs de São Paulo.

    A leitura principal do projeto é a pressão territorial:
    quanto menor a população residente estimada na área de abrangência da
    UBS, menor sua demanda potencial territorial no recorte analisado.

    A formula ideal também consideraria capacidade ou número de equipes,
    mas essa variável não está disponível publicamente de forma associável
    às unidades do recorte. Assim, cada UBS é tratada como uma unidade de
    capacidade comparável para fins acadêmicos.
    """

    def __init__(self, grafo: GrafoSP):
        """
        Inicializa com uma instância do grafo.

        Args:
            grafo: Instância de GrafoSP já construída.
        """
        self.grafo = grafo

    def _qtd_ubs_no_distrito_real(self, distrito_real_id: int) -> int:
        """Conta registros de UBS/equipes no distrito real informado."""
        qtd = sum(
            1
            for servico in self.grafo.servicos_por_distrito.get(distrito_real_id, [])
            if servico.get("tipo") == "ubs"
        )
        if qtd == 0:
            qtd = len(self.grafo.vertices_por_distrito.get(distrito_real_id, []))
        return qtd

    @staticmethod
    def _score_por_pressao(pressao: float, menor: float, maior: float) -> float:
        """Converte população de abrangência em índice 0-100 no recorte."""
        if pressao == float("inf"):
            return 0.0
        if maior <= menor:
            return 100.0
        score = ((maior - pressao) / (maior - menor)) * 100
        return round(max(0.0, min(100.0, score)), 1)

    def ranking_cobertura_ubs(self) -> pd.DataFrame:
        """
        Ranking realista de cobertura para o grafo de UBSs.

        A cobertura é calculada por pressão territorial estimada:
        população residente na área de abrangência da UBS (AAUBS).
        Quanto menor a população atribuída à área, menor a demanda
        potencial relativa, sob a hipótese de capacidades comparáveis.
        """
        centralidade = self.grafo.centralidade_proximidade()
        dados = []

        for ubs_id, ubs in self.grafo.distritos.items():
            distrito_real_id = int(ubs.get("distrito_id", ubs_id))
            qtd_ubs = self._qtd_ubs_no_distrito_real(distrito_real_id)
            populacao = int(float(ubs.get("populacao", 0) or 0))
            populacao_abrangencia = populacao if populacao > 0 else float("inf")
            cobertura_10_mil = (
                (1 / populacao) * 10_000
                if populacao > 0
                else 0.0
            )

            dados.append({
                "distrito_id": ubs_id,
                "ubs": ubs["nome"],
                "distrito": ubs.get("distrito", "N/D"),
                "bairro": ubs.get("bairro", ubs.get("distrito", "N/D")),
                "zona": ubs.get("zona", "N/D"),
                "subprefeitura": ubs.get("subprefeitura", "N/D"),
                "populacao": populacao,
                "populacao_distrito": int(float(ubs.get("populacao_distrito", 0) or 0)),
                "qtd_ubs_distrito": qtd_ubs,
                "populacao_abrangencia": populacao_abrangencia,
                "unidade_por_10_mil_abrangencia": cobertura_10_mil,
                "conexoes": self.grafo.G.degree(ubs_id),
                "centralidade": centralidade.get(ubs_id, 0.0),
            })

        pressoes = [
            item["populacao_abrangencia"]
            for item in dados
            if item["populacao_abrangencia"] < float("inf")
        ]
        menor = min(pressoes) if pressoes else 0.0
        maior = max(pressoes) if pressoes else 0.0

        for item in dados:
            item["score"] = self._score_por_pressao(
                item["populacao_abrangencia"],
                menor,
                maior,
            )
            if item["populacao_abrangencia"] < float("inf"):
                item["populacao_abrangencia"] = round(item["populacao_abrangencia"], 1)
            item["unidade_por_10_mil_abrangencia"] = round(item["unidade_por_10_mil_abrangencia"], 2)
            item["centralidade"] = round(item["centralidade"], 3)

        df = pd.DataFrame(dados)
        df = df.sort_values(
            ["populacao_abrangencia", "conexoes"],
            ascending=[True, False],
        )
        df["posicao"] = range(1, len(df) + 1)

        colunas = [
            "posicao", "distrito_id", "ubs", "distrito", "bairro", "zona",
            "subprefeitura", "populacao", "populacao_distrito", "qtd_ubs_distrito",
            "populacao_abrangencia", "unidade_por_10_mil_abrangencia", "conexoes",
            "centralidade", "score",
        ]
        return df[colunas].reset_index(drop=True)

    def resumo_cobertura_ubs(self) -> dict:
        """Resumo da população estimada das áreas de abrangência analisadas."""
        df = self.ranking_cobertura_ubs()
        pressoes = df["populacao_abrangencia"].astype(float)

        return {
            "total_ubs": int(len(df)),
            "media_populacao_abrangencia": round(float(pressoes.mean()), 1),
            "mediana_populacao_abrangencia": round(float(pressoes.median()), 1),
            "melhor_pressao": round(float(pressoes.min()), 1),
            "pior_pressao": round(float(pressoes.max()), 1),
            "score_medio": round(float(df["score"].mean()), 1),
            "media_unidade_por_10_mil_abrangencia": round(float(df["unidade_por_10_mil_abrangencia"].mean()), 2),
        }

    def analisar_ubs(self, ubs_id: int) -> dict:
        """Retorna a análise de cobertura da UBS selecionada."""
        df = self.ranking_cobertura_ubs()
        linha = df[df["distrito_id"] == ubs_id].iloc[0].to_dict()
        resumo = self.resumo_cobertura_ubs()

        pressoes = df["populacao_abrangencia"].astype(float)
        q1 = float(pressoes.quantile(0.25))
        q3 = float(pressoes.quantile(0.75))
        pressao = float(linha["populacao_abrangencia"])

        if pressao <= q1:
            classificacao = "Boa cobertura"
        elif pressao >= q3:
            classificacao = "Alta pressão"
        else:
            classificacao = "Cobertura intermediária"

        linha["diferenca_media_pressao"] = round(
            pressao - resumo["media_populacao_abrangencia"],
            1,
        )
        linha["classificacao"] = classificacao
        linha["total_ubs"] = resumo["total_ubs"]
        linha["media_populacao_abrangencia"] = resumo["media_populacao_abrangencia"]
        linha["mediana_populacao_abrangencia"] = resumo["mediana_populacao_abrangencia"]
        linha["score_medio"] = resumo["score_medio"]
        return linha

    def ubs_maior_pressao(self, percentil: float = 0.8) -> list[dict]:
        """Lista UBSs no pior grupo de pressão territorial."""
        df = self.ranking_cobertura_ubs()
        n = max(1, int(len(df) * (1 - percentil)))
        return (
            df.sort_values("populacao_abrangencia", ascending=False)
            .head(n)
            .to_dict("records")
        )

    def distancia_servico_mais_proximo(self, tipo_servico: str) -> dict[int, float]:
        """
        Calcula a distância de cada distrito ao serviço mais próximo.

        Args:
            tipo_servico: Tipo de serviço ('ubs', 'upa' ou 'hospital_sus').

        Returns:
            Dicionário {distrito_id: distância_km}.
        """
        distancias = {}
        for did in self.grafo.distritos:
            _, dist, _ = self.grafo.servico_mais_proximo(did, tipo_servico)
            distancias[did] = dist
        return distancias

    def score_acessibilidade(self, distrito_id: int, tipo_servico: str) -> float:
        """
        Calcula o score de acessibilidade de um distrito (0 a 100).

        Score 100 = serviço no próprio distrito.
        Score diminui proporcionalmente com a distância.

        Args:
            distrito_id: ID do distrito.
            tipo_servico: Tipo de serviço ('ubs', 'upa' ou 'hospital_sus').

        Returns:
            Score de 0 a 100.
        """
        _, distancia, _ = self.grafo.servico_mais_proximo(distrito_id, tipo_servico)

        if distancia == 0:
            return 100.0
        if distancia == float("inf"):
            return 0.0

        # Score inversamente proporcional à distância
        # Referência: 20 km = score 0
        max_dist = 20.0
        score = max(0, (1 - distancia / max_dist)) * 100
        return round(score, 1)

    def ranking(self, tipo_servico: str) -> pd.DataFrame:
        """
        Gera ranking de distritos por cobertura territorial para um tipo de serviço.

        Args:
            tipo_servico: Tipo de serviço.

        Returns:
            DataFrame com colunas: posição, distrito, zona, distância, score.
        """
        dados = []
        for did, d in self.grafo.distritos.items():
            _, dist, _ = self.grafo.servico_mais_proximo(did, tipo_servico)
            score = self.score_acessibilidade(did, tipo_servico)
            dados.append({
                "distrito_id": did,
                "distrito": d["nome"],
                "zona": d["zona"],
                "populacao": d["populacao"],
                "distancia_km": dist,
                "score": score,
            })

        df = pd.DataFrame(dados)
        df = df.sort_values("distancia_km", ascending=True)
        df["posicao"] = range(1, len(df) + 1)
        df = df[["posicao", "distrito_id", "distrito", "zona",
                  "populacao", "distancia_km", "score"]]
        return df.reset_index(drop=True)

    def media_cidade(self, tipo_servico: str) -> dict:
        """
        Calcula a média de acessibilidade da cidade.

        Args:
            tipo_servico: Tipo de serviço.

        Returns:
            Dicionário com média de distância, score médio, mediana.
        """
        distancias = self.distancia_servico_mais_proximo(tipo_servico)

        # Filtrar infinitos
        dists_finitas = [d for d in distancias.values() if d < float("inf")]

        if not dists_finitas:
            return {"media_distancia": 0, "score_medio": 0, "mediana_distancia": 0}

        dists_finitas.sort()
        n = len(dists_finitas)
        mediana = dists_finitas[n // 2] if n % 2 == 1 else (
            dists_finitas[n // 2 - 1] + dists_finitas[n // 2]) / 2

        scores = [self.score_acessibilidade(did, tipo_servico)
                  for did in distancias]

        return {
            "media_distancia": round(sum(dists_finitas) / n, 2),
            "score_medio": round(sum(scores) / len(scores), 1),
            "mediana_distancia": round(mediana, 2),
            "melhor_distancia": round(min(dists_finitas), 2),
            "pior_distancia": round(max(dists_finitas), 2),
        }

    def distritos_isolados(
        self, tipo_servico: str, percentil: float = 0.8
    ) -> list[dict]:
        """
        Identifica distritos relativamente isolados (distância acima do percentil).

        Args:
            tipo_servico: Tipo de serviço.
            percentil: Percentil de corte (0.8 = top 20% mais distantes).

        Returns:
            Lista de dicionários com informações dos distritos isolados.
        """
        distancias = self.distancia_servico_mais_proximo(tipo_servico)

        # Filtrar infinitos
        dists_finitas = sorted(
            [(did, d) for did, d in distancias.items() if d < float("inf")],
            key=lambda x: x[1],
            reverse=True
        )

        if not dists_finitas:
            return []

        # Corte pelo percentil
        n_isolados = max(1, int(len(dists_finitas) * (1 - percentil)))
        isolados = dists_finitas[:n_isolados]

        resultado = []
        for did, dist in isolados:
            d = self.grafo.distritos[did]
            score = self.score_acessibilidade(did, tipo_servico)
            resultado.append({
                "distrito_id": did,
                "distrito": d["nome"],
                "zona": d["zona"],
                "populacao": d["populacao"],
                "distancia_km": round(dist, 2),
                "score": score,
            })

        return resultado

    def comparar_com_media(self, distrito_id: int, tipo_servico: str) -> dict:
        """
        Compara a acessibilidade de um distrito com a média da cidade.

        Args:
            distrito_id: ID do distrito.
            tipo_servico: Tipo de serviço.

        Returns:
            Dicionário com comparação detalhada.
        """
        _, dist_distrito, _ = self.grafo.servico_mais_proximo(
            distrito_id, tipo_servico
        )
        score_distrito = self.score_acessibilidade(distrito_id, tipo_servico)
        media = self.media_cidade(tipo_servico)

        ranking_df = self.ranking(tipo_servico)
        posicao = ranking_df[
            ranking_df["distrito_id"] == distrito_id
        ]["posicao"].values[0]

        diff_dist = round(dist_distrito - media["media_distancia"], 2)
        diff_score = round(score_distrito - media["score_medio"], 1)

        if diff_dist < -0.5:
            classificacao = "Acima da média"
        elif diff_dist > 0.5:
            classificacao = "Abaixo da média"
        else:
            classificacao = "Na média"

        return {
            "distrito": self.grafo.get_nome(distrito_id),
            "distancia_km": round(dist_distrito, 2),
            "score": score_distrito,
            "posicao_ranking": posicao,
            "total_distritos": len(self.grafo.distritos),
            "media_distancia_cidade": media["media_distancia"],
            "score_medio_cidade": media["score_medio"],
            "diferenca_distancia": diff_dist,
            "diferenca_score": diff_score,
            "classificacao": classificacao,
        }
