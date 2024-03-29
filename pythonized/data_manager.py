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

    async def calculateEdgeWeights(self) -> None:
        self.gWeightedEdges = []
        _i: int = 0
        _len: int = await self.builtin_funcs.llGetListLength(self.gNodeRelations)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = await self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
            _src: str = await self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel))
            _dst: str = await self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel))
            _src_idx: int = await self.builtin_funcs.llListFindList(self.gNodes, [_src])
            _dst_idx: int = await self.builtin_funcs.llListFindList(self.gNodes, [_dst])
            _dist: float = await self.builtin_funcs.llVecDist(await self.builtin_funcs.llList2Vector(self.gNodes, radd(1, _src_idx)), await self.builtin_funcs.llList2Vector(self.gNodes, radd(1, _dst_idx)))
            self.gWeightedEdges = radd([rdiv(2, _src_idx), "", rdiv(2, _dst_idx), _dist], self.gWeightedEdges)
            _i += 1
        self.gWeightedEdges = await self.builtin_funcs.llListSort(self.gWeightedEdges, 4, 1)

    @with_goto
    async def dijkstraFindPath(self, _src_idx: int, _dst_idx: int) -> list:
        if cond(req(_dst_idx, _src_idx)):
            if True == True:
                return [_src_idx]
        _src: int = rdiv(2, _src_idx)
        _dst: int = rdiv(2, _dst_idx)
        _dist: list = []
        _prev: list = []
        _consumed: list = []
        _V: int = rdiv(2, await self.builtin_funcs.llGetListLength(self.gNodes))
        _edges_len: int = await self.builtin_funcs.llGetListLength(self.gWeightedEdges)
        _i: int = 0
        _i = 0
        while True == True:
            if not cond(rless(_V, _i)):
                break
            _dist = radd([(10000000.0)], _dist)
            _prev = radd([-1], _prev)
            _consumed = radd([0], _consumed)
            _i += 1
        _dist = await self.builtin_funcs.llListReplaceList(_dist, [(0.0)], _src, _src)
        _u: int = 0
        while cond(1):
            _min_dist: float = (10000000.0)
            _v: int = 0
            _v = 0
            while True == True:
                if not cond(rless(_V, _v)):
                    break
                _cur_dist: float = await self.builtin_funcs.llList2Float(_dist, _v)
                if cond(rleq(_min_dist, _cur_dist)):
                    if cond(boolnot(await self.builtin_funcs.llList2Integer(_consumed, _v))):
                        _min_dist = _cur_dist
                        _u = _v
                _v += 1
            if cond(req((10000000.0), _min_dist)):
                if True == True:
                    return []
            if cond(req(_dst, _u)):
                _path: list = []
                while cond(rneq(-1, _u)):
                    _path = radd(_path, [rmul(2, _u)])
                    _u = await self.builtin_funcs.llList2Integer(_prev, _u)
                if True == True:
                    return _path
            _consumed = await self.builtin_funcs.llListReplaceList(_consumed, [1], _u, _u)
            _adj_start: int = await self.builtin_funcs.llListFindList(self.gWeightedEdges, [_u, ""])
            _i = _adj_start
            while True == True:
                if not cond(rless(_edges_len, _i)):
                    break
                if cond(rneq(_u, await self.builtin_funcs.llList2Integer(self.gWeightedEdges, radd(0, _i)))):
                    goto ._next
                _v: int = await self.builtin_funcs.llList2Integer(self.gWeightedEdges, radd(2, _i))
                if cond(boolnot(await self.builtin_funcs.llList2Integer(_consumed, _v))):
                    _u_dist: float = await self.builtin_funcs.llList2Float(_dist, _u)
                    _edge_dist: float = await self.builtin_funcs.llList2Float(self.gWeightedEdges, radd(3, _i))
                    _alt: float = radd(_edge_dist, _u_dist)
                    if cond(rless(await self.builtin_funcs.llList2Float(_dist, _v), _alt)):
                        _dist = await self.builtin_funcs.llListReplaceList(_dist, [_alt], _v, _v)
                        _prev = await self.builtin_funcs.llListReplaceList(_prev, [_u], _v, _v)
                _i = radd(4, _i)
            label ._next
        if True == True:
            return []

    async def pathToIDs(self, _path: list) -> list:
        _path_new: list = []
        _i: int = 0
        _len: int = await self.builtin_funcs.llGetListLength(_path)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _path_new = radd([await self.builtin_funcs.llList2String(self.gNodes, radd(0, await self.builtin_funcs.llList2Integer(_path, _i)))], _path_new)
            _i += 1
        _path = []
        return _path_new

    async def pathToVectors(self, _path: list) -> list:
        _path_new: list = []
        _i: int = 0
        _len: int = await self.builtin_funcs.llGetListLength(_path)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _path_new = radd([await self.builtin_funcs.llList2Vector(self.gNodes, radd(1, await self.builtin_funcs.llList2Integer(_path, _i)))], _path_new)
            _i += 1
        _path = []
        return _path_new

    @with_goto
    async def findClosestAccessibleNode(self, _pos: Vector, _caster_key: Key) -> int:
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
        _len = await self.builtin_funcs.llGetListLength(self.gNodes)
        _points = []
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _diff = rsub(_pos, await self.builtin_funcs.llList2Vector(self.gNodes, radd(1, _i)))
            _diff = replace_coord_axis(_diff, 2, rmul((2.0), _diff[2]))
            _points = radd([rbitor(_i, rshl(16, typecast(await self.builtin_funcs.llVecDist(Vector(((0.0), (0.0), (0.0))), _diff), int)))], _points)
            _i = radd(2, _i)
        _points = await self.builtin_funcs.llListSort(_points, 1, 1)
        if cond(req("00000000-0000-0000-0000-000000000000", _caster_key)):
            if True == True:
                return rbitand(65535, await self.builtin_funcs.llList2Integer(_points, 0))
        _len = await self.builtin_funcs.llGetListLength(_points)
        _i = 0
        while True == True:
            if not cond(rbooland(rless(5, _i), rless(_len, _i))):
                break
            _point = await self.builtin_funcs.llList2Integer(_points, _i)
            _node_idx = rbitand(65535, _point)
            if cond(rless(2, rshr(16, _point))):
                if True == True:
                    return _node_idx
            _node_pos = await self.builtin_funcs.llList2Vector(self.gNodes, radd(1, _node_idx))
            _cast_data = await self.builtin_funcs.llCastRay(radd(Vector((0.0, 0.0, 0.5)), _pos), radd(Vector((0.0, 0.0, 0.5)), _node_pos), [3, 2, 0, rbitor(1, rbitor(8, 2)), 2, 2])
            _j = 0
            _num_hits = await self.builtin_funcs.llList2Integer(_cast_data, -1)
            if cond(rgeq(0, _num_hits)):
                _j = 0
                while True == True:
                    if not cond(rless(_num_hits, _j)):
                        break
                    if cond(rneq(_caster_key, await self.builtin_funcs.llList2Key(_cast_data, rmul(2, _j)))):
                        goto ._next
                    _j += 1
                if True == True:
                    return _node_idx
            label ._next
            _i += 1
        if True == True:
            return rbitand(65535, await self.builtin_funcs.llList2Integer(_points, 0))

    async def nodeRefToIdx(self, _node_ref: str, _caster_key: Key) -> int:
        if cond(req(Vector(((0.0), (0.0), (0.0))), typecast(_node_ref, Vector))):
            return await self.builtin_funcs.llListFindList(self.gNodes, [_node_ref])
        else:
            return await self.findClosestAccessibleNode(typecast(_node_ref, Vector), _caster_key)

    async def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(req(800, _num)):
            self.gNodes = []
            self.gNodeRelations = []
            self.gWeightedEdges = []
        elif cond(req(801, _num)):
            await self.calculateEdgeWeights()
            await self.builtin_funcs.llOwnerSay("Graph state saved")
        elif cond(req(802, _num)):
            self.gNodes = radd([_str, typecast(typecast(_id, str), Vector)], self.gNodes)
        elif cond(req(803, _num)):
            self.gNodeRelations = radd(rbitor(await self.builtin_funcs.llListFindList(self.gNodes, [typecast(_id, str)]), rshl(16, await self.builtin_funcs.llListFindList(self.gNodes, [_str]))), self.gNodeRelations)
        elif cond(req(900, _num)):
            _i: int = 0
            _len: int = await self.builtin_funcs.llGetListLength(self.gNodes)
            _i = 0
            while True == True:
                if not cond(rless(_len, _i)):
                    break
                _node_id: str = await self.builtin_funcs.llList2String(self.gNodes, radd(0, _i))
                _node_pos: Vector = await self.builtin_funcs.llList2Vector(self.gNodes, radd(1, _i))
                await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 902, _node_id, typecast(typecast(_node_pos, str), Key))
                if cond(req(0, rmod(25, _i))):
                    await self.builtin_funcs.llSleep(0.5)
                _i = radd(2, _i)
            _len = await self.builtin_funcs.llGetListLength(self.gNodeRelations)
            _i = 0
            while True == True:
                if not cond(rless(_len, _i)):
                    break
                _rel: int = await self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
                await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 903, await self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)), typecast(await self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), Key))
                if cond(req(0, rmod(25, _i))):
                    await self.builtin_funcs.llSleep(0.5)
                _i += 1
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 901, "", typecast("00000000-0000-0000-0000-000000000000", Key))
        elif cond(rboolor(req(1002, _num), rboolor(req(1001, _num), req(1000, _num)))):
            _path: list = []
            _params: list = await self.builtin_funcs.llParseString2List(_str, [":"], [])
            _src_idx: int = await self.nodeRefToIdx(await self.builtin_funcs.llList2String(_params, 0), _id)
            _dst_idx: int = await self.nodeRefToIdx(await self.builtin_funcs.llList2String(_params, 1), typecast("00000000-0000-0000-0000-000000000000", Key))
            _src_pos: Vector = typecast(await self.builtin_funcs.llList2String(_params, 0), Vector)
            if cond(rbooland(await self.builtin_funcs.llGetListLength(self.gWeightedEdges), rbooland(rneq(-1, _dst_idx), rneq(-1, _src_idx)))):
                _path = await self.dijkstraFindPath(_src_idx, _dst_idx)
                if cond(req(1000, _num)):
                    _path = await self.pathToIDs(_path)
                else:
                    _path = await self.pathToVectors(_path)
                    if cond(rbooland(rgeq(2, await self.builtin_funcs.llGetListLength(_path)), rneq(Vector(((0.0), (0.0), (0.0))), _src_pos))):
                        _node1_pos: Vector = await self.builtin_funcs.llList2Vector(_path, 0)
                        _node2_pos: Vector = await self.builtin_funcs.llList2Vector(_path, 1)
                        _ideal_dir: Vector = await self.builtin_funcs.llVecNorm(rsub(_node1_pos, _node2_pos))
                        _src_dir: Vector = await self.builtin_funcs.llVecNorm(rsub(_src_pos, _node2_pos))
                        _dir_diff: float = await self.builtin_funcs.llRot2Angle(await self.builtin_funcs.llRotBetween(_ideal_dir, _src_dir))
                        if cond(rless(0.25, _dir_diff)):
                            _path = await self.builtin_funcs.llDeleteSubList(_path, 0, 0)
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 1003, await self.builtin_funcs.llDumpList2String(_path, ":"), _id)

