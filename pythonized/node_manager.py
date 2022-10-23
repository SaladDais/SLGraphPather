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

    async def restoreLogicalID(self, _create: int) -> None:
        _desc: str = await self.builtin_funcs.llGetObjectDesc()
        if cond(rneq(-1, await self.builtin_funcs.llSubStringIndex(_desc, ":"))):
            _parsed: list = await self.builtin_funcs.llParseString2List(_desc, [":"], [])
            self.gOwnLogicalID = await self.builtin_funcs.llList2String(_parsed, 0)
            self.gParentLogicalID = await self.builtin_funcs.llList2String(_parsed, 1)
        elif cond(_create):
            self.gOwnLogicalID = await self.generateLogicalID()
            self.gParentLogicalID = ""
            await self.builtin_funcs.llSetObjectDesc(await self.generateDescription())

    async def generateDescription(self) -> str:
        return radd(self.gParentLogicalID, radd(":", self.gOwnLogicalID))

    async def strReplace(self, _subject: str, _search: str, _replace: str) -> str:
        return await self.builtin_funcs.llDumpList2String(await self.builtin_funcs.llParseStringKeepNulls(_subject, [_search], []), _replace)

    async def compressKey(self, _k: Key) -> str:
        _s: str = await self.builtin_funcs.llToLower(radd("0", await self.strReplace(typecast(_k, str), "-", "")))
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
            _A = await self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _B = await self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _C = await self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _D = "b"
            if cond(req("0", _A)):
                _A = "e"
                _D = "8"
            elif cond(req("d", _A)):
                _A = "e"
                _D = "9"
            elif cond(req("f", _A)):
                _A = "e"
                _D = "a"
            _ret = radd(radd(_C, radd("%b", radd(_B, radd(_D, radd("%", radd(_A, "%e")))))), _ret)
            0
        return await self.builtin_funcs.llUnescapeURL(_ret)

    async def padDash(self, _s: str) -> str:
        return radd(await self.builtin_funcs.llGetSubString(_s, 20, 31), radd("-", radd(await self.builtin_funcs.llGetSubString(_s, 16, 19), radd("-", radd(await self.builtin_funcs.llGetSubString(_s, 12, 15), radd("-", radd(await self.builtin_funcs.llGetSubString(_s, 8, 11), radd("-", await self.builtin_funcs.llGetSubString(_s, 0, 7)))))))))

    async def uncompressKey(self, _s: str) -> Key:
        _i: int = 0
        _ret: str = ""
        _A: str = ""
        _B: str = ""
        _C: str = ""
        _D: str = ""
        _s = await self.builtin_funcs.llToLower(await self.builtin_funcs.llEscapeURL(_s))
        _i = 0
        while True == True:
            if not cond(rless(99, _i)):
                break
            _A = await self.builtin_funcs.llGetSubString(_s, radd(2, _i), radd(2, _i))
            _B = await self.builtin_funcs.llGetSubString(_s, radd(5, _i), radd(5, _i))
            _C = await self.builtin_funcs.llGetSubString(_s, radd(8, _i), radd(8, _i))
            _D = await self.builtin_funcs.llGetSubString(_s, radd(4, _i), radd(4, _i))
            if cond(req("8", _D)):
                _A = "0"
            elif cond(req("9", _D)):
                _A = "d"
            elif cond(req("a", _D)):
                _A = "f"
            _ret = radd(_C, radd(_B, radd(_A, _ret)))
            _i = radd(9, _i)
        return typecast(await self.padDash(_ret), Key)

    async def generateLogicalID(self) -> str:
        return await self.builtin_funcs.llGetSubString(await self.builtin_funcs.llStringToBase64(await self.compressKey(await self.builtin_funcs.llGenerateKey())), 0, 5)

    async def nodeIDToKey(self, _node_id: str) -> Key:
        _idx: int = await self.builtin_funcs.llListFindList(self.gNodes, [_node_id])
        if cond(req(-1, _idx)):
            return typecast("00000000-0000-0000-0000-000000000000", Key)
        return await self.uncompressKey(await self.builtin_funcs.llList2String(self.gNodes, radd(1, _idx)))

    async def nodeKeyToID(self, _id: Key) -> str:
        _idx: int = await self.builtin_funcs.llListFindList(self.gNodes, [await self.compressKey(_id)])
        if cond(req(-1, _idx)):
            return ""
        return await self.builtin_funcs.llList2String(self.gNodes, rsub(1, _idx))

    async def dumpNodeDetails(self) -> None:
        _i: int = 0
        _len: int = await self.builtin_funcs.llGetListLength(self.gNodes)
        await self.builtin_funcs.llOwnerSay("gNodes:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            await self.builtin_funcs.llOwnerSay(radd(typecast(await self.uncompressKey(await self.builtin_funcs.llList2String(self.gNodes, radd(1, _i))), str), radd(": ", await self.builtin_funcs.llList2String(self.gNodes, radd(0, _i)))))
            _i = radd(2, _i)
        _len = await self.builtin_funcs.llGetListLength(self.gPendingNodes)
        await self.builtin_funcs.llOwnerSay("gPendingNodes:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            await self.builtin_funcs.llOwnerSay(radd(await self.builtin_funcs.llList2String(self.gPendingNodes, radd(1, _i)), radd(": ", await self.builtin_funcs.llList2String(self.gPendingNodes, radd(0, _i)))))
            _i = radd(2, _i)
        _len = await self.builtin_funcs.llGetListLength(self.gNodeRelations)
        await self.builtin_funcs.llOwnerSay("NODE RELATIONS:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = await self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
            await self.builtin_funcs.llOwnerSay(radd(await self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), radd(": ", await self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)))))
            _i += 1
        _len = await self.builtin_funcs.llGetListLength(self.gPendingRelations)
        await self.builtin_funcs.llOwnerSay("PENDING NODE RELATIONS:")
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = await self.builtin_funcs.llList2Integer(self.gPendingRelations, _i)
            await self.builtin_funcs.llOwnerSay(radd(await self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), radd(": ", await self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)))))
            _i += 1
        await self.builtin_funcs.llOwnerSay(radd(typecast(await self.builtin_funcs.llGetFreeMemory(), str), "Free Memory: "))

    async def trackNode(self, _node_id: str, _node_key: Key) -> None:
        self.gNodes = radd([_node_id, await self.compressKey(_node_key)], self.gNodes)

    async def untrackNode(self, _node_id: str, _kill_relations: int) -> None:
        _node_idx: int = await self.builtin_funcs.llListFindList(self.gNodes, [_node_id])
        if cond(req(-1, _node_idx)):
            return
        if cond(_kill_relations):
            _len: int = await self.builtin_funcs.llGetListLength(self.gNodeRelations)
            _i: int = 0
            _i = rsub(1, _len)
            while True == True:
                if not cond(rgeq(0, _i)):
                    break
                _rel: int = await self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
                _src_idx: int = rshr(16, _rel)
                _dst_idx: int = rbitand(65535, _rel)
                _new_src_idx: int = _src_idx
                _new_dst_idx: int = _dst_idx
                if cond(rgreater(_node_idx, _src_idx)):
                    _new_src_idx = rsub(2, _new_src_idx)
                if cond(rgreater(_node_idx, _dst_idx)):
                    _new_dst_idx = rsub(2, _new_dst_idx)
                if cond(rboolor(req(_node_idx, _dst_idx), req(_node_idx, _src_idx))):
                    _src_id: str = await self.builtin_funcs.llList2String(self.gNodes, _src_idx)
                    _dst_id: str = await self.builtin_funcs.llList2String(self.gNodes, _dst_idx)
                    await self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(_dst_id, radd(":", radd(_src_id, "arrow_kill:"))))
                    self.gNodeRelations = await self.builtin_funcs.llDeleteSubList(self.gNodeRelations, _i, _i)
                elif cond(rboolor(rneq(_dst_idx, _new_dst_idx), rneq(_src_idx, _new_src_idx))):
                    _new_rel: int = rbitor(_new_dst_idx, rshl(16, _new_src_idx))
                    self.gNodeRelations = await self.builtin_funcs.llListReplaceList(self.gNodeRelations, [_new_rel], _i, _i)
                _i -= 1
        self.gNodes = await self.builtin_funcs.llDeleteSubList(self.gNodes, _node_idx, rsub(1, radd(2, _node_idx)))

    async def pruneNodes(self) -> None:
        _len: int = await self.builtin_funcs.llGetListLength(self.gNodes)
        _i: int = 0
        _i = rsub(2, _len)
        while True == True:
            if not cond(rgeq(0, _i)):
                break
            _node_key: Key = await self.uncompressKey(await self.builtin_funcs.llList2String(self.gNodes, radd(1, _i)))
            if cond(req((0.0), await self.builtin_funcs.llGetObjectMass(_node_key))):
                await self.untrackNode(await self.builtin_funcs.llList2String(self.gNodes, radd(0, _i)), 1)
            _i = rsub(2, _i)

    async def saveNodes(self) -> None:
        await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 800, "", typecast("00000000-0000-0000-0000-000000000000", Key))
        _i: int = 0
        _len: int = await self.builtin_funcs.llGetListLength(self.gNodes)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _node_id: str = await self.builtin_funcs.llList2String(self.gNodes, radd(0, _i))
            _node_key: Key = await self.uncompressKey(await self.builtin_funcs.llList2String(self.gNodes, radd(1, _i)))
            _node_pos: Vector = await self.builtin_funcs.llList2Vector(await self.builtin_funcs.llGetObjectDetails(_node_key, [3]), 0)
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 802, _node_id, typecast(typecast(_node_pos, str), Key))
            if cond(req(0, rmod(25, _i))):
                await self.builtin_funcs.llSleep(0.5)
            _i = radd(2, _i)
        _len = await self.builtin_funcs.llGetListLength(self.gNodeRelations)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _rel: int = await self.builtin_funcs.llList2Integer(self.gNodeRelations, _i)
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 803, await self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel)), typecast(await self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel)), Key))
            if cond(req(0, rmod(25, _i))):
                await self.builtin_funcs.llSleep(0.5)
            _i += 1
        await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 801, "", typecast("00000000-0000-0000-0000-000000000000", Key))
        self.gGraphDirty = 0

    async def clearAll(self) -> None:
        await self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(self.gOwnLogicalID, "node_kill_all:"))
        await self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(self.gOwnLogicalID, "arrow_kill_all:"))
        self.gNodes = []
        self.gNodeRelations = []
        self.gPendingNodes = []
        self.gPendingRelations = []
        self.gArrowPool = []
        self.gNeededArrows = 0
        self.gNeededNodes = 0
        self.gAvailRezSlots = 5

    async def initRestoreNodes(self, _restore_arrows: int) -> None:
        await self.clearAll()
        self.gRestoring = 1
        self.gRestoreArrows = _restore_arrows
        self.gLastRezTime = await self.builtin_funcs.llGetUnixTime()
        await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 900, "", typecast("00000000-0000-0000-0000-000000000000", Key))

    async def addRelation(self, _src: str, _dst: str) -> None:
        _rel: list = [rbitor(await self.builtin_funcs.llListFindList(self.gNodes, [_dst]), rshl(16, await self.builtin_funcs.llListFindList(self.gNodes, [_src])))]
        if cond(req(-1, await self.builtin_funcs.llListFindList(self.gNodeRelations, _rel))):
            self.gPendingRelations = radd(_rel, self.gPendingRelations)
            self.gNeededArrows += 1
            await self.tryRezPending()

    async def removeRelation(self, _src: str, _dst: str) -> None:
        _rel: list = [rbitor(await self.builtin_funcs.llListFindList(self.gNodes, [_dst]), rshl(16, await self.builtin_funcs.llListFindList(self.gNodes, [_src])))]
        _idx: int = await self.builtin_funcs.llListFindList(self.gNodeRelations, _rel)
        if cond(rneq(-1, _idx)):
            self.gNodeRelations = await self.builtin_funcs.llDeleteSubList(self.gNodeRelations, _idx, _idx)
        await self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(_dst, radd(":", radd(_src, "arrow_kill:"))))

    async def updateNodeRelations(self) -> None:
        if cond(req([], self.gPendingRelations)):
            return
        _i: int = 0
        _len: int = await self.builtin_funcs.llGetListLength(self.gPendingRelations)
        _i = rsub(1, _len)
        while True == True:
            if not cond(rgeq(0, _i)):
                break
            if cond(req([], self.gArrowPool)):
                return
            _rel: int = await self.builtin_funcs.llList2Integer(self.gPendingRelations, _i)
            _src_id: str = await self.builtin_funcs.llList2String(self.gNodes, rshr(16, _rel))
            _dst_id: str = await self.builtin_funcs.llList2String(self.gNodes, rbitand(65535, _rel))
            _src_key: str = typecast(await self.nodeIDToKey(_src_id), str)
            _dst_key: str = typecast(await self.nodeIDToKey(_dst_id), str)
            if cond(rbooland(rneq("00000000-0000-0000-0000-000000000000", _dst_key), rneq("00000000-0000-0000-0000-000000000000", _src_key))):
                _msg: str = await self.builtin_funcs.llDumpList2String(["arrow_add", _src_id, _src_key, _dst_id, _dst_key, self.gOwnLogicalID], ":")
                await self.builtin_funcs.llRegionSayTo(await self.builtin_funcs.llList2Key(self.gArrowPool, 0), (typecast(-21461419, int)), _msg)
                self.gPendingRelations = await self.builtin_funcs.llDeleteSubList(self.gPendingRelations, _i, _i)
                self.gArrowPool = await self.builtin_funcs.llDeleteSubList(self.gArrowPool, 0, 0)
                self.gNodeRelations = radd([_rel], self.gNodeRelations)
            _i -= 1

    async def tryRezPending(self) -> None:
        while cond(rbooland(rgreater(0, self.gAvailRezSlots), rgreater(0, self.gNeededNodes))):
            await self.builtin_funcs.llMessageLinked((typecast(-1, int)), 1100, typecast(preincr(self.__dict__, "gRezNum"), str), typecast("node", Key))
            self.gAvailRezSlots -= 1
            self.gNeededNodes -= 1
        while cond(rbooland(rgreater(0, self.gAvailRezSlots), rgreater(0, self.gNeededArrows))):
            await self.builtin_funcs.llMessageLinked((typecast(-1, int)), 1100, typecast(preincr(self.__dict__, "gRezNum"), str), typecast("arrow", Key))
            self.gAvailRezSlots -= 1
            self.gNeededArrows -= 1

    async def handleNodeDuplicated(self, _existing_key: Key, _node_key: Key, _node_id: str) -> None:
        _gen_node_id: str = await self.generateLogicalID()
        await self.builtin_funcs.llRegionSayTo(_existing_key, (typecast(-21461419, int)), radd(self.gOwnLogicalID, radd(":", radd(_gen_node_id, "node_reset:"))))
        _node_idx: int = await self.builtin_funcs.llListFindList(self.gNodes, [_node_id])
        _node_key_idx: int = radd(1, _node_idx)
        self.gNodes = await self.builtin_funcs.llListReplaceList(self.gNodes, [await self.compressKey(_node_key)], _node_key_idx, _node_key_idx)
        await self.builtin_funcs.llRegionSay((typecast(-21461419, int)), radd(typecast(_node_key, str), radd(":", radd(_node_id, "arrow_node_identity:"))))
        await self.trackNode(_gen_node_id, _existing_key)
        await self.addRelation(_gen_node_id, _node_id)
        await self.addRelation(_node_id, _gen_node_id)

    async def handleNodeRenamed(self, _existing_id: str, _node_key: Key, _node_id: str) -> None:
        await self.untrackNode(_existing_id, 1)
        await self.trackNode(_node_id, _node_key)

    async def edefaultstate_entry(self) -> None:
        await self.restoreLogicalID(1)
        self.gMenuChannel = rbitxor(await self.builtin_funcs.llHash(await self.builtin_funcs.llGetObjectDesc()), -21461421)
        self.gConnectionMenuChannel = rbitxor(await self.builtin_funcs.llHash(await self.builtin_funcs.llGetObjectDesc()), -21461422)
        await self.builtin_funcs.llListen((typecast(-21461420, int)), "", typecast("", Key), "")
        await self.builtin_funcs.llListen((typecast(-21461423, int)), "", typecast("", Key), "")
        await self.builtin_funcs.llListen(self.gMenuChannel, "", typecast("", Key), "")
        await self.builtin_funcs.llListen(self.gConnectionMenuChannel, "", typecast("", Key), "")
        await self.builtin_funcs.llSetColor(Vector((1.0, 0.0, 1.0)), (typecast(-1, int)))
        await self.clearAll()
        await self.builtin_funcs.llSetTimerEvent(1.0)

    async def edefaulton_rez(self, _start_param: int) -> None:
        await self.builtin_funcs.llResetScript()

    async def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(rbooland(rneq((typecast(-21461423, int)), _channel), rneq(await self.builtin_funcs.llGetOwner(), await self.builtin_funcs.llGetOwnerKey(_id)))):
            return
        _params: list = await self.builtin_funcs.llParseStringKeepNulls(_msg, [":"], [])
        _cmd: str = await self.builtin_funcs.llList2String(_params, 0)
        _params = await self.builtin_funcs.llDeleteSubList(_params, 0, 0)
        if cond(req((typecast(-21461420, int)), _channel)):
            _node_key: Key = _id
            if cond(req("node_alive", _cmd)):
                _parent_id: str = await self.builtin_funcs.llList2String(_params, 1)
                if cond(rbooland(rneq(self.gOwnLogicalID, _parent_id), rneq("", _parent_id))):
                    return
                _node_id: str = await self.builtin_funcs.llList2String(_params, 0)
                _existing_id: str = await self.nodeKeyToID(_node_key)
                _existing_key: Key = await self.nodeIDToKey(_node_id)
                if cond(rbooland(req("00000000-0000-0000-0000-000000000000", _existing_key), req("", _existing_id))):
                    await self.trackNode(_node_id, _node_key)
                    await self.builtin_funcs.llRegionSayTo(_node_key, (typecast(-21461419, int)), radd(self.gOwnLogicalID, radd(":", radd(_node_id, "node_reset:"))))
                    self.gGraphDirty = 1
                elif cond(rbooland(rneq(_node_id, _existing_id), rneq("", _existing_id))):
                    await self.builtin_funcs.llOwnerSay(radd(_existing_id, radd(" != ", radd(_node_id, radd(" had mismatch, ", radd(typecast(_node_key, str), "node hello from "))))))
                    await self.handleNodeRenamed(_existing_id, _node_key, _node_id)
                    self.gGraphDirty = 1
                elif cond(rneq(_node_key, _existing_key)):
                    await self.handleNodeDuplicated(_existing_key, _node_key, _node_id)
                    self.gGraphDirty = 1
            elif cond(req("node_touched", _cmd)):
                _clicked_id: str = await self.nodeKeyToID(_node_key)
                if cond(req("", _clicked_id)):
                    return
                if cond(rneq(self.gOwnLogicalID, await self.builtin_funcs.llList2String(_params, 0))):
                    return
                _toucher_id: Key = await self.builtin_funcs.llList2Key(_params, 1)
                if cond(rneq(await self.builtin_funcs.llGetOwner(), _toucher_id)):
                    return
                if cond(rbooland(rneq("", self.gSecondClicked), rneq("", self.gFirstClicked))):
                    self.gFirstClicked = _clicked_id
                    self.gSecondClicked = ""
                elif cond(rneq("", self.gFirstClicked)):
                    if cond(rneq(self.gFirstClicked, _clicked_id)):
                        self.gSecondClicked = _clicked_id
                        await self.builtin_funcs.llDialog(_toucher_id, "What do you want to do with the connection?", ["one-way", "two-way", "remove", "find path"], self.gConnectionMenuChannel)
                else:
                    self.gFirstClicked = _clicked_id
                self.gClickTimeout = radd(20, await self.builtin_funcs.llGetUnixTime())
        elif cond(req(self.gMenuChannel, _channel)):
            if cond(req("dump", _msg)):
                await self.dumpNodeDetails()
            elif cond(req("save", _msg)):
                if cond(await self.builtin_funcs.llGetListLength(self.gNodes)):
                    await self.saveNodes()
                else:
                    await self.builtin_funcs.llOwnerSay("Refusing to save empty node list")
            elif cond(req("restore", _msg)):
                await self.initRestoreNodes(1)
            elif cond(req("rest. norel", _msg)):
                await self.initRestoreNodes(0)
            elif cond(req("clear", _msg)):
                await self.clearAll()
                await self.builtin_funcs.llResetScript()
        elif cond(req(self.gConnectionMenuChannel, _channel)):
            if cond(req("remove", _msg)):
                await self.removeRelation(self.gFirstClicked, self.gSecondClicked)
                await self.removeRelation(self.gSecondClicked, self.gFirstClicked)
                self.gGraphDirty = 1
            elif cond(req("one-way", _msg)):
                await self.addRelation(self.gFirstClicked, self.gSecondClicked)
                await self.removeRelation(self.gSecondClicked, self.gFirstClicked)
                self.gGraphDirty = 1
            elif cond(req("two-way", _msg)):
                await self.addRelation(self.gFirstClicked, self.gSecondClicked)
                await self.addRelation(self.gSecondClicked, self.gFirstClicked)
                self.gGraphDirty = 1
            elif cond(req("find path", _msg)):
                if cond(self.gGraphDirty):
                    await self.builtin_funcs.llOwnerSay("Refusing to find path, graph is dirty")
                else:
                    await self.builtin_funcs.llOwnerSay(radd(self.gSecondClicked, radd(" to ", radd(self.gFirstClicked, "Calculating path from "))))
                    await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 1000, radd(self.gSecondClicked, radd(":", self.gFirstClicked)), typecast("00000000-0000-0000-0000-000000000000", Key))
            self.gFirstClicked = ""
            self.gSecondClicked = ""
            self.gClickTimeout = 0
        elif cond(req((typecast(-21461423, int)), _channel)):
            _num: int = 0
            if cond(req("find_path", _cmd)):
                _num = 1000
            elif cond(req("find_path_vectors", _cmd)):
                _num = 1001
            else:
                return
            if cond(rboolor(rneq(self.gOwnLogicalID, await self.builtin_funcs.llList2String(_params, 0)), req("", self.gOwnLogicalID))):
                return
            _link_msg: str = radd(await self.builtin_funcs.llList2String(_params, 2), radd(":", await self.builtin_funcs.llList2String(_params, 1)))
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), _num, _link_msg, _id)

    async def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(req(902, _num)):
            self.gPendingNodes = radd([_str, typecast(typecast(_id, str), Vector)], self.gPendingNodes)
            self.gNeededNodes += 1
        elif cond(req(903, _num)):
            self.gPendingRelations = radd([rbitor(await self.builtin_funcs.llListFindList(self.gPendingNodes, [typecast(_id, str)]), rshl(16, await self.builtin_funcs.llListFindList(self.gPendingNodes, [_str])))], self.gPendingRelations)
            self.gNeededArrows += 1
        elif cond(req(901, _num)):
            if cond(boolnot(self.gRestoreArrows)):
                self.gNeededArrows = 0
                self.gNodeRelations = self.gPendingRelations
                self.gPendingRelations = []
            await self.builtin_funcs.llOwnerSay("Got data from data manager, rezzing...")
            await self.tryRezPending()
            self.gGraphDirty = 0
        elif cond(req(1003, _num)):
            if cond(_id):
                await self.builtin_funcs.llRegionSayTo(_id, (typecast(-21461424, int)), radd(_str, "path:"))
            else:
                await self.builtin_funcs.llOwnerSay("PATH:")
                await self.builtin_funcs.llOwnerSay(_str)

    async def edefaultobject_rez(self, _id: Key) -> None:
        self.gLastRezTime = await self.builtin_funcs.llGetUnixTime()
        self.gAvailRezSlots += 1
        if cond(rneq(await self.builtin_funcs.llGetOwner(), await self.builtin_funcs.llGetOwnerKey(_id))):
            await self.builtin_funcs.llOwnerSay("Failed a rez?")
            return
        _name: str = typecast(await self.builtin_funcs.llGetObjectDetails(_id, [1]), str)
        if cond(req("node", _name)):
            if cond(req([], self.gPendingNodes)):
                await self.builtin_funcs.llOwnerSay("Rezzed node with no pending nodes???")
                return
            _node_id: str = await self.builtin_funcs.llList2String(self.gPendingNodes, 0)
            _node_pos: Vector = await self.builtin_funcs.llList2Vector(self.gPendingNodes, 1)
            await self.builtin_funcs.llRegionSayTo(_id, (typecast(-21461419, int)), radd(typecast(_node_pos, str), radd(":", radd(self.gOwnLogicalID, radd(":", radd(_node_id, "node_assign:"))))))
            self.gPendingNodes = await self.builtin_funcs.llDeleteSubList(self.gPendingNodes, 0, rsub(1, 2))
            await self.trackNode(_node_id, _id)
        elif cond(req("arrow", _name)):
            if cond(req([], self.gPendingRelations)):
                await self.builtin_funcs.llOwnerSay("Rezzed arrow with no pending relations???")
                return
            self.gArrowPool = radd([_id], self.gArrowPool)
            await self.updateNodeRelations()
        if cond(rboolor(await self.builtin_funcs.llGetListLength(self.gPendingRelations), rboolor(await self.builtin_funcs.llGetListLength(self.gPendingNodes), rboolor(self.gNeededNodes, self.gNeededArrows)))):
            await self.tryRezPending()
        elif cond(self.gRestoring):
            self.gRestoring = 0
            await self.builtin_funcs.llOwnerSay("Done rez")

    async def edefaulttouch_start(self, _touch_num: int) -> None:
        if cond(rneq(await self.builtin_funcs.llGetOwner(), await self.builtin_funcs.llDetectedKey(0))):
            return
        await self.builtin_funcs.llDialog(await self.builtin_funcs.llDetectedKey(0), "Node Management", ["dump", "save", "restore", "rest. norel", "clear"], self.gMenuChannel)

    async def edefaulttimer(self) -> None:
        self.gTickCount += 1
        if cond(rneq(radd(":", self.gOwnLogicalID), await self.builtin_funcs.llGetObjectDesc())):
            if cond(rneq("", self.gOwnLogicalID)):
                await self.clearAll()
            await self.builtin_funcs.llResetScript()
        if cond(rbooland(rless(await self.builtin_funcs.llGetUnixTime(), self.gClickTimeout), self.gClickTimeout)):
            self.gFirstClicked = ""
            self.gSecondClicked = ""
            self.gClickTimeout = 0
        if cond(boolnot((rmod(5, self.gTickCount)))):
            await self.pruneNodes()
        if cond(rboolor(self.gNeededNodes, self.gNeededArrows)):
            if cond(rgreater(radd(10, self.gLastRezTime), await self.builtin_funcs.llGetUnixTime())):
                self.gNeededNodes = 0
                self.gNeededArrows = 0
                self.gRestoring = 0
                await self.builtin_funcs.llOwnerSay("Restore got stuck, inconsistent state! Is the parcel full?")
        await self.updateNodeRelations()

