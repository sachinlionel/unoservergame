from random import shuffle
from objects.u_card import deck_of_cards, Action
from objects.game_logger import game_logger
import copy
from config import port
import time
import socket
from collections import namedtuple

gLog = game_logger()


def reverse_items_at_index(items, index):
    return list(reversed(items[:index-1])) + list(reversed(items[index-1:]))

def send_data(player, data, expect_reply=False):
    time.sleep(0.5)
    player.send(data.encode())
    if expect_reply:
        while True:
            data = player.recv(2048)
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


    @play_right_card
    def play_card(self, ref_card):
        card_index = int(send_data(self.socket, "card index:", expect_reply=True))
        python_index = card_index - 1
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


class GameServer:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # establish server
    s.bind((socket.gethostname(), port))
    # open server for incoming connection
    s.listen(4)

    def __init__(self):
        self.init_cards = 7
        self.limit_players = 4
        self.deck_cards = deck_of_cards()
        shuffle(self.deck_cards)
        self.players = None
        self.team_up()
        self.distribute_cards()
        self.open_card = self.deck_cards.popleft()
        gLog.info("Game Starts")
        gLog.info("Number of cards in deck: {}".format(self.deck_cards.__len__()))
        self.winner = False
        self.initiate()
        # get deck of cards

    def team_up(self):
        # get players
        game_player = namedtuple('game_player', 'socket player')
        print("waiting for 2 players..")
        self.players = []

        while True:
            # accept incoming connection
            player_socket, addr = self.s.accept()
            send_data(player_socket, f"you are connected to game server, your ip address {addr}")
            name = send_data(player_socket, "name:", expect_reply=True)
            self.players.append(game_player(player_socket, Player(name, player_socket)))
            gLog.info(f"Player {name} is ready to play")
            if len(self.players) >= 2:
                break
        gLog.info("Player: {}".format(self.players))


    def distribute_cards(self):
        # distribute cards among players
        for num in range(self.init_cards):
            for _ in self.players:
                card = self.deck_cards.popleft()
                _.player.my_cards.append(card)

    def initiate(self):
        play_ref = self.open_card
        players_pool = self.players
        while not self.winner:
            for index, item in enumerate(players_pool):
                uno_player = item.player
                uno_player_socket = item.socket
                gLog.info("Open Card: %s", play_ref.__str__)
                gLog.info("%s's TURN", uno_player.name)
                player_cards = uno_player.display_my_cards()
                if play_ref.action == Action.SKIP_TURN:
                    gLog.info("SKIPPED %s's TURN", uno_player.name)
                    play_ref.action = Action.PLAY_NORMS
                    continue
                elif play_ref.action == Action.DRAW_TWO:
                    self.draw_cards(uno_player, 2)
                    play_ref.action = Action.PLAY_NORMS
                    continue
                elif play_ref.action == Action.DRAW_FOUR_COLOR_CHANGE:
                    self.draw_cards(uno_player, 4)
                    play_ref.action = Action.PLAY_NORMS
                    continue
                elif play_ref.action == Action.PLAY_NORMS:
                    if uno_player.has_playable_card(play_ref):
                        send_data(uno_player_socket, f"Your cards: {str(player_cards)}")
                        send_data(uno_player_socket, f"Ref card: {play_ref.__str__}")
                        send_data(uno_player_socket, f"{uno_player.name.capitalize()}, please play a card")
                        play_ref = uno_player.play_card(play_ref)
                    else:
                        self.draw_cards(uno_player, 1)

                print("{} played {}".format(uno_player.name, play_ref.__str__))
                if play_ref.action == Action.REVERSE_ORDER:
                    gLog.info("%s REVERSED ORDER", uno_player.name)
                    players_pool = reverse_items_at_index(players_pool, index)
                    play_ref.action = Action.PLAY_NORMS
                    break
                gLog.info("+"*30)
                time.sleep(2)

    def draw_cards(self, draw_player, number_of_cards):
        gLog.info("Uh!, I am drawing {} cards".format(number_of_cards))
        for _ in range(number_of_cards):
            new_card = self.deck_cards.popleft()
            draw_player.my_cards.append(new_card)


if __name__ == "__main__":
    GameServer()
