import pandas as pd
import streamlit as st
import folium
import numpy as np
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(layout='wide',
                   page_title = 'Projeto House Rocket by Vitor Ferreira',
                   page_icon='rocket')
@st.cache(allow_output_mutation=True)

def get_data (path):
    data = pd.read_csv (path)
    return data


def set_feature (data):
    
    data['date'] = pd.to_datetime(data['date'])
    data['month'] = data['date'].dt.month
    data['year'] = data['date'].dt.year
    data['price_m2'] = data['price'] / data['sqft_lot']
    
    # Adicionando a coluna season
    for i in range(len(data)):
        if (data.loc[i, 'month'] <= 2 ) or (data.loc[i, 'month'] == 12):
            data.loc[i, 'season'] = 'Inverno'
        elif data.loc[i, 'month'] <= 5:
            data.loc[i, 'season'] = 'Primavera'
        elif data.loc[i, 'month'] <= 8:
            data.loc[i, 'season'] = 'Verão'
        else:
            data.loc[i, 'season'] = 'Outono'

    # Cálculo da mediana por região:
    df = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()
    df = df.rename(columns={'price': 'median_price'})
    data = pd.merge( data, df, on='zipcode', how='inner')

    # Definindo regra para comprar ou não comprar (preço 30% abaixo da mediana e condição maior ou igual a 4):
    for i in range(len(data)):
        if (data.loc[i, 'price'] < (data.loc[i, 'median_price']* 0.7)) & (data.loc[i, 'condition'] >= 4):
            data.loc[i, 'status'] = 'buy'
        else:
            data.loc [i, 'status'] = 'not_buy'  
    data_buy = data[(data['status'] == 'buy')] [['id', 'condition', 'date', 'season', 'zipcode', 'lat', 'long', 'price', 'median_price' ]]
    data_buy['%_difference'] = data_buy['price'] / data_buy['median_price']

    # Montando a tabela com as sugestões de compra:
    df_temp = data[['zipcode', 'season', 'price']].groupby(['zipcode', 'season']).median().reset_index()
    for i in range(len(df_temp)):
        df_temp.loc[i, 'concat'] = str(df_temp.loc[i, 'zipcode']) + '_' + str(df_temp.loc[i, 'price'])

    # Criando a tabela de "melhores condições"
    better_season = df_temp[['zipcode', 'price']].groupby('zipcode').max().reset_index()
    for i in range(len(better_season)):
        better_season.loc[i, 'concat'] = str(better_season.loc[i, 'zipcode']) + '_' + str(better_season.loc[i, 'price'])
    better_season = pd.merge( better_season, df_temp[['concat', 'season']], on='concat', how='inner')
    better_season.columns = ['zipcode', 'max_price', 'concat', 'better_season']
    data_complete = pd.merge (data_buy, better_season[['zipcode', 'better_season', 'max_price']], on='zipcode', how='inner')

    # Adicionando a sugestão de preço à tabela principal (data_complete):
        # Sugestão de preço de revenda: 40% de lucro do preço de compra. 
    for i in range(len(data_complete)):
        data_complete.loc[i, 'sale_price'] = data_complete.loc[i, 'price'] * 1.4

    # Montando a tabela final:
    data_complete['profit'] = data_complete['sale_price'] - data_complete['price']
    data_final = data_complete[['zipcode', 'id', 'condition', 'median_price', 'price', 'sale_price', 'profit', 'better_season', 'max_price', 'lat', 'long']]
    data_final.columns = ['Zipcode', 'Id', 'Condição do Imóvel', 'Preço Médio da Região', 'Preço de Compra', 'Sugestão de Venda', 'Lucro', 'Quando Vender?', 'Melhor Média', 'Latitude', 'Longitude']

    return data_final

