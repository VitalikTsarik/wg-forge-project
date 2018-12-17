from client import *
from json_converter import dict_to_graph, dict_to_trains, dict_to_posts, dict_to_player, dict_to_lobbies
from game_components.path_manager import PathManager


class Game:
    def __init__(self):
        self.__client = ServerConnection()
        self.__lobby = None
        self.__path_manager = PathManager()
        self.player = None
        self.__map_graph = None
        self.__trains = {}
        self.__towns = {}
        self.__markets = {}
        self.__storages = {}
        self.__paths = {}
        self.__paths_to_market = {}
        self.__paths_to_storage = {}
        self.__trains_to_market = {}
        self.__trains_to_storage = {}
        self.__stopped_trains_direction = {}

    def start_game(self):
        self.__path_manager.init_all_paths(self.__map_graph, self.player.town.point_idx,
                                           self.__markets, self.__storages)

        for train in self.__trains_to_market.values():
            self.upgrade_train_if_possible(train)
        for train in self.__trains_to_storage.values():
            self.upgrade_train_if_possible(train)
        self.upgrade_post_if_possible(self.player.town)

        self.__paths_to_market = self.__path_manager.paths_to_market(self.__map_graph, self.player.town,
                                                                     self.__markets, self.__trains_to_market)
        self.__paths_to_storage = self.__path_manager.paths_to_storage(self.__map_graph, self.player.town,
                                                                       self.__storages, self.__trains_to_storage)
        for train in self.__trains_to_market.values():
            next_vert = self.__paths_to_market[train.idx].next_vert()
            if next_vert is None:
                continue
            else:
                self.set_direction(train, next_vert)
        for train in self.__trains_to_storage.values():
            next_vert = self.__paths_to_storage[train.idx].next_vert()
            if next_vert is None:
                continue
            else:
                self.set_direction(train, next_vert)

    def next_turn(self):
        self.update_layer1()
        self.update_player()

        if self.all_trains_in_group_in_town(self.__trains_to_market):
            for train in self.__trains_to_market.values():
                self.upgrade_train_if_possible(train)
            self.__paths_to_market = self.__path_manager.paths_to_market(self.__map_graph, self.player.town,
                                                                         self.__markets, self.__trains_to_market)
        for train in self.__trains_to_market.values():
            road = self.__map_graph.get_edge_by_idx(train.line_idx)
            if train.position == 0 or train.position == road['length']:
                if self.__paths_to_market[train.idx].has_next_vert():
                    next_vert = self.__paths_to_market[train.idx].next_vert()
                    if next_vert is None:
                        continue
                    else:
                        self.set_direction(train, next_vert)

        if self.all_trains_in_group_in_town(self.__trains_to_storage):
            self.upgrade_post_if_possible(self.player.town)
            self.__paths_to_storage = self.__path_manager.paths_to_storage(self.__map_graph, self.player.town,
                                                                           self.__storages, self.__trains_to_storage)
        for train in self.__trains_to_storage.values():
            road = self.__map_graph.get_edge_by_idx(train.line_idx)
            if train.position == 0 or train.position == road['length']:
                if self.__paths_to_storage[train.idx].has_next_vert():
                    next_vert = self.__paths_to_storage[train.idx].next_vert()
                    if next_vert is None:
                        continue
                    else:
                        self.set_direction(train, next_vert)
            else:
                if self.collision_can_happened(train):
                    self.stop_train(train)
                else:
                    self.move_forward(train)

    def update_layer1(self):
        layer1 = self.__client.map_action(Layer.Layer1)
        self.__trains = dict_to_trains(layer1)
        f = True
        for train in self.__trains.values():
            if train.player_idx == self.player.idx:
                if f:
                    self.__trains_to_market[train.idx] = train
                    f = False
                else:
                    self.__trains_to_storage[train.idx] = train
                    f = True
        self.__towns, self.__markets, self.__storages = dict_to_posts(layer1)

    def update_player(self):
        self.player = dict_to_player(self.__client.player_action())

    def move_train(self, train_idx, line_idx, speed):
        self.__client.move_action(train_idx, line_idx, speed)
        self.__trains[train_idx].line_idx = line_idx
        self.__trains[train_idx].speed = speed

    def set_direction(self, train, next_vert_idx):

        if train.position == 0:
            curr_vert = self.__map_graph.get_edge_by_idx(train.line_idx)['vert_from']
        else:
            curr_vert = self.__map_graph.get_edge_by_idx(train.line_idx)['vert_to']

        new_line = self.__map_graph.get_edge_by_adj_vert(next_vert_idx, curr_vert)
        if curr_vert == new_line['vert_from']:
            train.position = 0
            self.move_train(train.idx, new_line['edge_idx'], 1)
        else:
            train.position = new_line['length']
            self.move_train(train.idx, new_line['edge_idx'], -1)

    def collision_can_happened(self, train):
        line = self.map_graph.get_edge_by_idx(train.line_idx)
        if line['vert_from'] == self.player.town.point_idx and train.position == 1 and train.speed == -1:
            return False
        if line['vert_to'] == self.player.town.point_idx and train.position == line['length'] - 1 and train.speed == 1:
            return False

        for another_train in self.__trains.values():
            if train.line_idx == another_train.line_idx and another_train.speed == 0:
                if train.idx in self.__stopped_trains_direction.keys():
                    speed = self.__stopped_trains_direction[train.idx]
                else:
                    speed = train.speed
                if speed == 1 and another_train.position == train.position + 1 or \
                        speed == -1 and another_train.position == train.position - 1:
                    return True
        return False

    def move_forward(self, train):
        if train.speed == 0:
            speed = self.__stopped_trains_direction.pop(train.idx)
            self.move_train(train.idx, train.line_idx, speed)

    def stop_train(self, train):
        if train.speed != 0:
            self.__stopped_trains_direction[train.idx] = train.speed
            self.move_train(train.idx, train.line_idx, 0)

    def move_backwards(self):
        train_idx = 1  # временно
        train = self.trains[train_idx]
        self.move_train(train.idx, train.line_idx, -1)

    def next_turn_action(self):
        self.__client.turn_action()

    def upgrade_train_if_possible(self, train):
        if train.level == 1 and self.player.town.armor >= 40:
            self.__client.upgrade_action([], [train.idx])
            self.player.town.armor -= 40
            train.level = 2
        if train.level == 2 and self.player.town.armor >= 80:
            self.__client.upgrade_action([], [train.idx])
            self.player.town.armor -= 80
            train.level = 3

    def upgrade_post_if_possible(self, post):
        if post.level == 1 and self.player.town.armor >= 100:
            self.__client.upgrade_action([post.idx], [])
            self.player.town.armor -= 100
            post.level = 2
        if post.level == 2 and self.player.town.armor >= 200:
            self.__client.upgrade_action([post.idx], [])
            self.player.town.armor -= 200
            post.level = 3

    def all_trains_in_group_in_town(self, group):
        lines = self.__map_graph.get_adj_edges(self.player.town.point_idx)

        for train in group.values():
            town_line = None
            for line in lines:
                if train.line_idx == line['edge_idx']:
                    town_line = line
                    break
            if town_line is None:
                return False
            if town_line['start_vert'] == self.player.town.point_idx:
                if train.position != 0:
                    return False
            else:
                if train.position != town_line['length']:
                    return False
        return True

    def new_game(self, player_name, lobby):
        if self.player is not None:
            self.__client.logout_action()
            self.__client = ServerConnection()
        self.__lobby = lobby
        self.player = dict_to_player(self.__client.login_action(player_name, lobby.name, lobby.num_players, lobby.num_turns))
        self.__map_graph = dict_to_graph(self.__client.map_action(Layer.Layer0))
        self.update_layer1()
        self.update_player()

    def connect_to_game(self, player_name, lobby):
        if self.player is not None:
            self.__client.logout_action()
            self.__client = ServerConnection()
        self.__lobby = lobby
        self.player = dict_to_player(self.__client.connect_to_game(player_name, lobby.name))
        self.__map_graph = dict_to_graph(self.__client.map_action(Layer.Layer0))
        self.update_layer1()
        self.update_player()

    def get_existing_games(self):
        return dict_to_lobbies(self.__client.games_action())

    @property
    def map_graph(self):
        return self.__map_graph

    @property
    def trains(self):
        return self.__trains

    @property
    def towns(self):
        return self.__towns

    @property
    def markets(self):
        return self.__markets

    @property
    def storages(self):
        return self.__storages

    @property
    def lobby(self):
        return self.__lobby

    @lobby.setter
    def lobby(self, value):
        self.__lobby = value
