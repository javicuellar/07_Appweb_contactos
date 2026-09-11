from Herramientas.mail      import Envio_mail, Envio_mail_adjunto, Lectura_mail



#  Docuementar la alerta

def Alerta_CONTROL(usuario, password, usuario_javi, password_javi, destinatario):
    #  Recuperamos el número de correos con asunto CONTROL ACCESO
    num = Lectura_mail(usuario_javi, password_javi, 'inbox', '(SUBJECT "CONTROL ACCESO")', contar=True)
    
    if num > 3:
        # Si hay 5 avisos con correos de CONTROL ACCESO (no borrados, algo me ha pasado)
        alerta = 'IMPORTANTE JAVI - Mensaje con información por si me ha pasado algo'
        mensaje = "Hola, \n\nSi has recibido este correo es porque me puede haber pasado algo. " \
            "Es un mensaje automático que se envía si estoy más de 5 días desconectado.\n\n" \
            "Espero que todos estéis bien, ya sabéis que os quiero mucho y siempre estaré con vosotros. " \
            "Por favor díselo a los niños y cuidaros mucho.\n\n" \
            "Te comparto una excel con las cuentas y saldos, un resumen. En la pestaña Balance, están las entidades y saldos " \
            "de las cuentas. Seguro que sabrás que hacer.\n\n" \
            "Gracias, os quiero mucho.\n\n" \
            "Javi."
        # mensaje = f"Se han recibido {num} avisos. \nSE TOMARÁN MEDIDAS"
        # Envio_mail(usuario, password , alerta, mensaje, usuario_javi)

        # Cojemos el adjunto de la ruta que corresponda según el sistema operativo
        import sys, os
        if os.name == 'nt':
            sys.path.append(os.path.join(os.path.dirname(__file__), '\\Python'))
            adjunto = 'D:\\Documentos\\Finanzas\\Cuentas e inversiones\\2026 Informe Financiero.xlsx'
        else:
            adjunto = '/video/2026 Informe Financiero.xlsx'
        
        if num > 4:
            # Si hay 5 avisos con correos de CONTROL ACCESO (no borrados, algo me ha pasado)
            # Se envía a todos los destinatarios, están separados por un espacio
            for dest in destinatario.split():
                print(f"Mensaje enviado a {dest} con adjunto.")
                Envio_mail_adjunto(usuario_javi, password_javi, alerta, mensaje, dest, adjunto)
        else:
            # envío mensaje que recibirán al día siguiente los destinatarios
            print(f"Ultimo aviso a {usuario_javi} con adjunto {adjunto}")
            Envio_mail_adjunto(usuario, password, alerta, mensaje, usuario_javi, adjunto)
            
            # Envío último aviso CONTROL ACCESO
            asunto = 'CONTROL ACCESO - Mail de control automático'
            mensaje = f"Aviso de control de acceso num. {num + 1}."
            Envio_mail(usuario, password , asunto, mensaje, usuario_javi)
    else:
        asunto = 'CONTROL ACCESO - Mail de control automático'
        mensaje = f"Aviso de control de acceso num. {num + 1}."
        Envio_mail(usuario, password , asunto, mensaje, usuario_javi)




if __name__ == '__main__':
    from Herramientas.variables import leer_variables
    config = leer_variables()
    
    Alerta_CONTROL(config['USER_MAIL'], config['PASSWORD_MAIL'], config['USER_JAVI'], config['PASSWORD_JAVI'], config['DESTINATARIO_MAIL'])
