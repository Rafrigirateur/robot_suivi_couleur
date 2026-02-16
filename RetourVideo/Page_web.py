import os
import sys
import cv2
import threading
import time
from flask import Flask, Response, render_template_string
import socket
from datetime import datetime


root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)


from Hardware.moteur import Moteur
from Hardware.camera import Camera as cam
from Controlle.MoteurControlle import MoteurControle


# Initialisation de l'application Flask
app = Flask(__name__)

# Initialisation de la caméra
my_cam = cam(camId=0, width=320, height=240, fps=10)
moteur = Moteur(force=50)
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
    return render_template_string("""
    <html>
      <head>
        <title>Robot Control Center</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <style>
            .video-container {
                position: relative;
                display: inline-block;
            }
            /* Bouton discret superposé sur la vidéo */
            .capture-btn-mini {
                position: absolute;
                bottom: 10px;
                right: 10px;
                background: rgba(0, 0, 0, 0.6);
                color: white;
                border: 1px solid white;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                cursor: pointer;
                font-size: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: 0.3s;
            }
            .capture-btn-mini:hover {
                background: rgba(33, 150, 243, 0.8);
                transform: scale(1.1);
            }
            .capture-btn-mini:active { transform: scale(0.9); }
            
            /* Feedback visuel lors de la capture */
            .flash {
                animation: flash-animation 0.2s;
            }
            @keyframes flash-animation {
                0% { opacity: 1; }
                50% { opacity: 0.3; }
                100% { opacity: 1; }
            }
        </style>
      </head>
      <body>
        <h1>Robot Monitor</h1>
        
        <div class="container">
          <div class="video-container">
            <img id="video-feed" src="{{ url_for('video_feed_raw') }}">
            <button class="capture-btn-mini" onclick="capture()" title="Prendre une photo">📸</button>
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
          
          function capture() {
            const img = document.getElementById('video-feed');
            fetch('/capture')
              .then(response => {
                  if(response.ok) {
                      // Petit effet de flash visuel sur l'image
                      img.classList.add('flash');
                      setTimeout(() => img.classList.remove('flash'), 200);
                  }
              });
          }

          document.addEventListener('keydown', (e) => {
              const keys = {
                "ArrowUp": "forward", "ArrowDown": "backward", 
                "ArrowLeft": "left", "ArrowRight": "right", " ": "stop"
              };
              if(keys[e.key]) move(keys[e.key]);
              if(e.key.toLowerCase() === "c") capture();
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
        robot_moteur.avancer()
    elif direction == "backward":
        robot_moteur.reculer()
    elif direction == "left":
        robot_moteur.gauche()
    elif direction == "right":
        robot_moteur.droite()
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

@app.route("/capture")
def capture_frame():
    global output_frame_raw, lock
    
    # Création du dossier 'frames' s'il n'existe pas
    folder = os.path.join(root_path, "frames")
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    with lock:
        if output_frame_raw is not None:
            # Copie pour éviter les conflits pendant l'écriture
            frame_to_save = output_frame_raw.copy()
            
            # Nom de fichier unique : frame_20231027_153045.jpg
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"frame_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            
            # Sauvegarde de l'image
            cv2.imwrite(filepath, frame_to_save)
            print(f"Image sauvegardée : {filepath}")
            return f"Frame saved as {filename}", 200
        else:
            return "No frame available", 500

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
