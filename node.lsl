#include "shared.inc.lsl"


integer gStartTime;


tellAlive(key id) {
    string msg = "node_alive:" + llGetObjectDesc();
    if (id) {
        llRegionSayTo(id, NODE_MASTER_CHANNEL, msg);
    } else if (gParentLogicalID != "") {
        // if we can't target this to a particular parent, don't bother
        // broadcasting that we're alive to everyone.
        llRegionSay(NODE_MASTER_CHANNEL, msg);
    } else {
        // If we don't know who our parent is at all (maybe because the script
        // was just saved and we're not a duplicate) we can send a short-range broadcast.
        // asking for a node manager to pick us up.
        llWhisper(NODE_MASTER_CHANNEL, msg);
    }
}


default {
    state_entry() {
        // restore our node ID, creating one if it didn't exist
        llSetStatus(STATUS_PHANTOM, TRUE);
        restoreLogicalID(TRUE);
        llListen(NODE_CHANNEL, "", "", "");
        tellAlive(NULL_KEY);
        llSetText("", <1,1,1>, 0);
        gStartTime = llGetUnixTime();
    }

    on_rez(integer start_param) {
        // initialization logic for script startup case takes precedence if
        // object duplication just occured. That's the only case where we
        // expect state_entry() and on_rez() could trigger within a short
        // timeframe. Per the LSL wiki this shouldn't ever happen, but
        // I don't trust that won't change or isn't the case on OpenSim.
        if (llAbs(gStartTime - llGetUnixTime()) < 5)
            return;

        // if we just got rezzed, our old ID doesn't mean anything anymore.
        llSetObjectDesc("");
        gOwnLogicalID = "";
        gParentLogicalID = "";
        llSetText("", <1,1,1>, 0);
        // If We just got rezzed by the node manager, it's going to tell us
        // our node ID and our children. Don't generate an ID.
        if (!llGetStartParameter()) {
            restoreLogicalID(TRUE);
            tellAlive(NULL_KEY);
        }
    }

    touch_start(integer total_number) {
        llRegionSay(NODE_MASTER_CHANNEL, "node_touched:" + gParentLogicalID + ":" + (string)llDetectedKey(0));
    }

    listen(integer channel, string name, key id, string msg) {
        if (llGetOwnerKey(id) != llGetOwner())
            return;
        list params = llParseStringKeepNulls(msg, [":"], []);
        string cmd = llList2String(params, 0);
        params = llDeleteSubList(params, 0, 0);
        // The rez helper in a child prim might be sending the message,
        // but it's the parent that needs to receive the reply
        key parent = llList2Key(llGetObjectDetails(id, [OBJECT_ROOT]), 0);

        if (cmd == "node_assign") {
            // node manager is assigning us an ID and position because it
            // just rezzed us.
            // not for us!
            if (!llGetStartParameter())
                return;
            if (gOwnLogicalID != "")
                return;
            gOwnLogicalID = llList2String(params, 0);
            gParentLogicalID = llList2String(params, 1);
            vector pos = (vector)llList2String(params, 2);
            if (pos != ZERO_VECTOR)
                llSetRegionPos(pos);
            llSetObjectDesc(generateDescription());
        } else if (cmd == "node_reset") {
            // node manager is asking us to change our ID to something specific.
            // Maybe our ID collides with an existing node because we got
            // duplicated through shift drag? Assign ourselves the provided ID.
            // Could also happen if a node was manually rezzed.
            gOwnLogicalID = llList2String(params, 0);
            gParentLogicalID = llList2String(params, 1);
            llSetObjectDesc(generateDescription());
        } else if (cmd == "node_kill_all") {
            // if we haven't been parented yet just listen to all die broadcasts
            if (gParentLogicalID == "" || gParentLogicalID == llList2String(params, 0)) {
                llDie();
            }
        } else if (cmd == "node_ping") {
            // no need to respond if we have a parent, nobody should be looking
            // for us.
            if (gParentLogicalID != "")
                return;
            tellAlive(parent);
        } else if (cmd == "node_text") {
            llSetText(llList2String(params, 0), (vector)llList2String(params, 1), llList2Float(params, 2));
        } else if (cmd == "node_color") {
            llSetLinkPrimitiveParamsFast(LINK_THIS, [
                PRIM_COLOR, ALL_SIDES, (vector)llList2String(params, 0), llList2Float(params, 1)
            ]);
        }
    }
}
