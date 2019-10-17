# Written by Michelle Blom, 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from utils import *

import numpy
import random
import abc
import copy

def allsame(list):
    return len(set(list)) == 1

# We use the PlayerState class to represent a player's game state:
# a stack of tiles.
class PlayerState:
    def __init__(self, _id):
        self.id = _id
        self.stack = []

        self.dice_bank = []
        self.current_total = 0
        self.worms = False
        self.dice_left = 0

    def TopTile(self):
        if len(self.stack) == 0:
            return -1
        return self.stack[-1]

    def AddTileToStack(self, tile_id):
        self.stack.append(tile_id)

    def TakeTileFromStack(self):
        return self.stack.pop()
 
    def Reset(self):
        self.dice_bank = []
        self.current_total = 0
        self.worms = False
        self.dice_left = 0        


# The GameState class encapsulates the state of the game: the game 
# state for each player; and the state of the tile line.
class GameState:
    NUM_TILES = 16
    MIN_TILE = 21
    MAX_TILE = 36

    TILES = [21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
    WORMS = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4]

    NUM_DICE = 8
    WORM = 6
    WORM_WORTH = 5

    DICE = [1,2,3,4,5,6]
    DICE_VAL = [1,2,3,4,5,5]

    def __init__(self, num_players):
        # Create player states
        self.players = []
        for i in range(num_players):
            ps = PlayerState(i)
            self.players.append(ps)
          
        # Tile line
        self.tile_line = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        # Identify of player who will start the game
        self.first_player = -1

    def ScorePlayers(self):
        scores = {}
        for plyr in self.players:
            score = 0
            for tile_id in plyr.stack:
                score += self.WORMS[tile_id]
            scores[plyr.id] = score
        return scores

    def IsGameOver(self):
        return len(self.tile_line) == 0

    def ExecuteMove(self, i, move):
        plyr = self.players[i]

        assert(len(self.tile_line) > 0)

        cont = True
        if move[0] == Move.ROLL:
            # Update player's banked dice
            dbank = move[1]
           
            # A player cannot take dice with a face that they
            # have already banked.
            assert(not (dbank.dice_value in plyr.dice_bank))

            for j in range(dbank.number):
                plyr.dice_bank.append(dbank.dice_value)
                if dbank.is_worm:
                    plyr.current_total += self.WORM_WORTH
                    plyr.worms = True
                else:
                    plyr.current_total += dbank.dice_value

                plyr.dice_left -= 1
                assert(plyr.dice_left >= 0) 

            if plyr.dice_left == 0:
                cont = False

        elif move[0] == Move.BUST:
            # Player has gone Bust!  The top tile in their 
            # stack (if they have a tile) is returned to the
            # tile line, and the largest value tile in the line
            # is removed from the game.
            self.tile_line.pop()

            if len(plyr.stack) > 0:
                tpop = plyr.stack.pop()
            
                # Insert back into tile line
                if len(self.tile_line) == 0:
                    self.tile_line.append(tpop)    
                elif tpop > self.tile_line[-1]:
                    self.tile_line.append(tpop)
                elif tpop < self.tile_line[0]:
                    self.tile_line.insert(0, tpop)
                else:
                    for j in range(1,len(self.tile_line)):
                        if tpop < self.tile_line[j]:
                            self.tile_line.insert(j, tpop)
                            break
            plyr.Reset()
            cont = False
                
        elif move[0] == Move.STOP:
            # Player has banked dice and decided to take a tile
            # from either a player or the tile line

            # Update player's banked dice
            dbank = move[1]
           
            # A player cannot take dice with a face that they
            # have already banked.
            assert(not (dbank.dice_value in plyr.dice_bank))
            for j in range(dbank.number):
                plyr.dice_bank.append(dbank.dice_value)
                if dbank.dice_value == self.WORM:
                    plyr.current_total += self.WORM_WORTH
                    plyr.worms = True
                else:
                    plyr.current_total += dbank.dice_value
                plyr.dice_left -= 1

            # Player can only take a tile from a player if 
            # it has a value equal to the player's current total AND
            # it is at the top of the other players stack
            tgrab = move[2]
            if tgrab.from_player != -1:
                tval = self.TILES[tgrab.tile_id]
                assert(tval == plyr.current_total)

                oplyr = self.players[tgrab.from_player]
                assert(len(oplyr.stack) > 0)
                assert(oplyr.stack[-1] == tgrab.tile_id)

                oplyr.stack.pop()
                plyr.stack.append(tgrab.tile_id)
            else:
                assert(tgrab.tile_id in self.tile_line)

                plyr.stack.append(tgrab.tile_id)
                self.tile_line.remove(tgrab.tile_id)

            plyr.Reset()
            cont = False
                            
        return (cont, plyr.dice_left)


    def GetAvailableMoves(self, pindex, game_state, roll):
        plyr = self.players[pindex]
        
        # The player has rolled their available dice and we need to 
        # determine what they can now choose to do.

        moves = []
        # Filter out of the roll all the dice they already have
        # in their bank -- they cannot take these
        filtered_roll = [d for d in roll if not (d in plyr.dice_bank)]
        if filtered_roll == []:
            # The player has gone bust.
            moves = [(Move.BUST, None, None)]
        if allsame(roll) and roll[0] != self.WORM and \
            not (self.WORM in plyr.dice_bank):
            # The player has gone bust.
            moves = [(Move.BUST, None, None)]
        else:
            # Player can take one set of dice with the same face.
            dice_nums = [0 for d in self.DICE]
            for d in filtered_roll:
                dice_nums[d-1] += 1

            for i in range(len(self.DICE)):
                if dice_nums[i] > 0:
                    
                    # Player could take these dice
                    dbank = DiceBank()
                    dbank.dice_value = i+1
                    dbank.number = dice_nums[i]
                    dbank.is_worm = (dbank.dice_value == self.WORM)

                    # If there are dice remaining, the player could 
                    # roll again. 
                    if plyr.dice_left - dbank.number > 0:
                        moves.append((Move.ROLL, dbank, None))

                    # If they take these dice, what would be their 
                    # current total
                    total = dice_nums[i]*self.DICE_VAL[i] + plyr.current_total
                    
                    # If they have a worm they could take a tile if they
                    # have the right total
                    if total >= self.MIN_TILE and \
                        ((self.WORM in plyr.dice_bank) or \
                        (dbank.dice_value == self.WORM)):

                        # is their total equal to a players top tile?
                        opindex = 0
                        for oplyr in self.players:
                            if oplyr.id != plyr.id:
                                tt = oplyr.TopTile()
                                if tt != -1 and self.TILES[tt] == total:
                                    tgrab = TileGrab()
                                    tgrab.tile_id = tt
                                    tgrab.tile_value = self.TILES[tt]
                                    tgrab.from_player = opindex
                                    moves.append((Move.STOP, dbank, tgrab))

                                    # There is only one instance of each
                                    # tile in the game.
                                    break
                            opindex += 1

                        # can the player grab a tile from the line
                        for tid in self.tile_line:
                            if self.TILES[tid] <= total:
                                # player could take this tile
                                tgrab = TileGrab()
                                tgrab.tile_id = tid
                                tgrab.tile_value = self.TILES[tid]
                                tgrab.from_tile_line = True
                                moves.append((Move.STOP, dbank, tgrab))
            if moves == []:
                # Player can take the remaining dice but it does not 
                # give a total that allows them to take a tile.
                moves = [(Move.BUST, None, None)]

        assert(len(moves) >= 1)
        return moves


