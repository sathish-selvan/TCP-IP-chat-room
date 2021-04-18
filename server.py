import threading 
import socket

host = "127.0.0.1"
port = 59000

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen(5)
clients = []
aliases = []

def broadcast(sender,message):
    for client in clients:
        if client != sender:
            client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(client,message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            alias = aliases[index]
            broadcast(client,f"{alias} has left the chat room!".encode('utf-8'))
            aliases.remove(alias)
            break

def receive():
    while True:
        print("server runing")
        client,address = server.accept()
        print(f"Connection is established wth {str(address)}")
        client.send("Yourname:".encode('utf-8'))
        alias = client.recv(1024)
        aliases.append(alias)
        clients.append(client)
        broadcast(client,f'{alias} has connected to the chatroom'.encode('utf-8'))
        client.send("Your are now connected".encode('utf-8'))
        thread = threading.Thread(target=handle_client,args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()

