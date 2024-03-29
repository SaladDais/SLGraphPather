from lummao import *


class Script(BaseLSLScript):
    gWaypoints: list
    gLastPos: Vector
    gDesiredPos: Vector
    gHeightOffset: float

    def __init__(self):
        super().__init__()
        self.gWaypoints = []
        self.gLastPos = Vector((0.0, 0.0, 0.0))
        self.gDesiredPos = Vector((0.0, 0.0, 0.0))
        self.gHeightOffset = 0.0

    async def waypointToPos(self, _waypoint: Vector) -> Vector:
        return Vector((_waypoint[0], _waypoint[1], radd(self.gHeightOffset, rsub(0.25, _waypoint[2]))))

    async def posToWaypoint(self, _pos: Vector) -> Vector:
        return Vector((_pos[0], _pos[1], rsub(self.gHeightOffset, radd(0.25, _pos[2]))))

    async def goToNextWaypoint(self) -> None:
        while cond(rneq([], self.gWaypoints)):
            self.gDesiredPos = await self.waypointToPos(typecast(await self.builtin_funcs.llList2String(self.gWaypoints, 0), Vector))
            self.gWaypoints = await self.builtin_funcs.llDeleteSubList(self.gWaypoints, 0, 0)
            _diff: Vector = rsub(self.gLastPos, self.gDesiredPos)
            _travel_time: float = rmul(0.5, await self.builtin_funcs.llVecDist(self.gLastPos, self.gDesiredPos))
            if cond(rgeq(0.001, _travel_time)):
                if cond(rgeq(0.1, _travel_time)):
                    await self.builtin_funcs.llSetKeyframedMotion([_diff, _travel_time], [2, 2])
                await self.builtin_funcs.llSetTimerEvent(_travel_time)
                return
        await self.builtin_funcs.llSetTimerEvent((0.0))

    async def edefaultstate_entry(self) -> None:
        _min_corner: Vector = await self.builtin_funcs.llList2Vector(await self.builtin_funcs.llGetBoundingBox(await self.builtin_funcs.llGetKey()), 0)
        self.gHeightOffset = neg(_min_corner[2])
        await self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [30, 2])
        await self.builtin_funcs.llSetKeyframedMotion([Vector(((0.0), (0.0), (0.0))), 0.15], [2, 2])
        await self.builtin_funcs.llSitTarget(Vector((0.0, 0.0, 1.0)), Quaternion(((0.0), (0.0), (0.0), (1.0))))
        await self.builtin_funcs.llListen((typecast(-21461424, int)), "", typecast("", Key), "")
        await self.builtin_funcs.llListen(0, "", typecast("", Key), "I summon thee")

    async def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(req((typecast(-21461424, int)), _channel)):
            if cond(rneq(await self.builtin_funcs.llGetOwner(), await self.builtin_funcs.llGetOwnerKey(_id))):
                return
            _params: list = await self.builtin_funcs.llParseString2List(_msg, [":"], [])
            _cmd: str = await self.builtin_funcs.llList2String(_params, 0)
            _params = await self.builtin_funcs.llDeleteSubList(_params, 0, 0)
            if cond(rneq("path", _cmd)):
                return
            if cond(req([], _params)):
                await self.builtin_funcs.llOwnerSay("Couldn't find a path!")
                return
            await self.builtin_funcs.llOwnerSay(typecast(await self.builtin_funcs.llGetTime(), str))
            self.gLastPos = await self.builtin_funcs.llGetPos()
            self.gWaypoints = _params
            await self.goToNextWaypoint()
        elif cond(req(0, _channel)):
            await self.builtin_funcs.llSetKeyframedMotion([], [0, 2])
            await self.builtin_funcs.llSetTimerEvent(0.0)
            _target_pos: Vector = await self.builtin_funcs.llList2Vector(await self.builtin_funcs.llGetObjectDetails(_id, [3]), 0)
            _resp_msg: str = radd(typecast(_target_pos, str), radd(":", radd(typecast(await self.posToWaypoint(await self.builtin_funcs.llGetPos()), str), radd(":", radd("REPLACEME", "find_path_vectors:")))))
            await self.builtin_funcs.llRegionSay((typecast(-21461423, int)), _resp_msg)
            await self.builtin_funcs.llResetTime()

    async def edefaulttimer(self) -> None:
        await self.builtin_funcs.llSetKeyframedMotion([], [0, 2])
        await self.builtin_funcs.llSetRegionPos(self.gDesiredPos)
        self.gLastPos = self.gDesiredPos
        await self.goToNextWaypoint()