# Class representing a policy for playing HECKMECK.  
class Player(object):
    def __init__(self, _id):
        self.id = _id
        super().__init__()

    # Given a set of available moves for the player to execute, and
    # a copy of the current game state (including that of the player),
    # select one of the moves to execute. 
    def SelectMove(self, roll, moves, game_state):
        return random.choice(moves)


# Class that facilities a simulation of a game of AZUL. 
class GameRunner:
    def __init__(self, player_list, seed):
        random.seed(seed)

        self.game_state = GameState(len(player_list))
        self.players = player_list
    
        assert(len(player_list) <= 7)
        assert(len(player_list) > 1)

        # Player id's must be unique and increasing from 0 
        i = 0
        for plr in player_list:
            assert(plr.id == i)
            i += 1

        # randomly assign first player
        fp = random.randrange(len(player_list))
        self.game_state.first_player = fp


    def Run(self, log_state):
        player_order = []
        for i in range(self.game_state.first_player, len(self.players)):
            player_order.append(i)

        for i in range(0, self.game_state.first_player):
            player_order.append(i)

        game_continuing = True
        while game_continuing:
            for i in player_order:
                if log_state:
                    print("==================== Player {} " \
                        "====================".format(i))

                plr_state = self.game_state.players[i]

                num_dice = self.game_state.NUM_DICE
                plr_state.dice_left = num_dice

                while True:
                    # Roll Dice
                    roll = []
                    for j in range(num_dice):
                        v = random.choice(self.game_state.DICE)
                        roll.append(v)

                    if log_state:
                        print("\n> Player {} has rolled {}".format(i,
                            RollToString(roll, self.game_state.WORM)))

                    moves = self.game_state.GetAvailableMoves(
                        i, self.game_state, roll)

                    selected = None
                    if len(moves) == 1 and moves[0][0] == Move.BUST:
                        # Player has gone bust.
                        if log_state:
                            print("\n> Player {} has gone bust.\n".format(i))
                        selected = moves[0]
                    else:
                        gs_copy = copy.deepcopy(self.game_state)
                        moves_copy = copy.deepcopy(moves)
                        roll_copy = roll[:]
                        selected = self.players[i].SelectMove(roll_copy,
                            moves_copy, gs_copy)

                        if log_state:
                            print("\nPlayer {} has chosen the following" \
                                " move:".format(i))
                            print(MoveToString(i, selected))

                    cont,dl = self.game_state.ExecuteMove(i, selected)

                    if not cont or self.game_state.IsGameOver():
                        break

                    num_dice = dl

                if log_state:
                    print("--------------------------------------------------")
                    print("> The game state is:")
                    for j in player_order:
                        print("> {}".format(PlayerToString(j,self.game_state)))
                    print("> {}".format(GameToString(self.game_state)))

                # Have we reached the end of the game?
                if self.game_state.IsGameOver():
                    break

            # Have we reached the end of the game?
            if self.game_state.IsGameOver():
                break

        if log_state:
            print("--------------------------------------------------")
            print("THE GAME HAS ENDED")
            print("--------------------------------------------------")

        # Score players
        return self.game_state.ScorePlayers()
