from lummao import *


class Script(BaseLSLScript):
    gOwnLogicalID: str
    gParentLogicalID: str
    gStartTime: int

    def __init__(self):
        super().__init__()
        self.gOwnLogicalID = ""
        self.gParentLogicalID = ""
        self.gStartTime = 0

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

    async def generateLogicalID(self) -> str:
        return await self.builtin_funcs.llGetSubString(await self.builtin_funcs.llStringToBase64(await self.compressKey(await self.builtin_funcs.llGenerateKey())), 0, 5)

    async def tellAlive(self, _id: Key) -> None:
        _msg: str = radd(await self.builtin_funcs.llGetObjectDesc(), "node_alive:")
        if cond(_id):
            await self.builtin_funcs.llRegionSayTo(_id, (typecast(-21461420, int)), _msg)
        elif cond(rneq("", self.gParentLogicalID)):
            await self.builtin_funcs.llRegionSay((typecast(-21461420, int)), _msg)
        else:
            await self.builtin_funcs.llWhisper((typecast(-21461420, int)), _msg)

    async def edefaultstate_entry(self) -> None:
        await self.builtin_funcs.llSetStatus(16, 1)
        await self.restoreLogicalID(1)
        await self.builtin_funcs.llListen((typecast(-21461419, int)), "", typecast("", Key), "")
        await self.tellAlive(typecast("00000000-0000-0000-0000-000000000000", Key))
        await self.builtin_funcs.llSetText("", Vector((1.0, 1.0, 1.0)), 0.0)
        self.gStartTime = await self.builtin_funcs.llGetUnixTime()

    async def edefaulton_rez(self, _start_param: int) -> None:
        if cond(rless(5, await self.builtin_funcs.llAbs(rsub(await self.builtin_funcs.llGetUnixTime(), self.gStartTime)))):
            return
        await self.builtin_funcs.llSetObjectDesc("")
        self.gOwnLogicalID = ""
        self.gParentLogicalID = ""
        await self.builtin_funcs.llSetText("", Vector((1.0, 1.0, 1.0)), 0.0)
        if cond(boolnot(await self.builtin_funcs.llGetStartParameter())):
            await self.restoreLogicalID(1)
            await self.tellAlive(typecast("00000000-0000-0000-0000-000000000000", Key))

    async def edefaulttouch_start(self, _total_number: int) -> None:
        await self.builtin_funcs.llRegionSay((typecast(-21461420, int)), radd(typecast(await self.builtin_funcs.llDetectedKey(0), str), radd(":", radd(self.gParentLogicalID, "node_touched:"))))

    async def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(rneq(await self.builtin_funcs.llGetOwner(), await self.builtin_funcs.llGetOwnerKey(_id))):
            return
        _params: list = await self.builtin_funcs.llParseStringKeepNulls(_msg, [":"], [])
        _cmd: str = await self.builtin_funcs.llList2String(_params, 0)
        _params = await self.builtin_funcs.llDeleteSubList(_params, 0, 0)
        _parent: Key = await self.builtin_funcs.llList2Key(await self.builtin_funcs.llGetObjectDetails(_id, [18]), 0)
        if cond(req("node_assign", _cmd)):
            if cond(boolnot(await self.builtin_funcs.llGetStartParameter())):
                return
            if cond(rneq("", self.gOwnLogicalID)):
                return
            self.gOwnLogicalID = await self.builtin_funcs.llList2String(_params, 0)
            self.gParentLogicalID = await self.builtin_funcs.llList2String(_params, 1)
            _pos: Vector = typecast(await self.builtin_funcs.llList2String(_params, 2), Vector)
            if cond(rneq(Vector(((0.0), (0.0), (0.0))), _pos)):
                await self.builtin_funcs.llSetRegionPos(_pos)
            await self.builtin_funcs.llSetObjectDesc(await self.generateDescription())
        elif cond(req("node_reset", _cmd)):
            self.gOwnLogicalID = await self.builtin_funcs.llList2String(_params, 0)
            self.gParentLogicalID = await self.builtin_funcs.llList2String(_params, 1)
            await self.builtin_funcs.llSetObjectDesc(await self.generateDescription())
        elif cond(req("node_kill_all", _cmd)):
            if cond(rboolor(req(await self.builtin_funcs.llList2String(_params, 0), self.gParentLogicalID), req("", self.gParentLogicalID))):
                await self.builtin_funcs.llDie()
        elif cond(req("node_ping", _cmd)):
            if cond(rneq("", self.gParentLogicalID)):
                return
            await self.tellAlive(_parent)
        elif cond(req("node_text", _cmd)):
            await self.builtin_funcs.llSetText(await self.builtin_funcs.llList2String(_params, 0), typecast(await self.builtin_funcs.llList2String(_params, 1), Vector), await self.builtin_funcs.llList2Float(_params, 2))
        elif cond(req("node_color", _cmd)):
            await self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [18, (typecast(-1, int)), typecast(await self.builtin_funcs.llList2String(_params, 0), Vector), await self.builtin_funcs.llList2Float(_params, 1)])

