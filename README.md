# Projeto

## Nome do Projeto
**Rede de Acesso SP**

## Nome do Sistema
**Rede de Acesso SP - Saúde Territorial em São Paulo**

## Link
**Final**: https://redeasp.streamlit.app/
**Figma navegável**:https://ihc-iterativo.vercel.app/
---

# Tema

Desenvolvimento de um sistema interativo que modela a cidade de São Paulo como um grafo para analisar desigualdades no acesso a serviços públicos essenciais, em conformidade com a **ODS 10 – Redução das Desigualdades**.

---

# Objetivo Geral

Desenvolver um sistema funcional que utilize modelagem por grafos para analisar e visualizar desigualdades no acesso a serviços públicos a partir das UBSs da cidade de São Paulo.

---

# Objetivos Específicos

- Modelar as UBSs como **vértices** de um grafo.
- Modelar conexões geográficas entre UBSs próximas como **arestas ponderadas**.
- Implementar algoritmos clássicos de grafos, como **Dijkstra** e **BFS**.
- Calcular métricas de acessibilidade.
- Desenvolver uma interface interativa com foco em usabilidade.
- Realizar avaliação básica de usabilidade conforme princípios de **IHC**.

---

# Justificativa

A desigualdade urbana se manifesta no acesso desigual a serviços como saúde, educação e assistência social. Distritos periféricos tendem a apresentar maior tempo de deslocamento até serviços essenciais quando comparados a regiões centrais.

O projeto busca identificar padrões de acessibilidade, destacar regiões mais isoladas e fornecer uma visualização comparativa entre distritos, contribuindo para a discussão da **ODS 10 – Redução das Desigualdades**.

---

# Modelagem em Teoria dos Grafos

## Estrutura do Grafo

- **Vértices:** UBSs da cidade de São Paulo.
- **Arestas:** conexões geográficas por proximidade entre UBSs.
- **Peso dos vértices:** população residente estimada na área de abrangência de cada UBS (AAUBS), associada pelo CNES.
- **Peso das arestas:** distância estimada entre as coordenadas das UBSs.
- **Recomendação:** dentro de um raio local, inicia em 6 km, expande até 12 km se houver poucas opções e prioriza UBSs cuja área de abrangência apresenta menor população estimada.

O indicador ideal de pressão também dividiria a população adscrita pela
capacidade ou número de equipes de cada unidade. Como esses dados por UBS são
indicados pela SMS-SP em sistemas de acesso restrito, o sistema utiliza a
população pública da AAUBS como estimativa de demanda territorial, assumindo
capacidade comparável entre as candidatas.

Essa modelagem atende ao requisito mínimo de aproximadamente **70 vértices e 180 arestas**.

## Tipo de Grafo

- Grafo **não direcionado**.
- Grafo **ponderado**.
- Estrutura predominantemente **conexa**.

## Algoritmos Utilizados

- **Dijkstra:** cálculo do menor caminho entre uma UBS e o serviço mais próximo.
- **BFS:** análise de conectividade e alcance.
- **Grau do vértice:** identificação de UBSs mais conectadas.
- **Densidade:** avaliação da conectividade geral da rede.
- **Verificação euleriana:** análise da existência de percurso/ciclo euleriano.
- **Medidas simples de centralidade.**

---

# Funcionalidades do Sistema

O usuário poderá:

- Selecionar uma UBS.
- Escolher o tipo de serviço (UBS, UPA ou hospital SUS).

Visualizar:

- Distância até o serviço mais próximo.
- Caminho mínimo.
- Ranking de acessibilidade e pressão territorial.
- Recomendação de UBS com maior chance relativa de menor movimento.
- Comparação com a média da cidade.
- Identificação de UBSs relativamente isoladas na rede.

---

# Parte de Interação Humano-Computador (IHC)

Documentação separada: [`DOCUMENTACAO_IHC.md`](DOCUMENTACAO_IHC.md).

O projeto incluirá:

