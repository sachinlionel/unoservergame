import socket
from config import port

ps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ps.connect((socket.gethostname(), port))


while True:
    msg = ps.recv(512).decode()
    if msg == 'enter your name: ':
        ip = input("enter your name: ")
        ps.send(ip.encode())
    elif msg == 'play a card by index: ':
        ip = input(msg)
        ps.send(ip.encode())
    elif msg == "please chose a color: ":
        ip = input(msg)
        ps.send(ip.encode())
    else:
        print(f"{msg}")