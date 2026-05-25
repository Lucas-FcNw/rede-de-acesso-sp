# Documentação de Interação Humano-Computador

## Projeto

**Rede de Acesso SP - Saúde Territorial em São Paulo**

A Rede de Acesso SP é um sistema interativo para análise territorial de UBSs na cidade de São Paulo. A interface permite consultar unidades de saúde, visualizar sua posição no mapa, comparar a população estimada das áreas de abrangência e receber recomendações de UBSs próximas com menor demanda territorial potencial.

Esta documentação descreve a aplicação dos conceitos de **Interação Humano-Computador (IHC)** no projeto, considerando usuários, tarefas, requisitos de usabilidade, princípios de design, avaliação e melhorias implementadas.

---

## 1. Relação do Projeto com IHC

O projeto se enquadra em IHC porque envolve a criação de um sistema interativo no qual o usuário precisa compreender dados territoriais, inserir informações, interpretar respostas visuais e tomar decisões com base nos resultados apresentados.

Principais elementos de IHC presentes:

- interface gráfica interativa com mapa, filtros e indicadores;
- entrada de dados por endereço ou seleção de área;
- feedback visual imediato após busca ou seleção;
- organização de informações para reduzir esforço cognitivo;
- preocupação com clareza, eficiência, acessibilidade visual e facilidade de aprendizado;
- avaliação inicial de usabilidade com usuários potenciais.

---

## 2. Público-Alvo

O sistema foi pensado para usuários que precisam analisar informações de saúde pública territorial.

Usuários principais:

- estudantes e pesquisadores de tecnologia, saúde pública ou políticas urbanas;
- gestores públicos e analistas de planejamento;
- profissionais de saúde interessados em distribuição territorial de UBSs;
- cidadãos que desejam entender alternativas de atendimento próximas ao seu endereço.

## 3. Contexto de Uso

A Rede de Acesso SP pode ser utilizado em ambientes acadêmicos, administrativos ou exploratórios. O uso principal acontece em computador, com interação por teclado e mouse.

Cenários de uso:

- pesquisar uma UBS recomendada a partir de um endereço;
- comparar UBSs próximas considerando distância e pressão populacional;
- visualizar unidades por zona ou distrito;
- analisar cobertura territorial e ranking de pressão;
- compreender desigualdades de acesso à saúde dentro da cidade de São Paulo.

---

## 4. Personas

### Persona 1 - Estudante de Dados

**Nome:** Mariana  
**Perfil:** estudante de Ciência da Computação  
**Objetivo:** entender como grafos podem representar serviços públicos reais.  
**Necessidade:** visualizar rapidamente os vértices, arestas e métricas sem depender apenas de tabelas.

### Persona 2 - Analista de Planejamento

**Nome:** Rafael  
**Perfil:** trabalha com planejamento urbano e análise territorial.  
**Objetivo:** identificar áreas com maior pressão sobre UBSs.  
**Necessidade:** comparar regiões e localizar unidades próximas com dados claros.

### Persona 3 - Usuária Comum

**Nome:** Carla  
**Perfil:** moradora de São Paulo, sem conhecimento técnico em grafos.  
**Objetivo:** informar seu endereço e receber uma indicação compreensível de UBS próxima.  
**Necessidade:** interface simples, linguagem direta e resultado visual no mapa.

---

## 5. Análise de Tarefas

### Tarefa Principal

Encontrar uma UBS próxima com menor pressão territorial.

### Passos da Tarefa

1. Abrir o sistema.
2. Informar um endereço em São Paulo.
3. Receber a lista de UBSs recomendadas.
4. Ver a UBS recomendada no mapa.
5. Comparar distância, pressão populacional e índice de cobertura.
6. Selecionar outra UBS, se desejar.

### Tarefas Secundárias

- selecionar uma UBS manualmente;
- filtrar UBSs por zona ou distrito;
- visualizar UBSs vizinhas no grafo;
- consultar ranking de cobertura;
- comparar população estimada das áreas de abrangência das UBSs.

---

## 6. Modelo GOMS Simplificado

### Objetivo

Identificar uma UBS próxima com menor chance relativa de sobrecarga.

### Operações

- digitar endereço;
- acionar busca;
- observar mapa;
- ler indicadores;
- selecionar UBS recomendada;
- comparar opções.

