from lummao import *


class Script(BaseLSLScript):
    gOwnLogicalID: str
    gParentLogicalID: str
    gNodes: list
    gPendingNodes: list
    gNodeRelations: list
    gPendingRelations: list
    gArrowPool: list
    gRezNum: int
    gRestoreArrows: int
    gRestoring: int
    gNeededArrows: int
    gNeededNodes: int
    gAvailRezSlots: int
    gLastRezTime: int
    gClickTimeout: int
    gTickCount: int
    gFirstClicked: str
    gSecondClicked: str
    gGraphDirty: int
    gMenuChannel: int
    gConnectionMenuChannel: int

    def __init__(self):
        super().__init__()
        self.gOwnLogicalID = ""
        self.gParentLogicalID = ""
        self.gNodes = []
        self.gPendingNodes = []
        self.gNodeRelations = []
        self.gPendingRelations = []
        self.gArrowPool = []
        self.gRezNum = 0
        self.gRestoreArrows = 0
        self.gRestoring = 0
        self.gNeededArrows = 0
        self.gNeededNodes = 0
        self.gAvailRezSlots = 5
        self.gLastRezTime = 0
        self.gClickTimeout = 0
        self.gTickCount = 0
        self.gFirstClicked = ""
        self.gSecondClicked = ""
        self.gGraphDirty = 0
        self.gMenuChannel = 0
        self.gConnectionMenuChannel = 0

    def restoreLogicalID(self, _create: int) -> None:
        _desc: str = self.builtin_funcs.llGetObjectDesc()
        if cond(bitnot(self.builtin_funcs.llSubStringIndex(_desc, ":"))):
            _parsed: list = self.builtin_funcs.llParseString2List(_desc, typecast(":", list), [])
            self.gOwnLogicalID = self.builtin_funcs.llList2String(_parsed, 0)
            self.gParentLogicalID = self.builtin_funcs.llList2String(_parsed, 1)
        else:
            if cond(_create):
                self.gOwnLogicalID = self.generateLogicalID()
                self.gParentLogicalID = ""
                self.builtin_funcs.llSetObjectDesc(self.generateDescription())

    def generateDescription(self) -> str:
        return radd(self.gParentLogicalID, radd(":", self.gOwnLogicalID))

    def strReplace(self, _subject: str, _search: str, _replace: str) -> str:
        return self.builtin_funcs.llDumpList2String(self.builtin_funcs.llParseStringKeepNulls(_subject, typecast(_search, list), []), _replace)

    def compressKey(self, _k: Key) -> str:
        _s: str = self.builtin_funcs.llToLower(radd("0", self.strReplace(typecast(_k, str), "-", "")))
        _ret: str = ""
        _i: int = 0
        _A: str = ""
        _B: str = ""
        _C: str = ""
        _D: str = ""
        _i = 0
        while True == True:
            if not cond(rless(32, _i)):
                break
            _A = self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _B = self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _C = self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _D = "b"
            if cond(req("0", _A)):
                _A = "e"
                _D = "8"
            else:
                if cond(req("d", _A)):
                    _A = "e"
                    _D = "9"
                else:
                    if cond(req("f", _A)):
                        _A = "e"
                        _D = "a"
            _ret = radd((radd(_C, radd("%b", radd(_B, radd(_D, radd("%", radd(_A, "%e"))))))), _ret)
        return self.builtin_funcs.llUnescapeURL(_ret)

    def padDash(self, _s: str) -> str:
        return radd(self.builtin_funcs.llGetSubString(_s, 20, 31), radd("-", radd(self.builtin_funcs.llGetSubString(_s, 16, 19), radd("-", radd(self.builtin_funcs.llGetSubString(_s, 12, 15), radd("-", radd(self.builtin_funcs.llGetSubString(_s, 8, 11), radd("-", self.builtin_funcs.llGetSubString(_s, 0, 7)))))))))

    def uncompressKey(self, _s: str) -> Key:
        _i: int = 0
        _ret: str = ""
        _A: str = ""
        _B: str = ""
        _C: str = ""
        _D: str = ""
        _s = self.builtin_funcs.llToLower(self.builtin_funcs.llEscapeURL(_s))
        _i = 0
        while True == True:
            if not cond(rless(99, _i)):
                break
            _A = self.builtin_funcs.llGetSubString(_s, neg(bitnot(neg(bitnot(_i)))), neg(bitnot(neg(bitnot(_i)))))
            _B = self.builtin_funcs.llGetSubString(_s, radd(_i, 5), radd(_i, 5))
            _C = self.builtin_funcs.llGetSubString(_s, radd(_i, 8), radd(_i, 8))
            _D = self.builtin_funcs.llGetSubString(_s, radd(_i, 4), radd(_i, 4))
            if cond(req("8", _D)):
                _A = "0"
            else:
                if cond(req("9", _D)):
                    _A = "d"
                else:
                    if cond(req("a", _D)):
                        _A = "f"
            _ret = radd(_C, radd(_B, radd(_A, _ret)))
            _i = radd(_i, 9)
        return typecast(self.padDash(_ret), Key)

    def generateLogicalID(self) -> str:
        return self.builtin_funcs.llGetSubString(self.builtin_funcs.llStringToBase64(self.compressKey(self.builtin_funcs.llGenerateKey())), 0, 5)

    def nodeIDToKey(self, _node_id: str) -> Key:
        _idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(_node_id, list))
        if cond(boolnot(bitnot(_idx))):
            return typecast("00000000-0000-0000-0000-000000000000", Key)
        return self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(_idx))))

    def nodeKeyToID(self, _id: Key) -> str:
        _idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(self.compressKey(_id), list))
        if cond(boolnot(bitnot(_idx))):
            return ""
        return self.builtin_funcs.llList2String(self.gNodes, bitnot(neg(_idx)))

    def dumpNodeDetails(self) -> None:
        _i: int = 0
        _len: int = rneq([], self.gNodes)
        self.builtin_funcs.llOwnerSay("gNodes:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            self.builtin_funcs.llOwnerSay(radd(typecast(self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(_i)))), str), radd(": ", self.builtin_funcs.llList2String(self.gNodes, _i))))
            _i = neg(bitnot(neg(bitnot(_i))))
        _len = rneq([], self.gPendingNodes)
        self.builtin_funcs.llOwnerSay("gPendingNodes:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            self.builtin_funcs.llOwnerSay(radd(self.builtin_funcs.llList2String(self.gPendingNodes, neg(bitnot(_i))), radd(": ", self.builtin_funcs.llList2String(self.gPendingNodes, _i))))
            _i = neg(bitnot(neg(bitnot(_i))))
        _len = rneq([], self.gNodeRelations)
        self.builtin_funcs.llOwnerSay("NODE RELATIONS:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
            self.builtin_funcs.llOwnerSay(radd(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), radd(": ", self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)))))
            _i += 1
        _len = rneq([], self.gPendingRelations)
        self.builtin_funcs.llOwnerSay("PENDING NODE RELATIONS:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = self.builtin_funcs.llList2Integer(self.gPendingRelations, _i)
            self.builtin_funcs.llOwnerSay(radd(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), radd(": ", self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)))))
            _i += 1
        self.builtin_funcs.llOwnerSay(radd(typecast(self.builtin_funcs.llGetFreeMemory(), str), "Free Memory: "))

    def trackNode(self, _node_id: str, _node_key: Key) -> None:
        self.gNodes = radd([_node_id, self.compressKey(_node_key)], self.gNodes)

    def untrackNode(self, _node_id: str, _kill_relations: int) -> None:
        _node_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(_node_id, list))
        if cond(boolnot(bitnot(_node_idx))):
            return
        if cond(_kill_relations):
            _len: int = rneq([], self.gNodeRelations)
            _i: int = 0
            _i = bitnot(neg(_len))
            while True == True:
                if not cond(rless(_i, (typecast(-1, int)))):
                    break
                _rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
                _src_idx: int = rshr(16, _rel)
                _dst_idx: int = rbitand(65535, _rel)
                _new_src_idx: int = _src_idx
                _new_dst_idx: int = _dst_idx
                if cond(rless(_src_idx, _node_idx)):
                    _new_src_idx = bitnot(neg(bitnot(neg(_new_src_idx))))
                if cond(rless(_dst_idx, _node_idx)):
                    _new_dst_idx = bitnot(neg(bitnot(neg(_new_dst_idx))))
                if cond(rbitor(req(_node_idx, _dst_idx), req(_node_idx, _src_idx))):
                    _src_id: str = self.builtin_funcs.llList2String(self.gNodes, _src_idx)
                    _dst_id: str = self.builtin_funcs.llList2String(self.gNodes, _dst_idx)
                    self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(_dst_id, radd(":", radd(_src_id, "arrow_kill:"))))
                    self.gNodeRelations = self.builtin_funcs.llDeleteSubList(self.gNodeRelations, _i, _i)
                else:
                    if cond(rbitor(rbitxor(_dst_idx, _new_dst_idx), rbitxor(_src_idx, _new_src_idx))):
                        _new_rel: int = rbitor(_new_dst_idx, rmul(65536, _new_src_idx))
                        self.gNodeRelations = self.builtin_funcs.llListReplaceList(self.gNodeRelations, typecast(_new_rel, list), _i, _i)
                _i -= 1
        self.gNodes = self.builtin_funcs.llDeleteSubList(self.gNodes, _node_idx, neg(bitnot(_node_idx)))

    def pruneNodes(self) -> None:
        _len: int = rneq([], self.gNodes)
        _i: int = 0
        _i = bitnot(neg(bitnot(neg(_len))))
        while True == True:
            if not cond(rless(_i, (typecast(-1, int)))):
                break
            _node_key: Key = self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(_i))))
            if cond(req((0.0), self.builtin_funcs.llGetObjectMass(_node_key))):
                self.untrackNode(self.builtin_funcs.llList2String(self.gNodes, _i), 1)
            _i = bitnot(neg(bitnot(neg(_i))))

    def saveNodes(self) -> None:
        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 800, "", typecast("00000000-0000-0000-0000-000000000000", Key))
        _i: int = 0
        _len: int = rneq([], self.gNodes)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _node_id: str = self.builtin_funcs.llList2String(self.gNodes, _i)
            _node_key: Key = self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(_i))))
            _node_pos: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(_node_key, typecast(3, list)), 0)
            self.builtin_funcs.llMessageLinked((typecast(-4, int)), 802, _node_id, typecast(typecast(_node_pos, str), Key))
            if cond(boolnot((rmod(25, _i)))):
                self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
            _i = neg(bitnot(neg(bitnot(_i))))
        _len = rneq([], self.gNodeRelations)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
            self.builtin_funcs.llMessageLinked((typecast(-4, int)), 803, self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)), typecast(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), Key))
            if cond(boolnot((rmod(25, _i)))):
                self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
            _i += 1
        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 801, "", typecast("00000000-0000-0000-0000-000000000000", Key))
        self.gGraphDirty = 0

    def clearAll(self) -> None:
        self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(self.gOwnLogicalID, "node_kill_all:"))
        self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(self.gOwnLogicalID, "arrow_kill_all:"))
        self.gNodes = []
        self.gNodeRelations = []
        self.gPendingNodes = []
        self.gPendingRelations = []
        self.gArrowPool = []
        self.gNeededArrows = 0
        self.gNeededNodes = 0
        self.gAvailRezSlots = 5

    def initRestoreNodes(self, _restore_arrows: int) -> None:
        self.clearAll()
        self.gRestoring = 1
        self.gRestoreArrows = _restore_arrows
        self.gLastRezTime = self.builtin_funcs.llGetUnixTime()
        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 900, "", typecast("00000000-0000-0000-0000-000000000000", Key))

    def addRelation(self, _src: str, _dst: str) -> None:
        _rel: list = typecast(rbitor(self.builtin_funcs.llListFindList(self.gNodes, typecast(_dst, list)), rmul(65536, self.builtin_funcs.llListFindList(self.gNodes, typecast(_src, list)))), list)
        if cond(boolnot(bitnot(self.builtin_funcs.llListFindList(self.gNodeRelations, _rel)))):
            self.gPendingRelations = radd(_rel, self.gPendingRelations)
            self.gNeededArrows += 1
            self.tryRezPending()

    def removeRelation(self, _src: str, _dst: str) -> None:
        _rel: list = typecast(rbitor(self.builtin_funcs.llListFindList(self.gNodes, typecast(_dst, list)), rmul(65536, self.builtin_funcs.llListFindList(self.gNodes, typecast(_src, list)))), list)
        _idx: int = self.builtin_funcs.llListFindList(self.gNodeRelations, _rel)
        if cond(bitnot(_idx)):
            self.gNodeRelations = self.builtin_funcs.llDeleteSubList(self.gNodeRelations, _idx, _idx)
        self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(_dst, radd(":", radd(_src, "arrow_kill:"))))

    def updateNodeRelations(self) -> None:
        if cond(req([], self.gPendingRelations)):
            return
        _i: int = 0
        _len: int = rneq([], self.gPendingRelations)
        _i = bitnot(neg(_len))
        while True == True:
            if not cond(rless(_i, (typecast(-1, int)))):
                break
            if cond(req([], self.gArrowPool)):
                return
            _rel: int = self.builtin_funcs.llList2Integer(self.gPendingRelations, _i)
            _src_id: str = self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel))
            _dst_id: str = self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel))
            _src_key: str = typecast(self.nodeIDToKey(_src_id), str)
            _dst_key: str = typecast(self.nodeIDToKey(_dst_id), str)
            if cond(boolnot((rbitor(req("00000000-0000-0000-0000-000000000000", _dst_key), req("00000000-0000-0000-0000-000000000000", _src_key))))):
                _msg: str = radd((radd((radd((radd((radd((radd((radd((radd((radd(self.gOwnLogicalID, ":")), _dst_key)), ":")), _dst_id)), ":")), _src_key)), ":")), _src_id)), "arrow_add:")
                self.builtin_funcs.llRegionSayTo(self.builtin_funcs.llList2Key(self.gArrowPool, 0), (typecast(-21461419, int)), _msg)
                self.gPendingRelations = self.builtin_funcs.llDeleteSubList(self.gPendingRelations, _i, _i)
                self.gArrowPool = self.builtin_funcs.llDeleteSubList(self.gArrowPool, 0, 0)
                self.gNodeRelations = radd(_rel, self.gNodeRelations)
            _i -= 1

    def tryRezPending(self) -> None:
        while cond(rbitand(rless(self.gAvailRezSlots, 0), rless(self.gNeededNodes, 0))):
            self.builtin_funcs.llMessageLinked((typecast(-1, int)), 1100, typecast(preincr(self.__dict__, "gRezNum"), str), (typecast("node", Key)))
            self.gAvailRezSlots -= 1
            self.gNeededNodes -= 1
        while cond(rbitand(rless(self.gAvailRezSlots, 0), rless(self.gNeededArrows, 0))):
            self.builtin_funcs.llMessageLinked((typecast(-1, int)), 1100, typecast(preincr(self.__dict__, "gRezNum"), str), (typecast("arrow", Key)))
            self.gAvailRezSlots -= 1
            self.gNeededArrows -= 1

    def handleNodeDuplicated(self, _existing_key: Key, _node_key: Key, _node_id: str) -> None:
        _gen_node_id: str = self.generateLogicalID()
        self.builtin_funcs.llRegionSayTo(_existing_key, (typecast(-21461419, int)), radd(self.gOwnLogicalID, radd(":", radd(_gen_node_id, "node_reset:"))))
        _node_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(_node_id, list))
        _node_key_idx: int = neg(bitnot(_node_idx))
        self.gNodes = self.builtin_funcs.llListReplaceList(self.gNodes, typecast(self.compressKey(_node_key), list), _node_key_idx, _node_key_idx)
        self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(typecast(_node_key, str), radd(":", radd(_node_id, "arrow_node_identity:"))))
        self.trackNode(_gen_node_id, _existing_key)
        self.addRelation(_gen_node_id, _node_id)
        self.addRelation(_node_id, _gen_node_id)

    def handleNodeRenamed(self, _existing_id: str, _node_key: Key, _node_id: str) -> None:
        self.untrackNode(_existing_id, 1)
        self.trackNode(_node_id, _node_key)

    def edefaultstate_entry(self) -> None:
        self.restoreLogicalID(1)
        self.gMenuChannel = rbitxor(self.builtin_funcs.llHash(self.builtin_funcs.llGetObjectDesc()), (typecast(-21461421, int)))
        self.gConnectionMenuChannel = rbitxor(self.builtin_funcs.llHash(self.builtin_funcs.llGetObjectDesc()), (typecast(-21461422, int)))
        self.builtin_funcs.llListen((typecast(-21461420, int)), "", typecast("", Key), "")
        self.builtin_funcs.llListen((typecast(-21461423, int)), "", typecast("", Key), "")
        self.builtin_funcs.llListen(self.gMenuChannel, "", typecast("", Key), "")
        self.builtin_funcs.llListen(self.gConnectionMenuChannel, "", typecast("", Key), "")
        self.builtin_funcs.llSetColor(Vector(((1.0), (0.0), (1.0))), (typecast(-1, int)))
        self.clearAll()
        self.builtin_funcs.llSetTimerEvent(1.0)

    def edefaulton_rez(self, _start_param: int) -> None:
        self.builtin_funcs.llResetScript()

    def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(boolnot((rbitor(req((typecast(-21461423, int)), _channel), req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(_id)))))):
            return
        _params: list = self.builtin_funcs.llParseStringKeepNulls(_msg, typecast(":", list), [])
        _cmd: str = self.builtin_funcs.llList2String(_params, 0)
        _params = self.builtin_funcs.llDeleteSubList(_params, 0, 0)
        if cond(rbitxor((typecast(-21461420, int)), _channel)):
            if cond(rbitxor(self.gMenuChannel, _channel)):
                if cond(rbitxor(self.gConnectionMenuChannel, _channel)):
                    if cond(req((typecast(-21461423, int)), _channel)):
                        _num: int = 0
                        if cond(req("find_path", _cmd)):
                            _num = 1000
                        else:
                            if cond(req("find_path_vectors", _cmd)):
                                _num = 1001
                            else:
                                return
                        if cond(rbitor(boolnot((req(self.gOwnLogicalID, self.builtin_funcs.llList2String(_params, 0)))), req("", self.gOwnLogicalID))):
                            return
                        _link_msg: str = radd(self.builtin_funcs.llList2String(_params, 2), radd(":", self.builtin_funcs.llList2String(_params, 1)))
                        self.builtin_funcs.llMessageLinked((typecast(-4, int)), _num, _link_msg, _id)
                else:
                    if cond(req("remove", _msg)):
                        self.removeRelation(self.gFirstClicked, self.gSecondClicked)
                        self.removeRelation(self.gSecondClicked, self.gFirstClicked)
                        self.gGraphDirty = 1
                    else:
                        if cond(req("one-way", _msg)):
                            self.addRelation(self.gFirstClicked, self.gSecondClicked)
                            self.removeRelation(self.gSecondClicked, self.gFirstClicked)
                            self.gGraphDirty = 1
                        else:
                            if cond(req("two-way", _msg)):
                                self.addRelation(self.gFirstClicked, self.gSecondClicked)
                                self.addRelation(self.gSecondClicked, self.gFirstClicked)
                                self.gGraphDirty = 1
                            else:
                                if cond(req("find path", _msg)):
                                    if cond(self.gGraphDirty):
                                        self.builtin_funcs.llOwnerSay("Refusing to find path, graph is dirty")
                                    else:
                                        self.builtin_funcs.llOwnerSay(radd(self.gSecondClicked, radd(" to ", radd(self.gFirstClicked, "Calculating path from "))))
                                        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 1000, radd(self.gSecondClicked, radd(":", self.gFirstClicked)), typecast("00000000-0000-0000-0000-000000000000", Key))
                    self.gFirstClicked = ""
                    self.gSecondClicked = ""
                    self.gClickTimeout = 0
            else:
                if cond(req("dump", _msg)):
                    self.dumpNodeDetails()
                else:
                    if cond(req("save", _msg)):
                        if cond(rneq([], self.gNodes)):
                            self.saveNodes()
                        else:
                            self.builtin_funcs.llOwnerSay("Refusing to save empty node list")
                    else:
                        if cond(req("restore", _msg)):
                            self.initRestoreNodes(1)
                        else:
                            if cond(req("rest. norel", _msg)):
                                self.initRestoreNodes(0)
                            else:
                                if cond(req("clear", _msg)):
                                    self.clearAll()
                                    self.builtin_funcs.llResetScript()
        else:
            _node_key: Key = _id
            if cond(req("node_alive", _cmd)):
                _parent_id: str = self.builtin_funcs.llList2String(_params, 1)
                if cond(boolnot((rbitor(req(self.gOwnLogicalID, _parent_id), req("", _parent_id))))):
                    return
                _node_id: str = self.builtin_funcs.llList2String(_params, 0)
                _existing_id: str = self.nodeKeyToID(_node_key)
                _existing_key: Key = self.nodeIDToKey(_node_id)
                if cond(rbitand(req("00000000-0000-0000-0000-000000000000", _existing_key), req("", _existing_id))):
                    self.trackNode(_node_id, _node_key)
                    self.builtin_funcs.llRegionSayTo(_node_key, (typecast(-21461419, int)), radd(self.gOwnLogicalID, radd(":", radd(_node_id, "node_reset:"))))
                    self.gGraphDirty = 1
                else:
                    if cond(rbitor(req(_node_id, _existing_id), req("", _existing_id))):
                        if cond(boolnot((req(_node_key, _existing_key)))):
                            self.handleNodeDuplicated(_existing_key, _node_key, _node_id)
                            self.gGraphDirty = 1
                    else:
                        self.builtin_funcs.llOwnerSay(radd(_existing_id, radd(" != ", radd(_node_id, radd(" had mismatch, ", radd(typecast(_node_key, str), "node hello from "))))))
                        self.handleNodeRenamed(_existing_id, _node_key, _node_id)
                        self.gGraphDirty = 1
            else:
                if cond(req("node_touched", _cmd)):
                    _clicked_id: str = self.nodeKeyToID(_node_key)
                    if cond(req("", _clicked_id)):
                        return
                    if cond(boolnot((req(self.gOwnLogicalID, self.builtin_funcs.llList2String(_params, 0))))):
                        return
                    _toucher_id: Key = self.builtin_funcs.llList2Key(_params, 1)
                    if cond(boolnot((req(self.builtin_funcs.llGetOwner(), _toucher_id)))):
                        return
                    if cond(rbitor(req("", self.gSecondClicked), req("", self.gFirstClicked))):
                        if cond(req("", self.gFirstClicked)):
                            self.gFirstClicked = _clicked_id
                        else:
                            if cond(boolnot((req(self.gFirstClicked, _clicked_id)))):
                                self.gSecondClicked = _clicked_id
                                self.builtin_funcs.llDialog(_toucher_id, "What do you want to do with the connection?", radd("find path", radd("remove", radd("two-way", typecast("one-way", list)))), self.gConnectionMenuChannel)
                    else:
                        self.gFirstClicked = _clicked_id
                        self.gSecondClicked = ""
                    self.gClickTimeout = radd(self.builtin_funcs.llGetUnixTime(), 20)

    def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(rbitxor(902, _num)):
            if cond(rbitxor(903, _num)):
                if cond(rbitxor(901, _num)):
                    if cond(req(1003, _num)):
                        if cond(_id):
                            self.builtin_funcs.llRegionSayTo(_id, (typecast(-21461424, int)), radd(_str, "path:"))
                        else:
                            self.builtin_funcs.llOwnerSay("PATH:")
                            self.builtin_funcs.llOwnerSay(_str)
                else:
                    if cond(boolnot(self.gRestoreArrows)):
                        self.gNeededArrows = 0
                        self.gNodeRelations = self.gPendingRelations
                        self.gPendingRelations = []
                    self.builtin_funcs.llOwnerSay("Got data from data manager, rezzing...")
                    self.tryRezPending()
                    self.gGraphDirty = 0
            else:
                self.gPendingRelations = radd((rbitor(self.builtin_funcs.llListFindList(self.gPendingNodes, typecast(typecast(_id, str), list)), rmul(65536, self.builtin_funcs.llListFindList(self.gPendingNodes, typecast(_str, list))))), self.gPendingRelations)
                self.gNeededArrows += 1
        else:
            self.gPendingNodes = radd(typecast(typecast(_id, str), Vector), radd(_str, self.gPendingNodes))
            self.gNeededNodes += 1

    def edefaultobject_rez(self, _id: Key) -> None:
        self.gLastRezTime = self.builtin_funcs.llGetUnixTime()
        self.gAvailRezSlots += 1
        if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(_id))))):
            self.builtin_funcs.llOwnerSay("Failed a rez?")
            return
        _name: str = typecast(self.builtin_funcs.llGetObjectDetails(_id, typecast(1, list)), str)
        if cond(req("node", _name)):
            if cond(req([], self.gPendingNodes)):
                self.builtin_funcs.llOwnerSay("Rezzed node with no pending nodes???")
                return
            _node_id: str = self.builtin_funcs.llList2String(self.gPendingNodes, 0)
            _node_pos: Vector = self.builtin_funcs.llList2Vector(self.gPendingNodes, 1)
            self.builtin_funcs.llRegionSayTo(_id, (typecast(-21461419, int)), radd(typecast(_node_pos, str), radd(":", radd(self.gOwnLogicalID, radd(":", radd(_node_id, "node_assign:"))))))
            self.gPendingNodes = self.builtin_funcs.llDeleteSubList(self.gPendingNodes, 0, 1)
            self.trackNode(_node_id, _id)
        else:
            if cond(req("arrow", _name)):
                if cond(req([], self.gPendingRelations)):
                    self.builtin_funcs.llOwnerSay("Rezzed arrow with no pending relations???")
                    return
                self.gArrowPool = radd(_id, self.gArrowPool)
                self.updateNodeRelations()
        if cond(rbitor(rneq([], self.gPendingRelations), rbitor(rneq([], self.gPendingNodes), rbitor(self.gNeededNodes, self.gNeededArrows)))):
            self.tryRezPending()
        else:
            if cond(self.gRestoring):
                self.gRestoring = 0
                self.builtin_funcs.llOwnerSay("Done rez")

    def edefaulttouch_start(self, _touch_num: int) -> None:
        if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llDetectedKey(0))))):
            return
        self.builtin_funcs.llDialog(self.builtin_funcs.llDetectedKey(0), "Node Management", radd("clear", radd("rest. norel", radd("restore", radd("save", typecast("dump", list))))), self.gMenuChannel)

    def edefaulttimer(self) -> None:
        self.gTickCount += 1
        if cond(boolnot((req(radd(":", self.gOwnLogicalID), self.builtin_funcs.llGetObjectDesc())))):
            if cond(boolnot((req("", self.gOwnLogicalID)))):
                self.clearAll()
            self.builtin_funcs.llResetScript()
        if cond(rbitand(neg((rless(self.builtin_funcs.llGetUnixTime(), self.gClickTimeout))), self.gClickTimeout)):
            self.gFirstClicked = ""
            self.gSecondClicked = ""
            self.gClickTimeout = 0
        if cond(boolnot((rmod(5, self.gTickCount)))):
            self.pruneNodes()
        if cond(rbitor(self.gNeededNodes, self.gNeededArrows)):
            if cond(rless(self.builtin_funcs.llGetUnixTime(), radd(self.gLastRezTime, 10))):
                self.gNeededNodes = 0
                self.gNeededArrows = 0
                self.gRestoring = 0
                self.builtin_funcs.llOwnerSay("Restore got stuck, inconsistent state! Is the parcel full?")
        self.updateNodeRelations()

