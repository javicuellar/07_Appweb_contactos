#  Análisis de los ficheros del directorio enviando alerta mail con los ficheros mayores de x bytes.
# ---------------------------------------------------------------------------------------------------
from Herramientas.sheet import Actualizar_Hoja
from Herramientas.mail import Envio_mail_adjunto


import os, sys
import pandas as pd




# Función para buscar archivos mayores a t_minimo
def buscar_archivos_grandes(directorio, t_minimo):
    archivos_grandes = []

    for carpeta_raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta_archivo = os.path.join(carpeta_raiz, archivo)
            if os.path.getsize(ruta_archivo) > t_minimo:
                archivos_grandes.append((archivo, ruta_archivo, os.path.getsize(ruta_archivo)))
    return archivos_grandes


#  Alerta de Ficheros mayores de T_MINIMO
def Alerta_Ficheros_sheet(directorio, t_minimo):
    archivos_grandes = buscar_archivos_grandes(directorio, t_minimo)
    tamano = round(t_minimo / (1024 * 1024 * 1024), 2)

    if archivos_grandes:
        # Crear DataFrame y guardar en Excel
        df = pd.DataFrame(archivos_grandes, columns=['Nombre', 'Ruta', 'Tamaño (bytes)'])
        df = df.sort_values(by='Tamaño (bytes)', ascending=False)
        # archivo_excel = 'archivos_grandes.xlsx'
        # df.to_excel(archivo_excel, index=False)
        Actualizar_Hoja('Archivos Grandes', df)

        alerta = f'ALERTA - {len(archivos_grandes)} archivos de más de {tamano} Gb. detectados en {directorio}'
        mensaje = f"Se han encontrado {len(archivos_grandes)} archivos mayores de {tamano} Gb."
        print(mensaje)
    else:
        print(f'No se encontraron archivos mayores de {tamano} Gb. en {directorio}')




if __name__ == '__main__':
    # Para Windows añadimos path a librerías python, para añadir librerías mías de Herramientas
    if os.name == 'nt':
        sys.path.append(os.path.join(os.path.dirname(__file__), '\\Python'))
        DIRECTORIO = 'D:\\'
    else:
        DIRECTORIO = '/video'

    #  Analizamos ficheros en DIRECTORIO mayores de T_MINIMO 
    T_MINIMO = 2 * 1024 * 1024 * 1024      # 2 GB en bytes
    Alerta_Ficheros_sheet(DIRECTORIO, T_MINIMO)