### Métodos

**Método 1 - Busca por endereço**

1. Digitar rua, número e bairro.
2. Clicar em buscar.
3. Analisar recomendações.
4. Visualizar rota e UBS no mapa.

**Método 2 - Busca por área**

1. Selecionar zona.
2. Selecionar distrito, se necessário.
3. Observar UBSs exibidas.
4. Escolher uma UBS para análise.

### Regras de Seleção

- Se o usuário sabe seu endereço, deve usar a busca por endereço.
- Se o usuário deseja estudar uma região, deve usar os filtros de área.
- Se o usuário quer comparar cobertura, deve acessar a aba de ranking.

---

## 7. Estilos de Interação Utilizados

O sistema utiliza diferentes estilos de interação estudados em IHC:

- **Menus:** abas principais do Streamlit e menu nativo de tema.
- **Formulários:** campo de endereço e filtros de busca.
- **Pergunta-resposta:** usuário informa um endereço e o sistema retorna recomendações.
- **Manipulação direta:** interação com o mapa e seleção de UBSs.
- **Visualização interativa:** gráficos, ranking, métricas e mapa.

---

## 8. Requisitos de Usabilidade

| Requisito | Aplicação na Rede de Acesso SP |
|---|---|
| Eficácia | O usuário deve conseguir encontrar UBSs próximas e comparar pressão territorial. |
| Eficiência | A busca por endereço reduz o caminho até a recomendação principal. |
| Facilidade de aprendizado | A interface usa campos, filtros e abas familiares. |
| Prevenção de erro | A busca de endereço é limitada ao município de São Paulo. |
| Feedback | O sistema exibe mensagens quando localiza ou não localiza um endereço. |
| Consistência | Termos como UBS, distrito, zona e pressão territorial são usados de forma padronizada. |
| Satisfação | O mapa e os indicadores tornam a análise mais visual e compreensível. |
| Controle do usuário | O sistema permite limpar busca e filtros para retornar ao estado inicial. |

---

## 9. Heurísticas de Nielsen

| Heurística | Como o projeto atende |
|---|---|
| Visibilidade do estado do sistema | Após uma busca, o sistema mostra UBS selecionada, rota, mapa e indicadores. |
| Correspondência com o mundo real | Usa termos reconhecíveis, como endereço, UBS, bairro, distrito e zona. |
| Controle e liberdade do usuário | O usuário pode trocar UBS, alterar filtros e navegar pelas abas. |
| Consistência e padrões | A interface segue padrões do Streamlit, com abas, selectbox, botões e tabelas. |
| Prevenção de erros | Endereços fora de São Paulo são filtrados por limites geográficos e KML municipal. |
| Reconhecimento em vez de memorização | As opções de zona, distrito e UBS ficam visíveis em menus. |
| Flexibilidade e eficiência | Há busca direta por endereço e navegação por filtros. |
| Design estético e minimalista | A interface evita excesso de elementos e prioriza mapa, métricas e ranking. |
| Ajuda no reconhecimento de erros | Mensagens orientam o usuário a informar rua, número e bairro. |
| Ajuda e documentação | O projeto possui documentação técnica e documentação de IHC. |

---

## 10. Decisões de Interface

Principais decisões tomadas com foco em IHC:

- remover a barra lateral para reduzir distrações;
- manter o modo claro/escuro no menu padrão do Streamlit;
- deixar o mapa sempre claro para melhorar leitura cartográfica;
- priorizar busca por endereço com exemplo no campo;
- recomendar UBSs próximas, evitando resultados muito distantes;
- usar a população residente estimada da área de abrangência da UBS (AAUBS) como peso do vértice, com a limitação explícita de que capacidade/equipes não estão disponíveis publicamente no recorte;
- ordenar recomendações por menor pressão territorial;
- mostrar legenda do mapa para diferenciar endereço, UBS e rota;
- destacar o motivo da recomendação para reduzir ambiguidade;
- manter filtros de ranking para facilitar localização de UBSs específicas;
- remover informações redundantes do topo quando a busca por endereço já apresenta a UBS recomendada;
- concentrar estatísticas gerais e explicação do grafo na aba de método.

---

## 11. Avaliação com Usuários

Foi aplicado um questionário com **10 potenciais usuários** para identificar perfil, percepção de utilidade e dificuldades de uso.

