import unittest
from typing import Dict, Union, List

from lummao import BaseLSLScript, typecast, Key, Vector

from pythonized.data_manager import Script as DataManagerScript

# Alexandria Linden
TEST_OWNER = Key("ba2a564a-f0f1-4b82-9c61-b7520bfcd09f")
NULL_KEY = Key("00000000-0000-0000-0000-000000000000")

IPC_INIT_SAVE_INWORLD_STATE = 800
IPC_FINISH_SAVE_INWORLD_STATE = 801
IPC_SAVE_NODE = 802
IPC_SAVE_RELATION = 803

IPC_REQUEST_RESTORE_FROM_DATA = 900
IPC_FINISH_RESTORE_FROM_DATA = 901
IPC_RESTORE_NODE = 902
IPC_RESTORE_RELATION = 903

IPC_REQUEST_PATH = 1000
IPC_REQUEST_PATH_VECTORS = 1001

IPC_REQUEST_PATH_FROM_VECTORS = 1002
IPC_PATH_RESPONSE = 1003


def stub_functions(builtin_funcs: dict):
    builtin_funcs['llOwnerSay'] = lambda: None
    builtin_funcs['llGetOwner'] = lambda: TEST_OWNER
    builtin_funcs['llGetOwnerKey'] = lambda x: TEST_OWNER
    builtin_funcs['llSetColor'] = lambda *args: None


class ScriptMockMixin(BaseLSLScript):
    def __init__(self):
        super().__init__()
        stub_functions(self.builtin_funcs)
        self.description: str = ""
        self._listen_num = 0
        # channel -> handle
        self.listens: Dict[int, int] = dict()
        self.builtin_funcs['llGetObjectDesc'] = lambda: self.description
        self.builtin_funcs['llSetObjectDesc'] = self._set_description
        self.builtin_funcs['llListen'] = self._register_listen

    def _set_description(self, desc: str):
        self.description = desc

    def _register_listen(self, channel: int, name: str, who: Key, msg: str):
        self._listen_num += 1
        self.listens[self._listen_num] = channel
        return self._listen_num


class MockedDataManagerScript(DataManagerScript, ScriptMockMixin):
    def __init__(self):
        super().__init__()

    def add_node(self, node_id: str, node_pos: Vector):
        self.queue_event("link_message", (0, IPC_SAVE_NODE, node_id, typecast(typecast(node_pos, str), Key)))
        self.execute()

    def add_relation(self, node_src: str, node_dst: str):
        self.queue_event("link_message", (0, IPC_SAVE_RELATION, node_src, typecast(node_dst, Key)))
        self.execute()

    def request_path(self, node_src: Union[str, Vector], node_dst: Union[str, Vector]) -> List[int]:
        if isinstance(node_src, Vector):
            node_src = typecast(node_src, str)
        if isinstance(node_dst, Vector):
            node_dst = typecast(node_dst, str)
        src_idx = self.nodeRefToIdx(node_src, NULL_KEY)
        dst_idx = self.nodeRefToIdx(node_dst, NULL_KEY)
        return self.dijkstraFindPath(src_idx, dst_idx)


class PathfindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data_manager = MockedDataManagerScript()
        self.data_manager.execute()

        self.data_manager.add_node("1", Vector((1.0, 2.0, 3.0)))
        self.data_manager.add_node("2", Vector((1.0, 6.0, 3.0)))
        self.data_manager.add_node("3", Vector((1.0, 8.0, 3.0)))
        self.data_manager.add_node("-1", Vector((3.0, -1.0, 3.0)))
        self.data_manager.add_node("island", Vector((9.0, 9.0, 9.0)))

        self.data_manager.add_relation("1", "2")
        self.data_manager.add_relation("2", "1")
        # Unidirectional
        self.data_manager.add_relation("2", "3")

        # The only back to 1 from three is to go all the way back to -1
        self.data_manager.add_relation("1", "-1")
        self.data_manager.add_relation("-1", "1")
        self.data_manager.add_relation("-1", "3")
        self.data_manager.add_relation("3", "-1")

        self.data_manager.calculateEdgeWeights()

    def _get_path_ids(self, src: Union[Vector, str], dst: Union[Vector, str]):
        return self.data_manager.pathToIDs(self.data_manager.request_path(src, dst))

    def test_simple_path(self):
        # Straight line
        self.assertListEqual(["1", "2", "3"], self._get_path_ids("1", "3"))

    def test_unidirectional_path(self):
        # Have to take a less optimal path because 2->3 relation is unidirectional
        self.assertListEqual(["3", "-1", "1"], self._get_path_ids("3", "1"))

    def test_island_path(self):
        # No connection == no valid path
        self.assertListEqual([], self._get_path_ids("3", "island"))

    def test_closest_node_path(self):
        # 1 and 3 are closest to src and dst coords, respectively.
        self.assertListEqual(['1', '2', '3'], self._get_path_ids(Vector((1, 2, 3)), Vector((1, 8, 3))))

    def test_path_as_vectors(self):
        path_vecs = self.data_manager.pathToVectors(self.data_manager.request_path("1", "3"))
        self.assertListEqual(
            [
                Vector((1.0, 2.0, 3.0)),
                Vector((1.0, 6.0, 3.0)),
                Vector((1.0, 8.0, 3.0)),
            ],
            path_vecs,
        )


if __name__ == "__main__":
    unittest.main()
