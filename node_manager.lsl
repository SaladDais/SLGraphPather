#include "shared.inc.lsl"

#define MENU_CHANNEL_BASE -21461421
#define CONNECTION_MENU_CHANNEL_BASE -21461422

#define PRUNE_NODES_EVERY 5
#define MAX_REZ_SLOTS 5

#define NODE_STRIDE 2
#define NODE_ID_OFFSET 0
#define NODE_KEY_OFFSET 1
// pending list, before we have a key
#define NODE_POS_OFFSET 1


// node_id, node_object_key
list gNodes = [];
// node_id, node_pos
list gPendingNodes = [];
// ORed together indices into gNodes list
list gNodeRelations = [];
// same as above, but relations that can't be actualized
// because we haven't rezzed the dst node yet.
list gPendingRelations = [];
list gArrowPool = [];

integer gRezNum;
integer gRestoreArrows;
integer gRestoring;

integer gNeededArrows;
integer gNeededNodes;
// arbitrary, under the message queue limit
// so we don't overwhelm the rez servers with messages,
// or overwhelm ourselves with responses to the rezzes.
integer gAvailRezSlots = MAX_REZ_SLOTS;
integer gLastRezTime;

integer gClickTimeout;
integer gTickCount;

string gFirstClicked = "";
string gSecondClicked = "";

// data manager doesn't know about some changes to the graph
integer gGraphDirty;

integer gMenuChannel;
integer gConnectionMenuChannel;


key nodeIDToKey(string node_id) {
    integer idx = llListFindList(gNodes, [node_id]);
    if (idx == -1)
        return NULL_KEY;
    return uncompressKey(llList2String(gNodes, idx + NODE_KEY_OFFSET));
}

string nodeKeyToID(key id) {
    integer idx = llListFindList(gNodes, [compressKey(id)]);
    if (idx == -1)
        return "";
    return llList2String(gNodes, idx - NODE_KEY_OFFSET);
}

dumpNodeDetails() { 
    integer i;
    integer len = llGetListLength(gNodes);
    llOwnerSay("gNodes:");
    for(i=0; i<len; i+=NODE_STRIDE) {
        llOwnerSay(llList2String(gNodes, i + NODE_ID_OFFSET) + ": "
            + (string)uncompressKey(llList2String(gNodes, i + NODE_KEY_OFFSET)));
    }

    len = llGetListLength(gPendingNodes);
    llOwnerSay("gPendingNodes:");
    for(i=0; i<len; i+=NODE_STRIDE) {
        llOwnerSay(llList2String(gPendingNodes, i + NODE_ID_OFFSET) + ": "
            + llList2String(gPendingNodes, i + NODE_POS_OFFSET));
    }


    len = llGetListLength(gNodeRelations);
    llOwnerSay("NODE RELATIONS:");
    for(i=0; i<len; ++i) {
        integer rel = llList2Integer(gNodeRelations, i);
        llOwnerSay(llList2String(gNodes, UNPACK_REL_SRC(rel)) + ": "
            + llList2String(gNodes, UNPACK_REL_DST(rel)));
    }

    len = llGetListLength(gPendingRelations);
    llOwnerSay("PENDING NODE RELATIONS:");
    for(i=0; i<len; ++i) {
        integer rel = llList2Integer(gPendingRelations, i);
        llOwnerSay(llList2String(gNodes, UNPACK_REL_SRC(rel)) + ": "
            + llList2String(gNodes, UNPACK_REL_DST(rel)));
    }

    llOwnerSay("Free Memory: " + (string)llGetFreeMemory());
}

trackNode(string node_id, key node_key) {
    gNodes += [node_id, compressKey(node_key)];
}

