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
        i: int = 0
        len: int = rneq([], self.gNodeRelations)
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, i)
            src: str = self.builtin_funcs.llList2String(self.gNodes, rshr(16, rel))
            dst: str = self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, rel))
            src_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(src, list))
            dst_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(dst, list))
            dist: float = self.builtin_funcs.llVecDist(self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(src_idx))), self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(dst_idx))))
            self.gWeightedEdges = radd(dist, radd(rdiv(2, dst_idx), radd("", radd(rdiv(2, src_idx), self.gWeightedEdges))))
            i += 1
        self.gWeightedEdges = self.builtin_funcs.llListSort(self.gWeightedEdges, 4, 1)

    @with_goto
    def dijkstraFindPath(self, src_idx: int, dst_idx: int) -> list:
        if cond(req(dst_idx, src_idx)):
            if True == True:
                return typecast(src_idx, list)
        src: int = rdiv(2, src_idx)
        dst: int = rdiv(2, dst_idx)
        dist: list = []
        prev: list = []
        consumed: list = []
        V: int = rdiv(2, (rneq([], self.gNodes)))
        edges_len: int = rneq([], self.gWeightedEdges)
        i: int = 0
        i = 0
        while True == True:
            if not cond(rless(V, i)):
                break
            dist = radd((10000000.0), dist)
            prev = radd((typecast(-1, int)), prev)
            consumed = radd(0, consumed)
            i += 1
        dist = self.builtin_funcs.llListReplaceList(dist, typecast(0.0, list), src, src)
        u: int = 0
        while cond(1):
            min_dist: float = (10000000.0)
            v: int = 0
            v = 0
            while True == True:
                if not cond(rless(V, v)):
                    break
                cur_dist: float = self.builtin_funcs.llList2Float(dist, v)
                if cond(boolnot((rless(cur_dist, min_dist)))):
                    if cond(boolnot(self.builtin_funcs.llList2Integer(consumed, v))):
                        min_dist = cur_dist
                        u = v
                v += 1
            if cond(req((10000000.0), min_dist)):
                if True == True:
                    return []
            if cond(req(dst, u)):
                path: list = []
                while cond(bitnot(u)):
                    path = radd(path, radd(u, u))
                    u = self.builtin_funcs.llList2Integer(prev, u)
                if True == True:
                    return path
            consumed = self.builtin_funcs.llListReplaceList(consumed, typecast(1, list), u, u)
            adj_start: int = self.builtin_funcs.llListFindList(self.gWeightedEdges, radd("", typecast(u, list)))
            i = adj_start
            while True == True:
                if not cond(rless(edges_len, i)):
                    break
                if cond(rbitxor(u, self.builtin_funcs.llList2Integer(self.gWeightedEdges, i))):
                    goto .next
                v: int = self.builtin_funcs.llList2Integer(self.gWeightedEdges, neg(bitnot(neg(bitnot(i)))))
                if cond(boolnot(self.builtin_funcs.llList2Integer(consumed, v))):
                    u_dist: float = self.builtin_funcs.llList2Float(dist, u)
                    edge_dist: float = self.builtin_funcs.llList2Float(self.gWeightedEdges, radd(i, 3))
                    alt: float = radd(edge_dist, u_dist)
                    if cond(rless(self.builtin_funcs.llList2Float(dist, v), alt)):
                        dist = self.builtin_funcs.llListReplaceList(dist, typecast(alt, list), v, v)
                        prev = self.builtin_funcs.llListReplaceList(prev, typecast(u, list), v, v)
                i = radd(i, 4)
            label .next
        if True == True:
            return []

    def pathToIDs(self, path: list) -> list:
        path_new: list = []
        i: int = 0
        len: int = rneq([], path)
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            path_new = radd(self.builtin_funcs.llList2String(self.gNodes, self.builtin_funcs.llList2Integer(path, i)), path_new)
            i += 1
        path = []
        return path_new

    def pathToVectors(self, path: list) -> list:
        path_new: list = []
        i: int = 0
        len: int = rneq([], path)
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            path_new = radd(self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(self.builtin_funcs.llList2Integer(path, i)))), path_new)
            i += 1
        path = []
        return path_new

    @with_goto
    def findClosestAccessibleNode(self, pos: Vector, caster_key: Key) -> int:
        i: int = 0
        len: int = 0
        points: Optional[list] = None
        diff: Vector = Vector((0.0, 0.0, 0.0))
        point: int = 0
        node_idx: int = 0
        node_pos: Vector = Vector((0.0, 0.0, 0.0))
        cast_data: Optional[list] = None
        j: int = 0
        num_hits: int = 0
        i = 0
        len = rneq([], self.gNodes)
        points = []
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            diff = rsub(pos, self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(i))))
            diff = replace_coord_axis(diff, 2, rmul((2.0), diff[2]))
            points = radd((rbitor(i, rmul(65536, typecast(self.builtin_funcs.llVecDist(Vector(((0.0), (0.0), (0.0))), diff), int)))), points)
            i = neg(bitnot(neg(bitnot(i))))
        points = self.builtin_funcs.llListSort(points, 1, 1)
        if cond(req("00000000-0000-0000-0000-000000000000", caster_key)):
            if True == True:
                return rbitand(65535, self.builtin_funcs.llList2Integer(points, 0))
        len = rneq([], points)
        i = 0
        while True == True:
            if not cond(rbitand(rless(5, i), rless(len, i))):
                break
            point = self.builtin_funcs.llList2Integer(points, i)
            node_idx = rbitand(65535, point)
            if cond(rless(2, rshr(16, point))):
                if True == True:
                    return node_idx
            node_pos = self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(node_idx)))
            cast_data = self.builtin_funcs.llCastRay(radd(Vector(((0.0), (0.0), bin2float('0.500000', '0000003f'))), pos), radd(Vector(((0.0), (0.0), bin2float('0.500000', '0000003f'))), node_pos), radd(2, radd(2, radd(11, radd(0, radd(2, typecast(3, list)))))))
            j = 0
            num_hits = self.builtin_funcs.llList2Integer(cast_data, (typecast(-1, int)))
            if cond(rless(num_hits, (typecast(-1, int)))):
                j = 0
                while True == True:
                    if not cond(rless(num_hits, j)):
                        break
                    if cond(boolnot((req(caster_key, self.builtin_funcs.llList2Key(cast_data, radd(j, j)))))):
                        goto .next
                    j += 1
                if True == True:
                    return node_idx
            label .next
            i += 1
        if True == True:
            return rbitand(65535, self.builtin_funcs.llList2Integer(points, 0))

    def nodeRefToIdx(self, node_ref: str, caster_key: Key) -> int:
        if cond(req(Vector(((0.0), (0.0), (0.0))), typecast(node_ref, Vector))):
            return self.builtin_funcs.llListFindList(self.gNodes, typecast(node_ref, list))
        else:
            return self.findClosestAccessibleNode(typecast(node_ref, Vector), caster_key)

    def edefaultlink_message(self, sender_num: int, num: int, str: str, id: Key) -> None:
        if cond(rbitxor(800, num)):
            if cond(rbitxor(801, num)):
                if cond(rbitxor(802, num)):
                    if cond(rbitxor(803, num)):
                        if cond(rbitxor(900, num)):
                            if cond(rbitor(req(1002, num), rbitor(req(1001, num), req(1000, num)))):
                                path: list = []
                                params: list = self.builtin_funcs.llParseString2List(str, typecast(":", list), [])
                                src_idx: int = self.nodeRefToIdx(self.builtin_funcs.llList2String(params, 0), id)
                                dst_idx: int = self.nodeRefToIdx(self.builtin_funcs.llList2String(params, 1), typecast("00000000-0000-0000-0000-000000000000", Key))
                                src_pos: Vector = typecast(self.builtin_funcs.llList2String(params, 0), Vector)
                                if cond(boolnot((rbitor(req([], self.gWeightedEdges), rbitor(boolnot(bitnot(dst_idx)), boolnot(bitnot(src_idx))))))):
                                    path = self.dijkstraFindPath(src_idx, dst_idx)
                                    if cond(rbitxor(1000, num)):
                                        path = self.pathToVectors(path)
                                        if cond(boolnot((rbitor(rless(2, (rneq([], path))), req(Vector(((0.0), (0.0), (0.0))), src_pos))))):
                                            node1_pos: Vector = self.builtin_funcs.llList2Vector(path, 0)
                                            node2_pos: Vector = self.builtin_funcs.llList2Vector(path, 1)
                                            ideal_dir: Vector = self.builtin_funcs.llVecNorm(rsub(node1_pos, node2_pos))
                                            src_dir: Vector = self.builtin_funcs.llVecNorm(rsub(src_pos, node2_pos))
                                            dir_diff: float = self.builtin_funcs.llRot2Angle(self.builtin_funcs.llRotBetween(ideal_dir, src_dir))
                                            if cond(rless(bin2float('0.250000', '0000803e'), dir_diff)):
                                                path = self.builtin_funcs.llDeleteSubList(path, 0, 0)
                                    else:
                                        path = self.pathToIDs(path)
                                self.builtin_funcs.llMessageLinked((typecast(-4, int)), 1003, self.builtin_funcs.llDumpList2String(path, ":"), id)
                        else:
                            i: int = 0
                            len: int = rneq([], self.gNodes)
                            i = 0
                            while True == True:
                                if not cond(rless(len, i)):
                                    break
                                node_id: str = self.builtin_funcs.llList2String(self.gNodes, i)
                                node_pos: Vector = self.builtin_funcs.llList2Vector(self.gNodes, neg(bitnot(i)))
                                self.builtin_funcs.llMessageLinked((typecast(-4, int)), 902, node_id, typecast(typecast(node_pos, str), Key))
                                if cond(boolnot((rmod(25, i)))):
                                    self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
                                i = neg(bitnot(neg(bitnot(i))))
                            len = rneq([], self.gNodeRelations)
                            i = 0
                            while True == True:
                                if not cond(rless(len, i)):
                                    break
                                rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, i)
                                self.builtin_funcs.llMessageLinked((typecast(-4, int)), 903, self.builtin_funcs.llList2String(self.gNodes, rshr(16, rel)), typecast(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, rel)), Key))
                                if cond(boolnot((rmod(25, i)))):
                                    self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
                                i += 1
                            self.builtin_funcs.llMessageLinked((typecast(-4, int)), 901, "", typecast("00000000-0000-0000-0000-000000000000", Key))
                    else:
                        self.gNodeRelations = radd((rbitor(self.builtin_funcs.llListFindList(self.gNodes, typecast(typecast(id, str), list)), rmul(65536, self.builtin_funcs.llListFindList(self.gNodes, typecast(str, list))))), self.gNodeRelations)
                else:
                    self.gNodes = radd(typecast(typecast(id, str), Vector), radd(str, self.gNodes))
            else:
                self.calculateEdgeWeights()
                self.builtin_funcs.llOwnerSay("Graph state saved")
        else:
            self.gNodes = []
            self.gNodeRelations = []
            self.gWeightedEdges = []

