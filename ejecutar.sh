#!/bin/bash

echo "##############    AppWeb_contactos    #############"
echo "Instalando las dependencias necesarias"
cd ./Proyectos
cd ./07_Appweb_contactos
pip install -r requirements.txt  > ./requirements.log


echo "Copiar scripts Herramientas"
cp -r /usr/python/Herramientas /usr/local/lib/python3.13/site-packages


echo "Ejecutando el script de Alertas: CONTROL ACCESO, Madrid Digital y tamaño ficheros"
python3 ./alertas/alertas.py 


echo "Iniciando la aplicación web Appweb Contactos"
python3 ./run.py


# Esperar a que ambos procesos terminen
wait
echo "Todos los procesos han terminado."