untrackNode(string node_id, integer kill_relations) {
    integer node_idx = llListFindList(gNodes, [node_id]);
    if (node_idx == -1)
        return;

    if (kill_relations) {
        integer len = llGetListLength(gNodeRelations);
        integer i;
        // Backwards iteration so we can remove as we go without changing indices
        for(i=len-1; i>=0; --i) {
            integer rel = llList2Integer(gNodeRelations, i);
            integer src_idx = UNPACK_REL_SRC(rel);
            integer dst_idx = UNPACK_REL_DST(rel);
            integer new_src_idx = src_idx;
            integer new_dst_idx = dst_idx;

            // removing this node will shift all indices down, may need to update
            // the relation list to acommodate.
            if (src_idx > node_idx)
                new_src_idx -= NODE_STRIDE;
            if (dst_idx > node_idx)
                new_dst_idx -= NODE_STRIDE;

            if (src_idx == node_idx || dst_idx == node_idx) {
                // relation stemming from or pointing to the removed node,
                // remove the relation. make sure to account for the removed
                // node_idx when doing the lookup
                string src_id = llList2String(gNodes, src_idx);
                string dst_id = llList2String(gNodes, dst_idx);
                llRegionSay(NODE_CHANNEL, "arrow_kill:" + src_id + ":" + dst_id);
                gNodeRelations = llDeleteSubList(gNodeRelations, i, i);
            } else if (new_src_idx != src_idx || new_dst_idx != dst_idx) {
                integer new_rel = PACK_RELATION(new_src_idx, new_dst_idx);
                gNodeRelations = llListReplaceList(gNodeRelations, [new_rel], i, i);
            }
        }
    }
    gNodes = llDeleteSubList(gNodes, node_idx, node_idx + NODE_STRIDE - 1);
}

pruneNodes() {
    integer len = llGetListLength(gNodes);
    integer i;
    // disconnect nodes that are no longer represented in-world
    for(i=len-NODE_STRIDE; i>=0; i-=NODE_STRIDE) {
        // no mass == gone
        key node_key = uncompressKey(llList2String(gNodes, i + NODE_KEY_OFFSET));
        if (llGetObjectMass(node_key) == 0.0) {
            untrackNode(llList2String(gNodes, i + NODE_ID_OFFSET), TRUE);
        }
    }
}

saveNodes() {
    llMessageLinked(LINK_THIS, IPC_INIT_SAVE_INWORLD_STATE, "", NULL_KEY);
    integer i;
    integer len = llGetListLength(gNodes);
    for(i=0; i<len; i+=NODE_STRIDE) {
        string node_id = llList2String(gNodes, i + NODE_ID_OFFSET);
        key node_key = uncompressKey(llList2String(gNodes, i + NODE_KEY_OFFSET));
        vector node_pos = llList2Vector(llGetObjectDetails(node_key, [OBJECT_POS]), 0);
        llMessageLinked(LINK_THIS, IPC_SAVE_NODE, node_id, (key)((string)node_pos));
        // message queueing limits...
        if ((i % 25) == 0)
            llSleep(0.5);
    }
    len = llGetListLength(gNodeRelations);
    for(i=0; i<len; ++i) {
        integer rel = llList2Integer(gNodeRelations, i);
        llMessageLinked(
            LINK_THIS,
            IPC_SAVE_RELATION,
            llList2String(gNodes, UNPACK_REL_SRC(rel)),
            (key)llList2String(gNodes, UNPACK_REL_DST(rel))
        );
        if ((i % 25) == 0)
            llSleep(0.5);
    }
    llMessageLinked(LINK_THIS, IPC_FINISH_SAVE_INWORLD_STATE, "", NULL_KEY);
    gGraphDirty = FALSE;
}

clearAll() {
    llRegionSay(NODE_CHANNEL, "node_kill_all:" + gOwnLogicalID);
    llRegionSay(NODE_CHANNEL, "arrow_kill_all:" + gOwnLogicalID);
    gNodes = [];
    gNodeRelations = [];
    gPendingNodes = [];
    gPendingRelations = [];
    gArrowPool = [];
    gNeededArrows = 0;
    gNeededNodes = 0;
    gAvailRezSlots = MAX_REZ_SLOTS;
}

initRestoreNodes(integer restore_arrows) {
    clearAll();
    gRestoring = TRUE;
    gRestoreArrows = restore_arrows;
    gLastRezTime = llGetUnixTime();
    llMessageLinked(LINK_THIS, IPC_REQUEST_RESTORE_FROM_DATA, "", NULL_KEY);
}


addRelation(string src, string dst) {
    list rel = [PACK_RELATION_FROM_IDS(gNodes, src, dst)];
    if (llListFindList(gNodeRelations, rel) == -1) {
        gPendingRelations += rel;
        ++gNeededArrows;
        tryRezPending();
    }
}

