from lummao import *


class Script(BaseLSLScript):
    gNumScripts: int
    gScriptNum: int

    def __init__(self):
        super().__init__()
        self.gNumScripts = 0
        self.gScriptNum = 0

    def edefaultstate_entry(self) -> None:
        self.builtin_funcs.llSetMemoryLimit(10000)
        script_name: str = self.builtin_funcs.llGetScriptName()
        if cond(self.builtin_funcs.llSubStringIndex(self.builtin_funcs.llGetScriptName(), "rez_helper")):
            self.builtin_funcs.llOwnerSay("Script name must start with rez_helper!")
            return
        parsed_name: list = self.builtin_funcs.llParseString2List(script_name, typecast(" ", list), [])
        name_prefix: str = self.builtin_funcs.llList2String(parsed_name, 0)
        self.gScriptNum = self.builtin_funcs.llList2Integer(parsed_name, (typecast(-1, int)))
        i: int = 0
        len: int = self.builtin_funcs.llGetInventoryNumber(10)
        i = 0
        while True == True:
            if not cond(rless(len, i)):
                break
            if cond(boolnot(self.builtin_funcs.llSubStringIndex(self.builtin_funcs.llGetInventoryName(10, i), name_prefix))):
                self.gNumScripts += 1
            i += 1

    def edefaultlink_message(self, sender_num: int, num: int, str: str, id: Key) -> None:
        if cond(rbitxor(1100, num)):
            return
        if cond(boolnot(self.gNumScripts)):
            return
        obj_num: int = typecast(str, int)
        if cond(rbitxor(self.gScriptNum, rmod(self.gNumScripts, obj_num))):
            return
        self.builtin_funcs.llRezAtRoot(typecast(id, str), self.builtin_funcs.llGetPos(), Vector(((0.0), (0.0), (0.0))), Quaternion(((0.0), (0.0), (0.0), (1.0))), 1)

    def edefaultchanged(self, change: int) -> None:
        if cond(rbitand(1, change)):
            self.builtin_funcs.llResetScript()

