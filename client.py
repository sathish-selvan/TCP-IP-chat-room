import socket
import threading
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=59000)

args = parser.parse_args()

port = args.port
host = args.host

# parse host if host and port is provided in the host valueholder
if host != "127.0.0.1":
    host_socket_addr = host.split(":")
    
    if len(host_socket_addr)>2:
        host = host_socket_addr[1].replace("//", "")
        port = int(host_socket_addr[-1])

alais = input("Chose your name : ")

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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