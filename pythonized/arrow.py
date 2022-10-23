from lummao import *


class Script(BaseLSLScript):
    gParentLogicalID: str
    gStartNodeID: str
    gEndNodeID: str
    gStartNodeKey: Key
    gEndNodeKey: Key

    def __init__(self):
        super().__init__()
        self.gParentLogicalID = ""
        self.gStartNodeID = ""
        self.gEndNodeID = ""
        self.gStartNodeKey = Key("")
        self.gEndNodeKey = Key("")

    async def point(self) -> None:
        _start: Vector = await self.builtin_funcs.llList2Vector(await self.builtin_funcs.llGetObjectDetails(self.gStartNodeKey, [3]), 0)
        _end: Vector = await self.builtin_funcs.llList2Vector(await self.builtin_funcs.llGetObjectDetails(self.gEndNodeKey, [3]), 0)
        if cond(rboolor(req(Vector(((0.0), (0.0), (0.0))), _end), req(Vector(((0.0), (0.0), (0.0))), _start))):
            await self.builtin_funcs.llOwnerSay("Tracked object gone away?!?")
            await self.builtin_funcs.llDie()
        _diff: Vector = rsub(_start, _end)
        _facing_rot: Quaternion = await self.builtin_funcs.llRotBetween(Vector((0.0, 0.0, 1.0)), await self.builtin_funcs.llVecNorm(_diff))
        _color: Vector = rdiv(bin2float('3.141593', 'db0f4940'), await self.builtin_funcs.llRot2Euler(_facing_rot))
        await self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [7, Vector((0.15, 0.15, rsub(1.0, await self.builtin_funcs.llVecMag(_diff)))), 8, _facing_rot, 18, (typecast(-1, int)), _color, (1.0)])
        await self.builtin_funcs.llSetRegionPos(radd(rmul(0.5, _diff), _start))

    async def edefaultstate_entry(self) -> None:
        await self.builtin_funcs.llSetStatus(16, 1)
        await self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [9, 1, 0, Vector((0.0, 1.0, 0.0)), 0, Vector(((0.0), (0.0), (0.0))), Vector(((0.0), (0.0), (0.0))), Vector(((0.0), (0.0), (0.0)))])
        await self.builtin_funcs.llListen((typecast(-21461419, int)), "", typecast("", Key), "")

    async def edefaulttouch_start(self, _num_detected: int) -> None:
        await self.builtin_funcs.llRegionSay((typecast(-21461420, int)), radd(typecast(await self.builtin_funcs.llDetectedKey(0), str), radd(":", radd(self.gEndNodeID, radd(":", radd(self.gStartNodeID, "arrow_touched:"))))))

    async def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(rneq(await self.builtin_funcs.llGetOwner(), await self.builtin_funcs.llGetOwnerKey(_id))):
            return
        if cond(boolnot(await self.builtin_funcs.llGetStartParameter())):
            return
        _params: list = await self.builtin_funcs.llParseStringKeepNulls(_msg, [":"], [])
        _cmd: str = await self.builtin_funcs.llList2String(_params, 0)
        _params = await self.builtin_funcs.llDeleteSubList(_params, 0, 0)
        if cond(req("arrow_add", _cmd)):
            if cond(self.gStartNodeKey):
                return
            self.gStartNodeID = await self.builtin_funcs.llList2String(_params, 0)
            self.gStartNodeKey = await self.builtin_funcs.llList2Key(_params, 1)
            self.gEndNodeID = await self.builtin_funcs.llList2String(_params, 2)
            self.gEndNodeKey = await self.builtin_funcs.llList2Key(_params, 3)
            self.gParentLogicalID = await self.builtin_funcs.llList2String(_params, 4)
            await self.builtin_funcs.llSetTimerEvent((1.0))
            await self.point()
        elif cond(req("arrow_kill", _cmd)):
            if cond(rbooland(req(self.gEndNodeID, await self.builtin_funcs.llList2String(_params, 1)), req(self.gStartNodeID, await self.builtin_funcs.llList2String(_params, 0)))):
                await self.builtin_funcs.llDie()
        elif cond(req("arrow_kill_all", _cmd)):
            if cond(rboolor(req(await self.builtin_funcs.llList2String(_params, 0), self.gParentLogicalID), req("", self.gParentLogicalID))):
                await self.builtin_funcs.llDie()
        elif cond(req("arrow_node_identity", _cmd)):
            _node_id: str = await self.builtin_funcs.llList2String(_params, 0)
            _node_key: Key = await self.builtin_funcs.llList2Key(_params, 1)
            if cond(req(self.gStartNodeID, _node_id)):
                self.gStartNodeKey = _node_key
            elif cond(req(self.gEndNodeID, _node_id)):
                self.gEndNodeKey = _node_key
            else:
                return
            await self.point()

    async def edefaulttimer(self) -> None:
        await self.point()

