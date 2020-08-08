import copy
import random
from collections import namedtuple, deque

from objects.game_logger import game_logger
gLog = game_logger()


# power cards
REV = '<- REVERSE'
PLUS2 = '+2 PLUS TWO'
SKIP = '0 SKIP'
# wild powercards
PLUS4 = '+4 PLUS FOUR'
WILD = '* WILD'
# special cards
SWAP = '=>=< SWAP'


class Action:
    # play actions
    PLAY_NORMS = 'play a card'
    SKIP_TURN = 'skip turn'
    REVERSE_ORDER = 'reverse the player order'

    # draw actions
    DRAW_TWO = 'draw two cards'

    # color change
    DRAW_FOUR_COLOR_CHANGE = 'draw four cards with color change'
    COLOR_CHANGE = 'color change'


class CardFamily:
    NUMBER = 'number'
    POWER = 'power'
    WILD_POWER = 'wild power'
    SPECIAL = 'special'
    card_family = namedtuple('card_family', 'weight figures')
    families = {NUMBER: card_family(None, list(range(0, 10))),
                POWER: card_family(20, [REV, PLUS2, SKIP]),
                WILD_POWER: card_family(50, [PLUS4, WILD]),
                SPECIAL: card_family(100, [SWAP])}
    all_families = [NUMBER, POWER, WILD, SPECIAL]

    def __init__(self, family, figure):
        self.family = family
        self.figure = figure
        self.family_weight = self.families[self.family].weight
        self.validate_figure()

    @property
    def range_of_cards(self):
        return self.families[self.family].figures

    def validate_figure(self):
        assert self.figure in self.range_of_cards

    @property
    def weight(self):
        return self.family_weight if self.family_weight else self.figure


class UnoCard(CardFamily):

    def __init__(self, color, family, figure):
        self.color = color
        self.figure = figure
        self.family = family
        CardFamily.__init__(self, self.family, self.figure)
        self.action = None
        self.cast_action()
        assert self.action

    @property
    def __str__(self):
        # return "UnoCard: {} ({}) family: {}, ActNext: {}".format(self.figure, self.color, self.family, self.action)
        return "{} ({})".format(self.figure, self.color)

    def cast_action(self):
        if self.figure in self.families[self.NUMBER].figures or self.figure in [PLUS2, PLUS4, WILD]:
            self.action = Action.PLAY_NORMS
            if self.figure == PLUS2:
                self.action = Action.DRAW_TWO
            elif self.figure == PLUS4:
                self.action = Action.DRAW_FOUR_COLOR_CHANGE
            elif self.figure == WILD:
                self.action = Action.COLOR_CHANGE
        elif self.figure in [SKIP]:
            self.action = Action.SKIP_TURN
        elif self.figure in [REV]:
            self.action = Action.REVERSE_ORDER


def deck_of_cards():
    # colors
    colors = ['red', 'blue', 'green', 'yellow']
    # card range
    set_of_number_figures = CardFamily.families[CardFamily.NUMBER].figures
    second_set_of_number_figures = copy.deepcopy(set_of_number_figures)
    second_set_of_number_figures.pop(0)
    all_family_figures = {CardFamily.NUMBER: set_of_number_figures + second_set_of_number_figures,
                          CardFamily.POWER: CardFamily.families[CardFamily.POWER].figures + CardFamily.families[CardFamily.POWER].figures,
                          CardFamily.WILD_POWER: CardFamily.families[CardFamily.WILD_POWER].figures}
    playble_cards = deque([])
    for col in colors:
        for _ in all_family_figures:
            figures = all_family_figures[_]
            for figure in figures:
                playble_cards.append(UnoCard(color=col, family=_, figure=figure))

    assert len(playble_cards) == 108
    return playble_cards
