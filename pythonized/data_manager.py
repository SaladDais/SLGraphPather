from lummao import *


class Script(BaseLSLScript):
    gWeightedEdges: list
    gNodes: list
    gNodeRelations: list

    def __init__(self):
        super().__init__()
        self.gWeightedEdges = []
        self.gNodes = []
        self.gNodeRelations = []

    def calculateEdgeWeights(self) -> None:
        self.gWeightedEdges = []
        _i: int = 0
        _len: int = rneq([], self.gNodeRelations)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
            _src: str = self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel))
            _dst: str = self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel))
            _src_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(_src, list))
            _dst_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(_dst, list))
            _dist: float = self.builtin_funcs.llVecDist(self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(_src_idx))), self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(_dst_idx))))
            self.gWeightedEdges = radd(_dist, radd(rdiv(2, _dst_idx), radd("", radd(rdiv(2, _src_idx), self.gWeightedEdges))))
            _i += 1
        self.gWeightedEdges = self.builtin_funcs.llListSort(self.gWeightedEdges, 4, 1)

    @with_goto
    def dijkstraFindPath(self, _src_idx: int, _dst_idx: int) -> list:
        if cond(req(_dst_idx, _src_idx)):
            if True == True:
                return typecast(_src_idx, list)
        _src: int = rdiv(2, _src_idx)
        _dst: int = rdiv(2, _dst_idx)
        _dist: list = []
        _prev: list = []
        _consumed: list = []
        _V: int = rdiv(2, (rneq([], self.gNodes)))
        _edges_len: int = rneq([], self.gWeightedEdges)
        _i: int = 0
        _i = 0
        while True == True:
            if not cond(rless(_V, _i)):
                break
            _dist = radd((10000000.0), _dist)
            _prev = radd((typecast(-1, int)), _prev)
            _consumed = radd(0, _consumed)
            _i += 1
        _dist = self.builtin_funcs.llListReplaceList(_dist, typecast(0.0, list), _src, _src)
        _u: int = 0
        while cond(1):
            _min_dist: float = (10000000.0)
            _v: int = 0
            _v = 0
            while True == True:
                if not cond(rless(_V, _v)):
                    break
                _cur_dist: float = self.builtin_funcs.llList2Float(_dist, _v)
                if cond(boolnot((rless(_cur_dist, _min_dist)))):
                    if cond(boolnot(self.builtin_funcs.llList2Integer(_consumed, _v))):
                        _min_dist = _cur_dist
                        _u = _v
                _v += 1
            if cond(req((10000000.0), _min_dist)):
                if True == True:
                    return []
            if cond(req(_dst, _u)):
                _path: list = []
                while cond(bitnot(_u)):
                    _path = radd(_path, radd(_u, _u))
                    _u = self.builtin_funcs.llList2Integer(_prev, _u)
                if True == True:
                    return _path
            _consumed = self.builtin_funcs.llListReplaceList(_consumed, typecast(1, list), _u, _u)
            _adj_start: int = self.builtin_funcs.llListFindList(self.gWeightedEdges, radd("", typecast(_u, list)))
            _i = _adj_start
            while True == True:
                if not cond(rless(_edges_len, _i)):
                    break
                if cond(rbitxor(_u, self.builtin_funcs.llList2Integer(self.gWeightedEdges, _i))):
                    goto ._next
                _v: int = self.builtin_funcs.llList2Integer(self.gWeightedEdges, neg(bitnot(neg(bitnot(_i)))))
                if cond(boolnot(self.builtin_funcs.llList2Integer(_consumed, _v))):
                    _u_dist: float = self.builtin_funcs.llList2Float(_dist, _u)
                    _edge_dist: float = self.builtin_funcs.llList2Float(self.gWeightedEdges, radd(_i, 3))
                    _alt: float = radd(_edge_dist, _u_dist)
                    if cond(rless(self.builtin_funcs.llList2Float(_dist, _v), _alt)):
                        _dist = self.builtin_funcs.llListReplaceList(_dist, typecast(_alt, list), _v, _v)
                        _prev = self.builtin_funcs.llListReplaceList(_prev, typecast(_u, list), _v, _v)
                _i = radd(_i, 4)
            label ._next
        if True == True:
            return []

    def pathToIDs(self, _path: list) -> list:
        _path_new: list = []
        _i: int = 0
        _len: int = rneq([], _path)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _path_new = radd(self.builtin_funcs.llList2String(self.gNodes, self.builtin_funcs.llList2Integer(_path, _i)), _path_new)
            _i += 1
        _path = []
        return _path_new

    def pathToVectors(self, _path: list) -> list:
        _path_new: list = []
        _i: int = 0
        _len: int = rneq([], _path)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _path_new = radd(self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(self.builtin_funcs.llList2Integer(_path, _i)))), _path_new)
            _i += 1
        _path = []
        return _path_new

    @with_goto
    def findClosestAccessibleNode(self, _pos: Vector, _caster_key: Key) -> int:
        _i: int = 0
        _len: int = 0
        _points: Optional[list] = None
        _diff: Vector = Vector((0.0, 0.0, 0.0))
        _point: int = 0
        _node_idx: int = 0
        _node_pos: Vector = Vector((0.0, 0.0, 0.0))
        _cast_data: Optional[list] = None
        _j: int = 0
        _num_hits: int = 0
        _i = 0
        _len = rneq([], self.gNodes)
        _points = []
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _diff = rsub(_pos, self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(_i))))
            _diff = replace_coord_axis(_diff, 2, rmul((2.0), _diff[2]))
            _points = radd((rbitor(_i, rmul(65536, typecast(self.builtin_funcs.llVecDist(Vector(((0.0), (0.0), (0.0))), _diff), int)))), _points)
            _i = neg(bitnot(neg(bitnot(_i))))
        _points = self.builtin_funcs.llListSort(_points, 1, 1)
        if cond(req("00000000-0000-0000-0000-000000000000", _caster_key)):
            if True == True:
                return rbitand(65535, self.builtin_funcs.llList2Integer(_points, 0))
        _len = rneq([], _points)
        _i = 0
        while True == True:
            if not cond(rbitand(rless(5, _i), rless(_len, _i))):
                break
            _point = self.builtin_funcs.llList2Integer(_points, _i)
            _node_idx = rbitand(65535, _point)
            if cond(rless(2, rshr(16, _point))):
                if True == True:
                    return _node_idx
            _node_pos = self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(_node_idx)))
            _cast_data = self.builtin_funcs.llCastRay(radd(Vector(((0.0), (0.0), bin2float('0.500000', '0000003f'))), _pos), radd(Vector(((0.0), (0.0), bin2float('0.500000', '0000003f'))), _node_pos), radd(2, radd(2, radd(11, radd(0, radd(2, typecast(3, list)))))))
            _j = 0
            _num_hits = self.builtin_funcs.llList2Integer(_cast_data, (typecast(-1, int)))
            if cond(rless(_num_hits, (typecast(-1, int)))):
                _j = 0
                while True == True:
                    if not cond(rless(_num_hits, _j)):
                        break
                    if cond(boolnot((req(_caster_key, self.builtin_funcs.llList2Key(_cast_data, radd(_j, _j)))))):
                        goto ._next
                    _j += 1
                if True == True:
                    return _node_idx
            label ._next
            _i += 1
        if True == True:
            return rbitand(65535, self.builtin_funcs.llList2Integer(_points, 0))

    def nodeRefToIdx(self, _node_ref: str, _caster_key: Key) -> int:
        if cond(req(Vector(((0.0), (0.0), (0.0))), typecast(_node_ref, Vector))):
            return self.builtin_funcs.llListFindList(self.gNodes, typecast(_node_ref, list))
        else:
            return self.findClosestAccessibleNode(typecast(_node_ref, Vector), _caster_key)

    def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(rbitxor(800, _num)):
            if cond(rbitxor(801, _num)):
                if cond(rbitxor(802, _num)):
                    if cond(rbitxor(803, _num)):
                        if cond(rbitxor(900, _num)):
                            if cond(rbitor(req(1002, _num), rbitor(req(1001, _num), req(1000, _num)))):
                                _path: list = []
                                _params: list = self.builtin_funcs.llParseString2List(_str, typecast(":", list), [])
                                _src_idx: int = self.nodeRefToIdx(self.builtin_funcs.llList2String(_params, 0), _id)
                                _dst_idx: int = self.nodeRefToIdx(self.builtin_funcs.llList2String(_params, 1), typecast("00000000-0000-0000-0000-000000000000", Key))
                                _src_pos: Vector = typecast(self.builtin_funcs.llList2String(_params, 0), Vector)
                                if cond(boolnot((rbitor(req([], self.gWeightedEdges), rbitor(boolnot(bitnot(_dst_idx)), boolnot(bitnot(_src_idx))))))):
                                    _path = self.dijkstraFindPath(_src_idx, _dst_idx)
                                    if cond(rbitxor(1000, _num)):
                                        _path = self.pathToVectors(_path)
                                        if cond(boolnot((rbitor(rless(2, (rneq([], _path))), req(Vector(((0.0), (0.0), (0.0))), _src_pos))))):
                                            _node1_pos: Vector = self.builtin_funcs.llList2Vector(_path, 0)
                                            _node2_pos: Vector = self.builtin_funcs.llList2Vector(_path, 1)
                                            _ideal_dir: Vector = self.builtin_funcs.llVecNorm(rsub(_node1_pos, _node2_pos))
                                            _src_dir: Vector = self.builtin_funcs.llVecNorm(rsub(_src_pos, _node2_pos))
                                            _dir_diff: float = self.builtin_funcs.llRot2Angle(self.builtin_funcs.llRotBetween(_ideal_dir, _src_dir))
                                            if cond(rless(bin2float('0.250000', '0000803e'), _dir_diff)):
                                                _path = self.builtin_funcs.llDeleteSubList(_path, 0, 0)
                                    else:
                                        _path = self.pathToIDs(_path)
                                self.builtin_funcs.llMessageLinked((typecast(-4, int)), 1003, self.builtin_funcs.llDumpList2String(_path, ":"), _id)
                        else:
                            _i: int = 0
                            _len: int = rneq([], self.gNodes)
                            _i = 0
                            while True == True:
                                if not cond(rless(_len, _i)):
                                    break
                                _node_id: str = self.builtin_funcs.llList2String(self.gNodes, _i)
                                _node_pos: Vector = self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(_i)))
                                self.builtin_funcs.llMessageLinked((typecast(-4, int)), 902, _node_id, typecast(typecast(_node_pos, str), Key))
                                if cond(boolnot((rmod(25, _i)))):
                                    self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
                                _i = neg(bitnot(neg(bitnot(_i))))
                            _len = rneq([], self.gNodeRelations)
                            _i = 0
                            while True == True:
                                if not cond(rless(_len, _i)):
                                    break
                                _rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
                                self.builtin_funcs.llMessageLinked((typecast(-4, int)), 903, self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)), typecast(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), Key))
                                if cond(boolnot((rmod(25, _i)))):
                                    self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
                                _i += 1
                            self.builtin_funcs.llMessageLinked((typecast(-4, int)), 901, "", typecast("00000000-0000-0000-0000-000000000000", Key))
                    else:
                        self.gNodeRelations = radd((rbitor(self.builtin_funcs.llListFindList(self.gNodes, typecast(typecast(_id, str), list)), rmul(65536, self.builtin_funcs.llListFindList(self.gNodes, typecast(_str, list))))), self.gNodeRelations)
                else:
                    self.gNodes = radd(typecast(typecast(_id, str), Vector), radd(_str, self.gNodes))
            else:
                self.calculateEdgeWeights()
                self.builtin_funcs.llOwnerSay("Graph state saved")
        else:
            self.gNodes = []
            self.gNodeRelations = []
            self.gWeightedEdges = []

