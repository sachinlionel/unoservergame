from objects import u_card
import time
from objects.game_logger import game_logger
gLog = game_logger()
import socket

ps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ps.connect((socket.gethostname(), 1025))


while True:
    msg = ps.recv(512).decode()
    print(msg)
    if msg == 'name:':
        player_name = input("enter your name: ")
        ps.send(player_name.encode())


CardAction = u_card.Action


def send_data(player_socket, data, expect_reply=False):
    time.sleep(0.5)
    player_socket.send(data.encode())
    if expect_reply:
        while True:
            data = player_socket.recv(2048)
            if data:
                time.sleep(0.1)
                return data.decode()


def play_right_card(fn):
    def wrapper(self, ref_card):
        card = fn(self, ref_card)
        while not card:
            gLog.info("You cannot play that card, this is the Open card: {}".format(ref_card.__str__))
            card = fn(self, ref_card)
        return card
    return wrapper


def can_play(selected_card, ref_card):
    playable = False
    if selected_card.color == ref_card.color:
        playable = True
    elif selected_card.figure == ref_card.figure:
        playable = True
    return playable


class Player:

    def __init__(self, name, socket):
        self.name = name
        self.socket = socket
        self.my_cards = []
        send_data(self.socket, "messsage from player class")


    @play_right_card
    def play_card(self, ref_card):
        play_card_index = int(input("index of your card :"))
        python_index = play_card_index - 1
        if python_index < len(self.my_cards):
            card = self.my_cards[python_index]
            if can_play(card, ref_card):
                self.my_cards.remove(card)
                return card

    def display_my_cards(self):
        for _ in self.my_cards:
            gLog.info(_.__str__)
        return [_.__str__ for _ in self.my_cards]

    def has_playable_card(self, ref_card):
        playable_card = False
        available_colors = [_.color for _ in self.my_cards]
        available_figures = [_.figure for _ in self.my_cards]
        gLog.info("ref card: {}".format(ref_card.__str__))
        gLog.info("I am {}, i have {} and {}".format(self.name, available_colors, available_figures))
        if not available_colors and  not available_figures:
            print("I won")
        if ref_card.color in available_colors:
            playable_card = True
        elif ref_card.figure in available_figures:
            playable_card = True
        if playable_card:
            gLog.info("I have playable card")
        return playable_card


    def shout_uno(self):
        pass
