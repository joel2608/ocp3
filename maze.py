"""
Author: freezed <freezed@users.noreply.github.com> 2018-03-17
Version: 0.1
Licence: `GNU GPL v3` GNU GPL v3: http://www.gnu.org/licenses/

This file is part of [_ocp3_ project](https://github.com/freezed/ocp3)
"""
import os
import random
from pygame.locals import K_UP, K_DOWN, K_RIGHT, K_LEFT
from conf import (
    elmt_val, ERR_FILE, ERR_LINE, MSG_COLLECT, MSG_LOSER, MSG_OK,
    MSG_WALL, MSG_WINNER, HEAD_MESSAGES, MAZE_SIZE
)


class Maze:
    """
    Provides a usable maze from a text file
    Checks the maze compatibility
    Moves the player to it
    """

    def __init__(self, maze_file):
        """
        Initialise maze

        The Maze object has given attributes:

        :var int status: move status (what append after a move command)
        :var str status_message: feedback message for player
        :var lst splited_maze: splited maze in a list
        :var str _maze_in_a_string: maze string
        :var str _element_under_player: Element under player
        :var int _player_position: Player index in _maze_in_a_string

        :param maze_file: maze filename
        :rtype maze: str()
        :return: None
        """
        # Loading maze file
        if os.path.isfile(maze_file) is False:
            self.status = False
            print(ERR_FILE.format(maze_file))

        else:
            with open(maze_file, "r") as maze_data:
                splited_maze = maze_data.read().splitlines()

            if self.check_file(splited_maze):

                # Builds a square maze (if end-line spaces are missing in the file)
                self._maze_in_a_string = '\n'.join(
                    (self.check_line(line) for line in splited_maze)
                )

                # Gets player initial position
                self._player_position = self._maze_in_a_string.find(
                    elmt_val('symbol', 'name', 'player', 0)
                )

                # Defines Element under player at start
                self._element_under_player = elmt_val('symbol', 'name', 'void', 0)

                # Place collectables on the maze
                for symbol_to_place in elmt_val('symbol', 'collect', True):
                    position = random.choice(
                        [idx for (idx, value) in enumerate(
                            self._maze_in_a_string
                        ) if value == elmt_val(
                            'symbol', 'name', 'void', 0
                        )])
                    self.place_element(symbol_to_place, pos=position)

                self.MAX_ITEMS = sum(1 for _ in elmt_val('name', 'collect', True))
                self._COLUM = MAZE_SIZE + 1  # List starts to zero
                self._MAXIM = (self._COLUM * MAZE_SIZE) - 1

                self.status = True
                self.collected_items = []
                self.collected_items_num = 0

                self.status_message = {}
                self.status_message['title'] = HEAD_MESSAGES['title']
                self.status_message['status'] = HEAD_MESSAGES['status']
                self.status_message['items'] = HEAD_MESSAGES['items'].format(
                    self.collected_items_num, self.MAX_ITEMS
                )

            else:
                self.status = False

    @staticmethod
    def check_file(splited_maze):
        """
        Checks the maze conformity before starting the game

        :param list/str splited_maze: Maze splited in a list (line = index)
        """
        if len(splited_maze) != MAZE_SIZE:
            print(ERR_LINE.format(len(splited_maze)))
            return False

        # ++Add other checks here: elements inside, exit possible, etc++
        else:
            return True

    def maze_print(self):
        """ Return a string of the maze state """
        return self._maze_in_a_string.replace('\n', '')

    def move_to(self, pressed_key):
        """
        Move the player on the maze

        :param str pressed_key: direction (pygame const)
        """
        # Replace player on the maze by the under-element
        self._maze_in_a_string = self._maze_in_a_string.replace(
            elmt_val('symbol', 'name', 'player', 0),
            self._element_under_player
        )

        # Recupere la position suivante
        if pressed_key == K_UP:
            next_position = self._player_position - self._COLUM

        elif pressed_key == K_DOWN:
            next_position = self._player_position + self._COLUM

        elif pressed_key == K_RIGHT:
            next_position = self._player_position + 1

        elif pressed_key == K_LEFT:
            next_position = self._player_position - 1

        # Next position treatment
        if next_position >= 0 and next_position <= self._MAXIM:
            next_char = self._maze_in_a_string[next_position]

            if next_char == elmt_val('symbol', 'name', 'void', 0):
                self._player_position = next_position
                self.status_message['status'] = MSG_OK

            elif next_char in elmt_val('symbol', 'collect', True):
                self._player_position = next_position
                self._element_under_player = elmt_val(
                    'symbol', 'name', 'void', 0
                )
                self.collected_items.append(
                    elmt_val('name', 'symbol', next_char, 0)
                )
                self.collected_items_num += 1
                self.status_message['status'] = MSG_COLLECT.format(
                    elmt_val('name', 'symbol', next_char, 0)
                )
                self.status_message['items'] \
                    = HEAD_MESSAGES['items'].format(
                        self.collected_items_num, self.MAX_ITEMS
                    )

            elif next_char == elmt_val('symbol', 'name', 'exit', 0):
                self.status = False
                if sorted(self.collected_items) == sorted(
                        elmt_val('name', 'collect', True)
                ):
                    self.status_message['status'] = MSG_WINNER
                else:
                    missed_item_flist = ', '.join(
                        (item for item in elmt_val(
                            'name', 'collect', True
                        ) if item not in self.collected_items)
                    )
                    self.status_message['status'] = MSG_LOSER.format(
                        missed_item_flist
                    )

            else:  # wall or nline
                self.status_message['status'] = MSG_WALL
        else:
            self.status_message['status'] = MSG_WALL

        # Set the player on position
        self.place_element(elmt_val('symbol', 'name', 'player', 0))

    def place_element(self, element, **kwargs):
        """
        Set an element on the maze

        The position used is in ._player_position attribute
        Used for player and void after collecting items

        :param str element: the string of the element to place
        """
        # FIXME cannot find a way to define default value to the
        # method's arguments with class attributes
        if 'pos' in kwargs:
            pos = kwargs['pos']
        else:
            pos = self._player_position

        if 'txt' in kwargs:
            txt = kwargs['txt']
        else:
            txt = self._maze_in_a_string

        self._maze_in_a_string = txt[:pos] + element + txt[pos + 1:]

    @staticmethod
    def check_line(line):
        """
        Checks if a line has a good length (configured in MAZE_SIZE const).
        Fill it if it's too small, truncate if it's too long.
        """
        differance = MAZE_SIZE - len(str(line))
        if differance < 0:
            return line[:MAZE_SIZE]
        elif differance > 0:
            return line + (differance * elmt_val('symbol', 'name', 'void', 0))
        else:
            return line