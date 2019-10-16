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
from enum import IntEnum


# There are 2 types of moves a player can perform in the game
class Move(IntEnum):
    ROLL = 1
    STOP = 2
    BUST = 3

class DiceBank:
    def __init__(self):
        self.dice_value = -1
        self.number = -1
        self.is_worm = False

    def Print(self):
        if self.is_worm:
            print("{} dice with value worm".format(self.number))
        else:
            print("{} dice with value {}".format(self.number,
                self.dice_value))

class TileGrab:
    def __init__(self):
        self.tile_id = 0
        self.tile_value = 0
        self.from_player = -1
        self.from_tile_line = False

def SameDB(db1, db2):
    if db1 == None and db2 == None:
        return True

    if db1 == None:
        return False

    if db2 == None:
        return False

    return (db1.dice_value == db2.dice_value) and \
        (db1.number == db2.number) and (db1.is_worm == db2.is_worm)

def SameTG(tg1, tg2):
    if tg1 == None and tg2 == None:
        return True

    if tg1 == None:
        return False

    if tg2 == None:
        return False

    return (tg1.tile_id == tg2.tile_id) and \
        (tg1.tile_value == tg2.tile_value) and \
        (tg1.from_player == tg2.from_player) and \
        (tg1.from_tile_line == tg2.from_tile_line) 


def MoveToString(player_id, move):
    desc = ""
    if move[0] == Move.ROLL:
        dbank = move[1]
        if dbank.is_worm:
            desc += "Banked {} worms, opted to roll again".format(
                dbank.number)
        elif dbank.number > 1:
            desc += "Banked {} {}s, opted to roll again".format(
                dbank.number, dbank.dice_value)
        else: 
            desc += "Banked a {}, opted to roll again".format(
                dbank.dice_value)
    elif move[0] == Move.BUST:
        desc = "Bust!"
    else:
        dbank = move[1]
        if dbank.is_worm:
            desc += "Banked {} worms".format(dbank.number)
        elif dbank.number > 1:
            desc += "Banked {} {}s".format(dbank.number, dbank.dice_value)
        else: 
            desc += "Banked a {}".format(dbank.dice_value)

        tgrab = move[2]
        if tgrab.from_player != -1:
            desc += ", took {} from player {}".format(tgrab.tile_value,
                tgrab.from_player)
        else:
            desc += ", took {} from tile line".format(tgrab.tile_value)
            
    return desc   

def PlayerToString(player_id, game_state):
    ps = game_state.players[player_id]
    desc = "Player {} state: \n".format(player_id)
    if ps.current_total > 0:
        desc += "    Total of {} in bank with dice: ".format(ps.current_total)
        for d in ps.dice_bank:
            if d == game_state.WORM:
                desc += " worm" 
            else:
                desc += " {}".format(d)
        desc += "\n"
    desc += "    Stack: "
    for tid in ps.stack:
        desc += "{} ".format(game_state.TILES[tid])
    return desc

def GameToString(game_state):
    tl = ""
    for tid in game_state.tile_line:
        tl += " {}".format(game_state.TILES[tid])
    
    desc = "Tile line {}".format(tl)
    return desc


def RollToString(roll, WORM):
    desc = ""
    for d in roll:
        if d == WORM:
            desc += " worm"
        else:
            desc += " {}".format(d)
    return desc
