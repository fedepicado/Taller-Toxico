# taller toxico

import csv
import numpy as np
from datetime import datetime,timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mlp_dates
import folium
from folium.plugins import TimestampedGeoJson


############################Extraemos las fechas y las horas del archivo#######################################
fechas = []
horas = []
NO2_centenario = []
NO2_cordoba = []
NO2_boca = []
NO2_palermo = []

# setear el directorio en la misma carpeta que estan los archivos
def abrir_archivo():
    with open("calidad-aire.csv", 'rt') as archivo:
        filas = csv.reader(archivo)
        encabezado = next(filas)
        # print('Encabezado:')
        # print(encabezado)
        # print('Filas:')
        for fila in filas:
            # print(fila)
            fechas.append(str(fila[0]))
            horas.append(str(fila[1]))
            NO2_centenario.append(str(fila[3]))
            NO2_cordoba.append(str(fila[6]))
            NO2_boca.append(str(fila[9]))
            NO2_palermo.append(str(fila[12]))
        return None


abrir_archivo()

###############################Ponemos las fechas en formato correcto##########################################


# recibe las 2 listas y va a devolver una con el formato correcto
def convertirFechas(fechas, horas):
    Dia_Horario = []
    i = 0  # para ir recorriendo las horas
    dateFormatter = "%d%b%Y,%H:%M:%S"
    for fecha in fechas:
        separado = fecha.split(":", 1)
        fecha_solo = separado[0]
        hora_sola = separado[1]
        hora = str(int(horas[i]) % 24)
        dias_extra = int(horas[i])//24
        if int(hora) <= 9:
            hora = "0" + hora
        hora_sola = hora_sola.replace("00", hora, 1)
        fecha_hora = datetime.strptime(
            fecha_solo + "," + hora_sola, dateFormatter) + timedelta(dias_extra)
        Dia_Horario.append(fecha_hora)
        i += 1
    return Dia_Horario


fecha_correcta = convertirFechas(fechas, horas)

########################Ponemos los valores de NO2 en formato correcto#########################################


# recibe lista_correcta y devuelve 1 lista del mismo largo que lista_correcta.
def depuradora(listaNO2):
    for (indice, valor) in enumerate(listaNO2):
        try:
            aux = int(valor)
        except:
            aux = "NaN"
        # print(aux)
        listaNO2[indice] = aux
    return listaNO2


depuradora(NO2_centenario)
depuradora(NO2_cordoba)
depuradora(NO2_boca)
depuradora(NO2_palermo)

###################################Ordenamos las listas en funcion de la fecha#################################

def mezclarProlijo(l, a, b, s, l1, l2, l3, l4):
    res = []
    res1 = []
    res2 = []
    res3 = []
    res4 = []
    i = a
    j = s
    while i < s and j < b:
        if l[i] < l[j]:
            res.append(l[i])
            res1.append(l1[i])
            res2.append(l2[i])
            res3.append(l3[i])
            res4.append(l4[i])
            i += 1
        else:
            res.append(l[j])
            res1.append(l1[j])
            res2.append(l2[j])
            res3.append(l3[j])
            res4.append(l4[j])
            j += 1
    if i < s:
        res += l[i:s]
        res1 += l1[i:s]
        res2 += l2[i:s]
        res3 += l3[i:s]
        res4 += l4[i:s]
    else:
        res+=l[j:b]
        res1+=l1[j:b]
        res2+=l2[j:b]
        res3+=l3[j:b]
        res4+=l4[j:b]
    # print(l,res)
    l[a:b] = res
    # print(l,res)
    l1[a:b] = res1
    l2[a:b] = res2
    l3[a:b] = res3
    # print(l4,"l4'")
    l4[a:b] = res4
    # print(l4,"l4")
    return None

