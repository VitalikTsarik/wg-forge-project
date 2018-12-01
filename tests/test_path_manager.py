import unittest
from source.json_converter import dict_to_graph, read_graph_from_json
from source.game_components.path_manager import PathManager


class TestPathManager(unittest.TestCase):
    def setUp(self):
        self.__small_graph = dict_to_graph(read_graph_from_json('../test_graphs/small_graph.json'))
        self.__big_graph = dict_to_graph(read_graph_from_json('../test_graphs/my_graph.json'))
        self.__task3_graph = dict_to_graph(read_graph_from_json('../test_graphs/task3.json'))

    def test_Dijsktra(self):
        temp_path1 = PathManager(self.__small_graph, 4)
        self.assertEqual(temp_path1.paths, {4: 0, 3: 1, 10: 1, 9: 2, 11: 2, 5: 3, 8: 4, 2: 3, 12: 5, 7: 5, 1: 5, 6: 4})

        temp_path2 = PathManager(self.__big_graph, 2)
        self.assertEqual(temp_path2.paths, {2: 0, 9: 1, 3: 1, 7: 1, 4: 2, 5: 3, 6: 3})

        temp_path3 = PathManager(self.__task3_graph, 13)
        self.assertEqual(temp_path3.paths, {13: 0, 19: 1, 14: 2, 20: 2, 24: 2, 18:3, 15: 4, 21: 4, 17: 4, 16: 5, 23: 5, 22: 6})
