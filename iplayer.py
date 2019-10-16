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
from model import *
from utils import *

class InteractivePlayer(Player):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectMove(self, roll, moves, game_state):
        plr_state = game_state.players[self.id]

        print("\nMy dice bank: {}".format(RollToString(plr_state.dice_bank,
            game_state.WORM)))
        print("My current total is {}\n".format(plr_state.current_total))
        
        # Player can take one set of dice with the same face.
        filtered_roll = [d for d in roll if not (d in plr_state.dice_bank)]
        dice_nums = [0 for d in game_state.DICE]

        d_types = set(filtered_roll)
        for d in filtered_roll:
            dice_nums[d-1] += 1

        move = None
        while True:
            print("> Select Option ('back' returns to this menu): ")
            print("(1) See available moves")
            print("(2) Bank dice")

            option = input()

            if option == "back":
                continue

            if not option.isdigit():
                print("> Option not recognised. Repeating request.")
                continue

            ioption = int(option)

            cont = False
            if ioption == 1:
                # Print Moves 
                for mo in moves:
                    print(MoveToString(self.id, mo))
                    print("\n")
                continue

            elif ioption == 2:
                options = ""
                for d in d_types:
                    if d == game_state.WORM:
                        options += " worm"
                    else:
                        options += " {}".format(d)
                
                cont = False
                while True:
                    cont = False
                    print("> Select dice to bank: {}".format(options))
                    d_type = input()

                    if d_type == "back":
                        cont = True
                        break

                    dbank = DiceBank()
                    if d_type == "worm":
                        if not game_state.WORM in d_types:
                            print("> Invalid input. Repeating request")
                            continue
                        dbank.dice_value = game_state.WORM
                        dbank.is_worm = True
                    elif not d_type.isdigit():
                        print("> Invalid input. Repeating request")
                        continue
                    else:
                        id_type = int(d_type)
                        if not id_type in d_types:
                            print("> Invalid input. Repeating request")
                            continue
                        dbank.dice_value = id_type

                    dindex = dbank.dice_value - 1
                    dbank.number = dice_nums[dindex]
                    
                    next_total = dbank.number*game_state.DICE_VAL[dindex] + \
                        plr_state.current_total

                    # is there a tile grab available?
                    tgrab = None
                    if next_total >= game_state.MIN_TILE and \
                        ((game_state.WORM in plr_state.dice_bank) or \
                        (dbank.dice_value == game_state.WORM)):

                        # is their total equal to a players top tile?
                        for oplyr in game_state.players:
                            if oplyr.id != plr_state.id:
                                tt = oplyr.TopTile()
                                if tt != -1 and \
                                    game_state.TILES[tt] == next_total:
                                    tgrab = TileGrab()
                                    tgrab.tile_id = tt
                                    tgrab.tile_value = game_state.TILES[tt]
                                    tgrab.from_player = oplyr.id

                                    # There is only one instance of each
                                    # tile in the game.
                                    break

                        if tgrab == None:
                            # can the player grab a tile from the line
                            for k in range(len(game_state.tile_line)-1,-1,-1):
                                tid = game_state.tile_line[k]
                                if game_state.TILES[tid] <= next_total:
                                    # player could take this tile
                                    tgrab = TileGrab()
                                    tgrab.tile_id = tid
                                    tgrab.tile_value = game_state.TILES[tid]
                                    tgrab.from_tile_line = True
                                    break
                            
                    dice_left = plr_state.dice_left - dice_nums[dindex]
                    assert(dice_left > 0 or tgrab != None)

                    if tgrab == None:
                        move = (Move.ROLL, dbank, None)
                        break
                    
                    if dice_left == 0:
                        move = (Move.STOP, dbank, tgrab)
                        break

                    if dice_left > 0: 
                        while True:
                            print("> Roll again? y/n")

                            ans = input()
                            ans = ans.strip()

                            if ans == "back":
                                cont = True
                                break
                           
                            if ans == "y" or ans == "Y":
                                move = (Move.ROLL, dbank, None)
                                break
                            elif ans == "n" or ans == "N":
                                move = (Move.STOP, dbank, tgrab)
                                break
                            else:
                                print("> Invalid option. Repeating request")
                                continue

                    break
                    
                if cont:
                    continue
    
            else:
                cont = True
                print("Option not recognised. Repeating request.")

            if not cont:
                break

        # Does the move exist in the available set of moves?
        found = False
        assert(move != None)

        for m in moves:
            if m[0]==move[0] and SameDB(m[1],move[1]) and SameTG(m[2],move[2]):
                found = True
                break

        assert found

        return move