def mergeSortIndex(l, l1, l2, l3, l4):
    def aux(a, b):
        if b-a == 2:
            # print(a)
            if l[a] > l[a+1]:
                l[a], l[a+1] = l[a+1], l[a]
                l1[a], l1[a+1] = l1[a+1], l1[a]
                l2[a], l2[a+1] = l2[a+1], l2[a]
                l3[a], l3[a+1] = l3[a+1], l3[a]
                l4[a], l4[a+1] = l4[a+1], l4[a]
                return None
        if b-a <= 1:
            return None
        s = (b+a)//2
        aux(a, s)
        aux(s, b)
        return mezclarProlijo(l, a, b, s, l1, l2, l3, l4)
    return aux(0, len(l))

mergeSortIndex(fecha_correcta, NO2_centenario,NO2_cordoba, NO2_boca, NO2_palermo)

#######################################Generamos los indices de inicio de cada semana##########################

def extraer_semana():  # crea una lista con los indices de cada semana
    lista_indices_semanas = []
    variable = datetime.strptime("28NOV2021", "%d%b%Y")
    for (indice, fecha) in enumerate(fecha_correcta):
        if fecha.weekday() == 0 and fecha.date() != variable:
            variable = fecha.date()
            lista_indices_semanas.append(indice)
    return lista_indices_semanas

lista_lunes= extraer_semana()

##############################Promedio de Las semanas########################################

def promedio(lista, a, b):#Promedia el fragmento l[a:b] tomando en cuenta solo los valores enteros,o devuelve 0
    valores_enteros = []
    for x in lista[a:b]:
        if isinstance(x, int) or isinstance(x, float):
            valores_enteros.append(x)
    if len(valores_enteros) <= 6: ## si no estan todos los datos de una semana promedio cero?
        valores_enteros = [0]
    return np.average(valores_enteros)

fecha_inicio_semana = []
centenario_semanal = [] 
cordoba_semanal = []
boca_semanal = []
palermo_semanal = []
def obtener_promedios(fecha_correcta, lista_lunes, l1, l2, l3, l4):
    ultimo_lunes = lista_lunes[len(lista_lunes)-1]
    for (i, x) in enumerate(lista_lunes[:len(lista_lunes)-1]):
        fecha_inicio_semana.append(fecha_correcta[x])
        centenario_semanal.append(promedio(l1, x, lista_lunes[i+1]))
        cordoba_semanal.append(promedio(l2, x, lista_lunes[i+1]))
        boca_semanal.append(promedio(l3, x, lista_lunes[i+1]))
        palermo_semanal.append(promedio(l4, x, lista_lunes[i+1]))
    # promedio de la ultima semana
    fecha_inicio_semana.append(fecha_correcta[ultimo_lunes])
    centenario_semanal.append(promedio(l1, ultimo_lunes, len(fecha_correcta)))
    cordoba_semanal.append(promedio(l2, ultimo_lunes, len(fecha_correcta)))
    boca_semanal.append(promedio(l3, ultimo_lunes, len(fecha_correcta)))
    palermo_semanal.append(promedio(l4, ultimo_lunes, len(fecha_correcta)))
    return fecha_inicio_semana, centenario_semanal, cordoba_semanal, boca_semanal, palermo_semanal

obtener_promedios(fecha_correcta,lista_lunes,NO2_centenario,NO2_cordoba,NO2_boca,NO2_palermo)


##### sacamos informacion de las latitudes y longitudes de las estaciones meteorologicas 
estaciones_met=[]
latitud=[]
longitud=[]

def abrir_archivo():
    with open("estaciones-ambientales.csv","rt", encoding= "utf-8") as archivo:
        filas = csv.reader(archivo, delimiter = ";")
        encabezado = next(filas)
        #print('Encabezado:')
        #print(encabezado)
        #print('Filas:')
        for fila in filas:
            # print(fila)
            estaciones_met.append(fila[2])
            latitud.append(float(fila[1].replace(",",".")))
            longitud.append(float(fila[0].replace(",",".")))
        return None
abrir_archivo()

# asi se ve el mapa para la primer semana del dataset
abasto=[-34.604034, -58.411167] #punto medio(donde centra)

