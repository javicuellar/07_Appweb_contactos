import os



SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
DEBUG = True

# PWD = os.path.abspath(os.curdir) + '/instancias'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/dbase.db'.format(PWD)
SQLALCHEMY_DATABASE_URI = 'sqlite:////usr/bd/sqlite/contactos_07.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
