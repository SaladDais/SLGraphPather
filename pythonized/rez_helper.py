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
        _script_name: str = self.builtin_funcs.llGetScriptName()
        if cond(self.builtin_funcs.llSubStringIndex(self.builtin_funcs.llGetScriptName(), "rez_helper")):
            self.builtin_funcs.llOwnerSay("Script name must start with rez_helper!")
            return
        _parsed_name: list = self.builtin_funcs.llParseString2List(_script_name, typecast(" ", list), [])
        _name_prefix: str = self.builtin_funcs.llList2String(_parsed_name, 0)
        self.gScriptNum = self.builtin_funcs.llList2Integer(_parsed_name, (typecast(-1, int)))
        _i: int = 0
        _len: int = self.builtin_funcs.llGetInventoryNumber(10)
        _i = 0
        while True == True:
            if not cond(rless(_len, _i)):
                break
            if cond(boolnot(self.builtin_funcs.llSubStringIndex(self.builtin_funcs.llGetInventoryName(10, _i), _name_prefix))):
                self.gNumScripts += 1
            _i += 1

    def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(rbitxor(1100, _num)):
            return
        if cond(boolnot(self.gNumScripts)):
            return
        _obj_num: int = typecast(_str, int)
        if cond(rbitxor(self.gScriptNum, rmod(self.gNumScripts, _obj_num))):
            return
        self.builtin_funcs.llRezAtRoot(typecast(_id, str), self.builtin_funcs.llGetPos(), Vector(((0.0), (0.0), (0.0))), Quaternion(((0.0), (0.0), (0.0), (1.0))), 1)

    def edefaultchanged(self, _change: int) -> None:
        if cond(rbitand(1, _change)):
            self.builtin_funcs.llResetScript()

