# Projeto House Rocket

![seatle](https://user-images.githubusercontent.com/96602900/168178443-fba09fb3-8716-4fa2-be24-90f71bcbcfff.jpg)

## Identificação de imóveis para compra e revenda a fim de maximizar o lucro

## Contexto:

A House Rocket atua no ramo imobiliário e utiliza a tecnologia para simplificar a venda e compra de imóveis. Em uma próxima rodada de investimento, o CEO da empresa está com um portifólio com cerca de 22 mil imóveis, localizados em Seattle, e precisa definir como será destinado esse investimento e qual a expectativa de retorno 



*Obs.: os dados utilizados nesse projeto são fictícios e foram retirados do site: https://www.kaggle.com/datasets/shivachandel/kc-house-data

## Questões de Negócio:
### 1. Quais são os imóveis que a House Rocket deveria comprar e por qual preço?
### 2. Uma vez a casa comprada, qual o melhor momento para vendê-las e por qual preço?

Para construir a solução desejada, foi realizada a análise exploratória dos dados do portfólio de imóveis e foram selecionadas 811 casas como sugestão de compra. Essa seleção foi feita escolhendo os imóveis que estavam pelo menos 30% abaixo da média de preço da região e que estavam classificados com um ótimo estado de conservação (notas 4 e 5 em uma escala de 1 a 5).

Com relação a estratégia comercial, foi analisado o período do ano em que cada região apresentava maior média de preços, definindo assim quando é melhor revender cada imóvel. E a precificação foi estipulada buscando um ROI de 40% do investimento realizado.

## Apresentação da Solução:

Para apresentar as respostas das questões de negócio, foi desenvolvido um dashboard contendo:
  - Visão Geral do Portfólio: nessa etapa é apresentado o dataset original e feita uma analise estatística descritiva dos dados.
  - Análise do Investimento: a análise do investimento foi feita apresentando uma descrição do ROI, dos imóveis selecionados e a visualização no mapa.
  - Hipóteses de Negócio: análises complementares dos dados, validando hipóteses que possam gerar ações e auxiliar no direcionamento da tomada de decisão da empresa.

Link da solução: https://house-rocket-vitorhmf.herokuapp.com/

## Ferramentas utilizadas:

- Python, Pandas, Numpy e Seaborn.
- VS Code e Jupyter Notebook.
- Mapas interativos com Folium.
- Streamlit Python framework web.
- Heroku Cloud.

## Referências:

- O projeto apresentado foi desenvolvido na [Comunidade DS](https://www.comunidadedatascience.com/)
- Os dados utilizados nesse projeto são fictícios e estão disponíveis no [Kaggle](https://www.kaggle.com/datasets/shivachandel/kc-house-data)

