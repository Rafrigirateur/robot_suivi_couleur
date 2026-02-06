#!/bin/bash
# Aller dans le dossier pour que les imports relatifs fonctionnent
cd /home/robot/robot_suivi_couleur

# Lancer avec le Python de l'environnement virtuel
# Pas besoin de faire "source activate", appeler le binaire suffit
/home/robot/robot_suivi_couleur/.env/bin/python RetourVideo/Page_web.py >> /home/robot/robot_log.txt 2>&1