'''
m = folium.Map(location= abasto,tiles = "CartoDB Positron", zoom_start=14)
#la boca
folium.CircleMarker(
    location=[latitud[0], longitud[0]],
    radius=boca_semanal[0],
    popup=estaciones_met[0],
    tooltip=boca_semanal[0],
    color="blue",
    fill=True,
    fill_color="#3186cc",
).add_to(m)
#centenario
folium.CircleMarker(
    location=[latitud[1], longitud[1]],
    radius=centenario_semanal[0],
    popup=estaciones_met[1],
    tooltip=centenario_semanal[0],
    color="blue",
    fill=True,
    fill_color="#3186cc",
).add_to(m)
#cordoba
folium.CircleMarker(
    location=[latitud[2], longitud[2]],
    radius=cordoba_semanal[0],
    popup=estaciones_met[2],
    tooltip=cordoba_semanal[0],
    color="blue",
    fill=True,
    fill_color="#3186cc",
).add_to(m)
#palermo
folium.CircleMarker(
    location=[latitud[3], longitud[3]],
    radius=palermo_semanal[0],
    popup=estaciones_met[3],
    tooltip=palermo_semanal[0],
    color="blue",
    fill=True,
    fill_color="#3186cc",
).add_to(m)
m.save("mymap_primerSemana.html")

'''

#### funcion que crea un mapa
def creacionMapa(abasto, latitud, longitud, estaciones_met, boca_semanal, centenario_semanal, cordoba_semanal, palermo_semanal,semana):
    m = folium.Map(location= abasto,tiles = "CartoDB Positron", zoom_start=14)
    #la boca
    folium.CircleMarker(
        location=[latitud[0], longitud[0]],
        radius=boca_semanal,
        popup=estaciones_met[0],
        tooltip=boca_semanal,
        color="blue",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)
    #centenario
    folium.CircleMarker(
        location=[latitud[1], longitud[1]],
        radius=centenario_semanal,
        popup=estaciones_met[1],
        tooltip=centenario_semanal,
        color="blue",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)
    #cordoba
    folium.CircleMarker(
        location=[latitud[2], longitud[2]],
        radius=cordoba_semanal,
        popup=estaciones_met[2],
        tooltip=cordoba_semanal,
        color="blue",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)
    #palermo
    folium.CircleMarker(
        location=[latitud[3], longitud[3]],
        radius=palermo_semanal,
        popup=estaciones_met[3],
        tooltip= palermo_semanal,
        color="blue",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)
    # m.save("mymap"+ str(fecha_correcta[lista_lunes[semana]].date()) +".html")
    return None 
    
primermapa=creacionMapa(abasto, latitud, longitud, estaciones_met, boca_semanal[0], centenario_semanal[0], cordoba_semanal[0], palermo_semanal[0],1)

#crea multiples mapas
def multiplesMapas(fecha_inicio_semana):
    i=0
    while i < len(fecha_inicio_semana):
        creacionMapa(abasto, latitud, longitud, estaciones_met, boca_semanal[i], centenario_semanal[i], cordoba_semanal[i], palermo_semanal[i],i)
        i+=1
    return None

muchos_mapas= multiplesMapas(fecha_inicio_semana[:4])


########################### mapa interactivo por mes de todas las semanas 

## tengo que armarme un dataframe en formato tidy,
## esto se hubiese hecho de toque pivoteando 

tiempo_tidy=[]
latitud_tidy=[]
longitud_tidy=[]
NO2_tidy=[]
estacion_tidy=[]
indice_tidy=[]

## fecha inicio semana la obtuve de la funcion obtener promedios

def aux_tidy(fecha_inicio_semana,latitud,longitud,estacion,NO2_semanal):
    for (i,x) in enumerate(fecha_inicio_semana):
        tiempo_tidy.append(x)
        NO2_tidy.append(NO2_semanal[i])
        latitud_tidy.append(latitud)
        longitud_tidy.append(longitud)
        estacion_tidy.append(estacion)
        indice_tidy.append(i)
    return None

