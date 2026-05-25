# Roteiro de Video - Rede de Acesso SP

**Duracao planejada:** 4 min 20 s  
**Limite da entrega:** 5 min  
**Sistema:** https://redeasp.streamlit.app/  
**Repositorio:** https://github.com/Lucas-FcNw/rede-de-acesso-sp

## Antes de Gravar

Preencher:

- **Professor:** [nome do professor]
- **Curso:** [nome exato do curso]
- **Instituicao:** Universidade Presbiteriana Mackenzie - Faculdade de Computacao e Informatica

Deixar abertas estas telas:

- slide inicial ou capa do relatorio;
- aplicativo na aba `Mapa`, sem busca realizada;
- aplicativo nas abas `Analise`, `Cobertura` e `Metodo`;
- repositorio no GitHub.

Usar como demonstracao uma busca curta e testada, por exemplo:

```text
Rua Piaui, 144, Higienopolis
```

## Roteiro Cronometrado

### 0:00 - 0:25 | Apresentacao

**Tela:** capa com titulo e nomes.

**Fala:**

> Ola. Este e o projeto **Rede de Acesso SP - Saude Territorial em Sao Paulo**, desenvolvido para a disciplina de **Teoria dos Grafos**, ministrada pelo professor **[nome do professor]**, no curso de **[nome do curso]** da **Universidade Presbiteriana Mackenzie - Faculdade de Computacao e Informatica**. Os integrantes sao **Lucas Fernandes de Camargo**, **Lendy Naiara Pacheco** e **Anna Luiza Santos**.

### 0:25 - 1:00 | Problema Real e ODS

**Tela:** inicio do aplicativo ou secao de introducao do relatorio.

**Fala:**

> O problema abordado e o acesso desigual a Unidades Basicas de Saude na cidade de Sao Paulo. Uma pessoa pode ter diversas UBSs relativamente proximas, mas a unidade mais perto nem sempre e a que apresenta a melhor possibilidade relativa de atendimento. Regioes com maior populacao e poucas unidades podem sofrer maior pressao de demanda. O projeto se relaciona a **ODS 10 - Reducao das Desigualdades**, pois auxilia na visualizacao das diferencas territoriais de acesso a servicos publicos de saude.

### 1:00 - 1:55 | Modelagem por Grafos

**Tela:** aba `Metodo`, exibindo estatisticas e grafo completo; opcionalmente mostrar o diagrama do relatorio.

**Fala:**

> Para modelar essa situacao, construimos um grafo nao direcionado e ponderado. Cada **vertice** representa uma UBS real. O **peso do vertice** e a populacao residente estimada na **area de abrangencia da UBS**, associada pelo codigo CNES usando uma base publica da Secretaria Municipal da Saude e do Censo 2022. As **arestas** conectam unidades geograficamente proximas, e o **peso das arestas** representa a distancia aproximada em quilometros.
>
> O grafo final possui **71 vertices** e **215 arestas**, e e conexo, portanto existe caminho entre quaisquer duas UBSs do recorte. Sua densidade e **0,0865**, indicando uma rede esparsa, pois conectamos apenas unidades proximas, e nao todas entre si.

### 1:55 - 2:25 | Fundamentos Utilizados

**Tela:** continuar na aba `Metodo`, apontando para o grafo e indicadores.

**Fala:**

> Entre os fundamentos de Teoria dos Grafos utilizados estao grau dos vertices, densidade, conectividade, centralidade, busca em largura e caminhos minimos. A **BFS** permite analisar alcance por quantidade de conexoes. O algoritmo de **Dijkstra** calcula caminhos minimos considerando as distancias das arestas. Tambem verificamos propriedades estruturais: o grafo e conexo, mas nao e euleriano, pois possui mais de dois vertices de grau impar.

### 2:25 - 3:35 | Execucao da Aplicacao

**Tela:** aba `Mapa`; realizar a busca ao vivo.

**Acao:** digitar `Rua Piaui, 144, Higienopolis` e clicar em `Buscar UBSs recomendadas`.

**Fala:**

> Na aplicacao, o usuario informa um endereco dentro do municipio de Sao Paulo. Vou utilizar como exemplo a Rua Piaui, numero 144, em Higienopolis. O sistema localiza o endereco, delimita UBSs proximas inicialmente em um raio de 6 quilometros, podendo expandir ate 12 quilometros caso existam poucas opcoes.
>
> A recomendacao nao escolhe simplesmente a UBS mais proxima. Entre as unidades viaveis no entorno, o sistema prioriza aquela cuja area de abrangencia possui menor populacao estimada. O indicador ideal tambem consideraria capacidade ou numero de equipes da UBS; entretanto, esses dados aparecem nas fontes oficiais em sistemas de acesso restrito. Por isso, o projeto apresenta uma estimativa de demanda territorial potencial, e nao uma garantia de fila menor ou tempo real de atendimento. No mapa, vemos o ponto de origem, a UBS recomendada e a rota.

**Acao:** mostrar rapidamente os cards de recomendacao e o painel com motivo/caminho.

### 3:35 - 4:00 | Analise e Cobertura

**Tela:** alternar rapidamente para `Analise` e depois `Cobertura`.

**Fala:**

> Na aba **Analise**, e possivel selecionar uma UBS e observar a populacao estimada de sua area de abrangencia, o indice relativo e a comparacao com unidades vizinhas. Na aba **Cobertura**, o sistema apresenta o ranking das UBSs com menor e maior demanda territorial estimada, permitindo comparar diferentes territorios de Sao Paulo.

### 4:00 - 4:20 | GitHub e Encerramento

**Tela:** repositorio do GitHub na pagina inicial, mostrando `src`, `data`, `README.md` e documentacoes.

**Fala:**

> O codigo-fonte do projeto esta disponivel no GitHub, no repositorio **Lucas-FcNw/rede-de-acesso-sp**, contendo a aplicacao Streamlit, os modulos do grafo e das metricas, os dados finais e a documentacao. A aplicacao publicada esta disponivel em **redeasp.streamlit.app**. Assim, a Rede de Acesso SP aplica conceitos de Teoria dos Grafos a um problema real de acesso territorial a saude. Obrigado.

## Checklist da Gravacao

- Preencher professor e curso antes de gravar.
- Mostrar titulo, integrantes, disciplina, curso e instituicao.
- Mencionar explicitamente a ODS 10.
- Mostrar a busca funcionando no site publicado.
- Mostrar rapidamente as abas `Analise`, `Cobertura` e `Metodo`.
- Abrir o repositorio do GitHub durante o video.
- Confirmar que o video ficou com no maximo 5 minutos.
- Publicar o video como publico no YouTube.
- Trocar no relatorio o link generico do YouTube pelo link definitivo do video.