removeRelation(string src, string dst) {
    list rel = [PACK_RELATION_FROM_IDS(gNodes, src, dst)];
    integer idx = llListFindList(gNodeRelations, rel);
    if (idx != -1) {
        gNodeRelations = llDeleteSubList(gNodeRelations, idx, idx);
    }
    llRegionSay(NODE_CHANNEL, "arrow_kill:" + src + ":" + dst);
}


updateNodeRelations() {
    if (gPendingRelations == [])
        return;
    integer i;
    integer len = llGetListLength(gPendingRelations);
    for(i=len-1; i>=0; --i) {
        if (gArrowPool == [])
            return;
        integer rel = llList2Integer(gPendingRelations, i);
        string src_id = llList2String(gNodes, UNPACK_REL_SRC(rel));
        string dst_id = llList2String(gNodes, UNPACK_REL_DST(rel));
        string src_key = nodeIDToKey(src_id);
        string dst_key = nodeIDToKey(dst_id);
        if (src_key != NULL_KEY && dst_key != NULL_KEY) {
            string msg = llDumpList2String(["arrow_add", src_id, src_key, dst_id, dst_key, gOwnLogicalID], ":");
            llRegionSayTo(llList2Key(gArrowPool, 0), NODE_CHANNEL, msg);

            gPendingRelations = llDeleteSubList(gPendingRelations, i, i);
            gArrowPool = llDeleteSubList(gArrowPool, 0, 0);
            gNodeRelations += [rel];
        }
    }
}

tryRezPending() {
    integer i;
    while (gNeededNodes > 0 && gAvailRezSlots > 0) {
        llMessageLinked(LINK_SET, IPC_REZ_PRIM, (string)(++gRezNum), (key)"node");
        --gAvailRezSlots;
        --gNeededNodes;
    }
    while (gNeededArrows > 0 && gAvailRezSlots > 0) {
        llMessageLinked(LINK_SET, IPC_REZ_PRIM, (string)(++gRezNum), (key)"arrow");
        --gAvailRezSlots;
        --gNeededArrows;
    }
    // llOwnerSay("rez " + llDumpList2String([gAvailRezSlots, gNeededArrows, gNeededNodes], "|"));
}


handleNodeDuplicated(key existing_key, key node_key, string node_id) {
    // Ask the original object to give itself a new ID.
    string gen_node_id = generateLogicalID();
    llRegionSayTo(existing_key, NODE_CHANNEL, "node_reset:" + gen_node_id + ":" + gOwnLogicalID);
    // rebind node_id to the new object's key
    integer node_idx = llListFindList(gNodes, [node_id]);
    integer node_key_idx = node_idx + NODE_KEY_OFFSET;
    gNodes = llListReplaceList(gNodes, [compressKey(node_key)], node_key_idx, node_key_idx);
    // Tell any arrows to start pointing at the new object
    llRegionSay(NODE_CHANNEL, "arrow_node_identity:" + node_id + ":" + (string)node_key);
    // add the node back to the list with its new ID
    trackNode(gen_node_id, existing_key);
    // make a bidirectional relationship between the two nodes since that's what
    // you'll want most of the time.
    addRelation(gen_node_id, node_id);
    addRelation(node_id, gen_node_id);
}

handleNodeRenamed(string existing_id, key node_key, string node_id) {
    // kill all relations, too annoying to deal with for now.
    untrackNode(existing_id, TRUE);
    trackNode(node_id, node_key);
}


