# Fontes dos Dados

Este arquivo documenta a origem dos dados usados na entrega da Rede de Acesso SP.

## Arquivos do Projeto

| Arquivo | Conteudo | Fonte/origem |
| --- | --- | --- |
| `data/ubs_vertices.json` | UBSs usadas como vertices do grafo, com nome, endereco, CNES, distrito, coordenadas, populacao da AAUBS e populacao distrital preservada como contexto. | Equipamentos/servicos da SMS-SP; peso populacional associado por CNES a planilha AAUBS 2025 preliminar, CEInfo/SMS-SP e Censo 2022/IBGE. |
| `data/populacao_aaubs_2025.json` | Recorte tratado com os 71 vinculos CNES e a populacao estimada da area de abrangencia usada no peso dos vertices. | Derivado da planilha oficial AAUBS 2025 preliminar, variavel `V001AAUBS - Total de pessoas`. |
| `data/servicos.json` | Rede de servicos de saude usada como apoio contextual, incluindo hospitais SUS, UBSs e outros equipamentos. | Prefeitura de Sao Paulo/SMS, consulta de servicos de saude e Busca Saude. |
| `data/distritos.json` | Distritos administrativos, zona, centroide aproximado e populacao. | TABNET/SMS-SP para populacao intramunicipal e GeoSampa para divisao territorial. |
| `data/adjacencias.json` | Arestas/conexoes entre UBSs proximas e distancia aproximada em quilometros. | Gerado pelo projeto a partir das coordenadas das UBSs selecionadas. |
| `data/Sao Paulo.kml` / `data/São Paulo.kml` | Limite territorial do municipio e distritos usado para validar enderecos dentro de Sao Paulo. | GeoSampa/Mapa Digital da Cidade de Sao Paulo. |
| `grafo.txt` | Representacao textual final do grafo da disciplina. | Gerado pelo projeto a partir dos dados tratados acima. |

## Links Consultados

- Prefeitura de Sao Paulo - Secretaria Municipal da Saude: Servicos de Saude do Municipio de Sao Paulo  
  https://prefeitura.sp.gov.br/web/saude/w/estabelecimento_saude/311233

- Prefeitura de Sao Paulo - Busca Saude  
  https://buscasaude.prefeitura.sp.gov.br/

- Prefeitura de Sao Paulo - Areas de Abrangencia das UBSs  
  [Pagina oficial das AAUBS](https://prefeitura.sp.gov.br/saude/w/epidemiologia_e_informacao/geoprocessamento_e_informacoes_socioambientais/265863)

- SMS-SP/CEInfo - Dados demograficos e socioambientais por AAUBS 2025 preliminar (Censo 2022/IBGE)
  [Dados oficiais AAUBS 2025](https://drive.google.com/drive/folders/12w8xMlspq1f-yWxl_xRVFkv1p4psNMQZ?usp=sharing)

- SMS-SP - Quadro de parametros para territorializacao (Documento Norteador NUVIS-AB, versao 2025)
  [Quadro de territorializacao 2025](https://prefeitura.sp.gov.br/documents/d/saude/quadro_territorializacao_2025-pdf)

- GeoSampa - Download de dados geograficos do Mapa Digital da Cidade de Sao Paulo  
  https://download.geosampa.prefeitura.sp.gov.br/

- GeoSampa - Catalogo de Metadados Geograficos  
  https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/search

- Prefeitura de Sao Paulo/SMS - Populacao do Municipio de Sao Paulo por distrito, subprefeitura e regioes de saude  
  https://prefeitura.sp.gov.br/web/saude/w/tabnet/30417

## Rastreabilidade do Peso dos Vertices

| Item metodologico | Registro utilizado no projeto |
| --- | --- |
| Base efetivamente aplicada ao peso | Dados sociodemograficos por Area de Abrangencia de UBS (AAUBS 2025 preliminar), SMS-SP/CEInfo, estimados a partir do Censo Demografico 2022/IBGE |
| Variavel extraida | `V001AAUBS - Total de pessoas` |
| Chave de associacao | `CNESAAUBS` da base oficial associado ao campo `cnes` da UBS no projeto |
| Cobertura da associacao | `71 de 71` vertices associados a uma AAUBS |
| Limitacao do peso | Sem fonte publica completa de capacidade ou numero de equipes por UBS, o valor representa demanda territorial potencial, nao fila real ou tempo de espera. |

## Observacoes

- A base final do projeto nao replica integralmente as bases publicas. Ela usa um recorte tratado para fins academicos, mantendo apenas os campos necessarios para o funcionamento do sistema.
- Os 71 vertices foram associados a base AAUBS pelo codigo CNES. O peso do vertice representa a populacao residente estimada na area de abrangencia da UBS, utilizando `V001AAUBS - Total de pessoas`.
- A SMS-SP identifica populacao cadastrada por equipe e indicadores por UBS em sistemas de acesso restrito. Portanto, nao foi possivel incorporar capacidade ou numero de equipes de maneira publica e reproduzivel nesta entrega.
- O modelo interpreta menor populacao de abrangencia como menor demanda territorial potencial sob hipotese de capacidades comparaveis; nao afirma fila real nem tempo de espera garantido.
- As adjacencias do grafo nao sao uma fonte externa oficial: elas foram calculadas no projeto com base na proximidade geografica entre UBSs.
- Os enderecos e coordenadas devem ser entendidos como dados publicos tratados; caso seja necessaria validacao institucional, a referencia primaria deve ser a Prefeitura de Sao Paulo/SMS e o Busca Saude.