- Protótipo inicial de baixa fidelidade.
- Implementação funcional do sistema.
- Aplicação de heurísticas de usabilidade (por exemplo, heurísticas de Nielsen).
- Teste com usuários e coleta de feedback.
- Ajustes baseados nos resultados da avaliação.

O foco será:

- Clareza.
- Simplicidade de navegação.
- Feedback imediato ao usuário.
- Organização adequada das informações.

---

# Arquitetura do Sistema

## Camada de Dados

- Coleta de dados públicos da cidade de São Paulo.
- Tratamento e organização em formato estruturado (CSV ou JSON).

## Camada de Processamento

- Construção do grafo.
- Implementação e execução dos algoritmos.

## Camada de Interface

- Entrada de dados pelo usuário.
- Exibição dos resultados e métricas calculadas.

---

# Fontes de Dados

- Portal de Dados Abertos da Prefeitura de São Paulo.
- GeoSampa.
- Secretaria Municipal da Saúde de São Paulo / Busca Saúde.
- SMS-SP/CEInfo e Censo 2022/IBGE para população estimada por Área de Abrangência de UBS (AAUBS 2025 preliminar).
- TABNET/SMS-SP, IBGE e Fundação SEADE para dados distritais mantidos como contexto.

A origem de cada arquivo mantido em `data/` está detalhada em `FONTES_DADOS.md`.

---

# Cronograma Proposto

## Mês 1

- Coleta e tratamento de dados.
- Modelagem do grafo.
- Implementação dos algoritmos.

## Mês 2

- Desenvolvimento da interface.
- Integração entre processamento e interface.

## Mês 3

- Testes de usabilidade.
- Ajustes e refinamentos.
- Documentação e preparação da apresentação.

## Liderado por
 `Lucas Fernandes 10419400`
 `Lendy Naiara Pacheco 10428525`
 `Anna Luiza Santos 10417401`

---

# Entrega Final / Deploy

Arquivos mantidos na versão limpa:

- `src/app.py`: interface Streamlit principal.
- `src/grafo.py` e `src/metricas.py`: processamento do grafo e métricas.
- `data/`: dados finais usados em runtime.
- `data/populacao_aaubs_2025.json`: recorte rastreável da população de abrangência associada aos vértices por CNES.
- `grafo.txt`: grafo com 71 vértices e 215 arestas.
- `projeto_grafo_menu.py`: menu textual final com investigação por Dijkstra e métricas do grafo.
- `DOCUMENTACAO_IHC.md`: documentação separada de IHC.
- `FONTES_DADOS.md`: documentação das fontes usadas nos arquivos finais.
- `requirements.txt`: dependências da aplicação.

Executar o menu:

```bash
python projeto_grafo_menu.py
```

Executar a interface complementar:

```bash
python -m streamlit run src/app.py
```

## Publicação do Aplicativo

A interface foi desenvolvida em **Streamlit**. O deploy recomendado e o
**Streamlit Community Cloud**, que executa diretamente aplicacoes Streamlit
vinculadas ao GitHub.

Configuracao para publicar:

1. Acesse `https://share.streamlit.io/` e conecte sua conta do GitHub.
2. Clique em **Create app**.
3. Selecione o repositorio `Lucas-FcNw/rede-de-acesso-sp`.
4. Selecione a branch `main`.
5. Informe como arquivo principal: `src/app.py`.
6. Clique em **Deploy**.

O repositorio pode ser privado, desde que o Streamlit Community Cloud tenha
permissao de leitura para acessa-lo.

### Por que nao usar Vercel neste projeto

A Vercel identifica arquivos Python como funcoes web e espera que
`src/app.py` exporte uma variavel como `app`, `application` ou `handler`.
Neste projeto, `src/app.py` e uma aplicacao Streamlit e deve ser iniciada com
`streamlit run`; portanto, ela nao e um endpoint Python compativel com o
runtime serverless da Vercel sem uma reimplementacao da interface.

Observacoes da entrega:

- Os relatórios, PDFs, wireframes, imagens de apoio, dados brutos e caches foram removidos.
- O app usa os JSONs finais e o KML presentes na pasta `data/`.
