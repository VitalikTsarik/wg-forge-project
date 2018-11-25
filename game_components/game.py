from client import *
from json_converter import dict_to_graph, dict_to_trains, dict_to_posts


class Game:
    def __init__(self, window):
        self.__main_window = window
        self.__client = ServerConnection()
        self.__client.login_action('NeBoris')
        self.__map_graph = dict_to_graph(self.__client.map_action(Layer.Layer0)[1])
        layer1 = self.__client.map_action(Layer.Layer1)[1]
        self.__trains = dict_to_trains(layer1)
        self.__init_trains_start_idx_()
        self.__posts = dict_to_posts(layer1)

    def __init_trains_start_idx_(self):
        for train in self.__trains.values():
            train.start_vert = self.__map_graph.get_edge_by_idx(train.line_idx)['vert_from']

    def next_turn(self):
        for train in self.__trains.values():
            train.position += train.speed
            road = self.__map_graph.get_edge_by_idx(train.line_idx)

            if train.position == 0:
                train.speed = 0
                if train.start_vert == road['vert_from']:
                    self.__choose_direction(road['vert_from'])
                else:
                    self.__choose_direction(road['vert_to'])
            elif train.position == road['length']:
                train.speed = 0
                if train.start_vert == road['vert_from']:
                    self.__choose_direction(road['vert_to'])
                else:
                    self.__choose_direction(road['vert_from'])

    def move_train(self, train_idx, line_idx, speed):
        res, msg = self.__client.move_action(train_idx, line_idx, speed)
        if res == Result.OKEY.value:
            self.__trains[train_idx].line_idx = line_idx
            self.__trains[train_idx].speed = speed

    def __choose_direction(self, vert_idx):
        self.__main_window.centralWidget().create_dir_btns(self.__map_graph.get_adj_vertices(vert_idx))
        self.__main_window.centralWidget().add_dir_btns()

    def set_direction(self):
        # получение line_idx
        # вызов move_train
        self.__main_window.centralWidget().del_dir_btns()

    @property
    def map_graph(self):
        return self.__map_graph

    @property
    def trains(self):
        return self.__trains

    @property
    def posts(self):
        return self.__posts
