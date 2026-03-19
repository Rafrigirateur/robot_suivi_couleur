import cv2
import time
import random
import os
import sys

# Ajout du chemin racine pour trouver les modules Hardware
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from Hardware.moteur import Moteur
from Hardware.camera import Camera

def main():
    # 1. Initialisation du matériel
    print("Initialisation de la caméra...")
    cam = Camera(camId=0, width=640, height=480, fps=30)
    
    print("Initialisation des moteurs...")
    moteur = Moteur(force=50)

    # 2. Configuration de l'enregistrement vidéo (Codec XVID, format AVI)
    dossier_videos = os.path.join(root_path, "videos_enregistrees")
    if not os.path.exists(dossier_videos):
        os.makedirs(dossier_videos)
        
    nom_fichier = os.path.join(dossier_videos, f"enregistrement_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # Assure-toi que les dimensions correspondent à celles de la caméra
    out = cv2.VideoWriter(nom_fichier, fourcc, 30.0, (640, 480))
    
    print(f"Début de l'enregistrement dans : {nom_fichier}")
    print("Appuyez sur 'q' dans la fenêtre vidéo ou CTRL+C dans le terminal pour arrêter.")

    # Variables pour la gestion des mouvements aléatoires
    dernier_changement = time.time()
    duree_mouvement = 0 # Le premier changement sera immédiat

    try:
        while True:
            temps_actuel = time.time()

            # --- A. GESTION DE LA VIDÉO ---
            frame = cam.get_frame()
            if frame is not None:
                out.write(frame)
                # Affichage optionnel du retour vidéo (peut ralentir un peu le Raspberry Pi)
                # cv2.imshow('Camera Robot', frame)
            
            # --- B. GESTION DES MOUVEMENTS ALÉATOIRES ---
            # Si le temps écoulé dépasse la durée prévue pour le mouvement actuel, on change
            if temps_actuel - dernier_changement > duree_mouvement:
                
                # Choix aléatoire d'une action
                actions_possibles = ["avancer", "reculer", "courbe_gauche", "courbe_droite", "arret"]
                action = random.choice(actions_possibles)
                
                # Définition d'une durée aléatoire pour cette action (entre 1 et 3 secondes)
                duree_mouvement = random.uniform(1.0, 3.0)
                dernier_changement = temps_actuel
                
                print(f"Action: {action} | Durée: {duree_mouvement:.2f}s")
                
                # Application des puissances aux moteurs (gauche, droite)
                if action == "avancer":
                    moteur.piloter(50, 50)
                elif action == "reculer":
                    moteur.piloter(-40, -40)
                elif action == "courbe_gauche":
                    moteur.piloter(20, 60) # Moteur droit tourne plus vite
                elif action == "courbe_droite":
                    moteur.piloter(60, 20) # Moteur gauche tourne plus vite
                elif action == "arret":
                    moteur.stop()

            # Permet de quitter proprement si on affiche la vidéo avec cv2.imshow
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterruption clavier détectée. Arrêt en cours...")
        
    finally:
        # 3. Libération propre de toutes les ressources (TRÈS IMPORTANT)
        print("Libération des moteurs et de la caméra...")
        moteur.cleanup()
        cam.release()
        out.release()
        cv2.destroyAllWindows()
        print("Terminé ! Vidéo sauvegardée.")

if __name__ == "__main__":
    main()