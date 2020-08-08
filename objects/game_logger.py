import logging as log


def game_logger():
    log.basicConfig(format='%(message)s', level=log.DEBUG)
    return log
