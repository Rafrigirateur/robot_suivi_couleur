import os
import sys
import cv2
import threading
import time
from flask import Flask, Response, render_template_string
import socket


root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)


from Hardware.Moteur import Moteur
from Hardware.camera import Camera as cam
from Controlle.MoteurControlle import MoteurControle


# Initialisation de l'application Flask
app = Flask(__name__)

# Initialisation de la caméra
my_cam = cam(camId=0, width=320, height=240, fps=10)
moteur = Moteur(force=25)
robot_moteur = MoteurControle(moteur)

# Variables partagées entre les threads
output_frame_raw = None
output_frame_processed = None
lock = threading.Lock()

def process_video():
    global output_frame_raw, output_frame_processed, lock
    print("Démarrage du thread vidéo...") # DEBUG
    
    while True:
        frame = my_cam.get_frame()

        if frame is not None:
          with lock:
            output_frame_raw = frame.copy()
        else:
            time.sleep(0.01)

def generate_feed(mode='raw'):
  """
  Générateur qui récupère la dernière image disponible et l'envoie au navigateur.
  """
  global output_frame_raw, output_frame_processed, lock
  
  while True:
      with lock:
          if mode == 'raw':
              if output_frame_raw is None: continue
              frame_to_encode = output_frame_raw
          else:
              if output_frame_processed is None: continue
              frame_to_encode = output_frame_processed
          
          # Encodage en JPEG (nécessaire pour le web)
          encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
          (flag, encodedImage) = cv2.imencode(".jpg", frame_to_encode, encode_param)
          
          if not flag:
              continue

      # Envoi du flux d'octets au format MJPEG
      yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')
      time.sleep(0.05)  # Petite pause pour limiter la bande passante

# --- Routes Flask ---

@app.route("/")
def index():
    # Page HTML simple intégrée dans le code pour la démonstration
    return render_template_string("""
    <html>
      <head>
        <title>Robot Control Center</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
      </head>
      <body>
        <h1>Pilotage Raspberry Pi</h1>
        <div class="container">
          <div class="video-box">
            <img src="{{ url_for('video_feed_raw') }}">
          </div>
        </div>

        <div class="controls">
          <div></div><button onclick="move('forward')">▲</button><div></div>
          <button onclick="move('left')">◀</button>
          <button onclick="move('stop')" class="stop">■</button>
          <button onclick="move('right')">▶</button>
          <div></div><button onclick="move('backward')">▼</button><div></div>
        </div>

        <script>
          function move(direction) {
            fetch('/move/' + direction);
          }
          // Arrêt automatique si on relâche une touche (optionnel)
          document.addEventListener('keydown', (e) => {
              if(e.key === "ArrowUp") move('forward');
              if(e.key === "ArrowDown") move('backward');
              if(e.key === "ArrowLeft") move('left');
              if(e.key === "ArrowRight") move('right');
              if(e.key === " ") move('stop');
          });
        </script>
      </body>
    </html>
    """)

@app.route("/move/<direction>")
def move_robot(direction):
    # On définit une puissance par défaut (ex: 50%)
    power = 25 
    
    if direction == "forward":
        robot_moteur.droite()
    elif direction == "backward":
        robot_moteur.gauche()
    elif direction == "left":
        robot_moteur.avancer()
    elif direction == "right":
        robot_moteur.reculer()
    elif direction == "stop":
        robot_moteur.stop()
        
    return f"Robot moving {direction}", 200

@app.route("/video_feed_raw")
def video_feed_raw():
    return Response(generate_feed('raw'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/video_feed_processed")
def video_feed_processed():
    return Response(generate_feed('processed'),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# --- Démarrage ---

def wait_for_network():
    """Attend que le Raspberry Pi ait une adresse IP valide."""
    print("En attente de connexion réseau...")
    while True:
        try:
            # On tente de se connecter à un DNS public (Google) pour vérifier l'accès
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            print(f"Connecté ! Adresse IP : {ip}")
            return True
        except Exception:
            # Si échec, on attend 2 secondes avant de réessayer
            print("Pas de connexion réseau. Nouvelle tentative dans 2 secondes...")
            time.sleep(2)

if __name__ == "__main__":
    # Attendre que le réseau soit disponible
    wait_for_network()

    # Lancer le thread de traitement vidéo en arrière-plan
    t = threading.Thread(target=process_video)
    t.daemon = True # Le thread se fermera quand le script principal s'arrêtera
    t.start()

    # Lancer le serveur Flask
    # host='0.0.0.0' permet l'accès depuis d'autres PC sur le réseau
    app.run(host="0.0.0.0", port=8001, debug=False, threaded=True)
