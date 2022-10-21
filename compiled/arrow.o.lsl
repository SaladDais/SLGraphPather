//start_unprocessed_text
/*// A tapered cone rezzed by the node manager that points from
// the source of a relation to the destination

#include "shared.inc.lsl"

string gStartNodeID;
string gEndNodeID;
key gStartNodeKey;
key gEndNodeKey;

point() {
    vector start = llList2Vector(llGetObjectDetails(gStartNodeKey, [OBJECT_POS]), 0);
    vector end = llList2Vector(llGetObjectDetails(gEndNodeKey, [OBJECT_POS]), 0);
    if (start == ZERO_VECTOR || end == ZERO_VECTOR) {
        llOwnerSay("Tracked object gone away?!?");
        llDie();
    }
    vector diff = end - start;
    rotation facing_rot = llRotBetween(<0,0,1>, llVecNorm(diff));
    vector color = llRot2Euler(facing_rot) / PI;
    llSetLinkPrimitiveParamsFast(LINK_THIS, [
        // make sure the ends of the arrows are visible
        PRIM_SIZE, <0.15, 0.15, llVecMag(diff) - 1>,
        PRIM_ROTATION, facing_rot,
        PRIM_COLOR, ALL_SIDES, color, 1.
    ]);
    llSetRegionPos(start + (diff * 0.5));
}


default {
    state_entry() {
        llSetStatus(STATUS_PHANTOM, TRUE);
        // give it the proper arrow shape
        llSetLinkPrimitiveParamsFast(
            LINK_THIS,
            [PRIM_TYPE, PRIM_TYPE_CYLINDER, 0, <0, 1, 0>, 0, ZERO_VECTOR, ZERO_VECTOR, ZERO_VECTOR]
        );
        llListen(NODE_CHANNEL, "", "", "");
    }

    touch_start(integer num_detected) {
        llRegionSay(NODE_MASTER_CHANNEL, "arrow_touched:" + gStartNodeID + ":" + gEndNodeID + ":" + (string)llDetectedKey(0));
    }

    listen(integer channel, string name, key id, string msg) {
        if (llGetOwnerKey(id) != llGetOwner())
            return;
        if (!llGetStartParameter())
            return;
        list params = llParseStringKeepNulls(msg, [":"], []);
        string cmd = llList2String(params, 0);
        params = llDeleteSubList(params, 0, 0);

        if (cmd == "arrow_add") {
            if (gStartNodeKey) {
                return;
            }

            gStartNodeID = llList2String(params, 0);
            gStartNodeKey = llList2Key(params, 1);

            gEndNodeID = llList2String(params, 2);
            gEndNodeKey = llList2Key(params, 3);
            gParentLogicalID = llList2String(params, 4);
            llSetTimerEvent(1.0);
            point();
        } else if (cmd == "arrow_kill") {
            if (llList2String(params, 0) == gStartNodeID && llList2String(params, 1) == gEndNodeID) {
                llDie();
            }
        } else if (cmd == "arrow_kill_all") {
            // if we haven't been parented yet just listen to all die broadcasts
            if (gParentLogicalID == "" || gParentLogicalID == llList2String(params, 0)) {
                llDie();
            }
        } else if (cmd == "arrow_node_identity") {
            string node_id = llList2String(params, 0);
            key node_key = llList2Key(params, 1);
            if (node_id == gStartNodeID)
                gStartNodeKey = node_key;
            else if (node_id == gEndNodeID)
                gEndNodeKey = node_key;
            else
                return;
            point();
        }
    }

    timer() {
        point();
    }
}
*/
//end_unprocessed_text
//nfo_preprocessor_version 0
//program_version LSL PyOptimizer v0.3.0beta
//mono

string gParentLogicalID;
string gStartNodeID;
string gEndNodeID;
key gStartNodeKey;
key gEndNodeKey;

point()
{
    vector start = llList2Vector(llGetObjectDetails(gStartNodeKey, [3]), 0);
    vector end = llList2Vector(llGetObjectDetails(gEndNodeKey, [3]), 0);
    if (start == <((float)0), ((float)0), ((float)0)> || end == <((float)0), ((float)0), ((float)0)>)
    {
        llOwnerSay("Tracked object gone away?!?");
        llDie();
    }
    vector diff = end - start;
    rotation facing_rot = llRotBetween(<0, 0, 1>, llVecNorm(diff));
    vector color = llRot2Euler(facing_rot) / 3.1415927;
    llSetLinkPrimitiveParamsFast(((integer)-4), 
        [ 7
        , <0.15, 0.15, llVecMag(diff) - 1>
        , 8
        , facing_rot
        , 18
        , ((integer)-1)
        , color
        , ((float)1)
        ]);
    llSetRegionPos(start + diff * 0.5);
}

default
{
    state_entry()
    {
        llSetStatus(16, 1);
        llSetLinkPrimitiveParamsFast(((integer)-4), 
            [ 9
            , 1
            , 0
            , <0, 1, 0>
            , 0
            , <((float)0), ((float)0), ((float)0)>
            , <((float)0), ((float)0), ((float)0)>
            , <((float)0), ((float)0), ((float)0)>
            ]);
        llListen(((integer)-21461419), "", "", "");
    }

    touch_start(integer num_detected)
    {
        llRegionSay(((integer)-21461420), "arrow_touched:" + gStartNodeID + ":" + gEndNodeID + ":" + (string)llDetectedKey(0));
    }

    listen(integer channel, string name, key id, string msg)
    {
        if (llGetOwnerKey(id) != llGetOwner())
            return;
        if (!llGetStartParameter())
            return;
        list params = llParseStringKeepNulls(msg, [":"], []);
        string cmd = llList2String(params, 0);
        params = llDeleteSubList(params, 0, 0);
        if (cmd == "arrow_add")
        {
            if (gStartNodeKey)
            {
                return;
            }
            gStartNodeID = llList2String(params, 0);
            gStartNodeKey = llList2Key(params, 1);
            gEndNodeID = llList2String(params, 2);
            gEndNodeKey = llList2Key(params, 3);
            gParentLogicalID = llList2String(params, 4);
            llSetTimerEvent(((float)1));
            point();
        }
        else if (cmd == "arrow_kill")
        {
            if (llList2String(params, 0) == gStartNodeID && llList2String(params, 1) == gEndNodeID)
            {
                llDie();
            }
        }
        else if (cmd == "arrow_kill_all")
        {
            if (gParentLogicalID == "" || gParentLogicalID == llList2String(params, 0))
            {
                llDie();
            }
        }
        else if (cmd == "arrow_node_identity")
        {
            string node_id = llList2String(params, 0);
            key node_key = llList2Key(params, 1);
            if (node_id == gStartNodeID)
                gStartNodeKey = node_key;
            else if (node_id == gEndNodeID)
                gEndNodeKey = node_key;
            else
                return;
            point();
        }
    }

    timer()
    {
        point();
    }
}
