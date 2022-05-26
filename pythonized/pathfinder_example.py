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

    def waypointToPos(self, waypoint: Vector) -> Vector:
        return Vector((waypoint[0], waypoint[1], radd(self.gHeightOffset, radd(waypoint[2], (typecast(bin2float('-0.250000', '000080be'), float))))))

    def posToWaypoint(self, pos: Vector) -> Vector:
        return Vector((pos[0], pos[1], radd(neg(self.gHeightOffset), radd(pos[2], bin2float('0.250000', '0000803e')))))

    def goToNextWaypoint(self) -> None:
        while cond(rneq([], self.gWaypoints)):
            self.gDesiredPos = self.waypointToPos(typecast(self.builtin_funcs.llList2String(self.gWaypoints, 0), Vector))
            self.gWaypoints = self.builtin_funcs.llDeleteSubList(self.gWaypoints, 0, 0)
            diff: Vector = rsub(self.gLastPos, self.gDesiredPos)
            travel_time: float = rmul(bin2float('0.500000', '0000003f'), self.builtin_funcs.llVecDist(self.gLastPos, self.gDesiredPos))
            if cond(boolnot((rless(bin2float('0.001000', '6f12833a'), travel_time)))):
                if cond(boolnot((rless(bin2float('0.100000', 'cdcccc3d'), travel_time)))):
                    self.builtin_funcs.llSetKeyframedMotion(radd(travel_time, typecast(diff, list)), radd(2, typecast(2, list)))
                self.builtin_funcs.llSetTimerEvent(travel_time)
                return
        self.builtin_funcs.llSetTimerEvent((0.0))

    def edefaultstate_entry(self) -> None:
        min_corner: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetBoundingBox(self.builtin_funcs.llGetKey()), 0)
        self.gHeightOffset = neg(min_corner[2])
        self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), radd(2, typecast(30, list)))
        self.builtin_funcs.llSetKeyframedMotion(radd(bin2float('0.150000', '9a99193e'), typecast(Vector(((0.0), (0.0), (0.0))), list)), radd(2, typecast(2, list)))
        self.builtin_funcs.llSitTarget(Vector(((0.0), (0.0), (1.0))), Quaternion(((0.0), (0.0), (0.0), (1.0))))
        self.builtin_funcs.llListen((typecast(-21461424, int)), "", typecast("", Key), "")
        self.builtin_funcs.llListen(0, "", typecast("", Key), "I summon thee")

    def edefaultlisten(self, channel: int, name: str, id: Key, msg: str) -> None:
        if cond(rbitxor((typecast(-21461424, int)), channel)):
            if cond(boolnot(channel)):
                self.builtin_funcs.llSetKeyframedMotion([], radd(2, typecast(0, list)))
                self.builtin_funcs.llSetTimerEvent(0.0)
                target_pos: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(id, typecast(3, list)), 0)
                resp_msg: str = radd(typecast(target_pos, str), radd(":", radd(typecast(self.posToWaypoint(self.builtin_funcs.llGetPos()), str), "find_path_vectors:REPLACEME:")))
                self.builtin_funcs.llRegionSay((typecast(-21461423, int)), resp_msg)
                self.builtin_funcs.llResetTime()
        else:
            if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(id))))):
                return
            params: list = self.builtin_funcs.llParseString2List(msg, typecast(":", list), [])
            cmd: str = self.builtin_funcs.llList2String(params, 0)
            params = self.builtin_funcs.llDeleteSubList(params, 0, 0)
            if cond(boolnot((req("path", cmd)))):
                return
            if cond(req([], params)):
                self.builtin_funcs.llOwnerSay("Couldn't find a path!")
                return
            self.builtin_funcs.llOwnerSay(typecast(self.builtin_funcs.llGetTime(), str))
            self.gLastPos = self.builtin_funcs.llGetPos()
            self.gWaypoints = params
            self.goToNextWaypoint()

    def edefaulttimer(self) -> None:
        self.builtin_funcs.llSetKeyframedMotion([], radd(2, typecast(0, list)))
        self.builtin_funcs.llSetRegionPos(self.gDesiredPos)
        self.gLastPos = self.gDesiredPos
        self.goToNextWaypoint()