Resultados principais:

- 70% dos respondentes usam mapas ou dados territoriais de forma frequente ou ocasional;
- 80% atribuíram nota 4 ou 5 para clareza dos indicadores;
- 50% deram nota até 3 para comparação entre distritos;
- 70% concluíram a tarefa de referência em até 3 minutos;
- 60% sugeriram filtros por zona ou região.

Interpretação:

O sistema foi considerado útil e compreensível, mas a comparação territorial exigia melhorias. Por isso, o projeto passou a valorizar filtros por área, mapa mais claro e recomendações mais próximas.

---

## 12. Melhorias Implementadas Após Avaliação

Melhorias feitas com base em critérios de usabilidade:

- inclusão de busca por endereço;
- recomendação de UBSs dentro de raio local;
- limitação da busca ao município de São Paulo;
- uso de filtros por zona e distrito;
- exibição de rota no mapa;
- recorte das UBSs para evitar unidades muito distantes do centro;
- ajuste visual para aproximar o sistema de uma interface mais simples;
- remoção de informações externas desnecessárias, como nota do Google;
- uso do tema nativo do Streamlit para modo claro e escuro;
- inclusão de botão para limpar busca e filtros;
- feedback explícito quando o endereço é localizado dentro de São Paulo;
- leitura rápida na aba de análise para indicar pressão acima ou abaixo da média;
- filtros de texto e zona no ranking completo;
- compactação dos cards de recomendação para reduzir esforço visual;
- visualização do grafo completo com as 71 UBSs e 215 conexões;
- exemplo didático com Rua Piauí, 144, Higienópolis para explicar a recomendação.

---

## 13. Análise de Dados da Avaliação

A avaliação indicou que a clareza dos indicadores era um ponto forte, enquanto a comparação entre UBSs ou distritos era o principal ponto de melhoria.

Com base nisso, as decisões de projeto se concentraram em:

- reduzir ambiguidade na busca de endereço;
- melhorar a visualização no mapa;
- tornar recomendações mais próximas e realistas;
- destacar pressão territorial como critério de decisão;
- preservar navegação simples por abas.

---

## 14. Aderência ao Conteúdo Programático de IHC

| Conteúdo | Aderência do projeto |
|---|---|
| Introdução à IHC | O projeto considera usuário, interface, interação e contexto de uso. |
| Dispositivos de interação | Usa teclado, mouse, formulários e mapa interativo. |
| Estilos de interação | Usa menus, formulários, pergunta-resposta e manipulação direta. |
| Engenharia de usabilidade | Define metas, avalia uso e aplica melhorias. |
| Análise de usuários | Possui questionário de perfil e identificação de público-alvo. |
| Personas | Esta documentação define personas representativas. |
| Análise de tarefas | O projeto possui tarefa principal, tarefas secundárias e modelo GOMS. |
| Requisitos de usabilidade | Foram definidos critérios como eficácia, eficiência e prevenção de erro. |
| Princípios de design | Foram aplicadas heurísticas de Nielsen e organização visual. |
| Prototipagem | O sistema funciona como protótipo de alta fidelidade. |
| Avaliação | Houve questionário com usuários potenciais. |
| Análise de dados | Os resultados do questionário foram interpretados e usados em melhorias. |

---

## 15. Limitações

Apesar de atender a vários pontos de IHC, o projeto ainda pode evoluir:

- ampliar o número de participantes na avaliação;
- realizar teste observado com tarefas controladas;
- medir tempo de execução de tarefas diretamente no sistema;
- incluir comparação lado a lado entre UBSs;
- aplicar avaliação heurística formal por avaliadores externos.

---

## 16. Conclusão

A Rede de Acesso SP aplica conceitos de Interação Humano-Computador ao transformar uma modelagem de grafos em um sistema visual, interativo e orientado ao usuário. A interface busca facilitar a compreensão de dados territoriais complexos, permitindo que o usuário encontre UBSs próximas, compare pressão populacional e visualize resultados no mapa.

O projeto segue os principais tópicos de IHC ao considerar público-alvo, tarefas, estilos de interação, requisitos de usabilidade, princípios de design e avaliação com usuários. As melhorias realizadas ao longo do desenvolvimento mostram um processo iterativo, centrado na experiência de uso e na clareza da informação.
