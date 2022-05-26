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

    def restoreLogicalID(self, create: int) -> None:
        desc: str = self.builtin_funcs.llGetObjectDesc()
        if cond(bitnot(self.builtin_funcs.llSubStringIndex(desc, ":"))):
            parsed: list = self.builtin_funcs.llParseString2List(desc, typecast(":", list), [])
            self.gOwnLogicalID = self.builtin_funcs.llList2String(parsed, 0)
            self.gParentLogicalID = self.builtin_funcs.llList2String(parsed, 1)
        else:
            if cond(create):
                self.gOwnLogicalID = self.generateLogicalID()
                self.gParentLogicalID = ""
                self.builtin_funcs.llSetObjectDesc(self.generateDescription())

    def generateDescription(self) -> str:
        return radd(self.gParentLogicalID, radd(":", self.gOwnLogicalID))

    def strReplace(self, subject: str, search: str, replace: str) -> str:
        return self.builtin_funcs.llDumpList2String(self.builtin_funcs.llParseStringKeepNulls(subject, typecast(search, list), []), replace)

    def compressKey(self, k: Key) -> str:
        s: str = self.builtin_funcs.llToLower(radd("0", self.strReplace(typecast(k, str), "-", "")))
        ret: str = ""
        i: int = 0
        A: str = ""
        B: str = ""
        C: str = ""
        D: str = ""
        i = 0
        while True == True:
            if not cond(rless(32, i)):
                break
            A = self.builtin_funcs.llGetSubString(s, i, i)
            i += 1
            B = self.builtin_funcs.llGetSubString(s, i, i)
            i += 1
            C = self.builtin_funcs.llGetSubString(s, i, i)
            i += 1
            D = "b"
            if cond(req("0", A)):
                A = "e"
                D = "8"
            else:
                if cond(req("d", A)):
                    A = "e"
                    D = "9"
                else:
                    if cond(req("f", A)):
                        A = "e"
                        D = "a"
            ret = radd((radd(C, radd("%b", radd(B, radd(D, radd("%", radd(A, "%e"))))))), ret)
        return self.builtin_funcs.llUnescapeURL(ret)

    def padDash(self, s: str) -> str:
        return radd(self.builtin_funcs.llGetSubString(s, 20, 31), radd("-", radd(self.builtin_funcs.llGetSubString(s, 16, 19), radd("-", radd(self.builtin_funcs.llGetSubString(s, 12, 15), radd("-", radd(self.builtin_funcs.llGetSubString(s, 8, 11), radd("-", self.builtin_funcs.llGetSubString(s, 0, 7)))))))))

    def uncompressKey(self, s: str) -> Key:
        i: int = 0
        ret: str = ""
        A: str = ""
        B: str = ""
        C: str = ""
        D: str = ""
        s = self.builtin_funcs.llToLower(self.builtin_funcs.llEscapeURL(s))
        i = 0
        while True == True:
            if not cond(rless(99, i)):
                break
            A = self.builtin_funcs.llGetSubString(s, neg(bitnot(neg(bitnot(i)))), neg(bitnot(neg(bitnot(i)))))
            B = self.builtin_funcs.llGetSubString(s, radd(i, 5), radd(i, 5))
            C = self.builtin_funcs.llGetSubString(s, radd(i, 8), radd(i, 8))
            D = self.builtin_funcs.llGetSubString(s, radd(i, 4), radd(i, 4))
            if cond(req("8", D)):
                A = "0"
            else:
                if cond(req("9", D)):
                    A = "d"
                else:
                    if cond(req("a", D)):
                        A = "f"
            ret = radd(C, radd(B, radd(A, ret)))
            i = radd(i, 9)
        return typecast(self.padDash(ret), Key)

    def generateLogicalID(self) -> str:
        return self.builtin_funcs.llGetSubString(self.builtin_funcs.llStringToBase64(self.compressKey(self.builtin_funcs.llGenerateKey())), 0, 5)

    def nodeIDToKey(self, node_id: str) -> Key:
        idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(node_id, list))
        if cond(boolnot(bitnot(idx))):
            return typecast("00000000-0000-0000-0000-000000000000", Key)
        return self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(idx))))

    def nodeKeyToID(self, id: Key) -> str:
        idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(self.compressKey(id), list))
        if cond(boolnot(bitnot(idx))):
            return ""
        return self.builtin_funcs.llList2String(self.gNodes, bitnot(neg(idx)))

    def dumpNodeDetails(self) -> None:
        i: int = 0
        len: int = rneq([], self.gNodes)
        self.builtin_funcs.llOwnerSay("gNodes:")
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            self.builtin_funcs.llOwnerSay(radd(typecast(self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(i)))), str), radd(": ", self.builtin_funcs.llList2String(self.gNodes, i))))
            i = neg(bitnot(neg(bitnot(i))))
        len = rneq([], self.gPendingNodes)
        self.builtin_funcs.llOwnerSay("gPendingNodes:")
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            self.builtin_funcs.llOwnerSay(radd(self.builtin_funcs.llList2String(self.gPendingNodes, neg(bitnot(i))), radd(": ", self.builtin_funcs.llList2String(self.gPendingNodes, i))))
            i = neg(bitnot(neg(bitnot(i))))
        len = rneq([], self.gNodeRelations)
        self.builtin_funcs.llOwnerSay("NODE RELATIONS:")
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, i)
            self.builtin_funcs.llOwnerSay(radd(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, rel)), radd(": ", self.builtin_funcs.llList2String(self.gNodes, rshr(16, rel)))))
            i += 1
        len = rneq([], self.gPendingRelations)
        self.builtin_funcs.llOwnerSay("PENDING NODE RELATIONS:")
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            rel: int = self.builtin_funcs.llList2Integer(self.gPendingRelations, i)
            self.builtin_funcs.llOwnerSay(radd(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, rel)), radd(": ", self.builtin_funcs.llList2String(self.gNodes, rshr(16, rel)))))
            i += 1
        self.builtin_funcs.llOwnerSay(radd(typecast(self.builtin_funcs.llGetFreeMemory(), str), "Free Memory: "))

    def trackNode(self, node_id: str, node_key: Key) -> None:
        self.gNodes = radd([node_id, self.compressKey(node_key)], self.gNodes)

    def untrackNode(self, node_id: str, kill_relations: int) -> None:
        node_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(node_id, list))
        if cond(boolnot(bitnot(node_idx))):
            return
        if cond(kill_relations):
            len: int = rneq([], self.gNodeRelations)
            i: int = 0
            i = bitnot(neg(len))
            while True == True:
                if not cond(rless(i, (typecast(-1, int)))):
                    break
                rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, i)
                src_idx: int = rshr(16, rel)
                dst_idx: int = rbitand(65535, rel)
                new_src_idx: int = src_idx
                new_dst_idx: int = dst_idx
                if cond(rless(src_idx, node_idx)):
                    new_src_idx = bitnot(neg(bitnot(neg(new_src_idx))))
                if cond(rless(dst_idx, node_idx)):
                    new_dst_idx = bitnot(neg(bitnot(neg(new_dst_idx))))
                if cond(rbitor(req(node_idx, dst_idx), req(node_idx, src_idx))):
                    src_id: str = self.builtin_funcs.llList2String(self.gNodes, src_idx)
                    dst_id: str = self.builtin_funcs.llList2String(self.gNodes, dst_idx)
                    self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(dst_id, radd(":", radd(src_id, "arrow_kill:"))))
                    self.gNodeRelations = self.builtin_funcs.llDeleteSubList(self.gNodeRelations, i, i)
                else:
                    if cond(rbitor(rbitxor(dst_idx, new_dst_idx), rbitxor(src_idx, new_src_idx))):
                        new_rel: int = rbitor(new_dst_idx, rmul(65536, new_src_idx))
                        self.gNodeRelations = self.builtin_funcs.llListReplaceList(self.gNodeRelations, typecast(new_rel, list), i, i)
                i -= 1
        self.gNodes = self.builtin_funcs.llDeleteSubList(self.gNodes, node_idx, neg(bitnot(node_idx)))

    def pruneNodes(self) -> None:
        len: int = rneq([], self.gNodes)
        i: int = 0
        i = bitnot(neg(bitnot(neg(len))))
        while True == True:
            if not cond(rless(i, (typecast(-1, int)))):
                break
            node_key: Key = self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(i))))
            if cond(req((0.0), self.builtin_funcs.llGetObjectMass(node_key))):
                self.untrackNode(self.builtin_funcs.llList2String(self.gNodes, i), 1)
            i = bitnot(neg(bitnot(neg(i))))

    def saveNodes(self) -> None:
        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 800, "", typecast("00000000-0000-0000-0000-000000000000", Key))
        i: int = 0
        len: int = rneq([], self.gNodes)
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            node_id: str = self.builtin_funcs.llList2String(self.gNodes, i)
            node_key: Key = self.uncompressKey(self.builtin_funcs.llList2String(self.gNodes, neg(bitnot(i))))
            node_pos: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(node_key, typecast(3, list)), 0)
            self.builtin_funcs.llMessageLinked((typecast(-4, int)), 802, node_id, typecast(typecast(node_pos, str), Key))
            if cond(boolnot((rmod(25, i)))):
                self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
            i = neg(bitnot(neg(bitnot(i))))
        len = rneq([], self.gNodeRelations)
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            rel: int = self.builtin_funcs.llList2Integer(self.gNodeRelations, i)
            self.builtin_funcs.llMessageLinked((typecast(-4, int)), 803, self.builtin_funcs.llList2String(self.gNodes, rshr(16, rel)), typecast(self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, rel)), Key))
            if cond(boolnot((rmod(25, i)))):
                self.builtin_funcs.llSleep(bin2float('0.500000', '0000003f'))
            i += 1
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

    def initRestoreNodes(self, restore_arrows: int) -> None:
        self.clearAll()
        self.gRestoring = 1
        self.gRestoreArrows = restore_arrows
        self.gLastRezTime = self.builtin_funcs.llGetUnixTime()
        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 900, "", typecast("00000000-0000-0000-0000-000000000000", Key))

    def addRelation(self, src: str, dst: str) -> None:
        rel: list = typecast(rbitor(self.builtin_funcs.llListFindList(self.gNodes, typecast(dst, list)), rmul(65536, self.builtin_funcs.llListFindList(self.gNodes, typecast(src, list)))), list)
        if cond(boolnot(bitnot(self.builtin_funcs.llListFindList(self.gNodeRelations, rel)))):
            self.gPendingRelations = radd(rel, self.gPendingRelations)
            self.gNeededArrows += 1
            self.tryRezPending()

    def removeRelation(self, src: str, dst: str) -> None:
        rel: list = typecast(rbitor(self.builtin_funcs.llListFindList(self.gNodes, typecast(dst, list)), rmul(65536, self.builtin_funcs.llListFindList(self.gNodes, typecast(src, list)))), list)
        idx: int = self.builtin_funcs.llListFindList(self.gNodeRelations, rel)
        if cond(bitnot(idx)):
            self.gNodeRelations = self.builtin_funcs.llDeleteSubList(self.gNodeRelations, idx, idx)
        self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(dst, radd(":", radd(src, "arrow_kill:"))))

    def updateNodeRelations(self) -> None:
        if cond(req([], self.gPendingRelations)):
            return
        i: int = 0
        len: int = rneq([], self.gPendingRelations)
        i = bitnot(neg(len))
        while True == True:
            if not cond(rless(i, (typecast(-1, int)))):
                break
            if cond(req([], self.gArrowPool)):
                return
            rel: int = self.builtin_funcs.llList2Integer(self.gPendingRelations, i)
            src_id: str = self.builtin_funcs.llList2String(self.gNodes, rshr(16, rel))
            dst_id: str = self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, rel))
            src_key: str = typecast(self.nodeIDToKey(src_id), str)
            dst_key: str = typecast(self.nodeIDToKey(dst_id), str)
            if cond(boolnot((rbitor(req("00000000-0000-0000-0000-000000000000", dst_key), req("00000000-0000-0000-0000-000000000000", src_key))))):
                msg: str = radd((radd((radd((radd((radd((radd((radd((radd((radd(self.gOwnLogicalID, ":")), dst_key)), ":")), dst_id)), ":")), src_key)), ":")), src_id)), "arrow_add:")
                self.builtin_funcs.llRegionSayTo(self.builtin_funcs.llList2Key(self.gArrowPool, 0), (typecast(-21461419, int)), msg)
                self.gPendingRelations = self.builtin_funcs.llDeleteSubList(self.gPendingRelations, i, i)
                self.gArrowPool = self.builtin_funcs.llDeleteSubList(self.gArrowPool, 0, 0)
                self.gNodeRelations = radd(rel, self.gNodeRelations)
            i -= 1

    def tryRezPending(self) -> None:
        while cond(rbitand(rless(self.gAvailRezSlots, 0), rless(self.gNeededNodes, 0))):
            self.builtin_funcs.llMessageLinked((typecast(-1, int)), 1100, typecast(preincr(self.__dict__, "gRezNum"), str), (typecast("node", Key)))
            self.gAvailRezSlots -= 1
            self.gNeededNodes -= 1
        while cond(rbitand(rless(self.gAvailRezSlots, 0), rless(self.gNeededArrows, 0))):
            self.builtin_funcs.llMessageLinked((typecast(-1, int)), 1100, typecast(preincr(self.__dict__, "gRezNum"), str), (typecast("arrow", Key)))
            self.gAvailRezSlots -= 1
            self.gNeededArrows -= 1

    def handleNodeDuplicated(self, existing_key: Key, node_key: Key, node_id: str) -> None:
        gen_node_id: str = self.generateLogicalID()
        self.builtin_funcs.llRegionSayTo(existing_key, (typecast(-21461419, int)), radd(self.gOwnLogicalID, radd(":", radd(gen_node_id, "node_reset:"))))
        node_idx: int = self.builtin_funcs.llListFindList(self.gNodes, typecast(node_id, list))
        node_key_idx: int = neg(bitnot(node_idx))
        self.gNodes = self.builtin_funcs.llListReplaceList(self.gNodes, typecast(self.compressKey(node_key), list), node_key_idx, node_key_idx)
        self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(typecast(node_key, str), radd(":", radd(node_id, "arrow_node_identity:"))))
        self.trackNode(gen_node_id, existing_key)
        self.addRelation(gen_node_id, node_id)
        self.addRelation(node_id, gen_node_id)

    def handleNodeRenamed(self, existing_id: str, node_key: Key, node_id: str) -> None:
        self.untrackNode(existing_id, 1)
        self.trackNode(node_id, node_key)

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

    def edefaulton_rez(self, start_param: int) -> None:
        self.builtin_funcs.llResetScript()

    def edefaultlisten(self, channel: int, name: str, id: Key, msg: str) -> None:
        if cond(boolnot((rbitor(req((typecast(-21461423, int)), channel), req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(id)))))):
            return
        params: list = self.builtin_funcs.llParseStringKeepNulls(msg, typecast(":", list), [])
        cmd: str = self.builtin_funcs.llList2String(params, 0)
        params = self.builtin_funcs.llDeleteSubList(params, 0, 0)
        if cond(rbitxor((typecast(-21461420, int)), channel)):
            if cond(rbitxor(self.gMenuChannel, channel)):
                if cond(rbitxor(self.gConnectionMenuChannel, channel)):
                    if cond(req((typecast(-21461423, int)), channel)):
                        num: int = 0
                        if cond(req("find_path", cmd)):
                            num = 1000
                        else:
                            if cond(req("find_path_vectors", cmd)):
                                num = 1001
                            else:
                                return
                        if cond(rbitor(boolnot((req(self.gOwnLogicalID, self.builtin_funcs.llList2String(params, 0)))), req("", self.gOwnLogicalID))):
                            return
                        link_msg: str = radd(self.builtin_funcs.llList2String(params, 2), radd(":", self.builtin_funcs.llList2String(params, 1)))
                        self.builtin_funcs.llMessageLinked((typecast(-4, int)), num, link_msg, id)
                else:
                    if cond(req("remove", msg)):
                        self.removeRelation(self.gFirstClicked, self.gSecondClicked)
                        self.removeRelation(self.gSecondClicked, self.gFirstClicked)
                        self.gGraphDirty = 1
                    else:
                        if cond(req("one-way", msg)):
                            self.addRelation(self.gFirstClicked, self.gSecondClicked)
                            self.removeRelation(self.gSecondClicked, self.gFirstClicked)
                            self.gGraphDirty = 1
                        else:
                            if cond(req("two-way", msg)):
                                self.addRelation(self.gFirstClicked, self.gSecondClicked)
                                self.addRelation(self.gSecondClicked, self.gFirstClicked)
                                self.gGraphDirty = 1
                            else:
                                if cond(req("find path", msg)):
                                    if cond(self.gGraphDirty):
                                        self.builtin_funcs.llOwnerSay("Refusing to find path, graph is dirty")
                                    else:
                                        self.builtin_funcs.llOwnerSay(radd(self.gSecondClicked, radd(" to ", radd(self.gFirstClicked, "Calculating path from "))))
                                        self.builtin_funcs.llMessageLinked((typecast(-4, int)), 1000, radd(self.gSecondClicked, radd(":", self.gFirstClicked)), typecast("00000000-0000-0000-0000-000000000000", Key))
                    self.gFirstClicked = ""
                    self.gSecondClicked = ""
                    self.gClickTimeout = 0
            else:
                if cond(req("dump", msg)):
                    self.dumpNodeDetails()
                else:
                    if cond(req("save", msg)):
                        if cond(rneq([], self.gNodes)):
                            self.saveNodes()
                        else:
                            self.builtin_funcs.llOwnerSay("Refusing to save empty node list")
                    else:
                        if cond(req("restore", msg)):
                            self.initRestoreNodes(1)
                        else:
                            if cond(req("rest. norel", msg)):
                                self.initRestoreNodes(0)
                            else:
                                if cond(req("clear", msg)):
                                    self.clearAll()
                                    self.builtin_funcs.llResetScript()
        else:
            node_key: Key = id
            if cond(req("node_alive", cmd)):
                parent_id: str = self.builtin_funcs.llList2String(params, 1)
                if cond(boolnot((rbitor(req(self.gOwnLogicalID, parent_id), req("", parent_id))))):
                    return
                node_id: str = self.builtin_funcs.llList2String(params, 0)
                existing_id: str = self.nodeKeyToID(node_key)
                existing_key: Key = self.nodeIDToKey(node_id)
                if cond(rbitand(req("00000000-0000-0000-0000-000000000000", existing_key), req("", existing_id))):
                    self.trackNode(node_id, node_key)
                    self.builtin_funcs.llRegionSayTo(node_key, (typecast(-21461419, int)), radd(self.gOwnLogicalID, radd(":", radd(node_id, "node_reset:"))))
                    self.gGraphDirty = 1
                else:
                    if cond(rbitor(req(node_id, existing_id), req("", existing_id))):
                        if cond(boolnot((req(node_key, existing_key)))):
                            self.handleNodeDuplicated(existing_key, node_key, node_id)
                            self.gGraphDirty = 1
                    else:
                        self.builtin_funcs.llOwnerSay(radd(existing_id, radd(" != ", radd(node_id, radd(" had mismatch, ", radd(typecast(node_key, str), "node hello from "))))))
                        self.handleNodeRenamed(existing_id, node_key, node_id)
                        self.gGraphDirty = 1
            else:
                if cond(req("node_touched", cmd)):
                    clicked_id: str = self.nodeKeyToID(node_key)
                    if cond(req("", clicked_id)):
                        return
                    if cond(boolnot((req(self.gOwnLogicalID, self.builtin_funcs.llList2String(params, 0))))):
                        return
                    toucher_id: Key = self.builtin_funcs.llList2Key(params, 1)
                    if cond(boolnot((req(self.builtin_funcs.llGetOwner(), toucher_id)))):
                        return
                    if cond(rbitor(req("", self.gSecondClicked), req("", self.gFirstClicked))):
                        if cond(req("", self.gFirstClicked)):
                            self.gFirstClicked = clicked_id
                        else:
                            if cond(boolnot((req(self.gFirstClicked, clicked_id)))):
                                self.gSecondClicked = clicked_id
                                self.builtin_funcs.llDialog(toucher_id, "What do you want to do with the connection?", radd("find path", radd("remove", radd("two-way", typecast("one-way", list)))), self.gConnectionMenuChannel)
                    else:
                        self.gFirstClicked = clicked_id
                        self.gSecondClicked = ""
                    self.gClickTimeout = radd(self.builtin_funcs.llGetUnixTime(), 20)

    def edefaultlink_message(self, sender_num: int, num: int, str: str, id: Key) -> None:
        if cond(rbitxor(902, num)):
            if cond(rbitxor(903, num)):
                if cond(rbitxor(901, num)):
                    if cond(req(1003, num)):
                        if cond(id):
                            self.builtin_funcs.llRegionSayTo(id, (typecast(-21461424, int)), radd(str, "path:"))
                        else:
                            self.builtin_funcs.llOwnerSay("PATH:")
                            self.builtin_funcs.llOwnerSay(str)
                else:
                    if cond(boolnot(self.gRestoreArrows)):
                        self.gNeededArrows = 0
                        self.gNodeRelations = self.gPendingRelations
                        self.gPendingRelations = []
                    self.builtin_funcs.llOwnerSay("Got data from data manager, rezzing...")
                    self.tryRezPending()
                    self.gGraphDirty = 0
            else:
                self.gPendingRelations = radd((rbitor(self.builtin_funcs.llListFindList(self.gPendingNodes, typecast(typecast(id, str), list)), rmul(65536, self.builtin_funcs.llListFindList(self.gPendingNodes, typecast(str, list))))), self.gPendingRelations)
                self.gNeededArrows += 1
        else:
            self.gPendingNodes = radd(typecast(typecast(id, str), Vector), radd(str, self.gPendingNodes))
            self.gNeededNodes += 1

    def edefaultobject_rez(self, id: Key) -> None:
        self.gLastRezTime = self.builtin_funcs.llGetUnixTime()
        self.gAvailRezSlots += 1
        if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(id))))):
            self.builtin_funcs.llOwnerSay("Failed a rez?")
            return
        name: str = typecast(self.builtin_funcs.llGetObjectDetails(id, typecast(1, list)), str)
        if cond(req("node", name)):
            if cond(req([], self.gPendingNodes)):
                self.builtin_funcs.llOwnerSay("Rezzed node with no pending nodes???")
                return
            node_id: str = self.builtin_funcs.llList2String(self.gPendingNodes, 0)
            node_pos: Vector = self.builtin_funcs.llList2Vector(self.gPendingNodes, 1)
            self.builtin_funcs.llRegionSayTo(id, (typecast(-21461419, int)), radd(typecast(node_pos, str), radd(":", radd(self.gOwnLogicalID, radd(":", radd(node_id, "node_assign:"))))))
            self.gPendingNodes = self.builtin_funcs.llDeleteSubList(self.gPendingNodes, 0, 1)
            self.trackNode(node_id, id)
        else:
            if cond(req("arrow", name)):
                if cond(req([], self.gPendingRelations)):
                    self.builtin_funcs.llOwnerSay("Rezzed arrow with no pending relations???")
                    return
                self.gArrowPool = radd(id, self.gArrowPool)
                self.updateNodeRelations()
        if cond(rbitor(rneq([], self.gPendingRelations), rbitor(rneq([], self.gPendingNodes), rbitor(self.gNeededNodes, self.gNeededArrows)))):
            self.tryRezPending()
        else:
            if cond(self.gRestoring):
                self.gRestoring = 0
                self.builtin_funcs.llOwnerSay("Done rez")

    def edefaulttouch_start(self, touch_num: int) -> None:
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

