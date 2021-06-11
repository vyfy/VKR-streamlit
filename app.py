import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
import csv
import altair as alt
import pydeck as pdk
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from PIL import Image
import warnings
import plotly.graph_objects as go
import plotly.express as px

warnings.filterwarnings("ignore")

page = st.sidebar.selectbox("Выберите страницу",
                            ["Главная", "Сильная жара", "Сильный мороз", "Сильный ветер", "Тропический циклон",
                             "Сильный дождь", "Видимость", "Ураганный ветер", "Влажность", "Песчаные бури",
                             "Сильный туман",
                             "Реки"])
if page == "Главная":
    st.header("Приложение по визуализации ОЯ")
    st.write("Пожалуйста, для дальнейшей работы выберите страницу слева.")
    st.markdown("""
        Это приложение позволяет визуализировать идентификацию опасных явлений в природе, основываясь на данных, полученных от ** ЕСИМО ** .
        Выявляются наиболее свежие ОЯ по региону, соответствуя дате обновления данных на сайте.
        
Предоставляется возможность выбора и сортировки ключевых параметров по различным ОЯ: уровень опасности, скорость ветра, давление, температура. Например, выбрать диапазон температур для ОЯ типа "Сильная жара".
        Проект призван решить проблему ручного выявления ОЯ и показать возможности перевода данной сферы на автоматизацию и возможность своевременной доставки сообщений об ОЯ пользователям. 
        Проект реализован с помощью современных технологий, использовались знания о Big Data, науке о данных и различные возможновсти по визуализации и анализу. 
        """)
    image = Image.open('homepage.jpg')
    st.image(image, caption='Проект по автоматизации выявления ОЯ')

    st.header("Пример использования приложения")
    video_file = open('example.webm', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

    st.markdown("""
            Создал **Черкашин Владислав Олегович**
            """)


elif page == "Сильная жара":
    st.title('Сильная жара ОЯ')
    st.markdown("""
    В период с мая по август значение максимальной температуры воздуха достигает установленного для данной территории или выше его.
    Во время летних периодов повышенной температуры обычно наблюдается рост смертности среди людей старческого возраста, больных гипертонической болезнью,
     тяжелобольных. Повышенная температура также негативно влияет на работоспособность здоровых людей, делает дневную работу малоэффективной.""")
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("hot.csv")

    values = st.sidebar.slider(
        'Выберите диапазон температур',
        21.0, 50.0, (21.0, 50.0), key='slider-1')
    st.sidebar.write('Диапазон температур:', values[0], values[1])
    df = df[(df['Temperature'] >= values[0]) & (df['Temperature'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-1')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="hot.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение температуры в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['Temperature'])

    st.write("""
        ## Температура в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['Temperature'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    temperature = df_selected_sector['Temperature']


    def color_change(temp):
        """
        21-25 град С – желтый, 26-30 – оранжевый, >30 красный.
        """
        if float('21.0') <= float(temp) <= float('25.0'):
            return "orange"
        elif float('25.0') < float(temp) <= float('30.0'):
            return "lightred"
        elif float(temp) > float('30.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, temperature in zip(lat, lon, elevation, temperature):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(temperature) + "C",
                      icon=folium.Icon(color=color_change(float(temperature)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Сильный мороз":
    st.title('Сильный мороз ОЯ')
    st.markdown("""
    Значение минимальной температуры воздуха достигает установленного для данной территории опасного значения или ниже его.
    Высокий риск случаев обморожения.
    Такая погода приводит к авариям в жилищно-коммунальном хозяйстве, а также к вымерзанию сельскохозяйственных культур и зеленых насаждений.
    """)
    st.sidebar.header('Функции пользовательской настройки')

    df1 = pd.read_csv("cold.csv")

    values = st.sidebar.slider(
        'Выберите диапазон температур',
        -100.0, -24.0, (-100.0, -24.0), key='slider-2')
    st.sidebar.write('Диапазон температур:', values[0], values[1])
    df1 = df1[(df1['Temperature'] >= values[0]) & (df1['Temperature'] <= values[1])]

    sector1 = df1.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique1 = sorted(df1['danger'].unique())
    selected_sector1 = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique1, sorted_sector_unique1,
                                              key='sidebar-2')

    # Filtering data
    df_selected_sector1 = df1[(df1['danger'].isin(selected_sector1))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector1.shape[0]) + ' строк и ' + str(
        df_selected_sector1.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector1)


    def filedownload(df1):
        csv = df1.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="cold.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector1), unsafe_allow_html=True)

    st.write("""
    ## Распредедение температуры в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector1['Temperature'])

    st.write("""
    ## Температура в выбранном диапазоне по станциям
    """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector1['Temperature'], y=df_selected_sector1['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df1['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat1 = df_selected_sector1['latitude']
    lon1 = df_selected_sector1['longitude']
    elevation1 = df_selected_sector1['platform_name']
    temperature1 = df_selected_sector1['Temperature']


    def color_change1(temp):
        """
        -25 град С – желтый, -25-30 – оранжевый, <-30 красный.
        """
        if float('-25.0') <= float(temp) <= float('-24.0'):
            return "orange"
        elif float('-25.0') > float(temp) >= float('-30.0'):
            return "lightred"
        elif float(temp) < float('-30.0'):
            return "red"


    # center on Liberty Bell
    m1 = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m1)
    for lat1, lon1, elevation1, temperature1 in zip(lat1, lon1, elevation1, temperature1):
        folium.Marker(location=[lat1, lon1], popup=str(elevation1) + " " + str(temperature1) + "C",
                      icon=folium.Icon(color=color_change1(float(temperature1)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m1)


elif page == "Сильный ветер":
    st.title('Сильный ветер ОЯ')
    st.markdown(
        """
        По данным Росгидромета, это сильный ветер, с которым связана почти треть ЧС.
        Они наносят самый большой ущерб, так как развиваются очень быстро и неожиданно: их почти невозможно спрогнозировать, и к ним трудно заранее подготовиться.
        """
    )
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("wind.csv")

    values = st.sidebar.slider(
        'Выберите диапазон ветров',
        10.0, 90.0, (10.0, 90.0), key='slider-3')
    st.sidebar.write('Диапазон ветров, м/с:', values[0], values[1])
    df = df[(df['wind_speed'] >= values[0]) & (df['wind_speed'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-3')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="wind.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение ветра в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['wind_speed'])

    st.write("""
        ## Ветер в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['wind_speed'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    wind_speed = df_selected_sector['wind_speed']


    def color_change(temp):
        """
        Если ff=10-14 м/с, то УО=Ж.
        Если ff=15-20 м/с, то УО=O.
        Если ff=>20 м/с, то УО=К.
        """
        if float('10.0') <= float(temp) < float('15.0'):
            return "orange"
        elif float('15.0') <= float(temp) <= float('20.0'):
            return "lightred"
        elif float(temp) > float('20.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, wind_speed in zip(lat, lon, elevation, wind_speed):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(wind_speed) + "м/c",
                      icon=folium.Icon(color=color_change(float(wind_speed)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Тропический циклон":
    st.title('Тропический циклон ОЯ')
    st.markdown(
        """
        Тип циклона, или погодной системы низкого давления, которая возникает над тёплой морской поверхностью и сопровождается мощными грозами, выпадением ливневых осадков и ветрами штормовой силы.
        А в совокупности эти опасности взаимодействуют друг с другом и существенно увеличивают вероятность гибели людей и причинения материального ущерба.
        """
    )
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("trop.csv")

    values = st.sidebar.slider(
        'Выберите диапазон ветров,м/с',
        0.0, 90.0, (0.0, 90.0), key='slider-4')
    st.sidebar.write('Диапазон ветров, м/с:', values[0], values[1])
    df = df[(df['wind_speed'] >= values[0]) & (df['wind_speed'] <= values[1])]

    values1 = st.sidebar.slider(
        'Выберите диапазон давления',
        600.0, 1200.0, (600.0, 1200.0), key='slider-5')
    st.sidebar.write('Диапазон давления:', values1[0], values1[1])
    df = df[(df['pressure_sea'] >= values1[0]) & (df['pressure_sea'] <= values1[1])]

    values2 = st.sidebar.slider(
        'Выберите диапазон осадков,мм',
        0.0, 989.0, (0.0, 989.0), key='slider-6')
    st.sidebar.write('Диапазон осадков,мм:', values2[0], values2[1])
    df = df[(df['downfall'] >= values2[0]) & (df['downfall'] <= values2[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-4')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="trop.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение ветра в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['wind_speed'])
    st.write("""
        ## Распределение давления в выбранном диапазоне
        """)
    st.area_chart(df_selected_sector['pressure_sea'])
    st.write("""
        ## Распределение осадков в выбранном диапазоне
        """)
    st.area_chart(df_selected_sector['downfall'])

    st.write("""
        ## Ветер в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['wind_speed'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)
    st.write("""
        ## Давление в выбранном диапазоне по станциям
        """)
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=df_selected_sector['pressure_sea'], y=df_selected_sector['platform_local'],

                          name='TotalCases'))
    st.plotly_chart(fig1, use_container_width=True)
    st.write("""
        ## Осадки в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['downfall'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    wind_speed = df_selected_sector['wind_speed']
    pressure_sea = df_selected_sector['pressure_sea']


    def color_change(temp):
        """
        Если ff=10-14 м/с, то УО=Ж.
        Если ff=15-20 м/с, то УО=O.
        Если ff=>20 м/с, то УО=К.
        """
        if float('950.0') < float(temp) < float('1000.0'):
            return "orange"
        elif float('925.0') <= float(temp) <= float('950.0'):
            return "lightred"
        elif float(temp) < float('925.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, pressure_sea in zip(lat, lon, elevation, pressure_sea):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(pressure_sea),
                      icon=folium.Icon(color=color_change(float(pressure_sea)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Сильный дождь":
    st.title('Сильный дождь ОЯ')
    st.markdown("""
    Значительные жидкие и смешанные осадки (дождь, ливневый дождь, мокрый снег, снег с дождём).
    Ливневые дожди парализуют движение транспорта, заливают подземные переходы, складские помещения. Они вызывают психологический дискомфорт у населения.
    Мокрые, влажные и скользкие поверхности затрудняют и делают чрезвычайно травмоопасным передвижение людей. Во время дождя промокает одежда, обувь, продукты питания.
    Ливень способствует интенсивному переохлаждению организма.
    """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("rain.csv")

    values = st.sidebar.slider(
        'Выберите диапазон осадков',
        15.0, 989.0, (15.0, 989.0), key='slider-7')
    st.sidebar.write('Диапазон осадков:', values[0], values[1])
    df = df[(df['downfall'] >= values[0]) & (df['downfall'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-5')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="rain.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение осадков в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['downfall'])

    st.write("""
        ## Осадки в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['downfall'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    downfall = df_selected_sector['downfall']


    def color_change(temp):
        """
        Если Осадки =15-49 мм, то УО=О;
        Если Осадки =>50 мм, то УО=К.
        """
        if float('15.0') <= float(temp) < float('50.0'):
            return "lightred"
        elif float(temp) >= float('50.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, downfall in zip(lat, lon, elevation, downfall):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(downfall) + "мм",
                      icon=folium.Icon(color=color_change(float(downfall)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Видимость":
    st.title('Видимость ОЯ')
    st.markdown("""
    Ограниченная видимость, вызванная такими явлениями как туманы, метели, ливневые осадки.
    Затруднение движения транспорта, авиаперелетов, ориентации близ портов.
    """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("vis.csv")

    values = st.sidebar.slider(
        'Выберите диапазон температур',
        0.0, 2.0, (0.0, 2.0), key='slider-8')
    st.sidebar.write('Диапазон видимости:', values[0], values[1])
    df = df[(df['visibility_code'] >= values[0]) & (df['visibility_code'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-1')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="vis.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение видимости в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['Temperature'])

    st.write("""
        ## Видимость в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['visibility_code'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    visibility_code = df_selected_sector['visibility_code']


    def color_change(temp):
        """
        21-25 град С – желтый, 26-30 – оранжевый, >30 красный.
        """
        if float('2.0') >= float(temp) >= float('0.5'):
            return "orange"
        elif float('0.5') > float(temp) >= float('0.05'):
            return "lightred"
        elif float(temp) < float('0.05'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, visibility_code in zip(lat, lon, elevation, visibility_code):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(visibility_code) + "км",
                      icon=folium.Icon(color=color_change(float(visibility_code)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Ураганный ветер":
    st.title('Ураганный ветер ОЯ')
    st.markdown("""
    Ветер при достижении скорости 33 м/с и более. Большие разрушения наносят ураганные ветры. Возрастает риск смертности, ущербу инфраструктуре.
    """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("hurrah.csv")

    values = st.sidebar.slider(
        'Выберите диапазон ветров',
        35.0, 300.0, (25.0, 300.0), key='slider-9')
    st.sidebar.write('Диапазон ветров:', values[0], values[1])
    df = df[(df['wind_speed'] >= values[0]) & (df['wind_speed'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-9')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="hurrah.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение ветров в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['Temperature'])

    st.write("""
        ## Ветер в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['Temperature'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    wind_speed = df_selected_sector['wind_speed']


    def color_change(temp):
        """
        Если ff=>35м/с, включая и порывы (УО=К).
        """
        if float(temp) >= float('35.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, wind_speed in zip(lat, lon, elevation, wind_speed):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(wind_speed) + "м/с",
                      icon=folium.Icon(color=color_change(float(wind_speed)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)

elif page == "Влажность":
    st.title('Влажность ОЯ')
    st.markdown("""
    В результате опасных агрометеорологических явлений возможно снижение урожайности яровых сельскохозяйственных культур,
    к которым относится низкая влажность на период от нескольких дней. В купе с высокой температурой и отсутствием
    осадков может привести к экономическим потерям в аграрном секторе.
    """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("humidity.csv")

    values = st.sidebar.slider(
        'Выберите диапазон влажности',
        60.0, 100.0, (60.0, 100.0), key='slider-1')
    st.sidebar.write('Диапазон влажности:', values[0], values[1])
    df = df[(df['humidity_regard'] >= values[0]) & (df['humidity_regard'] <= values[1])]

    values = st.sidebar.slider(
        'Выберите диапазон температур',
        25.0, 50.0, (25.0, 50.0), key='slider-2')
    st.sidebar.write('Диапазон температур:', values[0], values[1])
    df = df[(df['Temperature'] >= values[0]) & (df['Temperature'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-1')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="humidity.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
        ## Распределение влажности в выбранном диапазоне
        """)
    st.area_chart(df_selected_sector['humidity_regard'])

    st.write("""
            ## Влажность в выбранном диапазоне по станциям
            """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['humidity_regard'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
        ## Общее распределение уровней опасности
        """)
    st.bar_chart(df['danger'])
    st.write("""
        ## Карта с выбранным диапазоном для ОЯ
        """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    humidity_regard = df_selected_sector['humidity_regard']


    def color_change(temp):
        """
        Если относительная влажность =60-75%, температура =25-27C, то УО=Ж.
        Если относительная влажность =76-85%, температура =28-30C, то УО=О.
        Если относительная влажность =>85%, температура =>30C, то УО=К.
        """
        if float('60.0') <= float(temp) <= float('75.0'):
            return "orange"
        elif float('75.0') < float(temp) <= float('85.0'):
            return "lightred"
        elif float(temp) > float('85.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, humidity_regard in zip(lat, lon, elevation, humidity_regard):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(humidity_regard) + "%",
                      icon=folium.Icon(color=color_change(float(humidity_regard)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Песчаные бури":
    st.title('Песчаные бури ОЯ')
    st.markdown("""
        Тип погоды, характеризуемый высокой температурой воздуха и низкой относительной влажностью воздуха, часто в сочетании с умеренным (6—9 м/с) или сильным (10 м/с и более) ветром. 
        При высокой температуре воздуха суховей вызывает интенсивное испарение воды из почвы, с поверхности растений и водоёмов, что может вызвать порчу урожаев зерновых и плодовых культур,
        гибель растений. Высокая температура и низкая влажность воздуха при суховеях являются результатом местной трансформации (прогревания) воздушных масс.
        """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("dry.csv")

    values = st.sidebar.slider(
        'Выберите диапазон влажности',
        0.0, 100.0, (0.0, 100.0), key='slider-11')
    st.sidebar.write('Диапазон влажности:', values[0], values[1])
    df = df[(df['humidity_regard'] >= values[0]) & (df['humidity_regard'] <= values[1])]

    values = st.sidebar.slider(
        'Выберите диапазон температкр',
        25.0, 100.0, (25.0, 100.0), key='slider-21')
    st.sidebar.write('Диапазон температур:', values[0], values[1])
    df = df[(df['Temperature'] >= values[0]) & (df['Temperature'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-11')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="dry.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение суховея в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['humidity_regard'])

    st.write("""
        ## Суховей в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['humidity_regard'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    humidity_regard = df_selected_sector['humidity_regard']


    def color_change(temp):
        """
        21-25 град С – желтый, 26-30 – оранжевый, >30 красный.
        """
        if float(temp) <= float('30.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, humidity_regard in zip(lat, lon, elevation, humidity_regard):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(humidity_regard) + "%",
                      icon=folium.Icon(color=color_change(float(humidity_regard)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Сильный туман":
    st.title('Сильный туман ОЯ')
    st.markdown("""
    Сильное помутнение воздуха за счет скопления мельчайших частиц воды (пыли, продуктов горения), при котором значение метеорологической дальности видимости не более 50 м.
    Высокая опасность движения транспорта, авиаперелетов, судов близ портов.

    """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("fog.csv")

    values = st.sidebar.slider(
        'Выберите диапазон видимости,км',
        0.0, 0.6, (0.0, 0.6), key='slider-1')
    st.sidebar.write('Диапазон видимости:', values[0], values[1])
    df = df[(df['visibility_code'] >= values[0]) & (df['visibility_code'] <= values[1])]

    sector = df.groupby('danger')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-1')

    # Filtering data
    df_selected_sector = df[(df['danger'].isin(selected_sector))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="fog.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение тумана в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['visibility_code'])

    st.write("""
        ## Туман в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['visibility_code'], y=df_selected_sector['platform_local'],

                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    visibility_code = df_selected_sector['visibility_code']


    def color_change(temp):
        """
        21-25 град С – желтый, 26-30 – оранжевый, >30 красный.
        """
        if float('0.1') < float(temp) <= float('0.5'):
            return "lightred"
        elif float(temp) < float('0.05'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, visibility_code in zip(lat, lon, elevation, visibility_code):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(visibility_code) + "км",
                      icon=folium.Icon(color=color_change(float(visibility_code)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)


elif page == "Реки":
    st.title('Реки ОЯ')
    st.markdown("""
    Уровень воды в реках это очень критический показатель для районов России, из-за превывшения уровня воды могут возникать паводки, наводнения,
    которые в свою очередь повлект за собой ущерб как биосфере, так и экономической составляющей (ущерб инфраструктуре, агросектору)
    Не говоря о смертельных случая во время крупных наводнений и разлива рек.
    """)
    st.sidebar.header('Функции пользовательской настройки')

    df = pd.read_csv("hydro.csv")

    values = st.sidebar.slider(
        'Выберите диапазон уровня воды, мм',
        0.0, 1000.0, (0.0, 1000.0), key='slider-14')
    st.sidebar.write('Диапазон уровня воды:', values[0], values[1])
    df = df[(df['water_post'] >= values[0]) & (df['water_post'] <= values[1])]

    sector = df.groupby('danger_lvl')
    # Sidebar - Sector selection
    sorted_sector_unique = sorted(df['danger_lvl'].unique())
    selected_sector = st.sidebar.multiselect('Уровень опасности:', sorted_sector_unique, sorted_sector_unique,
                                             key='sidebar-1')

    sector1 = df.groupby('org_name')
    sorted_sector_unique1 = sorted((df['org_name']).unique())
    selected_sector1 = st.sidebar.multiselect('Организация:', sorted_sector_unique1, sorted_sector_unique1,
                                              key='sidebar-1')
    # Filtering data
    df_selected_sector = df[(df['danger_lvl'].isin(selected_sector)) & (df['org_name'].isin(selected_sector1))]
    st.header('Идентифицированные ОЯ на основе данных')
    st.write('Измерение данных: ' + str(df_selected_sector.shape[0]) + ' строк и ' + str(
        df_selected_sector.shape[1]) + ' колонок.')
    st.dataframe(df_selected_sector)


    def filedownload(df):
        csv = df.to_csv(index=False, encoding='UTF-8')
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="hydro.csv">Загрузить CSV файл</a>'
        return href


    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    st.write("""
    ## Распределение уровня воды в выбранном диапазоне
    """)
    st.area_chart(df_selected_sector['water_post'])

    st.write("""
        ## Уровень воды в выбранном диапазоне по станциям
        """)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_selected_sector['water_post'], y=df_selected_sector['platform_local'],
                         name='TotalCases'))
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    ## Общее распределение уровней опасности
    """)
    st.bar_chart(df['danger_lvl'])
    st.write("""
    ## Карта с выбранным диапазоном для ОЯ
    """)
    lat = df_selected_sector['latitude']
    lon = df_selected_sector['longitude']
    elevation = df_selected_sector['platform_name']
    water_post = df_selected_sector['water_post']
    danger_lvl = df_selected_sector['danger_lvl']


    def color_change(temp):
        """
        1 – желтый, 2– оранжевый, 3 красный.
        """
        if float(temp) == float('1.0'):
            return "orange"
        elif float(temp) == float('2.0'):
            return "lightred"
        elif float(temp) == float('3.0'):
            return "red"


    # center on Liberty Bell
    m = folium.Map(location=[61, 89], zoom_start=2.5)
    marker_cluster = MarkerCluster().add_to(m)
    for lat, lon, elevation, water_post, danger_lvl in zip(lat, lon, elevation, water_post, danger_lvl):
        folium.Marker(location=[lat, lon], popup=str(elevation) + " " + str(water_post) + "мм",
                      icon=folium.Icon(color=color_change(float(danger_lvl)))).add_to(marker_cluster)

    # call to render Folium map in Streamlit
    folium_static(m)
