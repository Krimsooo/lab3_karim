import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import plotly_express as px
import time
import streamlit.components.v1 as component
from functools import wraps

#Fonctions utiles
def count_rows(rows): 
    return len(rows)

def get_dom(dt):
  return dt.day

def get_weekday(dt):
  return dt.weekday()

def get_hour(dt):
    return dt.hour

def titre(titre):
    return st.title(titre)

#-------------Fonction pour relever le temps d'execution d'une fonction------------------
def log_time(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(args, **kwargs):
        
        start = time.time()
        result = func(args, **kwargs)
        end = time.time()
        f = open("log_exec.txt",'a',encoding="utf8")
        time_res = end - start
        mes = "/n"+func.__name__+ " time = " + str(time_res) + " secondes"
        f.write(mes)
        return result

    return wrapper

titre('🗃️')
titre('Mon Dashboard pour les deux datasets')

file_path1="ny-trips-data.csv"
file_path2="uber-raw-data-apr14.csv"

#----------------------------------------------------------------------------------------------------------------------
@st.cache
@log_time
def read_and_transform1(file_path):
    data=pd.read_csv(file_path)
    data['Date/Time']=data['Date/Time'].map(pd.to_datetime)
    data['dom']=data['Date/Time'].map(get_dom)
    data['weekday']=data['Date/Time'].map(get_weekday)
    data['hour'] = data['Date/Time'].map(get_hour)
    return data

@st.cache
@log_time
def read_and_transform2(file_path):
    data1=pd.read_csv(file_path)
    data1['tpep_pickup_datetime']=pd.to_datetime(data1['tpep_pickup_datetime'])
    data1['tpep_dropoff_datetime']=pd.to_datetime(data1['tpep_dropoff_datetime'])
    data1['hour_pickup'] = data1['tpep_pickup_datetime'].map(get_hour)
    data1['hour_dropoff'] = data1['tpep_dropoff_datetime'].map(get_hour)
    return data1

df_1 = read_and_transform1(file_path1)
df_2 = read_and_transform2(file_path2)

choice = ['1er dataset: Uber Avril 2014','2ème dataset: New York Trips']
df_map = pd.DataFrame()
data_map_dropoff = pd.DataFrame()
data_map_pickup = pd.DataFrame()
option = st.sidebar.selectbox('Choisissez la dataset voulue',choice)

def choix():
    if option == choice[0]:
        
        st.text("Les 5 premières lignes du 1er dataset")
        st.write(df_1.head())
        but1=st.checkbox("Afficher le dataset 1 complet")
        
        if but1:
            st.write(df_1)
        
        df_map['lon'] = df_1['Lon']
        df_map['lat'] = df_1['Lat']
        st.text("🚗 Carte représentant les courses UBER en avril 2014 🚗")
        st.map(df_map)

        titre('🔎Recherches🔍')
        but2=st.checkbox("Cocher si vous voulez faire des recherches sur les dates")
        
        if but2:
            st.markdown('**Veuillez renseigner les dates de début et de fin**, une map devrait apparaître avec les courses entre ces deux dates.')
            nom_colonne_1, nom_colonne_2, nom_colonne_3 = st.columns(3)
            date_debut = nom_colonne_1.date_input(
                "Date de debut",
                datetime.date(2014, 4, 1))

            date_fin = nom_colonne_2.date_input(
                "Date de fin",
                datetime.date(2014, 4, 2))
            
            clique = nom_colonne_3.button(
                'Rechercher')
            if clique:
                
                mask = (df_1['Date/Time'].dt.date >
                        date_debut) & (df_1['Date/Time'].dt.date <= date_fin)
                df1 = df_1.loc[mask]
                df1.rename(columns={'Lat': 'lat', 'Lon': 'lon'}, inplace=True)
                st.write(df1)
                st.map(df1)

    elif option == choice[1]:
        
        st.text("Les 5 premières lignes du 2ème dataset")
        st.write(df_2.head())
        but1=st.checkbox("Afficher le dataset 2 complet")
        
        if but1:
            st.write(df_2)

        status = st.sidebar.radio("Sélectionner la carte à afficher : ", ('Carte des départs', 'Carte des arrivés'))

        if (status == 'Carte des départs'):
            st.text("🚗 Carte représentant le point de départ des courses UBER à New York 🚗")
            data_map_pickup['lon'] = df_2['pickup_longitude']
            data_map_pickup['lat'] = df_2['pickup_latitude']
            st.map(data_map_pickup)

        else: 
            st.text("🚗 Carte représentant la destination finale des courses UBER à New York 🚗")
            data_map_dropoff['lon'] = df_2['dropoff_longitude']
            data_map_dropoff['lat'] = df_2['dropoff_latitude']
            st.map(data_map_dropoff)
        
        titre('🚕 Distances moyennes en kilomètres en fonction du nombre de passager 🚕')
        count_passenger= df_2.groupby('passenger_count').mean()
        graph=px.bar(count_passenger,y="trip_distance")
        st.plotly_chart(graph)

        titre('🕒 Fréquences des courses en fonction des heures 🕒')
        graph1=plt.hist(df_2.hour_pickup, bins = 24, range = (0.5,24))
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

        titre('📘')
        titre('Deux pages WIKIPÉDIA pour les matheux (avec iFrame)')
        st.text("Page Wiki sur la loi de Bernoulli")
        component.iframe("https://fr.wikipedia.org/wiki/Loi_de_Bernoulli#:~:text=En%20math%C3%A9matiques%20et%20plus%20pr%C3%A9cis%C3%A9ment,probabilit%C3%A9%20q%20%3D%201%20%E2%80%93%20p.",scrolling=True, height=2000)
        st.text("Page Wiki sur le mathématicien Tchebytchev")
        component.iframe("https://fr.wikipedia.org/wiki/Pafnouti_Tchebychev",scrolling=True, height=2000)
choix()