import os
from app.app import app as aplicacion
from app.app import db





if __name__ == "__main__":
    try:
        with aplicacion.app_context():
            db.create_all()
    except Exception as e:
        print(f"Error occurred: {e}")
        
    if os.name == 'nt':
        aplicacion.run(port=5010)
    else:
        # Conexión segura https para el NAS
        # aplicacion.run(ssl_context=('/usr/config/cert.pem', '/usr/config/privkey.pem'),
        #               host="192.168.1.41", port=5010, debug=True)
        
        # Cambiamos a HTTP utilizando el proxy inverso del NAS -> javicu.synology.me:5001
        aplicacion.run(port=5010)