def armar_matriz_tidy(fecha_inicio_semana,latitud,longitud,estacion_met,centenario_semanal,palermo_semanal,boca_semanal,cordoba_semanal):
    aux_tidy(fecha_inicio_semana,latitud[0],longitud[0],estacion_met[0],boca_semanal)
    aux_tidy(fecha_inicio_semana,latitud[1],longitud[1],estacion_met[1],centenario_semanal)
    aux_tidy(fecha_inicio_semana,latitud[2],longitud[2],estacion_met[2],cordoba_semanal)
    aux_tidy(fecha_inicio_semana,latitud[3],longitud[3],estacion_met[3],palermo_semanal)
    return None

armar_matriz_tidy(fecha_inicio_semana,latitud,longitud,estaciones_met,centenario_semanal,palermo_semanal,boca_semanal,cordoba_semanal)

# print(tiempo_tidy[0])
# print(len(latitud_tidy))
# print(len(longitud_tidy))
# print(len(NO2_tidy))
# print(len(estacion_tidy))

datosNO2=pd.DataFrame(zip(indice_tidy,tiempo_tidy,estacion_tidy,latitud_tidy,longitud_tidy, NO2_tidy),columns=("indice","Tiempo", "Ubicacion","Latitud","Longitud","NO2 promedio semanal"))
datosNO2["Fecha"]=datosNO2["Tiempo"]
datosNO2= datosNO2.set_index('Tiempo')
#print(datosNO2)

def create_geojson_features(df):
    features = []
    
    for _, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type':'Point', 
                'coordinates':[row['Longitud'],row['Latitud']]
            },
            'properties': {
                'time': row['Fecha'].__str__(),
                'style': {'color' : 'red'},
                'icon': 'circle',
                "popup": row["Ubicacion"],
                'tooltip': row["NO2 promedio semanal"],
                'iconstyle':{
                    'fillColor': 'maroon',
                    'fillOpacity': 0.4,
                    'stroke': 'true',
                    'radius': row['NO2 promedio semanal'],
                    "minRadius": 2,
                }
            }
        }
        features.append(feature)
    return features

start_geojson = create_geojson_features(datosNO2) 
# print(len(start_geojson))

## otro estilo de mapa "CartoDB Positron","cartodbdark_matter"
m = folium.Map(location= abasto, tiles = "CartoDB Positron",zoom_start=13)
folium.plugins.TimestampedGeoJson(start_geojson,
                           period='P1M',
                           add_last_point=True,
                           auto_play=False,
                           loop=False,
                           max_speed=1,
                           loop_button=True,
                           date_options='YYYY/MM',
                           time_slider_drag_update=True,
                           duration='P1M').add_to(m)
m.save("mymapInteractivo.html")

#########Ploteado usando data frame de pandas de las 4 estaciones a lo largo de todos los años###########

datos1=pd.DataFrame(zip(fecha_inicio_semana,cordoba_semanal),columns=("Tiempo","Niveles de NO2"))
datos2=pd.DataFrame(zip(fecha_inicio_semana,centenario_semanal),columns=("Tiempo","Niveles de NO2"))
datos3=pd.DataFrame(zip(fecha_inicio_semana,boca_semanal),columns=("Tiempo","Niveles de NO2"))
datos4=pd.DataFrame(zip(fecha_inicio_semana,palermo_semanal),columns=("Tiempo","Niveles de NO2"))

fig = plt.figure()
plt.style.use('seaborn')
gs = fig.add_gridspec(2, 2, hspace=0.18, wspace=0.08)
axs = gs.subplots(sharex='col', sharey='row')
(ax1, ax2), (ax3, ax4) = gs.subplots(sharex='col', sharey='row')
fig.suptitle('Niveles de NO2 en CABA para las 4 estaciones meteorologicas')
ax1.plot(datos1["Tiempo"],
        datos1["Niveles de NO2"],
        linestyle="--",
        color="blue",
        alpha=1)
axs[0, 0].set_title('Cordoba')
ax2.plot(datos4["Tiempo"],
        datos4["Niveles de NO2"],
        linestyle="--",
        color="black",
        alpha=1)
axs[1, 1].set_title('Centenario')
ax3.plot(datos3["Tiempo"],
        datos3["Niveles de NO2"],
        linestyle="--",
        color="red",
        alpha=1)
