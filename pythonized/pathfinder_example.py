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
        return Vector((_waypoint[0], _waypoint[1], radd(self.gHeightOffset, radd(_waypoint[2], (typecast(bin2float('-0.250000', '000080be'), float))))))

    def posToWaypoint(self, _pos: Vector) -> Vector:
        return Vector((_pos[0], _pos[1], radd(neg(self.gHeightOffset), radd(_pos[2], bin2float('0.250000', '0000803e')))))

    def goToNextWaypoint(self) -> None:
        while cond(rneq([], self.gWaypoints)):
            self.gDesiredPos = self.waypointToPos(typecast(self.builtin_funcs.llList2String(self.gWaypoints, 0), Vector))
            self.gWaypoints = self.builtin_funcs.llDeleteSubList(self.gWaypoints, 0, 0)
            _diff: Vector = rsub(self.gLastPos, self.gDesiredPos)
            _travel_time: float = rmul(bin2float('0.500000', '0000003f'), self.builtin_funcs.llVecDist(self.gLastPos, self.gDesiredPos))
            if cond(boolnot((rless(bin2float('0.001000', '6f12833a'), _travel_time)))):
                if cond(boolnot((rless(bin2float('0.100000', 'cdcccc3d'), _travel_time)))):
                    self.builtin_funcs.llSetKeyframedMotion(radd(_travel_time, typecast(_diff, list)), radd(2, typecast(2, list)))
                self.builtin_funcs.llSetTimerEvent(_travel_time)
                return
        self.builtin_funcs.llSetTimerEvent((0.0))

    def edefaultstate_entry(self) -> None:
        _min_corner: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetBoundingBox(self.builtin_funcs.llGetKey()), 0)
        self.gHeightOffset = neg(_min_corner[2])
        self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), radd(2, typecast(30, list)))
        self.builtin_funcs.llSetKeyframedMotion(radd(bin2float('0.150000', '9a99193e'), typecast(Vector(((0.0), (0.0), (0.0))), list)), radd(2, typecast(2, list)))
        self.builtin_funcs.llSitTarget(Vector(((0.0), (0.0), (1.0))), Quaternion(((0.0), (0.0), (0.0), (1.0))))
        self.builtin_funcs.llListen((typecast(-21461424, int)), "", typecast("", Key), "")
        self.builtin_funcs.llListen(0, "", typecast("", Key), "I summon thee")

    def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(rbitxor((typecast(-21461424, int)), _channel)):
            if cond(boolnot(_channel)):
                self.builtin_funcs.llSetKeyframedMotion([], radd(2, typecast(0, list)))
                self.builtin_funcs.llSetTimerEvent(0.0)
                _target_pos: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(_id, typecast(3, list)), 0)
                _resp_msg: str = radd(typecast(_target_pos, str), radd(":", radd(typecast(self.posToWaypoint(self.builtin_funcs.llGetPos()), str), "find_path_vectors:REPLACEME:")))
                self.builtin_funcs.llRegionSay((typecast(-21461423, int)), _resp_msg)
                self.builtin_funcs.llResetTime()
        else:
            if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(_id))))):
                return
            _params: list = self.builtin_funcs.llParseString2List(_msg, typecast(":", list), [])
            _cmd: str = self.builtin_funcs.llList2String(_params, 0)
            _params = self.builtin_funcs.llDeleteSubList(_params, 0, 0)
            if cond(boolnot((req("path", _cmd)))):
                return
            if cond(req([], _params)):
                self.builtin_funcs.llOwnerSay("Couldn't find a path!")
                return
            self.builtin_funcs.llOwnerSay(typecast(self.builtin_funcs.llGetTime(), str))
            self.gLastPos = self.builtin_funcs.llGetPos()
            self.gWaypoints = _params
            self.goToNextWaypoint()

    def edefaulttimer(self) -> None:
        self.builtin_funcs.llSetKeyframedMotion([], radd(2, typecast(0, list)))
        self.builtin_funcs.llSetRegionPos(self.gDesiredPos)
        self.gLastPos = self.gDesiredPos
        self.goToNextWaypoint()