default {
    state_entry() {
        restoreLogicalID(TRUE);
        gMenuChannel = MENU_CHANNEL_BASE ^ llHash(llGetObjectDesc());
        gConnectionMenuChannel = CONNECTION_MENU_CHANNEL_BASE ^ llHash(llGetObjectDesc());
        llListen(NODE_MASTER_CHANNEL, "", "", "");
        llListen(PATHFINDING_REQ_CHANNEL, "", "", "");
        llListen(gMenuChannel, "", "", "");
        llListen(gConnectionMenuChannel, "", "", "");
        llSetColor(<1, 0, 1>, ALL_SIDES);
        clearAll();
        llSetTimerEvent(1);
    }

    on_rez(integer start_param) {
        llResetScript();
    }

    listen(integer channel, string name, key id, string msg) {
        // only non-owner messages we want to reply to are path requests
        if (llGetOwnerKey(id) != llGetOwner() && channel != PATHFINDING_REQ_CHANNEL)
            return;

        list params = llParseStringKeepNulls(msg, [":"], []);
        string cmd = llList2String(params, 0);
        params = llDeleteSubList(params, 0, 0);

        if (channel == NODE_MASTER_CHANNEL) {
            key node_key = id;
            if (cmd == "node_alive") {
                // A node just came on the scene and is telling us about itself
                string parent_id = llList2String(params, 1);
                if (parent_id != "" && parent_id != gOwnLogicalID) {
                    return;
                }
                string node_id = llList2String(params, 0);
                string existing_id = nodeKeyToID(node_key);
                key existing_key = nodeIDToKey(node_id);
                if (existing_id == "" && existing_key == NULL_KEY) {
                    trackNode(node_id, node_key);
                    llRegionSayTo(node_key, NODE_CHANNEL, "node_reset:" + node_id + ":" + gOwnLogicalID);
                    gGraphDirty = TRUE;
                } else if (existing_id != "" && existing_id != node_id) {
                    // an in-world object we were tracking is now claiming to represent a different node?
                    llOwnerSay("node hello from " + (string)node_key + " had mismatch, " + node_id + " != " + existing_id);
                    handleNodeRenamed(existing_id, node_key, node_id);
                    gGraphDirty = TRUE;
                } else if (existing_key != node_key) {
                    // node ID collides with an existing node object. Probably happened due to shift drag
                    // duplicate. That leaves the _original_ object selected and leaves a duplicate in the
                    // old position.
                    handleNodeDuplicated(existing_key, node_key, node_id);
                    gGraphDirty = TRUE;
                }
            } else if (cmd == "node_touched") {
                string clicked_id = nodeKeyToID(node_key);
                // not our node.
                if (clicked_id == "")
                    return;
                if (llList2String(params, 0) != gOwnLogicalID)
                    return;
                key toucher_id = llList2Key(params, 1);
                if (toucher_id != llGetOwner())
                    return;

                if (gFirstClicked != "" && gSecondClicked != "") {
                    // the dialog triggered, but they probably hit ignore.
                    // treat this as if it was a click on a first node.
                    gFirstClicked = clicked_id;
                    gSecondClicked = "";
                } else if (gFirstClicked != "") {
                    if (clicked_id != gFirstClicked) {
                        gSecondClicked = clicked_id;
                        llDialog(toucher_id, "What do you want to do with the connection?", ["one-way", "two-way", "remove", "find path"], gConnectionMenuChannel);
                    }
                } else {
                    gFirstClicked = clicked_id;
                }
                gClickTimeout = llGetUnixTime() + 20;
            }
        } else if (channel == gMenuChannel) {
            if (msg == "dump") {
                dumpNodeDetails();
            } else if (msg == "save") {
                if (llGetListLength(gNodes)) {
                    saveNodes();
                } else {
                    llOwnerSay("Refusing to save empty node list");
                }
            } else if (msg == "restore") {
                initRestoreNodes(TRUE);
            } else if (msg == "rest. norel") {
                initRestoreNodes(FALSE);
            } else if (msg == "clear") {
                clearAll();
                llResetScript();
            }
        } else if (channel == gConnectionMenuChannel) {
            if (msg == "remove") {
                removeRelation(gFirstClicked, gSecondClicked);
                removeRelation(gSecondClicked, gFirstClicked);
                gGraphDirty = TRUE;
            } else if (msg == "one-way") {
                addRelation(gFirstClicked, gSecondClicked);
                removeRelation(gSecondClicked, gFirstClicked);
                gGraphDirty = TRUE;
            } else if (msg == "two-way") {
                addRelation(gFirstClicked, gSecondClicked);
                addRelation(gSecondClicked, gFirstClicked);
                gGraphDirty = TRUE;
            } else if (msg == "find path") {
                if (gGraphDirty) {
                    llOwnerSay("Refusing to find path, graph is dirty");
                } else {
                    llOwnerSay("Calculating path from " + gFirstClicked + " to " + gSecondClicked);
                    llMessageLinked(LINK_THIS, IPC_REQUEST_PATH, gFirstClicked + ":" + gSecondClicked, NULL_KEY);
                }
            }
            gFirstClicked = "";
            gSecondClicked = "";
            gClickTimeout = 0;
        } else if (channel == PATHFINDING_REQ_CHANNEL) {
            integer num;
            if (cmd == "find_path")
                num = IPC_REQUEST_PATH;
            else if (cmd == "find_path_vectors")
                num = IPC_REQUEST_PATH_VECTORS;
            else
                return;

            // they weren't even asking us.
            if (gOwnLogicalID == "" || llList2String(params, 0) != gOwnLogicalID) {
                return;
            }

            string link_msg = llList2String(params, 1) + ":" + llList2String(params, 2);
            llMessageLinked(LINK_THIS, num, link_msg, id);
        }
    }

    link_message(integer sender_num, integer num, string str, key id) {
        if (num == IPC_RESTORE_NODE) {
            gPendingNodes += [str, (vector)((string)id)];
            ++gNeededNodes;
        } else if (num == IPC_RESTORE_RELATION) {
            // Don't try to rez the arrow yet, we expect more data to come in.
            // gPendingNodes should end up with the same order and stride length
            // as gNodes, so this is fine.
            gPendingRelations += [PACK_RELATION_FROM_IDS(gPendingNodes, str, (string)id)];
            ++gNeededArrows;
        } else if (num == IPC_FINISH_RESTORE_FROM_DATA) {
            if (!gRestoreArrows) {
                gNeededArrows = 0;
                gNodeRelations = gPendingRelations;
                gPendingRelations = [];
            }
            llOwnerSay("Got data from data manager, rezzing...");
            tryRezPending();
            gGraphDirty = FALSE;
        } else if (num == IPC_PATH_RESPONSE) {
            if (id) {
                llRegionSayTo(id, PATHFINDING_RESP_CHANNEL, "path:" + str);
            } else {
                llOwnerSay("PATH:");
                llOwnerSay(str);
            }
        }
    }

    object_rez(key id) {
        // a rez completing frees up a rez slot
        gLastRezTime = llGetUnixTime();
        ++gAvailRezSlots;
        if (llGetOwnerKey(id) != llGetOwner()) {
            llOwnerSay("Failed a rez?");
            return;
        }
        string name = (string)llGetObjectDetails(id, [OBJECT_NAME]);
        if (name == "node") {
            if (gPendingNodes == []) {
                llOwnerSay("Rezzed node with no pending nodes???");
                return;
            }
            string node_id = llList2String(gPendingNodes, NODE_ID_OFFSET);
            vector node_pos = llList2Vector(gPendingNodes, NODE_POS_OFFSET);

            llRegionSayTo(id, NODE_CHANNEL, "node_assign:" + node_id + ":" + gOwnLogicalID + ":" + (string)node_pos);

            gPendingNodes = llDeleteSubList(gPendingNodes, 0, NODE_STRIDE - 1);
            trackNode(node_id, id);
        } else if (name == "arrow") {
            if (gPendingRelations == []) {
                llOwnerSay("Rezzed arrow with no pending relations???");
                return;
            }
            gArrowPool += [id];
            updateNodeRelations();
        }
        if (gNeededArrows || gNeededNodes || llGetListLength(gPendingNodes) || llGetListLength(gPendingRelations)) {
            tryRezPending();
        } else if (gRestoring) {
            gRestoring = FALSE;
            llOwnerSay("Done rez");
        }
    }

    touch_start(integer touch_num) {
        if (llDetectedKey(0) != llGetOwner())
            return;
        llDialog(llDetectedKey(0), "Node Management", ["dump", "save", "restore", "rest. norel", "clear"], gMenuChannel);
    }

    timer() {
        ++gTickCount;
        // did the owner change our identity by editing the object description
        if (llGetObjectDesc() != gOwnLogicalID + ":") {
            if (gOwnLogicalID != "") {
                // get rid of any existing nodes or arrows
                clearAll();
            }
            llResetScript();
        }
        if (gClickTimeout && gClickTimeout < llGetUnixTime()) {
            gFirstClicked = "";
            gSecondClicked = "";
            gClickTimeout = 0;
        }
        if (!(gTickCount % PRUNE_NODES_EVERY)) {
            pruneNodes();
        }
        if (gNeededArrows || gNeededNodes) {
            // something screwed up and didn't even give us a failed rez message
            // parcel may be full.
            if (llGetUnixTime() > gLastRezTime + 10) {
                gNeededNodes = 0;
                gNeededArrows = 0;
                gRestoring = FALSE;
                llOwnerSay("Restore got stuck, inconsistent state! Is the parcel full?");
            }
        }
        updateNodeRelations();
    }
}
