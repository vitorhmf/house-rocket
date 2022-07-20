import pandas as pd
import streamlit as st
import folium
import numpy as np
import seaborn  as sns
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(layout='wide',
                   page_title = 'Sales Insights  by Vitor Ferreira',
                   page_icon='rocket')
@st.cache(allow_output_mutation=True)

def get_data (path):
    data = pd.read_csv (path)
    return data

def set_dashboard (data):

    # Lateral Menu:
    with st.sidebar:
        st.image('../image/house_rocket_logo.png')
        st.markdown('''---''')
        st.header('Dashboard Filter')

    f_group = st.sidebar.multiselect('House Group', data['house_group'].unique())

    with st.sidebar:
        st.header('🏠 House Group Description')
        st.write('''
            **- Group 1:** houses built 1990+, in good condition and good design.\n
            **- Group 2:** older houses, but in excellent condition.\n
            **- Group 3:** new and very cheap houses. To buy, renovate and sell.\n
            **- Group 4:** cheap houses, with sea views and good condition.\n
        ''')


    # Top of the Page:
    st.title('House Rocket Investment Dashboard')
    st.image('../image/seatle.jpg')
    
    # Filter:
    if (f_group !=[]):
        total_house = np.count_nonzero(data['price'].loc[data['house_group'].isin(f_group)])
        investment = sum(data['price'].loc[data['house_group'].isin(f_group)])
        revenue = sum(data['sale_price'].loc[data['house_group'].isin(f_group)])
        roi = revenue / investment -1
    else:
        total_house = np.count_nonzero(data['price'])
        investment = sum(data['price'])
        revenue = sum(data['sale_price'])
        roi = revenue / investment -1

    # Cards:
    c1, c2, c3, c4 = st.columns((1,1,1,1))
    c1.header(f'🏡 Total \n {total_house:.0f} Houses')
    c2.header(f'💲 Investment \n $ {investment:,.2f}')
    c3.header(f'➕ Revenue \n $ {revenue:,.2f}')
    c4.header(f'📈 ROI \n {roi:.1%}')

    st.markdown('''---''')

   ##############################################################################################
   
    # Map:  

    st.header('🌎 Map View')

    if (f_group !=[]):
        data_graf= data.loc[data['house_group'].isin(f_group), :]
    else:
        data_graf = data.copy()

    density_map = folium.Map(location = [data_graf['lat'].mean(), data_graf['long'].mean()],
                             width=1200,
                             height= 500,
                             default_zoom_start = 20,
                            )
                                        
    marker_cluster = MarkerCluster().add_to(density_map)

    for name, row in data_graf.iterrows():
        folium.Marker( [row['lat'], row['long']], 
            popup =  
                'Id: {0} \n Group: {4} \n Price: {1} \n Sale Price: {2} \n ROI(%): {3}'. format( 
                    row['id'],
                    row['price'],
                    row['sale_price'],
                    row['roi_%'],
                    row['house_group']
                    )).add_to(marker_cluster)
        
    
    folium_static(density_map, 1200, 500)

    st.markdown("""---""")

    ######################################################################################################

    # Graph

    st.header('📊 Features Overview')
    st.write(f'### Total Houses: {total_house:.0f}')

    if (f_group !=[]):
        data = data.loc[data['house_group'].isin(f_group), :]
    else:
        data = data.copy()

    # Conditions Graphs:
    plt.rcParams.update({'font.size': 7})
    fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,3))
    sns.countplot(data = data, x='grade', ax=ax1).set(xlabel=None)
    sns.countplot(data = data, x='condition', ax=ax2).set(xlabel=None)
    ax1.set_title('Design Grade')
    ax2.set_title('House Condition')

    fig1.set_tight_layout(True) # to prevent axis labels overlapping
    st.pyplot(fig1)

    # Price_group and Better Season
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,3))
    sns.countplot(data = data, x='price_group', ax=ax1).set(xlabel=None)
    sns.countplot(data = data, x='better_season_to_sell', ax=ax2).set(xlabel=None)
    ax1.set_title("Price/m2 Compared to the Regional Median")
    ax2.set_title('Better Season to Sell')
    fig2.set_tight_layout(True) # to prevent axis labels overlapping
    st.pyplot(fig2)

    # Zip Code:
    fig3, ax1 = plt.subplots(figsize=(12,3))
    sns.countplot(data = data, x='zipcode', ax=ax1).set(xlabel=None)
    plt.xticks (rotation=90);
    ax1.set_title('Zip Code')
    fig3.set_tight_layout(True)
    st.pyplot(fig3)

    # Year Built    
    fig4, ax1 = plt.subplots(figsize=(12, 3))
    sns.countplot(data = data, x='yr_built', ax=ax1).set(xlabel=None)
    plt.xticks (rotation=90);
    ax1.set_title('Year Built')
    fig4.set_tight_layout(True)
    st.pyplot(fig4)

    st.markdown("""---""")

#####################################################################################################

    # Table
    st.header('📋 Complete Details')
    st.dataframe(data[['id',
                       'house_group',                                          
                       'yr_built',
                       'condition',
                       'grade',
                       'm2_living',
                       'bedrooms',
                       'bathrooms',
                       'floors',
                       'waterfront',
                       'better_season_to_sell',
                       'price_m2',
                       'median_price_m2_zipcode',
                       'price_group',
                       'price',
                       'sale_price',
                       'roi_%']], height=500)


    
    st.markdown("""---""")

#####################################################################################################
    
    #Configurações de contatos:
    st.header('📞 Contacts')
    st.write('''[🤝 Linkedin](https://www.linkedin.com/in/vitorhmf/) │ 
                [💼 Portfolio](https://vitorhmf.github.io/portfolio/) |
                [📁 GitHub](https://github.com/vitorhmf)''' )

    return None    

#####################################################################################################

if __name__ == '__main__':
    path = '../data/suggestion_list.csv'
    data = get_data(path)
    set_dashboard (data)