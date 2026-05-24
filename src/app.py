"""
Rede de Acesso SP - Interface Interativa com Streamlit
=============================================
Sistema de análise territorial de acesso à saúde nas UBSs
de São Paulo, utilizando modelagem por grafos.

Integrantes:
- Lucas Fernandes de Camargo — RA 10419400
- Lendy Naiara Carpio Pacheco — RA 10428525
- Anna Luiza Stella Santos — RA 10417401

Histórico de alterações:
- 2026-02-12: Grupa Rede de Acesso SP - implementação da interface interativa.
- 2026-05-19: Codex - revisão do cabeçalho para o padrão da Parte 3.

Uso:
    streamlit run app.py
"""

import sys
import json
import importlib
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import unicodedata
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Adicionar a raiz do projeto ao path (para permitir import src.*)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.grafo import GrafoSP
import src.metricas as metricas_mod

metricas_mod = importlib.reload(metricas_mod)
MetricasAcessibilidade = metricas_mod.MetricasAcessibilidade

# ============================================================================
# Configuração da Página
# ============================================================================

st.set_page_config(
    page_title="Rede de Acesso SP - Saúde Territorial",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TEMA_STREAMLIT = getattr(st.context.theme, "type", None)
MODO_ESCURO = TEMA_STREAMLIT == "dark"
MODO_CLARO = not MODO_ESCURO

# CSS customizado
st.markdown("""
<style>
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.85rem;
    }

    h1 {
        letter-spacing: 0;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    h1::after {
        content: "";
        display: block;
        width: 74px;
        height: 3px;
        margin-top: 0.5rem;
        border-radius: 999px;
        background: var(--primary-color);
    }

    h2, h3 {
        letter-spacing: 0;
    }

    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stForm"],
    [data-testid="stExpander"] {
        border-radius: 8px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }

    [data-testid="stForm"] {
        padding: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding-left: 1rem;
        padding-right: 1rem;
        font-weight: 650;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary-color);
    }

    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 0.82rem 0.9rem;
    }

    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    [role="combobox"]:focus-visible {
        outline: 3px solid var(--primary-color);
        outline-offset: 2px;
    }

    .ihc-note {
        border-left: 4px solid var(--primary-color);
        padding: 0.75rem 0.9rem;
        background: var(--secondary-background-color);
        border-radius: 8px;
        margin: 0.35rem 0 0.6rem 0;
    }

    .ihc-note strong {
        color: var(--text-color);
    }

    .ihc-note span {
        color: var(--text-color);
        opacity: 0.76;
    }

    .stFormSubmitButton > button,
    .stButton > button[kind="primary"] {
        border-radius: 8px;
        background: var(--primary-color);
        border-color: var(--primary-color);
        color: #ffffff;
        font-weight: 700;
    }

    .stFormSubmitButton > button p,
    .stButton > button[kind="primary"] p {
        color: #ffffff;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 650;
    }

    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Cores por Zona
# ============================================================================

CORES_ZONA = {
    "Centro": "#f97316",
    "Norte": "#38bdf8",
    "Sul": "#22c55e",
    "Leste": "#facc15",
    "Oeste": "#a78bfa",
}

if MODO_CLARO:
    PLOT_BG = "#ffffff"
    PAPER_BG = "#ffffff"
    PLOT_FONT = "#15171c"
    PLOT_MUTED = "#5f6673"
    PLOT_GRID = "#d4d7de"
    ACCENT_BLUE = "#2563eb"
    ACCENT_GREEN = "#15803d"
    ACCENT_AMBER = "#b45309"
    ACCENT_RED = "#dc2626"
    MAP_STYLE = "carto-positron"
    HOVER_BG = "#ffffff"
else:
    PLOT_BG = "#101217"
    PAPER_BG = "#181a20"
    PLOT_FONT = "#f5f5f5"
    PLOT_MUTED = "#b7bbc2"
    PLOT_GRID = "#363a42"
    ACCENT_BLUE = "#4f8cff"
    ACCENT_GREEN = "#37b26c"
    ACCENT_AMBER = "#f5b84b"
    ACCENT_RED = "#ef6b5a"
    HOVER_BG = "#22342b"

MAP_STYLE = "carto-positron"
MAP_BG = "#ffffff"
MAP_FONT = "#1f2937"
MAP_MUTED = "#4b5563"
MAP_HOVER_BG = "#ffffff"

SP_BOUNDS = {
    "lat_min": -24.02,
    "lat_max": -23.35,
    "lon_min": -46.83,
    "lon_max": -46.36,
}

NOMES_SERVICO = {
    "hospital_sus": "Hospital (SUS)",
    "upa": "UPA",
    "ubs": "UBS",
}

RAIO_PADRAO_RECOMENDACAO_KM = 6.0
RAIO_MAXIMO_RECOMENDACAO_KM = 12.0
MIN_OPCOES_RECOMENDACAO = 3
MAX_OPCOES_RECOMENDACAO = 6
CHAVES_BUSCA = [
    "endereco_busca",
    "endereco_confirmado",
    "ubs_recomendada_id",
    "area_zona_ubs",
    "area_distrito_ubs",
    "filtro_distancia_maxima_ubs",
    "filtro_zona_ubs",
    "filtro_distrito_ubs",
    "filtro_mesmo_distrito_ubs",
]


def normalizar_nome(valor: str) -> str:
    texto = str(valor).strip().upper()
    texto = "".join(
        c for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )
    return texto


def titulo_endereco(valor: str) -> str:
    return " ".join(str(valor).replace("  ", " ").strip().title().split())


def formatar_endereco_ubs(endereco: str) -> str:
    """Converte endereço bruto da base para leitura mais natural."""
    texto = str(endereco or "").strip()
    if not texto:
        return ""

    tokens = [t.strip() for t in texto.split(",") if t.strip()]
    if not tokens:
        return texto

    tipos = {
        "R": "R",
        "RUA": "R",
        "AV": "Av",
        "AVENIDA": "Av",
        "PCA": "Praça",
        "PRACA": "Praça",
        "PRACA DA": "Praça da",
        "EST": "Estrada",
        "ESTRADA": "Estrada",
        "TRAV": "Travessa",
    }
    preposicoes = {"DA", "DAS", "DE", "DO", "DOS", "D"}

    numero = ""
    if tokens and re.fullmatch(r"(?i)(s/?n|\d+[a-z]?|\d+\s*[a-z]?)", tokens[-1].strip()):
        numero = tokens.pop().strip().upper().replace("S/N", "s/n")

    tipo_idx = next(
        (idx for idx, token in enumerate(tokens) if normalizar_nome(token) in tipos),
        None,
    )

    if tipo_idx is None:
        logradouro = titulo_endereco(" ".join(tokens))
    else:
        tipo = tipos[normalizar_nome(tokens[tipo_idx])]
        nome_tokens = tokens[:tipo_idx] + tokens[tipo_idx + 1:]
        if nome_tokens and normalizar_nome(nome_tokens[-1]) in preposicoes:
            prep_bruto = normalizar_nome(nome_tokens.pop())
            prep = "d." if prep_bruto == "D" else prep_bruto.lower()
            nome_tokens = [prep, *nome_tokens]
        partes_nome = [
            str(t).lower() if idx == 0 and normalizar_nome(t) in preposicoes else titulo_endereco(t)
            for idx, t in enumerate(nome_tokens)
        ]
        logradouro = " ".join([tipo, *partes_nome]).strip()

    return f"{logradouro}, {numero}" if numero else logradouro


def aplicar_formatacao_enderecos(grafo_obj: GrafoSP) -> None:
    for ubs in grafo_obj.distritos.values():
        endereco_original = ubs.get("endereco", "")
        ubs["endereco_original"] = endereco_original
        ubs["endereco"] = formatar_endereco_ubs(endereco_original)
    for ubs in grafo_obj.ubs.values():
        endereco_original = ubs.get("endereco", "")
        ubs["endereco_original"] = endereco_original
        ubs["endereco"] = formatar_endereco_ubs(endereco_original)


def limpar_estado_busca() -> None:
    for chave in CHAVES_BUSCA:
        st.session_state.pop(chave, None)


def hex_para_rgba(cor_hex: str, alpha: float) -> str:
    cor = cor_hex.lstrip("#")
    if len(cor) != 6:
        return f"rgba(120,120,120,{alpha})"
    r = int(cor[0:2], 16)
    g = int(cor[2:4], 16)
    b = int(cor[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def aplicar_tema_plotly(fig, height: int | None = None):
    """Aplica o tema visual da Rede de Acesso SP aos gráficos Plotly."""
    fig.update_layout(
        template="plotly_white" if MODO_CLARO else "plotly_dark",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=PLOT_FONT, family="Inter, Arial, sans-serif"),
        title_font=dict(color=PLOT_FONT, size=18),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=PLOT_MUTED),
        ),
        hoverlabel=dict(
            bgcolor=HOVER_BG,
            bordercolor=ACCENT_BLUE,
            font_color=PLOT_FONT,
        ),
        margin=dict(l=20, r=18, t=58, b=20),
    )
    fig.update_xaxes(
        gridcolor=PLOT_GRID,
        zerolinecolor=PLOT_GRID,
        linecolor=PLOT_GRID,
        tickfont=dict(color=PLOT_MUTED),
        title_font=dict(color=PLOT_MUTED),
    )
    fig.update_yaxes(
        gridcolor=PLOT_GRID,
        zerolinecolor=PLOT_GRID,
        linecolor=PLOT_GRID,
        tickfont=dict(color=PLOT_MUTED),
        title_font=dict(color=PLOT_MUTED),
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig


def criar_figura_grafo_completo(grafo_obj: GrafoSP):
    """Monta a visualização completa da rede de UBSs."""
    edge_lons: list[float | None] = []
    edge_lats: list[float | None] = []
    for origem, destino in grafo_obj.G.edges():
        u = grafo_obj.distritos[origem]
        v = grafo_obj.distritos[destino]
        edge_lons.extend([u["lon"], v["lon"], None])
        edge_lats.extend([u["lat"], v["lat"], None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_lons,
        y=edge_lats,
        mode="lines",
        line=dict(width=0.7, color="rgba(120, 130, 150, 0.34)"),
        hoverinfo="skip",
        name="Conexões",
    ))

    for zona in sorted({d.get("zona", "N/D") for d in grafo_obj.distritos.values()}):
        ids_zona = [
            did for did, dados in grafo_obj.distritos.items()
            if dados.get("zona", "N/D") == zona
        ]
        fig.add_trace(go.Scatter(
            x=[grafo_obj.distritos[did]["lon"] for did in ids_zona],
            y=[grafo_obj.distritos[did]["lat"] for did in ids_zona],
            mode="markers",
            marker=dict(
                size=[8 + min(8, grafo_obj.G.degree(did)) for did in ids_zona],
                color=CORES_ZONA.get(zona, ACCENT_BLUE),
                line=dict(width=0.8, color="#ffffff"),
                opacity=0.9,
            ),
            customdata=[
                [
                    grafo_obj.get_nome(did),
                    grafo_obj.distritos[did].get("bairro", "N/D"),
                    grafo_obj.distritos[did].get("distrito", "N/D"),
                    grafo_obj.G.degree(did),
                ]
                for did in ids_zona
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>Bairro: %{customdata[1]}"
                "<br>Distrito: %{customdata[2]}"
                "<br>Conexões: %{customdata[3]}"
                "<extra></extra>"
            ),
            name=zona,
        ))

    fig.update_layout(
        title="Grafo completo das 71 UBSs e suas 215 conexões",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        legend_title="Zona",
    )
    return aplicar_tema_plotly(fig, height=520)


def criar_figura_exemplo_recomendacao(grafo_obj: GrafoSP, metricas_obj: MetricasAcessibilidade):
    """Exemplo didático fixo para explicar a recomendação por pressão."""
    exemplo = {
        "label": "Rua Piauí, 144, Higienópolis",
        "lat": -23.5449808,
        "lon": -46.6585176,
    }
    ranking = listar_ubs_por_distancia(grafo_obj, exemplo["lat"], exemplo["lon"])
    ranking = anexar_pressao_ao_ranking(ranking, metricas_obj.ranking_cobertura_ubs())
    raio = calcular_raio_recomendacao(ranking)
    candidatas = [item for item in ranking if item["distancia_km"] <= raio]
    recomendada = ordenar_por_menor_pressao(candidatas)[0] if candidatas else ranking[0]
    ids_exemplo = {
        int(item["id"])
        for item in sorted(candidatas, key=lambda item: item["distancia_km"])[:6]
    }
    ids_exemplo.add(int(recomendada["id"]))

    fig = go.Figure()
    for did in ids_exemplo:
        ubs = grafo_obj.distritos[did]
        fig.add_trace(go.Scattermap(
            lat=[exemplo["lat"], ubs["lat"]],
            lon=[exemplo["lon"], ubs["lon"]],
            mode="lines",
            line=dict(
                color=ACCENT_RED if did == int(recomendada["id"]) else "rgba(90, 100, 115, 0.42)",
                width=4 if did == int(recomendada["id"]) else 1.4,
            ),
            hoverinfo="skip",
            showlegend=False,
        ))

    fig.add_trace(go.Scattermap(
        lat=[grafo_obj.distritos[did]["lat"] for did in ids_exemplo],
        lon=[grafo_obj.distritos[did]["lon"] for did in ids_exemplo],
        mode="markers",
        marker=dict(
            size=[17 if did == int(recomendada["id"]) else 11 for did in ids_exemplo],
            color=[ACCENT_RED if did == int(recomendada["id"]) else ACCENT_AMBER for did in ids_exemplo],
            opacity=0.95,
        ),
        customdata=[
            [
                grafo_obj.get_nome(did),
                grafo_obj.distritos[did].get("endereco", "N/D"),
                grafo_obj.distritos[did].get("bairro", "N/D"),
            ]
            for did in ids_exemplo
        ],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]}<extra></extra>",
        name="UBSs ao redor",
    ))
    fig.add_trace(go.Scattermap(
        lat=[exemplo["lat"]],
        lon=[exemplo["lon"]],
        mode="markers",
        marker=dict(size=16, color=ACCENT_BLUE, opacity=0.96),
        text=[exemplo["label"]],
        hovertemplate="<b>Endereço de exemplo</b><br>%{text}<extra></extra>",
        name="Endereço",
    ))

    fig.update_layout(
        template="plotly_white",
        title=f"Exemplo: {exemplo['label']} -> {grafo_obj.get_nome(int(recomendada['id']))}",
        margin=dict(l=0, r=0, t=44, b=0),
        paper_bgcolor=MAP_BG,
        font=dict(color=MAP_FONT),
        legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="left", x=0.0),
        map=dict(
            style=MAP_STYLE,
            center=dict(lat=exemplo["lat"], lon=exemplo["lon"]),
            zoom=12,
        ),
        height=430,
    )
    return fig, recomendada, raio, len(candidatas)


def area_anel(anel: list[tuple[float, float]]) -> float:
    """Área assinada aproximada de anel (lon/lat)."""
    if len(anel) < 3:
        return 0.0
    a = 0.0
    for i in range(len(anel) - 1):
        x1, y1 = anel[i]
        x2, y2 = anel[i + 1]
        a += (x1 * y2) - (x2 * y1)
    return a / 2.0


def ponto_em_poligono(x: float, y: float, poligono: list[tuple[float, float]]) -> bool:
    """Teste simples de ponto no polígono (ray casting)."""
    dentro = False
    n = len(poligono)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = poligono[i]
        xj, yj = poligono[j]
        cond = ((yi > y) != (yj > y))
        if cond:
            x_inter = (xj - xi) * (y - yi) / ((yj - yi) if (yj - yi) != 0 else 1e-12) + xi
            if x < x_inter:
                dentro = not dentro
        j = i
    return dentro


def ponto_representativo_anel(anel: list[tuple[float, float]]) -> tuple[float, float]:
    """Retorna ponto representativo preferencialmente dentro do anel."""
    if len(anel) < 3:
        return (0.0, 0.0)

    a = area_anel(anel)
    if abs(a) < 1e-12:
        return anel[len(anel) // 2]

    cx_num = 0.0
    cy_num = 0.0
    for i in range(len(anel) - 1):
        x1, y1 = anel[i]
        x2, y2 = anel[i + 1]
        cross = (x1 * y2) - (x2 * y1)
        cx_num += (x1 + x2) * cross
        cy_num += (y1 + y2) * cross

    cx = cx_num / (6.0 * a)
    cy = cy_num / (6.0 * a)

    if ponto_em_poligono(cx, cy, anel):
        return (cx, cy)

    # fallback robusto: ponto de um vértice (sempre no contorno do distrito)
    return anel[len(anel) // 2]


def zoom_por_extensao(lats: list[float], lons: list[float]) -> float:
    """Zoom aproximado para mapa de tiles a partir da extensão lat/lon."""
    if not lats or not lons:
        return 10

    span = max(max(lats) - min(lats), max(lons) - min(lons))
    if span <= 0.015:
        return 14
    if span <= 0.035:
        return 13
    if span <= 0.07:
        return 12
    if span <= 0.14:
        return 11
    if span <= 0.28:
        return 10
    if span <= 0.55:
        return 9
    return 8


def parse_coord_usuario(valor: str) -> tuple[float, float] | None:
    """Aceita coordenadas no formato -23.55, -46.63."""
    texto = str(valor).strip()
    if "," not in texto:
        return None

    partes = [p.strip() for p in texto.split(",")]
    if len(partes) != 2:
        return None

    try:
        lat = float(partes[0])
        lon = float(partes[1])
    except ValueError:
        return None

    if -90 <= lat <= 90 and -180 <= lon <= 180:
        return lat, lon
    return None


def interpretar_endereco_usuario(valor: str) -> dict:
    """Interpreta rua, número e bairro opcional em entradas parecidas com mapas."""
    texto = re.sub(r"\s+", " ", str(valor).strip())
    if not texto:
        return {"original": ""}

    partes = [
        p.strip()
        for p in texto.split(",")
        if p.strip() and normalizar_nome(p.strip()) not in {"SAO PAULO", "SP", "BRASIL", "BRAZIL"}
    ]
    base = texto
    bairro = ""

    if len(partes) >= 3:
        base = f"{partes[0]}, {partes[1]}"
        bairro = partes[2]
    elif len(partes) == 2:
        primeira, segunda = partes
        if re.fullmatch(r"\d+[A-Za-z]?", segunda):
            base = f"{primeira}, {segunda}"
        else:
            base = primeira
            bairro = segunda
    elif partes:
        base = partes[0]

    logradouro = base
    numero = ""
    match_com_numero = re.match(
        r"^(?P<rua>.+?)(?:,?\s+)(?P<num>\d+[A-Za-z]?)(?:\s+(?P<bairro>.+))?$",
        base,
    )
    if match_com_numero:
        logradouro = match_com_numero.group("rua").strip(" ,")
        numero = match_com_numero.group("num").strip()
        bairro = bairro or (match_com_numero.group("bairro") or "").strip()

    return {
        "original": texto,
        "logradouro": logradouro.strip(" ,"),
        "numero": numero,
        "bairro": bairro.strip(" ,"),
    }


def montar_consultas_endereco(endereco: str) -> list[dict[str, str | int]]:
    partes = interpretar_endereco_usuario(endereco)
    logradouro = partes.get("logradouro", "")
    numero = partes.get("numero", "")
    bairro = partes.get("bairro", "")

    consultas: list[dict[str, str | int]] = []

    if logradouro:
        trecho_rua = f"{logradouro}, {numero}" if numero else logradouro
        if bairro:
            consultas.append({
                "q": f"{trecho_rua}, {bairro}, São Paulo, SP, Brasil",
            })
        consultas.append({
            "q": f"{trecho_rua}, São Paulo, SP, Brasil",
        })
        consultas.append({
            "street": f"{numero} {logradouro}".strip(),
            "city": "São Paulo",
            "state": "São Paulo",
            "country": "Brasil",
        })

    consultas.append({
        "q": f"{endereco}, São Paulo, SP, Brasil",
    })

    vistos = set()
    unicas: list[dict[str, str | int]] = []
    for consulta in consultas:
        chave = tuple(sorted((str(k), str(v)) for k, v in consulta.items()))
        if chave not in vistos:
            vistos.add(chave)
            unicas.append(consulta)
    return unicas


def resultado_de_sao_paulo(item: dict) -> bool:
    endereco = item.get("address") or {}
    cidade = (
        endereco.get("city")
        or endereco.get("town")
        or endereco.get("village")
        or endereco.get("municipality")
        or endereco.get("county")
        or ""
    )

    if cidade and normalizar_nome(cidade) != "SAO PAULO":
        return False

    campos = [
        cidade,
        endereco.get("city_district", ""),
        endereco.get("suburb", ""),
        endereco.get("state_district", ""),
        item.get("display_name", ""),
    ]
    return any("SAO PAULO" in normalizar_nome(campo) for campo in campos if campo)


def pontuar_resultado_endereco(item: dict, bairro: str, numero: str) -> int:
    texto = normalizar_nome(" ".join([
        item.get("display_name", ""),
        " ".join(str(v) for v in (item.get("address") or {}).values()),
    ]))
    score = 0
    if bairro and normalizar_nome(bairro) in texto:
        score += 40
    if numero and numero in texto:
        score += 15
    if "SAO PAULO" in texto:
        score += 10
    return score


def dentro_de_sao_paulo_aproximado(lat: float, lon: float) -> bool:
    """Mantém buscas e recomendações dentro do município de São Paulo."""
    dentro_retangulo = (
        SP_BOUNDS["lat_min"] <= lat <= SP_BOUNDS["lat_max"]
        and SP_BOUNDS["lon_min"] <= lon <= SP_BOUNDS["lon_max"]
    )
    if not dentro_retangulo:
        return False

    try:
        aneis = carregar_aneis_municipio_sp()
    except Exception:
        aneis = []

    if not aneis:
        return True

    return any(ponto_em_poligono(lon, lat, anel) for anel in aneis)


def buscar_nominatim(params_extra: dict[str, str | int]) -> list[dict]:
    params = {
        "format": "json",
        "limit": 8,
        "countrycodes": "br",
        "addressdetails": 1,
        "viewbox": (
            f"{SP_BOUNDS['lon_min']},{SP_BOUNDS['lat_max']},"
            f"{SP_BOUNDS['lon_max']},{SP_BOUNDS['lat_min']}"
        ),
        "bounded": 1,
    }
    params.update(params_extra)
    url = f"https://nominatim.openstreetmap.org/search?{urlencode(params)}"
    req = Request(
        url,
        headers={
            "User-Agent": "RedeAcessoSP/1.0 (academic project)",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return []

    return payload if isinstance(payload, list) else []


@st.cache_data(ttl=60 * 60 * 24)
def geocodificar_endereco(endereco: str) -> dict | None:
    """
    Geocodifica endereço usando Nominatim/OpenStreetMap.

    A busca é limitada a São Paulo para evitar resultados em outras cidades
    quando o usuário digita apenas rua e número.
    """
    endereco = str(endereco).strip()
    if not endereco:
        return None

    coords = parse_coord_usuario(endereco)
    if coords:
        lat, lon = coords
        if not dentro_de_sao_paulo_aproximado(lat, lon):
            return None
        return {
            "lat": lat,
            "lon": lon,
            "label": f"{lat:.6f}, {lon:.6f}",
        }

    partes = interpretar_endereco_usuario(endereco)
    candidatos = []
    for consulta in montar_consultas_endereco(endereco):
        for item in buscar_nominatim(consulta):
            try:
                lat = float(item["lat"])
                lon = float(item["lon"])
            except (KeyError, TypeError, ValueError):
                continue

            if not dentro_de_sao_paulo_aproximado(lat, lon):
                continue
            if not resultado_de_sao_paulo(item):
                continue

            candidatos.append((
                pontuar_resultado_endereco(
                    item,
                    partes.get("bairro", ""),
                    partes.get("numero", ""),
                ),
                item,
                lat,
                lon,
            ))

    if not candidatos:
        return None

    _, item, lat, lon = max(candidatos, key=lambda c: c[0])
    return {
        "lat": lat,
        "lon": lon,
        "label": item.get("display_name", endereco),
    }


def ubs_mais_proxima(grafo: GrafoSP, lat: float, lon: float) -> tuple[int, float]:
    ponto = {"lat": lat, "lon": lon}
    melhor_id = -1
    menor_dist = float("inf")
    for vid, ubs in grafo.distritos.items():
        dist = GrafoSP.distancia_geografica_km(ponto, ubs)
        if dist < menor_dist:
            menor_dist = dist
            melhor_id = vid
    return melhor_id, round(menor_dist, 2)


def listar_ubs_por_distancia(grafo: GrafoSP, lat: float, lon: float) -> list[dict]:
    """Retorna todas as UBSs ordenadas pela distância geográfica aproximada."""
    ponto = {"lat": lat, "lon": lon}
    ranking = []

    for vid, ubs in grafo.distritos.items():
        if not dentro_de_sao_paulo_aproximado(float(ubs["lat"]), float(ubs["lon"])):
            continue
        dist = GrafoSP.distancia_geografica_km(ponto, ubs)
        ranking.append({
            "id": vid,
            "nome": ubs["nome"],
            "distrito": ubs.get("distrito", "N/D"),
            "bairro": ubs.get("bairro", ubs.get("distrito", "N/D")),
            "zona": ubs.get("zona", "N/D"),
            "distancia_km": round(dist, 2),
        })

    return sorted(ranking, key=lambda item: item["distancia_km"])


def listar_ubs_por_area(
    grafo: GrafoSP,
    zona: str = "Todas",
    distrito: str = "Todos",
) -> list[dict]:
    """Retorna UBSs filtradas por zona e/ou distrito."""
    resultado = []

    for vid, ubs in grafo.distritos.items():
        if not dentro_de_sao_paulo_aproximado(float(ubs["lat"]), float(ubs["lon"])):
            continue
        if zona != "Todas" and ubs.get("zona") != zona:
            continue
        if distrito != "Todos" and ubs.get("distrito") != distrito:
            continue

        resultado.append({
            "id": vid,
            "nome": ubs["nome"],
            "distrito": ubs.get("distrito", "N/D"),
            "bairro": ubs.get("bairro", ubs.get("distrito", "N/D")),
            "zona": ubs.get("zona", "N/D"),
            "endereco": ubs.get("endereco", "N/D"),
            "cnes": ubs.get("cnes", "N/D"),
        })

    return sorted(resultado, key=lambda item: (item["zona"], item["distrito"], item["nome"]))


def filtrar_ranking_ubs(
    ranking: list[dict],
    zona: str = "Todas",
    distrito: str = "Todos",
    distancia_maxima: float | None = None,
    ids_permitidos: set[int] | None = None,
) -> list[dict]:
    """Aplica filtros aos candidatos antes da ordenação por pressão."""
    resultado = ranking

    if zona != "Todas":
        resultado = [item for item in resultado if item["zona"] == zona]

    if distrito != "Todos":
        resultado = [item for item in resultado if item["distrito"] == distrito]

    if distancia_maxima is not None:
        resultado = [
            item for item in resultado
            if item["distancia_km"] <= distancia_maxima
        ]

    if ids_permitidos is not None:
        resultado = [
            item for item in resultado
            if int(item["id"]) in ids_permitidos
        ]

    return resultado


def anexar_pressao_ao_ranking(
    ranking: list[dict],
    ranking_cobertura: pd.DataFrame,
) -> list[dict]:
    """Acrescenta pressão territorial aos candidatos encontrados por distância."""
    cobertura_por_id = ranking_cobertura.set_index("distrito_id").to_dict("index")
    resultado = []

    for item in ranking:
        item_id = int(item["id"])
        cobertura = cobertura_por_id.get(item_id, {})
        novo = dict(item)
        novo["bairro"] = cobertura.get("bairro", novo.get("bairro", "N/D"))
        novo["populacao"] = int(float(cobertura.get("populacao", 0) or 0))
        novo["qtd_ubs_distrito"] = int(cobertura.get("qtd_ubs_distrito", 0) or 0)
        novo["habitantes_por_ubs"] = float(
            cobertura.get("habitantes_por_ubs", float("inf"))
        )
        novo["score_cobertura"] = float(cobertura.get("score", 0.0) or 0.0)
        resultado.append(novo)

    return resultado


def ordenar_por_menor_pressao(ranking: list[dict]) -> list[dict]:
    """Prioriza UBSs com menor pressão e usa distância apenas como desempate."""
    return sorted(
        ranking,
        key=lambda item: (
            float(item.get("habitantes_por_ubs", float("inf"))),
            float(item.get("distancia_km", float("inf"))),
        ),
    )


def calcular_raio_recomendacao(ranking: list[dict]) -> float:
    """Escolhe um raio próximo e só expande até o limite quando há poucas UBSs."""
    if not ranking:
        return RAIO_PADRAO_RECOMENDACAO_KM

    distancias = sorted(float(item["distancia_km"]) for item in ranking)
    no_raio_padrao = [
        dist for dist in distancias
        if dist <= RAIO_PADRAO_RECOMENDACAO_KM
    ]
    if len(no_raio_padrao) >= MIN_OPCOES_RECOMENDACAO:
        return RAIO_PADRAO_RECOMENDACAO_KM

    no_raio_maximo = [
        dist for dist in distancias
        if dist <= RAIO_MAXIMO_RECOMENDACAO_KM
    ]
    if len(no_raio_maximo) >= MIN_OPCOES_RECOMENDACAO:
        raio = no_raio_maximo[MIN_OPCOES_RECOMENDACAO - 1]
    elif no_raio_maximo:
        raio = no_raio_maximo[-1]
    else:
        raio = RAIO_MAXIMO_RECOMENDACAO_KM

    return round(
        min(
            RAIO_MAXIMO_RECOMENDACAO_KM,
            max(RAIO_PADRAO_RECOMENDACAO_KM, raio),
        ),
        1,
    )


def adicionar_rota_ao_item(
    grafo: GrafoSP,
    item: dict,
    endereco_localizado: dict,
) -> dict:
    """Acrescenta rota e endereço completo ao item de UBS exibido na busca."""
    item = dict(item)
    item_id = int(item["id"])
    ubs_item = grafo.distritos[item_id]
    rota_item = obter_rota_osrm(
        endereco_localizado["lat"],
        endereco_localizado["lon"],
        ubs_item["lat"],
        ubs_item["lon"],
    )
    item["rota"] = rota_item
    item["distancia_rota_km"] = (
        float(rota_item["distancia_km"])
        if rota_item
        else None
    )
    item["endereco"] = ubs_item.get("endereco", "")
    item["bairro"] = ubs_item.get("bairro", item.get("bairro", "N/D"))
    return item


@st.cache_data(ttl=60 * 60 * 24)
def obter_rota_osrm(
    origem_lat: float,
    origem_lon: float,
    destino_lat: float,
    destino_lon: float,
) -> dict | None:
    """Busca rota viária entre endereço e UBS; retorna None se o serviço falhar."""
    coordenadas = f"{origem_lon},{origem_lat};{destino_lon},{destino_lat}"
    params = urlencode({
        "overview": "full",
        "geometries": "geojson",
        "alternatives": "false",
        "steps": "false",
    })

    for perfil in ("foot", "driving"):
        url = f"https://router.project-osrm.org/route/v1/{perfil}/{coordenadas}?{params}"
        req = Request(
            url,
            headers={
                "User-Agent": "RedeAcessoSP/1.0 (academic project)",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(req, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            continue

        rotas = payload.get("routes") or []
        if not rotas:
            continue

        rota = rotas[0]
        coords = rota.get("geometry", {}).get("coordinates") or []
        if len(coords) < 2:
            continue

        return {
            "perfil": perfil,
            "distancia_km": round(float(rota.get("distance", 0)) / 1000, 2),
            "duracao_min": round(float(rota.get("duration", 0)) / 60, 1),
            "lons": [float(p[0]) for p in coords],
            "lats": [float(p[1]) for p in coords],
        }

    return None

# ============================================================================
# Cache de Dados
# ============================================================================

@st.cache_resource
def carregar_grafo():
    """Carrega e constrói o grafo (executado apenas uma vez)."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    return GrafoSP(data_dir=data_dir)


def carregar_metricas(_grafo):
    """Inicializa o calculador de métricas."""
    return MetricasAcessibilidade(_grafo)


@st.cache_data
def carregar_poligonos_kml(caminho_kml: Path) -> dict[str, list[list[tuple[float, float]]]]:
    """Carrega polígonos distritais a partir de KML (nome -> lista de anéis)."""
    if not caminho_kml.exists():
        return {}

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    root = ET.parse(caminho_kml).getroot()
    poligonos: dict[str, list[list[tuple[float, float]]]] = {}

    for placemark in root.findall(".//kml:Placemark", ns):
        nome = placemark.findtext("kml:name", default="", namespaces=ns)
        nome_norm = normalizar_nome(nome)

        aneis: list[list[tuple[float, float]]] = []
        for coord_node in placemark.findall(
            ".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns
        ):
            txt = (coord_node.text or "").strip()
            if not txt:
                continue

            pontos: list[tuple[float, float]] = []
            for token in txt.replace("\n", " ").split():
                partes = token.split(",")
                if len(partes) < 2:
                    continue
                try:
                    lon = float(partes[0])
                    lat = float(partes[1])
                    pontos.append((lon, lat))
                except ValueError:
                    continue

            if len(pontos) < 3:
                continue

            # Simplificação leve para reduzir custo de renderização
            n = len(pontos)
            passo = 1
            if n > 2000:
                passo = 8
            elif n > 1000:
                passo = 6
            elif n > 600:
                passo = 4
            elif n > 300:
                passo = 3
            elif n > 150:
                passo = 2

            simplificado = pontos[::passo]
            if simplificado[0] != simplificado[-1]:
                simplificado.append(simplificado[0])

            aneis.append(simplificado)

        if aneis:
            poligonos[nome_norm] = aneis

    return poligonos


@st.cache_data
def carregar_aneis_municipio_sp() -> list[list[tuple[float, float]]]:
    """Carrega todos os anéis dos distritos do município de São Paulo."""
    caminho_kml = Path(__file__).resolve().parent.parent / "data" / "São Paulo.kml"
    poligonos = carregar_poligonos_kml(caminho_kml)
    return [anel for aneis in poligonos.values() for anel in aneis]


# ============================================================================
# Verificar se os dados existem
# ============================================================================

data_dir = Path(__file__).resolve().parent.parent / "data"
if not (data_dir / "ubs_vertices.json").exists():
    st.error("Arquivos de dados não encontrados.")
    st.info(
        "Inclua os arquivos finais da pasta `data/` no deploy: "
        "`ubs_vertices.json`, `distritos.json`, `adjacencias.json`, "
        "`servicos.json` e `São Paulo.kml`."
    )
    st.stop()

# Carregar dados
grafo = carregar_grafo()
aplicar_formatacao_enderecos(grafo)
metricas = carregar_metricas(grafo)
stats = grafo.estatisticas()

# ============================================================================
# Cabeçalho e Seleção de Contexto
# ============================================================================

# Seleção de UBS
nomes = grafo.get_nomes_ordenados()
opcoes_distrito = {nome: did for did, nome in nomes}

if "distrito_id" not in st.session_state:
    st.session_state["distrito_id"] = (
        opcoes_distrito.get("Sé", next(iter(opcoes_distrito.values())))
    )

nomes_lista = list(opcoes_distrito.keys())

st.title("Rede de Acesso SP")
st.caption(
    "Saúde territorial em São Paulo: proximidade, pressão populacional e rede de UBSs reais."
)

distrito_id = int(st.session_state["distrito_id"])
distrito_selecionado_nome = grafo.get_nome(distrito_id)

tipo_servico = "ubs"

# ============================================================================
# Conteúdo Principal
# ============================================================================

# Abas
tab1, tab2, tab3, tab4 = st.tabs([
    "Mapa",
    "Análise",
    "Cobertura",
    "Método"
])

# ============================================================================
# Tab 1: Visão Geral do Grafo
# ============================================================================

with tab1:
    st.subheader("Encontrar UBS próxima com maior chance de atendimento rápido")
    st.caption(
        "Informe um endereço ou filtre uma área. O sistema compara UBSs próximas e prioriza menor pressão territorial, indicando maior chance de atendimento mais rápido."
    )

    with st.container(border=True):
        endereco_padrao = st.session_state.get("endereco_busca", "")
        with st.form("form_busca_endereco"):
            endereco = st.text_input(
                "Endereço em São Paulo",
                value=endereco_padrao,
                placeholder="Ex.: Rua Piauí, 144, Higienópolis",
            )
            st.caption("Use rua e número; para evitar ambiguidade, acrescente o bairro. Ex.: Rua Piauí 144 Higienópolis.")
            buscar_endereco = st.form_submit_button("Buscar UBSs recomendadas")
        st.caption("Teste do raio automático: Rua Eurico Dias Baptista, Grajaú tende a expandir a busca para além de 6 km.")

        if buscar_endereco:
            limpar_estado_busca()
            st.session_state["endereco_busca"] = endereco
            st.session_state["endereco_confirmado"] = endereco

        tem_busca_ativa = (
            bool(st.session_state.get("endereco_confirmado"))
            or st.session_state.get("area_zona_ubs", "Todas") != "Todas"
            or st.session_state.get("area_distrito_ubs", "Todos") != "Todos"
        )
        if tem_busca_ativa:
            if st.button("Limpar busca e filtros", use_container_width=True):
                limpar_estado_busca()
                st.rerun()

        st.markdown("#### Buscar por área")
        zonas_area = ["Todas"] + sorted({
            ubs.get("zona", "N/D")
            for ubs in grafo.distritos.values()
            if ubs.get("zona")
        })
        col_area_zona, col_area_distrito = st.columns(2)
        with col_area_zona:
            zona_area = st.selectbox(
                "Zona de SP",
                options=zonas_area,
                key="area_zona_ubs",
            )

        distritos_area = ["Todos"] + sorted({
            ubs.get("distrito", "N/D")
            for ubs in grafo.distritos.values()
            if zona_area == "Todas" or ubs.get("zona") == zona_area
        })
        distrito_area_key = "area_distrito_ubs"
        if st.session_state.get(distrito_area_key, "Todos") not in distritos_area:
            st.session_state[distrito_area_key] = "Todos"
        with col_area_distrito:
            distrito_area = st.selectbox(
                "Distrito",
                options=distritos_area,
                key=distrito_area_key,
            )

        area_ativa = zona_area != "Todas" or distrito_area != "Todos"
        ubs_area = listar_ubs_por_area(grafo, zona_area, distrito_area) if area_ativa else []
        ids_area_mapa = {int(item["id"]) for item in ubs_area}

        endereco_consulta = "" if area_ativa else st.session_state.get("endereco_confirmado", "")

        endereco_localizado = None
        ubs_destino_id = distrito_id
        distancia_endereco_ubs = None
        rota_endereco_ubs = None
        ranking_distancias: list[dict] = []
        ranking_filtrado: list[dict] = []
        opcoes_categoria: list[dict] = []
        ids_categoria_mapa: set[int] = set()
        rotas_mapa: dict[int, float | None] = {}

        if area_ativa and ubs_area:
            if distrito_id not in ids_area_mapa:
                distrito_id = int(ubs_area[0]["id"])
                distrito_selecionado_nome = grafo.get_nome(distrito_id)
                st.session_state["distrito_id"] = distrito_id
            ubs_destino_id = distrito_id

            st.markdown(f"#### UBSs na área selecionada ({len(ubs_area)})")
            df_area = pd.DataFrame(ubs_area).rename(columns={
                "nome": "UBS",
                "distrito": "Distrito",
                "bairro": "Bairro",
                "zona": "Zona",
                "endereco": "Endereço",
                "cnes": "CNES",
            })
            st.dataframe(
                df_area[["UBS", "Bairro", "Distrito", "Zona", "Endereço", "CNES"]],
                width="stretch",
                hide_index=True,
                height=min(420, 72 + (len(df_area) * 35)),
            )
        elif area_ativa:
            st.info("Nenhuma UBS encontrada nessa área.")

        if endereco_consulta.strip():
            endereco_localizado = geocodificar_endereco(endereco_consulta)
            if endereco_localizado:
                ubs_destino_id = None
                ranking_distancias = listar_ubs_por_distancia(
                    grafo, endereco_localizado["lat"], endereco_localizado["lon"]
                )
                ranking_distancias = anexar_pressao_ao_ranking(
                    ranking_distancias,
                    metricas.ranking_cobertura_ubs(),
                )

                raio_sugerido = calcular_raio_recomendacao(ranking_distancias)
                raio_maximo = RAIO_MAXIMO_RECOMENDACAO_KM
                if raio_sugerido > RAIO_PADRAO_RECOMENDACAO_KM:
                    st.info(
                        f"O raio foi expandido automaticamente de {RAIO_PADRAO_RECOMENDACAO_KM:.0f} km "
                        f"para {raio_sugerido:.1f} km porque havia poucas UBSs no raio inicial."
                    )
                endereco_label = str(endereco_localizado.get("label", "Endereço informado"))
                if len(endereco_label) > 120:
                    endereco_label = endereco_label[:117] + "..."
                st.markdown(
                    f"""
                    <div class="ihc-note">
                        <strong>Endereço localizado em São Paulo.</strong><br>
                        <span>{endereco_label}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                zona_filtro = "Todas"
                distrito_filtro = "Todos"
                distancia_maxima = raio_sugerido
                mesmo_distrito = False

                with st.expander("Filtros avançados (opcional)", expanded=False):
                    zonas_disponiveis = ["Todas"] + sorted({
                        item["zona"] for item in ranking_distancias
                        if item.get("zona")
                    })
                    zona_filtro = st.selectbox(
                        "Zona",
                        options=zonas_disponiveis,
                        key="filtro_zona_ubs",
                    )

                    ranking_para_distritos = [
                        item for item in ranking_distancias
                        if zona_filtro == "Todas" or item["zona"] == zona_filtro
                    ]
                    distritos_disponiveis = ["Todos"] + sorted({
                        item["distrito"] for item in ranking_para_distritos
                        if item.get("distrito")
                    })
                    distrito_key = "filtro_distrito_ubs"
                    if st.session_state.get(distrito_key, "Todos") not in distritos_disponiveis:
                        st.session_state[distrito_key] = "Todos"
                    distrito_filtro = st.selectbox(
                        "Distrito",
                        options=distritos_disponiveis,
                        key=distrito_key,
                    )

                    distancia_key = "filtro_distancia_maxima_ubs"
                    valor_distancia = st.session_state.get(distancia_key, raio_sugerido)
                    if valor_distancia < 1.0 or valor_distancia > raio_maximo:
                        st.session_state.pop(distancia_key, None)
                    distancia_maxima = st.slider(
                        "Raio de busca (km)",
                        min_value=1.0,
                        max_value=raio_maximo,
                        value=raio_sugerido,
                        step=0.5,
                        key=distancia_key,
                    )
                    st.caption(
                        "A recomendação compara apenas UBSs dentro desse raio; "
                        "a pressão territorial ordena as candidatas próximas."
                    )
                    mesmo_distrito = st.checkbox(
                        "Mesmo distrito da UBS selecionada",
                        key="filtro_mesmo_distrito_ubs",
                    )

                ranking_filtrado = filtrar_ranking_ubs(
                    ranking_distancias,
                    zona=zona_filtro,
                    distrito=distrito_filtro,
                    distancia_maxima=distancia_maxima,
                )

                if mesmo_distrito:
                    distrito_base = grafo.distritos[distrito_id].get("distrito", "")
                    ranking_filtrado = [
                        item for item in ranking_filtrado
                        if item["distrito"] == distrito_base
                    ]

                recomendadas = ordenar_por_menor_pressao(ranking_filtrado)
                opcoes_categoria = [
                    adicionar_rota_ao_item(grafo, item, endereco_localizado)
                    for item in recomendadas[:MAX_OPCOES_RECOMENDACAO]
                ]

                opcoes_categoria = sorted(
                    opcoes_categoria,
                    key=lambda item: (
                        float(item.get("habitantes_por_ubs", float("inf"))),
                        item["distancia_rota_km"] is None,
                        item["distancia_rota_km"]
                        if item["distancia_rota_km"] is not None
                        else item["distancia_km"],
                    ),
                )
                ids_categoria_mapa = {
                    int(item["id"])
                    for item in opcoes_categoria
                }
                rotas_mapa = {
                    int(item["id"]): item.get("distancia_rota_km")
                    for item in opcoes_categoria
                }

                id_estado = st.session_state.get("ubs_recomendada_id")
                if opcoes_categoria and id_estado not in ids_categoria_mapa:
                    id_estado = int(opcoes_categoria[0]["id"])
                    st.session_state["ubs_recomendada_id"] = id_estado

                ubs_escolhida = None
                if id_estado in ids_categoria_mapa:
                    ubs_escolhida = next(
                        item for item in opcoes_categoria
                        if int(item["id"]) == id_estado
                    )

                if opcoes_categoria:
                    st.markdown(f"#### UBSs recomendadas em até {distancia_maxima:.1f} km")
                    st.caption(
                        f"{len(opcoes_categoria)} opções comparadas. A recomendação prioriza menor habitantes por UBS; distância entra como critério de desempate."
                    )
                    colunas_cards = st.columns(min(3, max(1, len(opcoes_categoria))))
                    for idx, item in enumerate(opcoes_categoria):
                        item_id = int(item["id"])
                        selecionada = item_id == st.session_state.get("ubs_recomendada_id")
                        with colunas_cards[idx % len(colunas_cards)]:
                            with st.container(border=True):
                                if selecionada:
                                    st.success("Melhor opção no raio atual")
                                else:
                                    st.caption("Alternativa próxima")
                                st.markdown(f"**{item['nome']}**")
                                rota_texto_card = (
                                    f"{item['distancia_rota_km']:.1f} km"
                                    if item["distancia_rota_km"] is not None
                                    else "N/D"
                                )
                                pressao_texto_card = (
                                    f"{item['habitantes_por_ubs']:,.0f}".replace(",", ".")
                                )
                                st.markdown(
                                    f"Pressão: **{pressao_texto_card} hab./UBS**  \n"
                                    f"Rota: **{rota_texto_card}**"
                                )
                                st.caption(
                                    f"Índice {item['score_cobertura']:.1f}/100 · {item['bairro']} · {item['distrito']} · {item['zona']}"
                                )
                                if item.get("endereco"):
                                    st.markdown(f"Endereço: {item['endereco']}")
                                if st.button(
                                    "Ver caminho",
                                    key=f"ver_caminho_{item_id}",
                                    type="primary" if selecionada else "secondary",
                                    use_container_width=True,
                                ):
                                    st.session_state["ubs_recomendada_id"] = item_id
                                    st.session_state["distrito_id"] = item_id
                                    st.rerun()

                if ubs_escolhida:
                    ubs_destino_id = int(ubs_escolhida["id"])
                    distancia_endereco_ubs = float(ubs_escolhida["distancia_km"])

                    if ubs_destino_id in grafo.distritos and ubs_destino_id != distrito_id:
                        st.session_state["distrito_id"] = ubs_destino_id
                        distrito_id = ubs_destino_id
                        distrito_selecionado_nome = grafo.get_nome(distrito_id)

                    rota_endereco_ubs = ubs_escolhida.get("rota")

                    st.success(f"UBS selecionada: {grafo.get_nome(ubs_destino_id)}")
                    if rota_endereco_ubs:
                        st.caption(f"Rota estimada até a UBS selecionada: {rota_endereco_ubs['distancia_km']:.1f} km.")
                    else:
                        st.caption("Rota estimada indisponível para esta UBS.")
                else:
                    st.info(
                        f"Nenhuma UBS encontrada em até {distancia_maxima:.1f} km "
                        "com os filtros atuais."
                    )
            else:
                st.warning("Não consegui localizar esse endereço dentro do município de São Paulo. Tente usar rua, número e bairro.")

    col_info, col_mapa = st.columns([0.95, 1.65])

    with col_mapa:
        fig_map = go.Figure()

        if endereco_localizado:
            vizinhos_ids = set()
            ids_mapa = set(ids_categoria_mapa)
            if ubs_destino_id in grafo.distritos:
                ids_mapa.add(ubs_destino_id)
        elif area_ativa:
            vizinhos_ids = set()
            ids_mapa = set(ids_area_mapa)
            if not ids_mapa:
                ids_mapa = {distrito_id}
        else:
            vizinhos_ids = set(grafo.G.neighbors(distrito_id))
            ids_mapa = {distrito_id, *vizinhos_ids}

        grupos_marcadores = {
            "UBS recomendada": {"color": ACCENT_RED, "lats": [], "lons": [], "custom": [], "text": [], "sizes": []},
            "UBSs próximas": {"color": ACCENT_AMBER, "lats": [], "lons": [], "custom": [], "text": [], "sizes": []},
            "UBSs vizinhas": {"color": ACCENT_GREEN, "lats": [], "lons": [], "custom": [], "text": [], "sizes": []},
            "Outras UBSs": {"color": PLOT_MUTED, "lats": [], "lons": [], "custom": [], "text": [], "sizes": []},
        }

        for did in sorted(ids_mapa):
            if did not in grafo.distritos:
                continue

            dno = grafo.distritos[did]
            rota_ubs = rotas_mapa.get(did)
            rota_texto = f"{rota_ubs:.1f} km" if rota_ubs is not None else "N/D"
            custom = [
                "ubs",
                did,
                dno["nome"],
                dno["zona"],
                dno.get("distrito", ""),
                dno.get("endereco", "N/D"),
                rota_texto,
            ]

            if ubs_destino_id in grafo.distritos and did == ubs_destino_id:
                grupo = "UBS recomendada"
                tamanho = 19
            elif did in ids_categoria_mapa:
                grupo = "UBSs próximas"
                tamanho = 12
            elif did in ids_area_mapa:
                grupo = "UBSs próximas"
                tamanho = 12
            elif did in vizinhos_ids:
                grupo = "UBSs vizinhas"
                tamanho = 10
            else:
                grupo = "Outras UBSs"
                tamanho = 8

            grupos_marcadores[grupo]["lats"].append(dno["lat"])
            grupos_marcadores[grupo]["lons"].append(dno["lon"])
            grupos_marcadores[grupo]["custom"].append(custom)
            grupos_marcadores[grupo]["text"].append(dno["nome"])
            grupos_marcadores[grupo]["sizes"].append(tamanho)

        hover_ubs = (
            "<b>%{customdata[2]}</b>"
            "<br>Rota: %{customdata[6]}"
            "<br>Distrito: %{customdata[4]}"
            "<br>Zona: %{customdata[3]}"
            "<br>Endereço: %{customdata[5]}"
            "<extra></extra>"
            if endereco_localizado
            else (
                "<b>%{customdata[2]}</b>"
                "<br>Distrito: %{customdata[4]}"
                "<br>Zona: %{customdata[3]}"
                "<br>Endereço: %{customdata[5]}"
                "<extra></extra>"
            )
        )

        for nome_grupo, dados_grupo in grupos_marcadores.items():
            if not dados_grupo["lats"]:
                continue
            fig_map.add_trace(go.Scattermap(
                lat=dados_grupo["lats"],
                lon=dados_grupo["lons"],
                mode="markers",
                marker=dict(
                    size=dados_grupo["sizes"],
                    color=dados_grupo["color"],
                    opacity=0.92,
                ),
                customdata=dados_grupo["custom"],
                text=dados_grupo["text"],
                hovertemplate=hover_ubs,
                name=nome_grupo,
                showlegend=True,
            ))

        zoom_lats = [
            lat
            for dados_grupo in grupos_marcadores.values()
            for lat in dados_grupo["lats"]
        ]
        zoom_lons = [
            lon
            for dados_grupo in grupos_marcadores.values()
            for lon in dados_grupo["lons"]
        ]

        if endereco_localizado and ubs_destino_id in grafo.distritos:
            ubs_destino = grafo.distritos[ubs_destino_id]
            if rota_endereco_ubs:
                rota_lats = rota_endereco_ubs["lats"]
                rota_lons = rota_endereco_ubs["lons"]
            else:
                rota_lats = [endereco_localizado["lat"], ubs_destino["lat"]]
                rota_lons = [endereco_localizado["lon"], ubs_destino["lon"]]

            fig_map.add_trace(go.Scattermap(
                lat=rota_lats,
                lon=rota_lons,
                mode="lines",
                line=dict(color=ACCENT_RED, width=5),
                hoverinfo="skip",
                name="Rota até a UBS",
                showlegend=True,
            ))

            zoom_lats = list(rota_lats)
            zoom_lons = list(rota_lons)
            titulo_mapa = "Caminho até a UBS selecionada"

        if endereco_localizado:
            fig_map.add_trace(go.Scattermap(
                lat=[endereco_localizado["lat"]],
                lon=[endereco_localizado["lon"]],
                mode="markers",
                marker=dict(size=17, color=ACCENT_BLUE, opacity=0.96),
                text=[endereco_localizado.get("label", "Endereço informado")],
                hovertemplate="<b>Endereço informado</b><br>%{text}<extra></extra>",
                name="Seu endereço",
                showlegend=True,
            ))

            zoom_lats = [*zoom_lats, endereco_localizado["lat"]]
            zoom_lons = [*zoom_lons, endereco_localizado["lon"]]
            if ubs_destino_id not in grafo.distritos:
                titulo_mapa = "Endereço informado"
        elif area_ativa:
            titulo_mapa = "UBSs da área selecionada"
        else:
            titulo_mapa = "UBS selecionada e vizinhas"

        centro_lat = (min(zoom_lats) + max(zoom_lats)) / 2
        centro_lon = (min(zoom_lons) + max(zoom_lons)) / 2

        fig_map.update_layout(
            template="plotly_white",
            margin=dict(l=0, r=0, t=42, b=0),
            title=titulo_mapa,
            title_font=dict(size=18, color=MAP_FONT),
            font=dict(color=MAP_FONT),
            legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="left", x=0.0),
            legend_font=dict(color=MAP_MUTED),
            paper_bgcolor=MAP_BG,
            hoverlabel=dict(
                bgcolor=MAP_HOVER_BG,
                bordercolor=ACCENT_BLUE,
                font_color=MAP_FONT,
            ),
            map=dict(
                style=MAP_STYLE,
                center=dict(lat=centro_lat, lon=centro_lon),
                zoom=zoom_por_extensao(zoom_lats, zoom_lons),
            ),
            height=720,
        )

        st.plotly_chart(
            fig_map,
            width="stretch",
            key="mapa_interativo_sp",
        )

    with col_info:
        titulo_painel = (
            "UBS Recomendada"
            if endereco_localizado and distancia_endereco_ubs is not None
            else "UBS Selecionada"
        )
        st.markdown(f"### {titulo_painel}")
        d = grafo.distritos[distrito_id]
        st.markdown(f"**{d['nome']}**")
        st.markdown(f"Bairro: **{d.get('bairro', 'N/D')}**")
        st.markdown(f"Distrito: **{d.get('distrito', 'N/D')}**")
        st.markdown(f"Zona: **{d['zona']}**")
        st.markdown(f"População do distrito: **{d['populacao']:,}**".replace(",", "."))
        if d.get("endereco"):
            st.markdown(f"Endereço: {d['endereco']}")
        st.markdown(f"Lat: {d['lat']:.4f} | Lon: {d['lon']:.4f}")

        grau = grafo.G.degree(distrito_id)
        st.markdown(f"Conexões: **{grau}**")

        st.markdown("---")
        st.markdown("### UBSs Vizinhas")
        vizinhos = list(grafo.G.neighbors(distrito_id))
        if not vizinhos:
            st.info("Sem UBSs vizinhas cadastradas.")
        else:
            for v in sorted(vizinhos, key=lambda x: grafo.get_nome(x)):
                peso = grafo.G[distrito_id][v]["weight"]
                st.markdown(f"• {grafo.get_nome(v)} ({peso:.1f} km)")

        if endereco_localizado and distancia_endereco_ubs is not None:
            st.markdown("---")
            st.markdown("### Motivo da recomendação")
            st.markdown(
                "A UBS foi comparada com outras unidades próximas e aparece pelo menor indicador de pressão territorial no raio atual."
            )
            st.markdown("### Caminho")
            if rota_endereco_ubs:
                st.markdown(f"Pela rota: **{rota_endereco_ubs['distancia_km']:.1f} km**")
            else:
                st.markdown("Pela rota: **não disponível**")

        st.markdown("---")
        st.markdown("### Serviços no Distrito")
        servicos_local = grafo.contar_servicos_distrito(distrito_id)
        qtd_ubs = int(servicos_local.get("ubs", 0))
        st.metric("Quantidade de UBS", qtd_ubs)


# ============================================================================
# Tab 2: Análise Distrital
# ============================================================================

with tab2:
    nome_atual_analise = grafo.get_nome(st.session_state["distrito_id"])
    index_analise = nomes_lista.index(nome_atual_analise) if nome_atual_analise in nomes_lista else 0

    with st.container(border=True):
        col_seletor_analise, col_stat_a, col_stat_b, col_stat_c = st.columns([2.3, 0.8, 0.8, 0.8])
        with col_seletor_analise:
            nome_analise = st.selectbox(
                "Selecionar UBS para análise",
                options=nomes_lista,
                index=index_analise,
                key="seletor_ubs_analise",
            )
            st.caption("Use este campo para trocar a UBS analisada e atualizar os indicadores abaixo.")
        novo_distrito_analise = int(opcoes_distrito[nome_analise])
        if novo_distrito_analise != st.session_state["distrito_id"]:
            st.session_state["distrito_id"] = novo_distrito_analise
            st.session_state["ubs_recomendada_id"] = novo_distrito_analise
            st.rerun()

        with col_stat_a:
            st.metric("UBSs", stats["num_vertices"])
        with col_stat_b:
            st.metric("Conexões", stats["num_arestas"])
        with col_stat_c:
            st.metric("Grau médio", stats["grau_medio"])

    distrito_id = int(st.session_state["distrito_id"])
    distrito_selecionado_nome = grafo.get_nome(distrito_id)
    st.subheader(f"Análise da UBS: {distrito_selecionado_nome}")

    dados_ubs = grafo.distritos[distrito_id]
    analise = metricas.analisar_ubs(distrito_id)
    ranking_cobertura_df = metricas.ranking_cobertura_ubs()
    vizinhos_analise = sorted(list(grafo.G.neighbors(distrito_id)), key=lambda x: grafo.get_nome(x))
    hab_vizinhos = []
    for vid in vizinhos_analise:
        linha_vizinha = ranking_cobertura_df[
            ranking_cobertura_df["distrito_id"] == vid
        ]
        if not linha_vizinha.empty:
            hab_vizinhos.append(float(linha_vizinha.iloc[0]["habitantes_por_ubs"]))
    delta_vizinhos_texto = "sem vizinhas suficientes para comparação"
    if hab_vizinhos:
        delta_vizinhos_analise = float(analise["habitantes_por_ubs"]) - (sum(hab_vizinhos) / len(hab_vizinhos))
        delta_vizinhos_texto = f"{delta_vizinhos_analise:+.0f} hab./UBS em relação às vizinhas"

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "População do distrito",
            f"{int(analise['populacao']):,}".replace(",", "."),
        )
    with col2:
        st.metric(
            "UBSs no distrito",
            int(analise["qtd_ubs_distrito"]),
            delta=f"{analise['ubs_por_10_mil']:.2f} por 10 mil hab.",
        )
    with col3:
        st.metric(
            "Habitantes por UBS",
            f"{analise['habitantes_por_ubs']:,.0f}".replace(",", "."),
            delta=f"{analise['diferenca_media_pressao']:+.0f} vs média",
            delta_color="inverse",
        )
    with col4:
        st.metric(
            "Índice de cobertura",
            f"{analise['score']:.1f}/100",
            delta=analise["classificacao"],
        )

    diferenca_pressao = float(analise["diferenca_media_pressao"])
    if diferenca_pressao > 0:
        st.warning(
            "Leitura rápida: esta UBS está em um território com pressão acima da média do recorte."
        )
    else:
        st.success(
            "Leitura rápida: esta UBS está em um território com pressão igual ou menor que a média do recorte."
        )

    st.markdown("#### Resumo textual")
    habitantes_texto = f"{analise['habitantes_por_ubs']:,.0f}".replace(",", ".")
    media_recorte_texto = f"{analise['media_habitantes_por_ubs']:,.0f}".replace(",", ".")
    st.markdown(
        f"A **{dados_ubs['nome']}** fica em **{dados_ubs.get('bairro', 'N/D')}**, "
        f"no distrito **{dados_ubs.get('distrito', 'N/D')}**. "
        f"A cobertura foi classificada como **{analise['classificacao']}**, "
        f"na posição **{analise['posicao']} de {analise['total_ubs']}** do ranking. "
        f"O território tem **{habitantes_texto} habitantes por UBS**, "
        f"com média do recorte de **{media_recorte_texto} hab./UBS**. "
        f"A diferença em relação às UBSs vizinhas é **{delta_vizinhos_texto}**."
    )

    st.markdown("---")

    col_contexto, col_vizinhos = st.columns(2)

    with col_contexto:
        st.markdown("#### Dados da UBS")
        st.markdown(f"**Nome:** {dados_ubs['nome']}")
        st.markdown(f"**Bairro:** {dados_ubs.get('bairro', 'N/D')}")
        st.markdown(f"**Distrito:** {dados_ubs.get('distrito', 'N/D')}")
        st.markdown(f"**Subprefeitura:** {dados_ubs.get('subprefeitura', 'N/D')}")
        st.markdown(f"**Zona:** {dados_ubs.get('zona', 'N/D')}")
        if dados_ubs.get("endereco"):
            st.markdown(f"**Endereço:** {dados_ubs['endereco']}")
        if dados_ubs.get("cnes"):
            st.markdown(f"**CNES:** {dados_ubs['cnes']}")

        st.markdown("---")
        st.markdown("#### Cobertura Territorial")
        st.markdown(f"**Classificação:** {analise['classificacao']}")
        st.markdown(f"**Posição no ranking:** {analise['posicao']} de {analise['total_ubs']}")
        st.markdown(f"**Índice de cobertura:** {analise['score']:.1f}/100")
        st.markdown(f"**Média do recorte:** {analise['media_habitantes_por_ubs']:,.0f} hab./UBS".replace(",", "."))

    with col_vizinhos:
        st.markdown("#### UBSs Vizinhas")

        if not vizinhos_analise:
            st.info("Sem UBSs vizinhas cadastradas para comparação.")
        else:
            dados_vizinhos = []
            for vid in vizinhos_analise:
                linha = ranking_cobertura_df[
                    ranking_cobertura_df["distrito_id"] == vid
                ].iloc[0]
                dados_vizinhos.append({
                    "UBS": grafo.get_nome(vid),
                    "Bairro": linha.get("bairro", "N/D"),
                    "Distrito": linha["distrito"],
                    "Relação": f"{grafo.G[distrito_id][vid]['weight']:.1f} km",
                    "Hab./UBS": round(float(linha["habitantes_por_ubs"]), 0),
                    "Índice": float(linha["score"]),
                })

            df_vizinhos = pd.DataFrame(dados_vizinhos).sort_values("Hab./UBS")
            st.dataframe(df_vizinhos, width="stretch", hide_index=True)

            media_vizinhos = float(df_vizinhos["Hab./UBS"].mean())
            delta_vizinhos = float(analise["habitantes_por_ubs"]) - media_vizinhos
            st.metric(
                "Diferença vs vizinhas",
                f"{delta_vizinhos:+.0f} hab./UBS",
                delta_color="inverse",
            )


# ============================================================================
# Tab 3: Ranking
# ============================================================================

with tab3:
    st.subheader("Cobertura das UBSs")

    ranking_df = metricas.ranking_cobertura_ubs()
    media = metricas.resumo_cobertura_ubs()

    with st.container(border=True):
        col_rank_zona, col_rank_busca = st.columns([0.9, 1.6])
        with col_rank_zona:
            zona_ranking = st.selectbox(
                "Filtrar ranking por zona",
                options=["Todas"] + sorted(ranking_df["zona"].dropna().unique().tolist()),
                key="ranking_zona_filtro",
            )
        with col_rank_busca:
            busca_ranking = st.text_input(
                "Buscar UBS, bairro ou distrito",
                key="ranking_texto_filtro",
                placeholder="Ex.: Mooca, Sé, Humaitá",
            )

    ranking_tabela_df = ranking_df.copy()
    if zona_ranking != "Todas":
        ranking_tabela_df = ranking_tabela_df[ranking_tabela_df["zona"] == zona_ranking]
    if busca_ranking.strip():
        termo = normalizar_nome(busca_ranking)
        ranking_tabela_df = ranking_tabela_df[
            ranking_tabela_df.apply(
                lambda row: termo in normalizar_nome(
                    " ".join([
                        str(row.get("ubs", "")),
                        str(row.get("bairro", "")),
                        str(row.get("distrito", "")),
                    ])
                ),
                axis=1,
            )
        ]

    # Métricas resumo
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("UBSs analisadas", media["total_ubs"])
    with col2:
        st.metric("Média hab./UBS", f"{media['media_habitantes_por_ubs']:,.0f}".replace(",", "."))
    with col3:
        st.metric("Mediana hab./UBS", f"{media['mediana_habitantes_por_ubs']:,.0f}".replace(",", "."))
    with col4:
        st.metric("Melhor pressão", f"{media['melhor_pressao']:,.0f}".replace(",", "."))
    with col5:
        st.metric("Pior pressão", f"{media['pior_pressao']:,.0f}".replace(",", "."))

    st.markdown("---")

    col_top, col_bottom = st.columns(2)

    with col_top:
        st.markdown("#### Menor pressão territorial")
        top10 = ranking_df.head(10)

        fig_top = px.bar(
            top10,
            x="ubs",
            y="habitantes_por_ubs",
            color="zona",
            color_discrete_map=CORES_ZONA,
            title="UBSs em distritos com menor habitantes por UBS",
            labels={"habitantes_por_ubs": "Habitantes por UBS", "ubs": "UBS", "zona": "Zona"},
        )
        aplicar_tema_plotly(fig_top, height=400)
        fig_top.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_top, width="stretch")

    with col_bottom:
        st.markdown("#### Maior pressão territorial")
        bottom10 = ranking_df.tail(10).sort_values("habitantes_por_ubs", ascending=False)

        fig_bottom = px.bar(
            bottom10,
            x="ubs",
            y="habitantes_por_ubs",
            color="zona",
            color_discrete_map=CORES_ZONA,
            title="UBSs em distritos com maior habitantes por UBS",
            labels={"habitantes_por_ubs": "Habitantes por UBS", "ubs": "UBS", "zona": "Zona"},
        )
        aplicar_tema_plotly(fig_bottom, height=400)
        fig_bottom.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bottom, width="stretch")

    st.markdown("---")
    st.markdown("#### UBSs com Maior Pressão")

    maior_pressao = metricas.ubs_maior_pressao(percentil=0.8)
    if maior_pressao:
        df_pressao = pd.DataFrame(maior_pressao)
        st.dataframe(
            df_pressao[[
                "ubs", "bairro", "distrito", "zona", "populacao",
                "qtd_ubs_distrito", "habitantes_por_ubs", "score",
            ]].rename(columns={
                "ubs": "UBS",
                "bairro": "Bairro",
                "distrito": "Distrito",
                "zona": "Zona",
                "populacao": "População",
                "qtd_ubs_distrito": "UBSs no Distrito",
                "habitantes_por_ubs": "Habitantes por UBS",
                "score": "Índice",
            }),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("Não há UBSs com pressão territorial destacada.")

    st.markdown("---")
    st.markdown("#### População vs. Pressão Territorial")

    fig_scatter = px.scatter(
        ranking_df,
        x="populacao",
        y="habitantes_por_ubs",
        color="zona",
        color_discrete_map=CORES_ZONA,
        size="qtd_ubs_distrito",
        hover_name="ubs",
        title="Relação entre população do distrito e habitantes por UBS",
        labels={
            "populacao": "População",
            "habitantes_por_ubs": "Habitantes por UBS",
            "zona": "Zona",
            "qtd_ubs_distrito": "UBSs no Distrito",
        },
    )
    fig_scatter.add_hline(
        y=media["media_habitantes_por_ubs"],
        line_dash="dash",
        line_color=ACCENT_RED,
        annotation_text=f"Média: {media['media_habitantes_por_ubs']:.0f}",
        annotation_font_color=PLOT_FONT,
    )
    aplicar_tema_plotly(fig_scatter, height=500)
    st.plotly_chart(fig_scatter, width="stretch")

    st.markdown("---")
    st.markdown("#### Ranking Completo")
    st.caption(f"{len(ranking_tabela_df)} UBSs exibidas com os filtros atuais.")

    ranking_display = ranking_tabela_df.rename(columns={
        "posicao": "Posição",
        "ubs": "UBS",
        "bairro": "Bairro",
        "distrito": "Distrito",
        "zona": "Zona",
        "populacao": "População",
        "qtd_ubs_distrito": "UBSs no Distrito",
        "habitantes_por_ubs": "Habitantes por UBS",
        "ubs_por_10_mil": "UBSs por 10 mil hab.",
        "conexoes": "Conexões",
        "score": "Índice",
    })

    if ranking_display.empty:
        st.info("Nenhuma UBS encontrada com os filtros atuais.")
    else:
        st.dataframe(
            ranking_display[[
                "Posição", "UBS", "Bairro", "Distrito", "Zona", "População",
                "UBSs no Distrito", "Habitantes por UBS",
                "UBSs por 10 mil hab.", "Conexões", "Índice",
            ]],
            width="stretch",
            hide_index=True,
            height=400,
        )


# ============================================================================
# Tab 4: Sobre
# ============================================================================

with tab4:
    st.subheader("Sobre o Projeto")

    st.markdown("### Estatísticas do Grafo")
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
    with col_stat1:
        st.metric("Vértices (UBSs)", stats["num_vertices"])
    with col_stat2:
        st.metric("Arestas", stats["num_arestas"])
    with col_stat3:
        st.metric("Grau Médio", stats["grau_medio"])
    with col_stat4:
        st.metric("Densidade", stats["densidade"])
    with col_stat5:
        st.metric("Conexo", "Sim" if stats["eh_conexo"] else "Não")

    st.markdown("---")

    st.markdown("### Grafo completo das UBSs")
    st.caption(
        "Cada ponto é uma UBS. As linhas mostram conexões por proximidade geográfica entre unidades."
    )
    st.plotly_chart(criar_figura_grafo_completo(grafo), width="stretch")

    st.markdown("---")

    st.markdown("### Como a recomendação funciona")
    st.markdown(
        """
        O sistema recebe um endereço, localiza esse ponto dentro do município de São Paulo
        e compara as UBSs próximas. A distância delimita o conjunto de candidatas, mas a
        ordenação principal usa a **pressão territorial**, isto é, a população do território
        dividida pela quantidade de UBSs disponíveis ali.

        O raio começa em **6 km** e pode expandir até **12 km** quando há poucas opções
        próximas. Assim, o sistema evita indicar uma UBS muito distante sem necessidade,
        mas ainda consegue encontrar alternativas quando o endereço está em uma área com
        menos unidades no entorno.
        """
    )

    fig_exemplo, ubs_exemplo, raio_exemplo, total_exemplo = criar_figura_exemplo_recomendacao(grafo, metricas)
    col_exemplo_a, col_exemplo_b, col_exemplo_c = st.columns(3)
    with col_exemplo_a:
        st.metric("Endereço de exemplo", "Rua Piauí 144")
    with col_exemplo_b:
        st.metric("Raio usado", f"{raio_exemplo:.1f} km")
    with col_exemplo_c:
        st.metric("UBSs comparadas", total_exemplo)
    st.info(
        f"No exemplo de Higienópolis, a UBS recomendada pelo critério de menor pressão é "
        f"**{grafo.get_nome(int(ubs_exemplo['id']))}**."
    )
    st.plotly_chart(fig_exemplo, width="stretch")

    st.markdown("---")

    col_about1, col_about2 = st.columns(2)

    with col_about1:
        st.markdown("""
        ### Rede de Acesso SP

        Sistema interativo que modela a cidade de São Paulo como um **grafo**
        de **UBSs reais** para analisar desigualdades territoriais no acesso à saúde.

        ### Objetivo

        Desenvolver um sistema funcional que utilize **modelagem por grafos**
        para analisar e visualizar desigualdades no acesso a **UBS, UPA e hospitais SUS**
        a partir das UBSs da cidade de São Paulo.

        ### ODS 10 — Redução das Desigualdades

        A desigualdade urbana se manifesta no acesso desigual a serviços de saúde.
        UBSs em regiões periféricas tendem a apresentar menor cobertura relativa
        de UPA e hospitais SUS quando comparadas a unidades mais centrais.

        O projeto busca identificar padrões de cobertura territorial, destacar
        UBSs com menor acesso relativo e fornecer uma visualização comparativa
        da rede.
        """)

    with col_about2:
        st.markdown("""
        ### Modelagem em Grafos

        - **Vértices:** UBSs reais da cidade de São Paulo
        - **Arestas:** Conexões por proximidade geográfica entre UBSs
        - **Peso dos vértices:** População de referência do território da UBS
        - **Peso das arestas:** Distância estimada entre coordenadas das UBSs (km)
        - **Tipo:** Grafo não direcionado e ponderado

        ### Algoritmos Implementados

        - **Recomendação por pressão:** UBSs próximas com menor habitantes por UBS
        - **Distâncias ponderadas:** Caminhos e relações na rede de UBSs
        - **BFS:** Busca em largura para análise de alcance
        - **Centralidade de Grau:** Identificação de UBSs mais conectadas
        - **Centralidade de Proximidade:** Eficiência territorial de acesso
        - **Centralidade de Intermediação:** Importância como ponto de passagem

        ### Serviços Analisados

        - **Hospitais (SUS)** — Rede hospitalar pública
        - **UPA** — Unidades de Pronto Atendimento
        - **UBS** — Unidades Básicas de Saúde
        """)

    st.markdown("---")

    st.markdown("""
    ### Tecnologias

    | Componente | Tecnologia |
    |---|---|
    | Linguagem | Python 3.11+ |
    | Grafos | NetworkX |
    | Interface | Streamlit |
    | Visualização | Matplotlib + Plotly |
    | Dados | JSON |

    ### Equipe

    | Nome | RA |
    |---|---|
    | Lucas Fernandes | 10419400 |
    | Lendy Naiara Pacheco | 10428525 |
    | Anna Luiza Santos | 10417401 |
    """)
