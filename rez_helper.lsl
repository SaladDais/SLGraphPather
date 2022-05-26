// There should be multiple copies of this in the node manager object
// named "rez_helper", "rez_helper 1", "rez_helper 2", ...

#include "shared.inc.lsl"

integer gNumScripts;
integer gScriptNum;


default {
    state_entry() {
        llSetMemoryLimit(10000);
        string script_name = llGetScriptName();
        if (llSubStringIndex(llGetScriptName(), "rez_helper") != 0) {
            llOwnerSay("Script name must start with rez_helper!");
            return;
        }
        list parsed_name = llParseString2List(script_name, [" "], []);
        string name_prefix = llList2String(parsed_name, 0);
        gScriptNum = llList2Integer(parsed_name, -1);
        integer i;
        integer len = llGetInventoryNumber(INVENTORY_SCRIPT);
        for(i=0; i<len; ++i) {
            // find all scripts that have the same prefix
            if(!llSubStringIndex(llGetInventoryName(INVENTORY_SCRIPT, i), name_prefix)) {
                ++gNumScripts;
            }
        }
    }

    link_message(integer sender_num, integer num, string str, key id) {
        if (num != IPC_REZ_PRIM)
            return;
        if (!gNumScripts)
            return;
        integer obj_num = (integer)str;
        if ((obj_num % gNumScripts) != gScriptNum)
            return;
        llRezAtRoot((string)id, llGetPos(), ZERO_VECTOR, ZERO_ROTATION, 1);
    }

    changed(integer change) {
        if (change & CHANGED_INVENTORY)
            llResetScript();
    }
}
