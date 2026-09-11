#  Recuperamos los puestos que hay en la web de Madrid Digital, si los hay.
# --------------------------------------------------------------------------
#       Url Madrid Digital
URL_MD = "https://www.comunidad.madrid/servicios/empleo/procesos-selectivos-agencia-administracion-digital"
#
#  Se recupera la tabla de puestos que hay en la web.

from Herramientas.scraping import Recuperar_tablas
from Herramientas.mail import Envio_mail
import pandas as pd




def Alerta_MD(usuario, password, destinatario): 
    #  Recuperamos la tabla con los puestos
    tablas = Recuperar_tablas(URL_MD)

    if tablas is None or len(tablas) == 0:
        print('No se han encontrado tablas en la página de Madrid Digital')
        return
    
    #  Comprobamos si hay puestos, y si los hay se envía alerta
    puestos = tablas[0].iloc[:, :5]
    puestos = puestos.drop(columns=['REFERENCIA', 'IMPRESCINDIBLE'])
    puestos = puestos.rename(columns={'PUESTOS OFERTADOS': '.                      NUM. PUESTOS'})
    
    # Si los datos de la columna 1 y 3 son iguales, No hay puestos
    # Si es nula, No hay puestos
    if puestos.iloc[0, 0] == puestos.iloc[0, 2] or pd.isna(puestos.iloc[0, 0]):
        print('No se encontrado puestos en Madrid Digital')
        # alerta = 'Puestos Madrid Digital - NO HAY NINGUNO'
        # mensaje = f"\nVisita la pagina web\n{URL_MD}"
        # Envio_mail(usuario, password , alerta, mensaje, destinatario)
    else:
        alerta = 'ALERTA - Han salido puestos en Madrid Digital'
        mensaje = f"Han salido los siguientes puestos en Madrid Digital.\n\n{puestos.to_string(index=False)}\n\n Visita la pagina web\n{URL_MD}"
        print(alerta)
        Envio_mail(usuario, password , alerta, mensaje, destinatario)




if __name__ == '__main__':
    from Herramientas.variables import USUARIO, PASSWORD, DESTINATARIO
    
    Alerta_MD(USUARIO, PASSWORD, DESTINATARIO)