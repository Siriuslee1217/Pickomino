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

class NaivePlayer(Player):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectMove(self, roll, moves, game_state):
        # Prefer to stop and collect a tile whenever possible.
        # Bank worms in preference to all other dice.
        # Bank higher numbered dice in preference to lower numbered dice. 
        if len(moves) == 1:
            return moves[0]

        bm_type,bm_dbank,bm_tgrab = moves[0]

        for i in range(1, len(moves)):
            mtype,dbank,tgrab = moves[i]
            if (tgrab != None and bm_tgrab == None) or \
                (tgrab != None and bm_tgrab != None and \
                    tgrab.tile_id > bm_tgrab.tile_id) or \
                (tgrab == None and bm_tgrab == None and \
                    dbank.dice_value > bm_dbank.dice_value):
                bm_type,bm_dbank,bm_tgrab = mtype,dbank,tgrab
       
        return (bm_type,bm_dbank,bm_tgrab)
