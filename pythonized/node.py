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

    def restoreLogicalID(self, _create: int) -> None:
        _desc: str = self.builtin_funcs.llGetObjectDesc()
        if cond(bitnot(self.builtin_funcs.llSubStringIndex(_desc, ":"))):
            _parsed: list = self.builtin_funcs.llParseString2List(_desc, typecast(":", list), [])
            self.gOwnLogicalID = self.builtin_funcs.llList2String(_parsed, 0)
            self.gParentLogicalID = self.builtin_funcs.llList2String(_parsed, 1)
        elif cond(_create):
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
            elif cond(req("d", _A)):
                _A = "e"
                _D = "9"
            elif cond(req("f", _A)):
                _A = "e"
                _D = "a"
            _ret = radd((radd(_C, radd("%b", radd(_B, radd(_D, radd("%", radd(_A, "%e"))))))), _ret)
        return self.builtin_funcs.llUnescapeURL(_ret)

    def generateLogicalID(self) -> str:
        return self.builtin_funcs.llGetSubString(self.builtin_funcs.llStringToBase64(self.compressKey(self.builtin_funcs.llGenerateKey())), 0, 5)

    def tellAlive(self, _id: Key) -> None:
        _msg: str = radd(self.builtin_funcs.llGetObjectDesc(), "node_alive:")
        if cond(_id):
            self.builtin_funcs.llRegionSayTo(_id, (typecast(-21461420, int)), _msg)
        elif cond(req("", self.gParentLogicalID)):
            self.builtin_funcs.llWhisper((typecast(-21461420, int)), _msg)
        else:
            self.builtin_funcs.llRegionSay((typecast(-21461420, int)), _msg)

    def edefaultstate_entry(self) -> None:
        self.builtin_funcs.llSetStatus(16, 1)
        self.restoreLogicalID(1)
        self.builtin_funcs.llListen((typecast(-21461419, int)), "", typecast("", Key), "")
        self.tellAlive(typecast("00000000-0000-0000-0000-000000000000", Key))
        self.builtin_funcs.llSetText("", Vector(((1.0), (1.0), (1.0))), 0.0)
        self.gStartTime = self.builtin_funcs.llGetUnixTime()

    def edefaulton_rez(self, _start_param: int) -> None:
        if cond(rless(5, self.builtin_funcs.llAbs(radd(neg(self.builtin_funcs.llGetUnixTime()), self.gStartTime)))):
            return
        self.builtin_funcs.llSetObjectDesc("")
        self.gOwnLogicalID = ""
        self.gParentLogicalID = ""
        self.builtin_funcs.llSetText("", Vector(((1.0), (1.0), (1.0))), 0.0)
        if cond(boolnot(self.builtin_funcs.llGetStartParameter())):
            self.restoreLogicalID(1)
            self.tellAlive(typecast("00000000-0000-0000-0000-000000000000", Key))

    def edefaulttouch_start(self, _total_number: int) -> None:
        self.builtin_funcs.llRegionSay((typecast(-21461420, int)), radd(typecast(self.builtin_funcs.llDetectedKey(0), str), radd(":", radd(self.gParentLogicalID, "node_touched:"))))

    def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(_id))))):
            return
        _params: list = self.builtin_funcs.llParseStringKeepNulls(_msg, typecast(":", list), [])
        _cmd: str = self.builtin_funcs.llList2String(_params, 0)
        _params = self.builtin_funcs.llDeleteSubList(_params, 0, 0)
        _parent: Key = typecast(typecast(self.builtin_funcs.llGetObjectDetails(_id, typecast(18, list)), str), Key)
        if cond(req("node_assign", _cmd)):
            if cond(boolnot(self.builtin_funcs.llGetStartParameter())):
                return
            if cond(boolnot((req("", self.gOwnLogicalID)))):
                return
            self.gOwnLogicalID = self.builtin_funcs.llList2String(_params, 0)
            self.gParentLogicalID = self.builtin_funcs.llList2String(_params, 1)
            _pos: Vector = typecast(self.builtin_funcs.llList2String(_params, 2), Vector)
            if cond(boolnot((req(Vector(((0.0), (0.0), (0.0))), _pos)))):
                self.builtin_funcs.llSetRegionPos(_pos)
            self.builtin_funcs.llSetObjectDesc(self.generateDescription())
        elif cond(req("node_reset", _cmd)):
            self.gOwnLogicalID = self.builtin_funcs.llList2String(_params, 0)
            self.gParentLogicalID = self.builtin_funcs.llList2String(_params, 1)
            self.builtin_funcs.llSetObjectDesc(self.generateDescription())
        elif cond(req("node_kill_all", _cmd)):
            if cond(rbitor(req(self.builtin_funcs.llList2String(_params, 0), self.gParentLogicalID), req("", self.gParentLogicalID))):
                self.builtin_funcs.llDie()
        elif cond(req("node_ping", _cmd)):
            if cond(boolnot((req("", self.gParentLogicalID)))):
                return
            self.tellAlive(_parent)
        elif cond(req("node_text", _cmd)):
            self.builtin_funcs.llSetText(self.builtin_funcs.llList2String(_params, 0), typecast(self.builtin_funcs.llList2String(_params, 1), Vector), self.builtin_funcs.llList2Float(_params, 2))
        elif cond(req("node_color", _cmd)):
            self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), radd(self.builtin_funcs.llList2Float(_params, 1), radd(typecast(self.builtin_funcs.llList2String(_params, 0), Vector), radd((typecast(-1, int)), typecast(18, list)))))