axs[1, 0].set_title('La Boca')
ax4.plot(datos2["Tiempo"],
        datos2["Niveles de NO2"],
        linestyle="--",
        color="green",
        alpha=1)
axs[0, 1].set_title('Palermo')
for ax in axs.flat:
    ax.set(xlabel='Tiempo', ylabel=' Medición NO2')
for ax in axs.flat:
    ax.label_outer()
plt.savefig("grafico Niveles de NO2.png")
plt.show()

#### depurando

def sin_ceros(l,li):
    l_=[]
    li_=[]
    for x in range(len(l)):
        if l[x] != 0:
            l_.append(l[x])
            li_.append(li[x])
    return l_,li_

#####################################Plot de los promedios semanales de semanas completas#####################################

y_cente,x_cente=sin_ceros(centenario_semanal,fecha_inicio_semana)
y_cordoba,x_cordoba=sin_ceros(cordoba_semanal,fecha_inicio_semana)
y_boca,x_boca=sin_ceros(boca_semanal,fecha_inicio_semana)
y_palermo,x_palermo=sin_ceros(palermo_semanal,fecha_inicio_semana)
# plt.style.use('seaborn')
# plt.plot_date(x,y)#,linestyle='-')#,marker=None)
# plt.gcf().autofmt_xdate()
# plt.show()
type(x_cente[0])
##########################################Graficado de los promedios###########################################
# Grafico para representar NO2 en CABA
datos11=pd.DataFrame(zip(x_cordoba,y_cordoba),columns=("Tiempo","Niveles de NO2"))
datos22=pd.DataFrame(zip(x_cente,y_cente),columns=("Tiempo","Niveles de NO2"))
datos33=pd.DataFrame(zip(x_boca,y_boca),columns=("Tiempo","Niveles de NO2"))
datos44=pd.DataFrame(zip(x_palermo,y_palermo),columns=("Tiempo","Niveles de NO2"))

fig = plt.figure()
plt.style.use('seaborn')
gs = fig.add_gridspec(2, 2, hspace=0.18, wspace=0.08)
axs = gs.subplots(sharex='col', sharey='row')
(ax1, ax2), (ax3, ax4) = gs.subplots(sharex='col', sharey='row')
ax1.set_ylim([0,80])
ax2.set_ylim([0,80])
ax3.set_ylim([0,80])
ax4.set_ylim([0,80])
fig.suptitle('Niveles de NO2 en CABA para las 4 estaciones meteorologicas, depurado')
ax1.plot(datos11["Tiempo"],
        datos11["Niveles de NO2"],
        linestyle="--",
        color="blue",
        alpha=1)
axs[0, 0].set_title('Cordoba')
ax2.plot(datos44["Tiempo"],
        datos44["Niveles de NO2"],
        # linestyle="--",
        color="black",
        alpha=1)
axs[1, 1].set_title('Centenario')
ax3.plot(datos33["Tiempo"],
        datos33["Niveles de NO2"],
        # linestyle="--",
        color="red",
        alpha=1)
axs[1, 0].set_title('La Boca')
ax4.plot(datos22["Tiempo"],
        datos22["Niveles de NO2"],
        linestyle="--",
        color="green",
        alpha=1)
axs[0, 1].set_title('Palermo')
#plt.xticks(rotation=45)
for ax in axs.flat:
    ax.set(xlabel='Tiempo', ylabel=' Medición NO2')
for ax in axs.flat:
    ax.label_outer()
ax1.set_ylim([0,80])
ax2.set_ylim([0,80])
ax3.set_ylim([0,80])
ax4.set_ylim([0,80])
plt.savefig("grafico Niveles de NO2, depurado.png")
plt.show()

### promedio de NO2 por hora 

def extraer_dia():# lista de indices de los dias
    lista_indices_dias = []
    variable = datetime.strptime("28NOV2021", "%d%b%Y")
    for (indice, fecha) in enumerate(fecha_correcta):
        if fecha.date() != variable:
            variable = fecha.date()
            lista_indices_dias.append(indice)
    return lista_indices_dias

