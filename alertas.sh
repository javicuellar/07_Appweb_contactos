#!/bin/bash

echo "##############    Alertas    #############"
cd ./Proyectos/07_Appweb_contactos

echo "Ejecutando el script de Alertas: CONTROL ACCESO, Madrid Digital y tamaño ficheros"
python3 ./alertas/alertas.py 

wait
echo "Todos los procesos han terminado."