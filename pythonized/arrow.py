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

    def point(self) -> None:
        _start: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(self.gStartNodeKey, [3]), 0)
        _end: Vector = self.builtin_funcs.llList2Vector(self.builtin_funcs.llGetObjectDetails(self.gEndNodeKey, [3]), 0)
        if cond(rboolor(req(Vector(((0.0), (0.0), (0.0))), _end), req(Vector(((0.0), (0.0), (0.0))), _start))):
            self.builtin_funcs.llOwnerSay("Tracked object gone away?!?")
            self.builtin_funcs.llDie()
        _diff: Vector = rsub(_start, _end)
        _facing_rot: Quaternion = self.builtin_funcs.llRotBetween(Vector((0.0, 0.0, 1.0)), self.builtin_funcs.llVecNorm(_diff))
        _color: Vector = rdiv(bin2float('3.141593', 'db0f4940'), self.builtin_funcs.llRot2Euler(_facing_rot))
        self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [7, Vector((bin2float('0.150000', '9a99193e'), bin2float('0.150000', '9a99193e'), rsub(1.0, self.builtin_funcs.llVecMag(_diff)))), 8, _facing_rot, 18, (typecast(-1, int)), _color, (1.0)])
        self.builtin_funcs.llSetRegionPos(radd(rmul(bin2float('0.500000', '0000003f'), _diff), _start))

    def edefaultstate_entry(self) -> None:
        self.builtin_funcs.llSetStatus(16, 1)
        self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), [9, 1, 0, Vector((0.0, 1.0, 0.0)), 0, Vector(((0.0), (0.0), (0.0))), Vector(((0.0), (0.0), (0.0))), Vector(((0.0), (0.0), (0.0)))])
        self.builtin_funcs.llListen((typecast(-21461419, int)), "", typecast("", Key), "")

    def edefaulttouch_start(self, _num_detected: int) -> None:
        self.builtin_funcs.llRegionSay((typecast(-21461420, int)), radd(typecast(self.builtin_funcs.llDetectedKey(0), str), radd(":", radd(self.gEndNodeID, radd(":", radd(self.gStartNodeID, "arrow_touched:"))))))

    def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(rneq(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(_id))):
            return
        if cond(boolnot(self.builtin_funcs.llGetStartParameter())):
            return
        _params: list = self.builtin_funcs.llParseStringKeepNulls(_msg, [":"], [])
        _cmd: str = self.builtin_funcs.llList2String(_params, 0)
        _params = self.builtin_funcs.llDeleteSubList(_params, 0, 0)
        if cond(req("arrow_add", _cmd)):
            if cond(self.gStartNodeKey):
                return
            self.gStartNodeID = self.builtin_funcs.llList2String(_params, 0)
            self.gStartNodeKey = self.builtin_funcs.llList2Key(_params, 1)
            self.gEndNodeID = self.builtin_funcs.llList2String(_params, 2)
            self.gEndNodeKey = self.builtin_funcs.llList2Key(_params, 3)
            self.gParentLogicalID = self.builtin_funcs.llList2String(_params, 4)
            self.builtin_funcs.llSetTimerEvent((1.0))
            self.point()
        elif cond(req("arrow_kill", _cmd)):
            if cond(rbooland(req(self.gEndNodeID, self.builtin_funcs.llList2String(_params, 1)), req(self.gStartNodeID, self.builtin_funcs.llList2String(_params, 0)))):
                self.builtin_funcs.llDie()
        elif cond(req("arrow_kill_all", _cmd)):
            if cond(rboolor(req(self.builtin_funcs.llList2String(_params, 0), self.gParentLogicalID), req("", self.gParentLogicalID))):
                self.builtin_funcs.llDie()
        elif cond(req("arrow_node_identity", _cmd)):
            _node_id: str = self.builtin_funcs.llList2String(_params, 0)
            _node_key: Key = self.builtin_funcs.llList2Key(_params, 1)
            if cond(req(self.gStartNodeID, _node_id)):
                self.gStartNodeKey = _node_key
            elif cond(req(self.gEndNodeID, _node_id)):
                self.gEndNodeKey = _node_key
            else:
                return
            self.point()

    def edefaulttimer(self) -> None:
        self.point()

