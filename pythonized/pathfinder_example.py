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

    def waypointToPos(self, _waypoint: Vector) -> Vector:
        return Vector((_waypoint[0], _waypoint[1], radd(self.gHeightOffset, rsub(bin2float('0.250000', '0000803e'), _waypoint[2]))))

    def posToWaypoint(self, _pos: Vector) -> Vector:
        return Vector((_pos[0], _pos[1], rsub(self.gHeightOffset, radd(bin2float('0.250000', '0000803e'), _pos[2]))))

    def goToNextWaypoint(self) -> None:
        while cond(rneq([], self.gWaypoints)):
            self.gDesiredPos = self.waypointToPos(typecast(self.builtin_funcs.llList2String(self.gWaypoints, 0), Vector))
            self.gWaypoints = self.builtin_funcs.llDeleteSubList(self.gWaypoints, 0, 0)
            _diff: Vector = rsub(self.gLastPos, self.gDesiredPos)
            _travel_time: float = rmul(bin2float('0.500000', '0000003f'), self.builtin_funcs.llVecDist(self.gLastPos, self.gDesiredPos))
            if cond(rgeq(bin2float('0.001000', '6f12833a'), _travel_time)):
                if cond(rgeq(bin2float('0.100000', 'cdcccc3d'), _travel_time)):
                    self.builtin_funcs.llSetKeyframedMotion([_diff, _travel_time], [2, 2])
                self.builtin_funcs.llSetTimerEvent(_travel_time)
                return
        self.builtin_funcs.llSetTimerEvent((0.0))

    def edefaultstate_entry(self) -> None:
        _min_corner: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetBoundingBox(self.builtin_funcs.llGetKey()), 0)
        self.gHeightOffset = neg(_min_corner[2])
        self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [30, 2])
        self.builtin_funcs.llSetKeyframedMotion([Vector(((0.0), (0.0), (0.0))), bin2float('0.150000', '9a99193e')], [2, 2])
        self.builtin_funcs.llSitTarget(Vector((0.0, 0.0, 1.0)), Quaternion(((0.0), (0.0), (0.0), (1.0))))
        self.builtin_funcs.llListen((typecast(-21461424, int)), "", typecast("", Key), "")
        self.builtin_funcs.llListen(0, "", typecast("", Key), "I summon thee")

    def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(req((typecast(-21461424, int)), _channel)):
            if cond(rneq(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(_id))):
                return
            _params: list = self.builtin_funcs.llParseString2List(_msg, [":"], [])
            _cmd: str = self.builtin_funcs.llList2String(_params, 0)
            _params = self.builtin_funcs.llDeleteSubList(_params, 0, 0)
            if cond(rneq("path", _cmd)):
                return
            if cond(req([], _params)):
                self.builtin_funcs.llOwnerSay("Couldn't find a path!")
                return
            self.builtin_funcs.llOwnerSay(typecast(self.builtin_funcs.llGetTime(), str))
            self.gLastPos = self.builtin_funcs.llGetPos()
            self.gWaypoints = _params
            self.goToNextWaypoint()
        elif cond(req(0, _channel)):
            self.builtin_funcs.llSetKeyframedMotion([], [0, 2])
            self.builtin_funcs.llSetTimerEvent(0.0)
            _target_pos: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(_id, [3]), 0)
            _resp_msg: str = radd(typecast(_target_pos, str), radd(":", radd(typecast(self.posToWaypoint(self.builtin_funcs.llGetPos()), str), radd(":", radd("REPLACEME", "find_path_vectors:")))))
            self.builtin_funcs.llRegionSay((typecast(-21461423, int)), _resp_msg)
            self.builtin_funcs.llResetTime()

    def edefaulttimer(self) -> None:
        self.builtin_funcs.llSetKeyframedMotion([], [0, 2])
        self.builtin_funcs.llSetRegionPos(self.gDesiredPos)
        self.gLastPos = self.gDesiredPos
        self.goToNextWaypoint()

