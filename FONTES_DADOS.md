# Fontes dos Dados

Este arquivo documenta a origem dos dados usados na entrega da Rede de Acesso SP.

## Arquivos do Projeto

| Arquivo | Conteudo | Fonte/origem |
| --- | --- | --- |
| `data/ubs_vertices.json` | UBSs usadas como vertices do grafo, com nome, endereco, CNES, distrito, coordenadas e populacao de referencia. | Derivado da base de equipamentos/servicos de saude da Prefeitura de Sao Paulo/SMS e complementado com populacao por distrito. |
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
  https://prefeitura.sp.gov.br/saude/w/epidemiologia_e_informacao/geoprocessamento_e_informacoes_socioambientais/265863

- GeoSampa - Download de dados geograficos do Mapa Digital da Cidade de Sao Paulo  
  https://download.geosampa.prefeitura.sp.gov.br/

- GeoSampa - Catalogo de Metadados Geograficos  
  https://metadados.geosampa.prefeitura.sp.gov.br/geonetwork/srv/search

- Prefeitura de Sao Paulo/SMS - Populacao do Municipio de Sao Paulo por distrito, subprefeitura e regioes de saude  
  https://prefeitura.sp.gov.br/web/saude/w/tabnet/30417

## Observacoes

- A base final do projeto nao replica integralmente as bases publicas. Ela usa um recorte tratado para fins academicos, mantendo apenas os campos necessarios para o funcionamento do sistema.
- As populacoes usadas como peso dos vertices representam a populacao de referencia do distrito/territorio associado a cada UBS.
- As adjacencias do grafo nao sao uma fonte externa oficial: elas foram calculadas no projeto com base na proximidade geografica entre UBSs.
- Os enderecos e coordenadas devem ser entendidos como dados publicos tratados; caso seja necessaria validacao institucional, a referencia primaria deve ser a Prefeitura de Sao Paulo/SMS e o Busca Saude.
