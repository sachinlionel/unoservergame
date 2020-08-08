import socket
from config import port

ps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ps.connect((socket.gethostname(), port))


while True:
    msg = ps.recv(512).decode()
    print(msg)
    if msg == 'name:':
        player_name = input("enter your name: ")
        ps.send(player_name.encode())
    elif msg == 'card index:':
        player_name = input("enter your the card index: ")
        ps.send(player_name.encode())
