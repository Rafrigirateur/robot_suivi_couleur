import cv2
import time
import random
import os
import sys
import signal

# Ajout du chemin racine pour trouver les modules Hardware
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from Hardware.moteur import Moteur
from Hardware.camera import Camera

# Variable globale pour maintenir la boucle en vie
running = True

def gestionnaire_signaux(signum, frame):
    """
    Cette fonction est appelée automatiquement si le script reçoit un signal
    d'arrêt (Ctrl+C, déconnexion SSH, etc.)
    """
    global running
    print(f"\n[INFO] Signal {signum} reçu (ex: perte SSH ou Ctrl+C).")
    print("Fermeture sécurisée en cours pour sauvegarder la vidéo...")
    running = False # Fait sortir proprement de la boucle while

def main():
    global running
    
    # 1. Capture des signaux du système pour éviter la corruption vidéo
    signal.signal(signal.SIGINT, gestionnaire_signaux)  # Ctrl+C
    signal.signal(signal.SIGHUP, gestionnaire_signaux)  # Coupure SSH (Broken pipe)
    signal.signal(signal.SIGTERM, gestionnaire_signaux) # Demande de terminaison standard

    print("Initialisation de la caméra...")
    cam = Camera(camId=0, width=640, height=480, fps=30)
    
    print("Initialisation des moteurs...")
    moteur = Moteur(force=50)

    # 2. Configuration de l'enregistrement vidéo
    dossier_videos = os.path.join(root_path, "videos_enregistrees")
    if not os.path.exists(dossier_videos):
        os.makedirs(dossier_videos)
        
    nom_fichier = os.path.join(dossier_videos, f"enregistrement_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(nom_fichier, fourcc, 30.0, (640, 480))
    
    print(f"Début de l'enregistrement dans : {nom_fichier}")

    dernier_changement = time.time()
    duree_mouvement = 0 

    try:
        while running:
            temps_actuel = time.time()

            # --- A. GESTION DE LA VIDÉO ---
            frame = cam.get_frame()
            if frame is not None:
                out.write(frame)
            
            # --- B. GESTION DES MOUVEMENTS ALÉATOIRES (Plus doux) ---
            if temps_actuel - dernier_changement > duree_mouvement:
                
                actions_possibles = ["avancer", "reculer", "courbe_gauche", "courbe_droite", "arret"]
                action = random.choice(actions_possibles)
                
                # Temps de mouvement légèrement allongé pour apprécier la douceur
                duree_mouvement = random.uniform(1.5, 3.5)
                dernier_changement = temps_actuel
                
                print(f"Action: {action} | Durée: {duree_mouvement:.2f}s")
                
                # Vitesses réduites (max ~35%) pour éviter les chutes de tension
                if action == "avancer":
                    moteur.piloter(30, 30)
                elif action == "reculer":
                    moteur.piloter(-25, -25)
                elif action == "courbe_gauche":
                    moteur.piloter(15, 35) 
                elif action == "courbe_droite":
                    moteur.piloter(35, 15)
                elif action == "arret":
                    moteur.stop()

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        
    finally:
        # 3. Libération garantie des ressources
        print("\nArrêt des moteurs et clôture du fichier vidéo...")
        moteur.stop()
        moteur.cleanup()
        cam.release()
        out.release() # <-- C'est ça qui sauve ton fichier !
        cv2.destroyAllWindows()
        print(f"Terminé ! Vidéo sauvegardée avec succès sous : {nom_fichier}")

if __name__ == "__main__":
    main()