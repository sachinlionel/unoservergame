import socket
import time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# establish server
s.bind((socket.gethostname(), 1024))
# open server for incoming connection
s.listen(1)
players = {}


def send_data(player, data, expect_reply=False):
    time.sleep(0.5)
    player.send(data.encode())
    if expect_reply:
        while True:
            data = player.recv(2048)
            if data:
                time.sleep(0.1)
                return data.decode()


while True:
    # accept incoming connection
    player, addr = s.accept()
    players[player] = addr
    send_data(player, f"you are connected to game server, your ip address {addr}")
    name = send_data(player, 'name:', expect_reply=True)
    print("player name", name)

