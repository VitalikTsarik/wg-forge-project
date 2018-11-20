from client import *
from json_converter import dict_to_graph, dict_to_trains


class Game:
    def __init__(self, window):
        self.__main_window = window
        self.__client = ServerConnection()
        self.__client.login_action('NeBoris')
        self.__map_graph = dict_to_graph(self.__client.map_action(Layer.Layer0)[1])
        layer1 = self.__client.map_action(Layer.Layer1)[1]
        self.__trains = self.__trains = dict_to_trains(layer1)
        self.__posts = []

    @property
    def map_graph(self):
        return self.__map_graph

    @property
    def trains(self):
        return self.__trains

    @property
    def posts(self):
        return self.__posts