lista_dias= extraer_dia()

def obtener_horas_por_dia(l1_, l1=NO2_cordoba):#devuelve la lista de indices de cada dia y la cantidad 
                                                                   #de horas de este en dos listas
    ultimo_indice = lista_dias[len(lista_dias)-1]
    for (i, x) in enumerate(lista_dias[:len(lista_dias)-1]):
        l1_.append(len(l1[x:lista_dias[i+1]]))
    # promedio del ultimo dia
    l1_.append(len(l1[ultimo_indice:len(fecha_correcta)]))
    return l1_

l1_=[]
horas_por_dia=obtener_horas_por_dia(l1_,NO2_centenario)
fechas_dias=[]
for i in lista_dias:
    fechas_dias.append(fecha_correcta[i])
# for x in range(lista_dias[3514],lista_dias[3514]+40):
#     print(fecha_correcta[x],NO2_centenario[x])

#########################################################Grafico de horas por dia######################################3

# plt.style.use('seaborn')
# plt.plot_date(fechas_dias[3117:3178],l1_[3117:3178])#,linestyle='-')#,marker=None)
# plt.gcf().autofmt_xdate()
# plt.show()

#########################################################Consigo promedio por hora en rango de dias###################

# lista_dias[3117:3178]
# 61 dias analizados, entonces listas por hora tendra 61 elementos en cada posicion
listas_por_hora=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
lista_promedios_por_hora=[]

# print(listas_por_hora)
for x in range(lista_dias[3117],lista_dias[3178]):
    listas_por_hora[fecha_correcta[x].hour].append(NO2_centenario[x])
print(listas_por_hora)

#saco los pocos NaN que habia
def depurar_horas(l):
    valores_enteros = []
    for x in l:
        if isinstance(x, int) or isinstance(x, float):
            valores_enteros.append(x)
    return valores_enteros

lista_horas_depuradas=[]

for x in listas_por_hora:
    lista_horas_depuradas.append(depurar_horas(x))

def promedio_de_horas(l):
    valores_enteros = []
    for x in l:
        if isinstance(x, int) or isinstance(x, float):
            valores_enteros.append(x)
    return np.average(valores_enteros)

for x in lista_horas_depuradas:
    lista_promedios_por_hora.append(promedio_de_horas(x))
    
x=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
plt.style.use('seaborn') 
plt.suptitle('Niveles de NO2 promedio por hora en Centenario ')
plt.plot(x,lista_promedios_por_hora,'o')#,linestyle='-')#,marker=None)
plt.gcf().autofmt_xdate()
plt.xlabel("Horas")
plt.ylabel("Niveles de NO2 por hora en Centenario")
plt.savefig("Niveles de NO2 promedio horas.png")
plt.show()


#### se viene el boxplot, paso la lista de listas a un diccionario

#creo el diccionario
def crear_diccionario():
    diccionario={}
    for i in range(24):
        diccionario[i]=[]
    return diccionario

diccionario_horas=crear_diccionario()
# print(diccionario_horas)

#saco los pocos NaN que habia
def depurar_horas(l):
    valores_enteros = []
    for x in l:
        if isinstance(x, int) or isinstance(x, float):
            valores_enteros.append(x)
    return valores_enteros

lista_horas_depuradas=[]

for x in listas_por_hora:
    lista_horas_depuradas.append(depurar_horas(x))


## recorro la lista de listas y voy agragando los elementos a cada key del diccionario(que son las horas)
for (i,una_hora) in enumerate(lista_horas_depuradas):
    for x in una_hora:
        diccionario_horas[i].append(x)

print(diccionario_horas)

####################################################3grafico boxplot###################################################
plt.style.use('seaborn')
fig, ax = plt.subplots()
ax.boxplot(diccionario_horas.values())
ax.set_xticklabels(diccionario_horas.keys())
ax.set_title("Niveles de NO2 por hora en Centenario")
ax.set_xlabel('Horas')
ax.set_ylabel('Concentracion NO2')
plt.show()
plt.savefig("Boxplot niveles de NO2 horas.png")





