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

    def generateLogicalID(self) -> str:
        return self.builtin_funcs.llGetSubString(self.builtin_funcs.llStringToBase64(self.compressKey(self.builtin_funcs.llGenerateKey())), 0, 5)

    def tellAlive(self, id: Key) -> None:
        msg: str = radd(self.builtin_funcs.llGetObjectDesc(), "node_alive:")
        if cond(id):
            self.builtin_funcs.llRegionSayTo(id, (typecast(-21461420, int)), msg)
        else:
            if cond(req("", self.gParentLogicalID)):
                self.builtin_funcs.llWhisper((typecast(-21461420, int)), msg)
            else:
                self.builtin_funcs.llRegionSay((typecast(-21461420, int)), msg)

    def edefaultstate_entry(self) -> None:
        self.builtin_funcs.llSetStatus(16, 1)
        self.restoreLogicalID(1)
        self.builtin_funcs.llListen((typecast(-21461419, int)), "", typecast("", Key), "")
        self.tellAlive(typecast("00000000-0000-0000-0000-000000000000", Key))
        self.builtin_funcs.llSetText("", Vector(((1.0), (1.0), (1.0))), 0.0)
        self.gStartTime = self.builtin_funcs.llGetUnixTime()

    def edefaulton_rez(self, start_param: int) -> None:
        if cond(rless(5, self.builtin_funcs.llAbs(radd(neg(self.builtin_funcs.llGetUnixTime()), self.gStartTime)))):
            return
        self.builtin_funcs.llSetObjectDesc("")
        self.gOwnLogicalID = ""
        self.gParentLogicalID = ""
        self.builtin_funcs.llSetText("", Vector(((1.0), (1.0), (1.0))), 0.0)
        if cond(boolnot(self.builtin_funcs.llGetStartParameter())):
            self.restoreLogicalID(1)
            self.tellAlive(typecast("00000000-0000-0000-0000-000000000000", Key))

    def edefaulttouch_start(self, total_number: int) -> None:
        self.builtin_funcs.llRegionSay((typecast(-21461420, int)), radd(typecast(self.builtin_funcs.llDetectedKey(0), str), radd(":", radd(self.gParentLogicalID, "node_touched:"))))

    def edefaultlisten(self, channel: int, name: str, id: Key, msg: str) -> None:
        if cond(boolnot((req(self.builtin_funcs.llGetOwner(), self.builtin_funcs.llGetOwnerKey(id))))):
            return
        params: list = self.builtin_funcs.llParseStringKeepNulls(msg, typecast(":", list), [])
        cmd: str = self.builtin_funcs.llList2String(params, 0)
        params = self.builtin_funcs.llDeleteSubList(params, 0, 0)
        parent: Key = typecast(typecast(self.builtin_funcs.llGetObjectDetails(id, typecast(18, list)), str), Key)
        if cond(req("node_assign", cmd)):
            if cond(boolnot(self.builtin_funcs.llGetStartParameter())):
                return
            if cond(boolnot((req("", self.gOwnLogicalID)))):
                return
            self.gOwnLogicalID = self.builtin_funcs.llList2String(params, 0)
            self.gParentLogicalID = self.builtin_funcs.llList2String(params, 1)
            pos: Vector = typecast(self.builtin_funcs.llList2String(params, 2), Vector)
            if cond(boolnot((req(Vector(((0.0), (0.0), (0.0))), pos)))):
                self.builtin_funcs.llSetRegionPos(pos)
            self.builtin_funcs.llSetObjectDesc(self.generateDescription())
        else:
            if cond(req("node_reset", cmd)):
                self.gOwnLogicalID = self.builtin_funcs.llList2String(params, 0)
                self.gParentLogicalID = self.builtin_funcs.llList2String(params, 1)
                self.builtin_funcs.llSetObjectDesc(self.generateDescription())
            else:
                if cond(req("node_kill_all", cmd)):
                    if cond(rbitor(req(self.builtin_funcs.llList2String(params, 0), self.gParentLogicalID), req("", self.gParentLogicalID))):
                        self.builtin_funcs.llDie()
                else:
                    if cond(req("node_ping", cmd)):
                        if cond(boolnot((req("", self.gParentLogicalID)))):
                            return
                        self.tellAlive(parent)
                    else:
                        if cond(req("node_text", cmd)):
                            self.builtin_funcs.llSetText(self.builtin_funcs.llList2String(params, 0), typecast(self.builtin_funcs.llList2String(params, 1), Vector), self.builtin_funcs.llList2Float(params, 2))
                        else:
                            if cond(req("node_color", cmd)):
                                self.builtin_funcs.llSetLinkPrimitiveParamsFast((typecast(-4, int)), radd(self.builtin_funcs.llList2Float(params, 1), radd(typecast(self.builtin_funcs.llList2String(params, 0), Vector), radd((typecast(-1, int)), typecast(18, list)))))

