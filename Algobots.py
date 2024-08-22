import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.flag = 0
        self.alternate = 0
        self.increase = 0
        self.previous_health = 30
        self.did_attack = 0
        self.failed_attacks = 0

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(
            game_state.turn_number))
        # Comment or remove this line to enable warnings.
        game_state.suppress_warnings(True)

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        # First, place basic defenses
        """if game_state.my_health <= 10:
            if self.flag == 1:
                support_locations = [[23, 12], [22, 11], [21, 10], [20, 9], [19, 8], [18, 7], [
                    9, 13], [10, 3], [11, 3], [12, 3], [13, 3], [14, 3], [11, 2], [12, 2], [13, 2]]
                game_state.attempt_spawn(
                    TURRET, [[15,11], [23, 13], [24, 13], [25, 13]])
                game_state.attempt_spawn(SUPPORT, support_locations)
                game_state.attempt_upgrade(support_locations)
                self.attack_with_scout1(game_state)
                self.flag = -1
        else:"""

        if self.did_attack == 1:
            if game_state.enemy_health >= self.previous_health:
                self.failed_attacks += 1
                if game_state.my_health <= 10:
                    self.increase += 2
                else:
                    self.increase += 1
            self.did_attack = 0

        temp = 0
        for coord in self.scored_on_locations:
            if (coord[0]+coord[1]) <= 13:
                if temp == 1:
                    self.alternate = 1
                else:
                    temp = -1
            else:
                if temp == -1:
                    self.alternate = 1
                else:
                    temp = 1

        if game_state.turn_number <= 9:
            if game_state.turn_number % 5 == 4:
                self.attack_with_scout(game_state)
                self.did_attack = 1
                self.previous_health = game_state.enemy_health
        else:
            if game_state.turn_number % 4 == 3:
                self.attack_with_scout1(game_state)
                self.did_attack = 1
                self.previous_health = game_state.enemy_health

        self.build_defences(game_state)

    def build_defences(self, game_state):

        for x in range(1, 27):
            for y in range(1, 27):
                if not game_state.contains_stationary_unit([x, y]) == False:
                    if game_state.contains_stationary_unit([x, y]).health < game_state.contains_stationary_unit([x, y]).max_health * 0.4:
                        game_state.attempt_remove([x, y])

        inital_turret_locations = [[4, 11], [2, 13], [2, 11], [4, 13], [5, 12], [5, 10], [6, 12], [7, 12], [8, 12],  [10, 12], [11, 12], [12, 12], [13, 12], [27, 13], [26, 13], [25, 13], [26, 12], [25, 12], [25, 11], [24, 10], [23, 13], [22, 12], [
            23, 12], [23, 11], [22, 10], [21, 12], [20, 12], [19, 12], [18, 13], [17, 12], [16, 12], [15, 12], [14, 12], [6, 9], [21, 9], [3, 13], [24, 13]]
        left_locations = [[0, 13], [1, 13], [2, 13], [1, 12], [2, 12], [2, 11], [3, 10], [4, 13], [5, 12], [
            4, 11], [5, 10], [6, 12], [7, 12], [8, 12], [9, 13], [10, 12], [11, 12], [12, 12], [13, 12]]
        right_locations = [[27, 13], [26, 13], [25, 13], [26, 12], [25, 12], [25, 11], [24, 10], [23, 13], [22, 12], [
            23, 12], [23, 11], [22, 10], [21, 12], [20, 12], [19, 12], [18, 13], [17, 12], [16, 12], [15, 12], [14, 12]]
        # additional_turret_locations = [[14, 7], [16, 12], [
        #    13, 6]]
        support_locations1 = [[13, 10], [14, 10]]
        support_locations2 = [[13, 11], [14, 11]]
        support_locations3 = [[12, 10], [15, 10]]
        support_locations4 = [[12, 11], [15, 11]]

        """if game_state.my_health <= 10:
            if len(self.scored_on_locations) > 0 and (self.scored_on_locations[0][0] + self.scored_on_locations[0][1] <= 13):
                game_state.attempt_spawn(
                    TURRET, [[0, 13], [1, 13], [2, 13], [3, 13], [1, 12]])
                game_state.attempt_upgrade([[2, 13]])
            if self.flag == 0:
                game_state.attempt_remove([[16, 12], [7, 9], [9, 9], [11, 9], [13, 9], [
                    15, 9], [24, 10], [23, 9], [22, 8], [21, 7], [20, 6], [6, 12], [5, 11], [4, 11], [3, 10], [4, 11], [3, 12]])
                game_state.attempt_remove(
                    [[26, 12], [15, 4], [16, 3]])
                game_state.attempt_spawn(SUPPORT, support_locations)
                game_state.attempt_upgrade(support_locations)
                self.flag = 1
            elif self.flag == -1:
                self.flag = 0

        else:"""

        """if len(self.scored_on_locations) > 0 and (self.scored_on_locations[len(self.scored_on_locations) - 1][0] + self.scored_on_locations[len(self.scored_on_locations) - 1][1] > 13) and self.alternate == 0:
            if self.failed_attacks >= 2:
                game_state.attempt_remove([9, 13])
            else:
                game_state.attempt_spawn(TURRET, [[9, 13]])

            game_state.attempt_remove([[4, 11]])
            game_state.attempt_spawn(TURRET, right_locations)
        elif len(self.scored_on_locations) > 0 and (self.scored_on_locations[len(self.scored_on_locations) - 1][0] + self.scored_on_locations[len(self.scored_on_locations) - 1][1] <= 13) and self.alternate == 0:
            if self.failed_attacks >= 2:
                game_state.attempt_remove([9, 13])
            else:
                game_state.attempt_spawn(TURRET, [[9, 13]])

            game_state.attempt_remove(
                [[23, 11]])
            game_state.attempt_spawn(TURRET, left_locations)
        else:"""

        if self.failed_attacks >= 3:
            game_state.attempt_remove([9, 13])
        else:
            game_state.attempt_spawn(TURRET, [[9, 13]])

        game_state.attempt_spawn(TURRET, inital_turret_locations)

        if game_state.turn_number <= 12:
            if game_state.turn_number % 5 == 0 or game_state.turn_number % 5 == 1 or game_state.turn_number % 5 == 2 or game_state.turn_number % 5 == 3:
                game_state.attempt_spawn(
                    TURRET, [[3, 10], [2, 12], [1, 12], [0, 13], [1, 13]])
            if game_state.turn_number % 5 == 3:
                game_state.attempt_remove(
                    [[3, 10], [2, 12], [1, 12], [0, 13], [1, 13]])
        else:
            if game_state.turn_number % 4 == 0 or game_state.turn_number % 4 == 1 or game_state.turn_number % 4 == 2:
                game_state.attempt_spawn(
                    TURRET, [[3, 10], [2, 12], [1, 12], [0, 13], [1, 13]])
            if game_state.turn_number % 4 == 2:
                game_state.attempt_remove(
                    [[3, 10], [2, 12], [1, 12], [0, 13], [1, 13]])

        if len(self.scored_on_locations) > 0 and (self.scored_on_locations[0][0] + self.scored_on_locations[0][1] <= 13) and self.alternate == 0:
            for x in [[2, 13], [3, 13], [2, 12]]:
                if not game_state.contains_stationary_unit(x) == False:
                    if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                        game_state.attempt_upgrade(x)
        elif len(self.scored_on_locations) > 0 and (self.scored_on_locations[0][0] + self.scored_on_locations[0][1] > 13) and self.alternate == 0:
            for x in [[25, 13], [24, 13], [26, 12]]:
                if not game_state.contains_stationary_unit(x) == False:
                    if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                        game_state.attempt_upgrade(x)
        else:
            for x in [[2, 13], [25, 13], [3, 13], [24, 13]]:
                if not game_state.contains_stationary_unit(x) == False:
                    if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                        game_state.attempt_upgrade(x)

        game_state.attempt_spawn(SUPPORT, support_locations1)
        for x in support_locations1:
            if not game_state.contains_stationary_unit(x) == False:
                if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                    game_state.attempt_upgrade(x)
        game_state.attempt_spawn(SUPPORT, support_locations2)
        for x in support_locations2:
            if not game_state.contains_stationary_unit(x) == False:
                if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                    game_state.attempt_upgrade(x)
        game_state.attempt_spawn(SUPPORT, support_locations3)
        for x in support_locations3:
            if not game_state.contains_stationary_unit(x) == False:
                if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                    game_state.attempt_upgrade(x)
        game_state.attempt_spawn(SUPPORT, support_locations4)
        for x in support_locations4:
            if not game_state.contains_stationary_unit(x) == False:
                if game_state.contains_stationary_unit(x).health > game_state.contains_stationary_unit(x).max_health * 0.5:
                    game_state.attempt_upgrade(x)

    def attack_with_scout(self, game_state):
        game_state.attempt_spawn(SCOUT, [22, 8], max(
            min(7, 5+self.increase), int(game_state.get_resource(MP, 0))-int(game_state.enemy_health)-2))
        game_state.attempt_spawn(SCOUT, [23, 9], 100)

    def attack_with_scout1(self, game_state):
        game_state.attempt_spawn(SCOUT, [22, 8], max(
            min(7, 5+self.increase), int(game_state.get_resource(MP, 0))-int(game_state.enemy_health)-2))
        game_state.attempt_spawn(SCOUT, [23, 9], 100)

    def attack_with_scout2(self, game_state):
        game_state.attempt_spawn(SCOUT, [4, 9], min(5, (self.MP)/2))
        game_state.attempt_spawn(SCOUT, [3, 10], 100)

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write(
                    "All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
