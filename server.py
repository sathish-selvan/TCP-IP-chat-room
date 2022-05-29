import threading
import socket
import time
from sys import platform, exit
import os
from urllib.request import urlopen
import zipfile
import subprocess
import argparse
import tarfile
import logging

logging.basicConfig(filename='chat-room.log', filemode='a',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

parser = argparse.ArgumentParser()
parser.add_argument("--ngrok-link", type=str)
parser.add_argument("--authtoken", type=str)
parser.add_argument("--port", type=int, default=59000)
args = parser.parse_args()

port = args.port
authtoken = args.authtoken
ngrok_link = args.ngrok_link
# host listener
host = "127.0.0.1"

# check the platform
if platform == "linux" or platform == "linux2":
    # path to ngrok binary
    ngrok_file_path = os.path.join(os.getcwd(), 'ngrok')

    # check if ngrok binary exists in the current directory
    if not os.path.exists(ngrok_file_path):

        print("Downloading ngrok for linux...")
        logging.info("Downloading ngrok for linux...")

        # download the zip file
        link = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
        zip_file = urlopen(link)
        zip_file_path = os.path.join(os.getcwd(), 'ngrok.tgz')
        try:
            with open(zip_file_path, 'wb') as output:
                output.write(zip_file.read())
                output.flush()

            print("Extracting ngrok...")
            logging.info("Extracting ngrok...")
            # unzip the download file to get the binary file
            with tarfile.open(zip_file_path) as tar_ref:
                tar_ref.extractall(os.getcwd())
        except Exception as e:
            logging.info(e)
            print(e)
            exit()

elif platform == "win32":

    # path to ngrok binary
    ngrok_file_path = os.path.join(os.getcwd(), 'ngrok.exe')

    # check if ngrok binary exists in the current directory
    if not os.path.exists(ngrok_file_path):

        print("Downloading ngrok for windows...")
        logging.info("Downloading ngrok for windows...")

        # download the zip file
        link = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        zip_file = urlopen(link)
        zip_file_path = os.path.join(os.getcwd(), 'ngrok.zip')
        try:
            with open(zip_file_path, 'wb') as output:
                output.write(zip_file.read())
                output.flush()

            print("Extracting ngrok.exe")
            logging.info("Extracting ngrok.exe")
            # unzip the download file to get the binary file
            zip_file_path = os.path.join(os.getcwd(), 'ngrok.zip')
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
        except Exception as e:
            logging.info(e)
            print(e)
            exit()

else:
    print("Unknown platform, Exiting the application")
    logging.error("Extracting ngrok.exe")
    exit()
print("Starting the server...")
logging.info("Starting the server...")
# create a socket, bind a socket and start listening
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)

clients = []
aliases = []
thread_list = []


def generate_public_address(port):
    '''
    Generate public address for the current server using ngork
    '''
    try:
        subprocess.Popen([ngrok_file_path, "tcp", str(port)])
    except Exception as e:
        logging.error(e)
        print(e)
        exit()


def broadcast(sender, message):
    '''
    Send text to all the connected clients
    '''
    for client in clients:
        if client != sender:
            client.send(message)


def handle_client(client):
    '''
    Keep listening to the client messages and broadcast to all the connected clients.
    '''
    while 1:
        try:
            # get the message from the client
            message = client.recv(1024)

            # send the message to all the client
            broadcast(client, message)

        # something went wrong
        except Exception as e:
            logging.error(e)
            # get the index of the current client
            index = clients.index(client)

            # remove the client
            clients.remove(client)

            # close the connection
            client.close()

            # get the alias for the current client
            alias = aliases[index]

            # alert all users and remove the alias from current client
            broadcast(
                client, f"{alias} has left the chat room!".encode('utf-8'))
            aliases.remove(alias)
            break
        # give CPU some break, half a second
        time.sleep(0.5)


def receive(port):
    '''
    Listens for the new connection and create a session for each client
    '''

    # if auth token is provided, set the authtoken using ngrok.exe
    if authtoken:
        print("Setting authtoken...")
        logging.info("Setting authtoken...")
        try:
            # add auth token
            subprocess.Popen([ngrok_file_path, "config",
                              "add-authtoken",
                              authtoken])
        except Exception as e:
            logging.info(e)
            print(e)
            exit()

    # run the ngrok client as seperate process
    thread = threading.Thread(target=generate_public_address, args=([port]))
    thread.start()

    print("Listening for new connections...")
    logging.info("Listening for new connections...")

    # listen continously
    while 1:

        # accept the connection if any
        client, address = server.accept()

        print(f"{str(address)} : connected")
        logging.info(f"{str(address)} : connected")

        # ask client to enter the name
        client.send("Yourname:".encode('utf-8'))

        # recieve the client name and add it to alias
        alias = client.recv(1024)
        aliases.append(alias)
        clients.append(client)

        # alert all the connected clients about the new connection
        broadcast(
            client, f'{alias} has connected to the chatroom'.encode('utf-8'))

        # alert the current client
        client.send("Your are now connected".encode('utf-8'))

        # start the thread for the current client for handling the messages
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

        # add to the thread list
        thread_list.append(thread)

        # give CPU some break, half a second
        time.sleep(0.5)


if __name__ == "__main__":
    # start the server
    receive(port)
