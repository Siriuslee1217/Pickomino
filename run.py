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
from model import GameRunner,Player
from iplayer import InteractivePlayer


players = [InteractivePlayer(0), Player(1), InteractivePlayer(2)]

# Player id's must be unique and increasing from 0 
i = 0
for plr in players:
    assert(plr.id == i)
    i += 1

gr = GameRunner(players, 457846578367)

scores = gr.Run(True)

print("Player 0 score is {}".format(scores[0]))
print("Player 1 score is {}".format(scores[1]))
print("Player 2 score is {}".format(scores[2]))
