import socket
import threading

alais = input("Chose your name : ")

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = "127.0.0.1"
port = 59000
client.connect((host,port))

def client_receive():
    while True:
        try:
            message = client.recv(1024)
            message = message.decode('utf-8')
            if message == "Yourname:":
                client.send(alais.encode('utf-8'))
            else:
                print(message)
        except:
            print("Error......404")
            client.close
            break

def clinet_send():
    while True:
        message = f'{alais} : {input("")}'
        client.send(message.encode('utf-8'))

receving_thread =threading.Thread(target=client_receive)
receving_thread.start()
sending_thread = threading.Thread(target=clinet_send)
sending_thread.start()