def overview (data):

    #Configuração da pagina:   
    st.title('Projeto House Rocket')
    st.image('seatle.jpg')
    st.write('### Identificação de imóveis para compra e revenda a fim de maximizar o lucro')
    st.markdown('A partir da análise exploratória dos dados de um portfólio com aproximadamente 22 mil imóveis em Seatle, foram selecionadas 811 casas como sugestão de compra. Todas estão anunciadas pelo menos 30% abaixo da média de preço da região e estão classificadas com um ótimo estado de conservação (notas 4 e 5 em uma escala de 1 a 5).')
    st.markdown('Com relação a estratégia comercial, foi analisado o período do ano em que cada região apresentava maior média de preços, definindo assim quando é melhor revender cada imóvel. E a precificação foi estipulada buscando um ROI de 40% do investimento realizado.')

    #Configuração do menu lateral:
    with st.sidebar:
        st.image('house_rocket_logo.png')
        st.header('Etapas do projeto')
        st.markdown('''
            📋 [Visão Geral do Portfólio de Imóveis](#identifica-o-de-im-veis-para-compra-e-revenda-a-fim-de-maximizar-o-lucro) \n
            📈 [Análise do Investimento](#an-lise-do-investimento) \n
            💡 [Hipóteses de Negócio](#hip-teses-de-neg-cio) \n
            📞[Contatos](#contatos)
            ''', unsafe_allow_html=True)
        st.markdown('''---''')
        st.header('Análise dos Imóveis Selecionados')

    #Visão Geral dos dados
    st.header( 'Visão Geral do Portfólio de Imóveis' )
    st.dataframe(data)

    c1, c2 = st.columns((1,1))

    c1.write('### Valores Médios')
    df1 = data[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df2 = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df3 = data[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = data[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()

    m1 = pd.merge( df1, df2, on='zipcode', how='inner')
    m2 = pd.merge(m1, df3, on='zipcode', how='inner')
    df = pd.merge(m2, df4, on='zipcode', how='inner')
    df.columns = ['Zipcode', 'Qtde Imóveis', 'Preço', 'Área', 'Preço/m2']
    c1.dataframe(df, height=500)

    c2.write('### Análise Descritiva')
    num_attributes = data.select_dtypes(include=['int64', 'float64'])
    media   = pd.DataFrame(num_attributes.apply(np.mean))
    mediana = pd.DataFrame(num_attributes.apply(np.median))
    std     = pd.DataFrame(num_attributes.apply(np.std))
    max_    = pd.DataFrame(num_attributes.apply(np.max))
    min_    = pd.DataFrame(num_attributes.apply(np.min))

    df1 = pd.concat( [max_, min_, media, mediana, std], axis=1 ).reset_index()
    df1.columns = ['Atributo', 'Max', 'Min', 'Média', 'Mediana', 'Desvio']
    c2.dataframe(df1, height=500)

    st.markdown("""---""")
    
    return None


def answer (data_final):
    
    f_attributes = st.sidebar.multiselect('Selecione as informações que deseja avaliar', data_final.columns)
    f_zipcode = st.sidebar.multiselect('Escolha a região', data_final['Zipcode'].unique())

    st.header( 'Análise do Investimento' )
    st.write('### Retorno do Investimento')
    if (f_zipcode !=[]):
        qtde_imoveis = np.count_nonzero(data_final['Preço de Compra'].loc[data_final['Zipcode'].isin(f_zipcode)])
        investimento = sum(data_final['Preço de Compra'].loc[data_final['Zipcode'].isin(f_zipcode)])
        receita = sum(data_final['Sugestão de Venda'].loc[data_final['Zipcode'].isin(f_zipcode)])
        roi = receita / investimento -1
    else:
        qtde_imoveis = np.count_nonzero(data_final['Preço de Compra'])
        investimento = sum(data_final['Preço de Compra'])
        receita = sum(data_final['Sugestão de Venda'])
        roi = receita / investimento -1

    c1, c2, c3, c4 = st.columns((1,1,1,1))
    c1.write(f'Qtd de Imóveis: {qtde_imoveis:.0f}')
    c2.write(f'Investimento: R$ {investimento:,.2f}')
    c3.write(f'Receita: R$ {receita:,.2f}')
    c4.write(f'ROI: {roi:.0%}')

    #Imóveis selecionados:
    st.write('### Descrição dos Imóveis Selecionados')

    if (f_zipcode !=[]) & (f_attributes !=[]):
        data_table = data_final.loc[data_final['Zipcode'].isin(f_zipcode), f_attributes]
    elif (f_zipcode !=[]) & (f_attributes == []):
        data_table = data_final.loc[data_final['Zipcode'].isin(f_zipcode), : ]
    elif (f_zipcode == []) & (f_attributes !=[]):
        data_table = data_final.loc[: , f_attributes]
    else:
        data_table = data_final.copy()

    st.dataframe(data_table)

    # Gráfico com o Folium:
  

    st.write('### Visualização no Mapa')
    # Filtro do gráfico
    if (f_zipcode !=[]):
        data_graf= data_final.loc[data_final['Zipcode'].isin(f_zipcode), :]
    else:
        data_graf = data_final.copy()

    # Plotar o gráfico
    density_map = folium.Map(location = [data_graf['Latitude'].mean(), data_graf['Longitude'].mean()],
                             width='100%',
                             height= '80%',
                             default_zoom_start = 15,
                            )
                                        
    marker_cluster = MarkerCluster().add_to(density_map)

    for name, row in data_graf.iterrows():
        folium.Marker( [row['Latitude'], row['Longitude']], 
            popup =  
                'Id: {0} \n Zipcode: {1}'. format( 
                    row['Id'],
                    row['Zipcode'])).add_to(marker_cluster)
        
    
    folium_static(density_map)

    st.markdown("""---""")
    
    return None

def analysis(data):
    st.header('Hipóteses de Negócio')
    st.write('Abaixo são apresentadas análises complementares dos dados, validando hipóteses que possam gerar ações e auxiliar no direcionamento da tomada de decisão da empresa.')

    #1:
    st.write('#### Hipótese 1: o crescimento do preço dos imóveis de 2014 para 2015 foi de 10%.')
    #st.subheader('Hipótese 1: o crescimento do preço dos imóveis de 2014 para 2015 foi de 10%.')
    price_yr = data[['price', 'year']].groupby('year').mean().reset_index()
    yoy = price_yr.loc[1, 'price'] / price_yr.loc[0, 'price'] -1
    st.write(f'R: o crescimento médio dos preços no período foi de {yoy:.1%}.')

    #2:
    st.write('#### Hipótese 2: imóveis que possuem vista para água são 20% mais caros na média.')
    price_wf = data[['waterfront', 'price']].groupby('waterfront').mean().reset_index()
    price_wf = price_wf.loc[1, 'price'] / price_wf.loc[0, 'price'] -1
    st.write(f'R: imóveis com vista para a água são {price_wf:.1%} mais caros que os demais.')

    #3:
    st.write('#### Hipótese 3: a área dos imoveis com vista para a agua, em média, é 50% maior que os demais.')
    wf_1 = data[data['waterfront'] == 1]['sqft_lot'].mean()
    wf_0 = data[data['waterfront'] == 0]['sqft_lot'].mean()
    rate_wf = wf_1 / wf_0 -1
    st.write(f'R: os imóveis que possuem vista para a água são, em média, {rate_wf:.1%} maiores que os demais.')

    #4:
    st.write('#### Hipótese 4: imóveis sem porão possuem área total 40% maior que os imoveis com porão.')
    without_basement = data[(data['sqft_basement'] == 0)]['sqft_lot'].mean()
    with_basement = data[(data['sqft_basement'] > 0)] ['sqft_lot'].mean()
    rate_basement = without_basement / with_basement -1
    st.write(f'R: Imóveis sem porão possuem uma área em média {rate_basement:.1%} maior que os imóveis com porão.')

    #5: Hipótese sem ação (colocar MoM na primeira questão faz mais sentido do que YoY)
    st.write('#### Hipótese 5: imóveis com 3 banheiros tiveram um crescimento de 15% ao mês (MoM)')
    bathroom3 = data[(data['bathrooms'] == 3)][['price', 'year', 'month']]
    bathroom3 = bathroom3[['price', 'year', 'month']].groupby(['year', 'month']).mean().reset_index()
    bathroom3['diff'] = bathroom3['price'].diff()
    bathroom3['MoM'] = bathroom3['price'].pct_change()
    bathroom3

    #6:
    st.write('#### Hipótese 6: imóveis que foram reformados e estão em boas condições são, em média, 20% mais caros que os não reformados nas mesmas condições.')
    condition3_4 = data[(data['condition'] == 3) | (data['condition'] == 4)] [['price', 'yr_renovated', 'condition']]
    not_renovated = condition3_4[(condition3_4['yr_renovated'] == 0)].mean()
    renovated = condition3_4[(condition3_4['yr_renovated'] != 0)].mean()
    ratio3_4 = renovated['price'] / not_renovated['price'] -1
    st.write(f'R: Os imóveis reformados são em média {ratio3_4:.1%} mais caros que imóveis nas mesmas condições que não foram reformados.')

    #7:
    st.write('#### Hipótese 7: imóveis em más condições são 20% mais baratos que imoveis em boas condições.')
    condition = data[['price', 'condition']].groupby('condition').mean().reset_index()
    mean_bad = condition[(condition['condition'] <=2)]['price'].mean()
    mean_good = condition[(condition['condition'] > 2 ) & (condition['condition'] < 5)]['price'].mean()
    mean_great = condition[(condition['condition'] == 5)]['price'].mean()
    ratio_bad_good = 1- mean_bad / mean_good 
    ratio_bad_great = 1- mean_bad / mean_great
    st.write(f'R: Imóveis em más condições são em média {ratio_bad_good:.1%} mais baratos que imóveis em boas condições e são {ratio_bad_great:.1%} mais baratos que imóveis em ótimas condições.')

    #8:.\venve
    st.write('#### Hipótese 8: imóveis construídos depois dos anos 2000 possuem área total 20% menor que os demais.')
    mean_2000 = data[data['yr_built'] >= 2000] ['sqft_lot']. mean()
    mean_1900 = data[data['yr_built'] < 2000] ['sqft_lot']. mean()
    ratio_sqft2000 = 1- mean_2000 / mean_1900
    st.write(f'R: Imóveis construídos depois dos anos 2000 são em média {ratio_sqft2000:.1%} menores que os demais.')

    #9:
    st.write('#### Hipótese 9: imoveis construídos depois dos anos 2000 são 30% mais caros que os demais')
    price_1900 = data[data['yr_built'] < 2000] ['price']. mean()
    price_2000 = data[data['yr_built'] >= 2000] ['price']. mean()
    ratio_price2000 = price_2000 / price_1900 -1
    st.write(f'R: Imóveis construídos depois dos anos 2000 são em média {ratio_price2000:.1%} mais caros que os demais.')

    #10:
    st.write('#### Hipótese 10: imóveis com data de construção menor que 1955 são 50% mais baratos na média.')
    # Mediana de preço dos imoveis construidos depois de 1955
    over_55 = data[(data['yr_built'] > 1955)]['price'].mean()
    under_55 = data[(data['yr_built'] <= 1955)]['price'].mean()
    ratio_price55 = 1- under_55 / over_55
    st.write(f'R: Imóveis construídos antes de 1955 são em média {ratio_price55:.1%} mais baratos.')
    st.write('*Os dados utilizados nesse projeto são fictícios e foram retirados do site: https://www.kaggle.com/datasets/shivachandel/kc-house-data')
    
    #Configurações de contatos:
    st.markdown("""---""")
    st.header('Contatos')
    st.write('''[🤝 Linkedin](https://www.linkedin.com/in/vitorhmf/) │ 
                [💼 Portfólio](https://vitorhmf.github.io/portfolio/) |
                [📁 GitHub](https://github.com/vitorhmf)''' )
    with st.sidebar:
        st.markdown("""---""")
        st.header('Sobre o Autor')
        st.image('perfil.jpg')
        st.write('Olá! Meu nome é Vitor Ferreira, tenho 14 anos de experiência de mercado com foco em Gestão de Negócios e Gestão Comercial.')
        st.write('Sou apaixonado por Ciência de Dados e acredito que a cada dia a análise de dados vai influenciar mais na tomada de decisão de empresas e líderes, independente da sua área de atuação.')
        st.markdown("""---""")
        st.header('Contatos')
        st.write('''[🤝 Linkedin](https://www.linkedin.com/in/vitorhmf/) │ 
                    [💼 Portfólio](https://vitorhmf.github.io/portfolio/) |
                    [📁 GitHub](https://github.com/vitorhmf)''' )
    return None

if __name__ == '__main__':
    path = 'kc_house_data.csv'
    data = get_data(path) 
    data_final = set_feature(data)
    overview (data)
    answer(data_final)
    analysis(data)