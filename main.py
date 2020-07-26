# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import PIL
import io
from datetime import datetime
from shapely.geometry import Polygon

# leer shapefile
us_map = gpd.read_file(r'cb_2018_us_state_500k.shp')

# csv a dataframe para los casos
data_cases = pd.read_csv('data-daily.csv')

# cambiando el nombre de la columna para que tanto el mapa y los casos tengan el mismo nombre de columna para los estados
data_cases.rename(columns = {'state': 'NAME'}, inplace = True)

# geodataframe de Alaska
alaska_gdf = us_map.loc[us_map['NAME'] == "Alaska"]  # se selecciona Alaska
alaska_mp = alaska_gdf['geometry'].values[0]         # multipoligono del dataframe
ak_exp_gdf = gpd.GeoDataFrame(alaska_mp)             # se crea un GeoDataFrame 
ak_exp_gdf.columns = ['geometry']                    # se añade una columna de geometria

target_poly = Polygon([(-180,50), (-180,75),         # se crea un poligono que cubra Alaska hasta el meridiano 180
                       (-100,75), (-100,50)])

western_isles = ak_exp_gdf[ak_exp_gdf.intersects(target_poly) == False].copy()     # filtracion lado oeste
eastern_ak = ak_exp_gdf[ak_exp_gdf.intersects(target_poly)].copy()                 # filtracion lado este

eastern_ak['NAME'] = 'Alaska'    # se añade una columna para el nombre del estado

alaska_trimmed = eastern_ak.dissolve(by='NAME')    # se combinan los poligonos

states_trimmed = us_map.copy()      # se crea una copia del GeoDataFrame original
states_trimmed.loc[states_trimmed['NAME'] == 'Alaska', 'geometry'] = alaska_trimmed['geometry'].values  # se reemplaza Alaska 


# uniendo el mapa con los casos
merge = states_trimmed.merge(data_cases, on = 'NAME')

# quitando territorios que no son estados
merge = merge[merge.NAME != 'American Samoa']
merge = merge[merge.NAME != 'Commonwealth of the Northern Mariana Islands']
merge = merge[merge.NAME != 'Guam']

# lista de las imagenes
image_frames = []

# Ciclo para crear cada imagen
for dates in merge.columns.to_list()[11:158]:
    date_f = datetime.strptime(dates, '%Y%m%d').strftime('%d/%m/%Y') # formato de las fechas
    
    # creacion del mapa
    ax = merge.plot(column = dates, 
                    cmap = 'OrRd',       # Colores del mapa
                    figsize = (10,6),    # Tamaño del mapa
                    legend = True,       # Leyenda
                    legend_kwds = {'fontsize':8},   # Tamaño de letra de la leyenda
                    scheme = 'user_defined', # Esquema
                    classification_kwds = {'bins':[100, 500, 1000, 5000, 10000, 30000, 50000, 100000, 300000, 500000]},  # Division de los datos
                    edgecolor = 'black', # color del borde
                    linewidth = 0.4)   # ancho de las lineas
    
    # poner titulo
    ax.set_title('Casos de COVID-19 por estado en Estados Unidos ' + date_f, fontdict = {'fontsize':10}, pad = 12.5)
    
    # quitar ejes
    ax.set_axis_off()
    
    # mover leyenda
    ax.get_legend().set_bbox_to_anchor((1,1.005))
    
    # convirtiendo a imagen
    img = ax.get_figure()
    
    # guardado de la imagen en la lista
    f = io.BytesIO()
    img.savefig(f, format = 'png', bbox_inches = 'tight', dpi = 300)
    f.seek(0)
    image_frames.append(PIL.Image.open(f))
    plt.close(img)
    
# crear GIF
image_frames[0].save('US-Covid19-by-state-daily.gif', format = 'GIF',
                      append_images = image_frames[1:],
                      save_all = True, duration = 300,
                      loop = 0)

f.close() 

    
    
    
    

