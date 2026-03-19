import cv2
import time
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

# =====================================================================
# PROGRAMMATION DES MOUVEMENTS
# Format : (vitesse_moteur_gauche, vitesse_moteur_droit, temps_en_secondes)
# =====================================================================
SEQUENCE_MOUVEMENTS = [
    (0, 0, 2.0),      # Attendre 2 secondes sur place avant de commencer
    (30, 30, 2.0),    # Avancer tout droit pendant 2s
    (0, 0, 1.0),      # Pause d'1 seconde
    (-15, -15, 0.5),    # Avancer tout droit pendant 2s
    (-30, -30, 1.0),    # Avancer tout droit pendant 2s
    (-15, -15, 0.5),    # Avancer tout droit pendant 2s
    (0, 0, 1.0),      # Pause d'1 seconde
    (35, 15, 2.5),    # Courbe vers la droite pendant 2.5s
    (15, 35, 2.5),    # Courbe vers la gauche pendant 2.5s
    (0, 0, 0.5),      # Petite pause
    (-25, -25, 2.0),  # Reculer tout droit pendant 2s
    (0, 0, 1.0)       # Arrêt final de 1 seconde avant de couper la vidéo
]

def gestionnaire_signaux(signum, frame):
    """Intercepte les signaux d'arrêt pour sauvegarder la vidéo proprement."""
    global running
    print(f"\n[INFO] Signal {signum} reçu. Arrêt propre en cours...")
    running = False 

def main():
    global running
    
    # 1. Capture des signaux
    signal.signal(signal.SIGINT, gestionnaire_signaux)
    signal.signal(signal.SIGHUP, gestionnaire_signaux)
    signal.signal(signal.SIGTERM, gestionnaire_signaux)

    print("Initialisation de la caméra...")
    cam = Camera(camId=0, width=640, height=480, fps=30)
    
    print("Initialisation des moteurs...")
    moteur = Moteur(force=50)

    # 2. Configuration de la vidéo
    dossier_videos = os.path.join(root_path, "videos_enregistrees")
    if not os.path.exists(dossier_videos):
        os.makedirs(dossier_videos)
        
    nom_fichier = os.path.join(dossier_videos, f"sequence_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(nom_fichier, fourcc, 30.0, (640, 480))
    
    print(f"Début de l'enregistrement dans : {nom_fichier}")

    # Variables de suivi de la séquence
    etape_actuelle = 0
    dernier_changement = time.time()
    duree_mouvement = 0 # Force le déclenchement immédiat de la première étape

    try:
        while running:
            temps_actuel = time.time()

            # --- A. ENREGISTREMENT VIDÉO ---
            frame = cam.get_frame()
            if frame is not None:
                out.write(frame)
            
            # --- B. LECTURE DE LA SÉQUENCE ---
            # Si le temps prévu pour le mouvement actuel est écoulé
            if temps_actuel - dernier_changement >= duree_mouvement:
                
                # S'il reste des étapes dans notre séquence
                if etape_actuelle < len(SEQUENCE_MOUVEMENTS):
                    # On récupère les consignes de l'étape
                    v_gauche, v_droite, duree = SEQUENCE_MOUVEMENTS[etape_actuelle]
                    
                    # On applique aux moteurs
                    moteur.piloter(v_gauche, v_droite)
                    
                    # On met à jour les chronomètres
                    duree_mouvement = duree
                    dernier_changement = temps_actuel
                    
                    print(f"Étape {etape_actuelle + 1}/{len(SEQUENCE_MOUVEMENTS)} | "
                          f"Gauche: {v_gauche}%, Droite: {v_droite}% | Durée: {duree}s")
                    
                    etape_actuelle += 1
                
                # Si toutes les étapes ont été lues
                else:
                    print("Séquence terminée avec succès.")
                    running = False # Fait sortir de la boucle while

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        
    finally:
        # 3. Libération garantie des ressources
        print("\nArrêt des moteurs et clôture du fichier vidéo...")
        moteur.stop()
        moteur.cleanup()
        cam.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Vidéo sauvegardée sous : {nom_fichier}")

if __name__ == "__main__":
    main()