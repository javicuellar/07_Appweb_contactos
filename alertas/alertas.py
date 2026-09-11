# Librerias comunes
from Herramientas.variables import leer_variables
config = leer_variables()

from alerta_CONTROL import Alerta_CONTROL
from alerta_MD import Alerta_MD
# from alerta_ficheros import Alerta_Ficheros               # Genera fichero excel
from alerta_ficheros_sheet import Alerta_Ficheros_sheet     # Actualiza hoja de cálculo





#     Analizamos las alertas:

#  Alerta CONTROL ACCESO, si no borro los correos de CONTROL ACCESO se activa la alerta
Alerta_CONTROL(config['USER_MAIL'], config['PASSWORD_MAIL'], config['USER_JAVI'], config['PASSWORD_JAVI'], config['DESTINATARIO_MAIL'])

#  Alerta puestos en Madrid Digital
Alerta_MD(config['USER_MAIL'], config['PASSWORD_MAIL'], config['USER_JAVI'])


#  Analizamos ficheros en DIRECTORIO mayores de T_MINIMO, bajamos a 4000 bytes
# T_MINIMO = 5 * 1024 * 1024 * 1024    # GB en bytes (1024 bytes x 1024 Mb x 1024 Gb)
T_MINIMO = 4000 * 1024 * 1024          # Megabytes

# Para Windows añadimos path a librerías python, para añadir librerías mías de Herramientas
import sys, os
if os.name == 'nt':
    sys.path.append(os.path.join(os.path.dirname(__file__), '\\Python'))
    DIRECTORIO = 'D:\\'
else:
    DIRECTORIO = '/video'

Alerta_Ficheros_sheet(DIRECTORIO, T_MINIMO)


if os.name == 'nt':
    from alerta_esqui import Alerta_viaje_esqui

    Alerta_viaje_esqui(["viaje esqui ayuntamiento", "viaje esqui ayuntamiento 2026"])
