#ifndef SHARED_LSL_H
#define SHARED_LSL_H

integer NODE_CHANNEL = -21461419;
integer NODE_MASTER_CHANNEL = -21461420;
integer PATHFINDING_REQ_CHANNEL = -21461423;
integer PATHFINDING_RESP_CHANNEL = -21461424;


// relations are represented by a single shifted-together integer
// of src_idx and dst_idx, which are indices into gNodes pointing
// to a node ID.
#define UNPACK_REL_SRC(_shifted) ((_shifted) >> 16)
#define UNPACK_REL_DST(_shifted) ((_shifted) & 0xFFff)
#define PACK_RELATION(_src, _dst) (((_src) << 16) | (_dst))
// same as above, but using the node IDs rather than indices
#define PACK_RELATION_FROM_IDS(_list, _src_id, _dst_id) (PACK_RELATION( \
    llListFindList((_list), [(_src_id)]), \
    llListFindList((_list), [(_dst_id)]) \
))

///// node manager -> data manager
// start saving - no params
integer IPC_INIT_SAVE_INWORLD_STATE = 800;
// saving finished, send to server - no params
integer IPC_FINISH_SAVE_INWORLD_STATE = 801;
// str = node id, key = position vector
integer IPC_SAVE_NODE = 802;
// str = src id, id = dst id
integer IPC_SAVE_RELATION = 803;


// clear objects, restoring from data - no params
integer IPC_REQUEST_RESTORE_FROM_DATA = 900;
// all objects and relations restored - no params
integer IPC_FINISH_RESTORE_FROM_DATA = 901;
// str = node id, key = position vector
integer IPC_RESTORE_NODE = 902;
// str = src id, id = dst id
integer IPC_RESTORE_RELATION = 903;


// want a path in terms of node names from src->dst
// str = src_id:dst_id, id = callback_id
integer IPC_REQUEST_PATH = 1000;
// want a path in terms of vectors from src->dst
// str = src_id:dst_id, id = callback_id
integer IPC_REQUEST_PATH_VECTORS = 1001;
// want a path in terms of vectors from src->dst
// str = start_pos:end_pos, id = callback_id
integer IPC_REQUEST_PATH_FROM_VECTORS = 1002;
// str = list of vectors joined by ":"
integer IPC_PATH_RESPONSE = 1003;


// str=rez_num:object_name, id=message
integer IPC_REZ_PRIM = 1100;

string gOwnLogicalID;
string gParentLogicalID;

restoreLogicalID(integer create) {
    string desc = llGetObjectDesc();
    // does this even look like a valid description for us?
    if (llSubStringIndex(desc, ":") != -1) {
        list parsed = llParseString2List(desc, [":"], []);
        gOwnLogicalID = llList2String(parsed, 0);
        gParentLogicalID = llList2String(parsed, 1);
    } else if (create) {
        // Roughly 64**5 bits of entropy. Unique enough for us.
        gOwnLogicalID = generateLogicalID();
        gParentLogicalID = "";
        llSetObjectDesc(generateDescription());
    }
}

string generateDescription() {
    return gOwnLogicalID + ":" + gParentLogicalID;
}

string strReplace(string subject, string search, string replace) {
    return llDumpList2String(llParseStringKeepNulls(subject, [search], []), replace);
}

string compressKey(key k) {
    // Key Compression Copyright (C) 2009 Adam Wozniak and Doran Zemlja
    // Released into the public domain.
    // It produces fixed length encodings of 11 characters.
    string s = llToLower(strReplace((string) k, "-", "") + "0");
    string ret;
    integer i;

    string A;
    string B;
    string C;
    string D;

    for (i = 0; i < 32; 0) {
        A = llGetSubString(s, i, i);
        i++;
        B = llGetSubString(s, i, i);
        i++;
        C = llGetSubString(s, i, i);
        i++;
        D = "b";

        if (A == "0") {
            A = "e";
            D = "8";
        }
        else if (A == "d") {
            A = "e";
            D = "9";
        }
        else if (A == "f") {
            A = "e";
            D = "a";
        }

        ret += "%e"+A+"%"+D+B+"%b"+C;
    }
    return llUnescapeURL(ret);
}

string padDash(string s) {
    return
        llGetSubString(s, 0, 7) + "-" +
        llGetSubString(s, 8,11) + "-" +
        llGetSubString(s,12,15) + "-" +
        llGetSubString(s,16,19) + "-" +
        llGetSubString(s,20,31);
}

key uncompressKey(string s) {
    integer i;
    string ret;
    string A;
    string B;
    string C;
    string D;

    s = llToLower(llEscapeURL(s));
    for (i = 0; i < 99; i += 9) {
        A = llGetSubString(s,i+2,i+2);
        B = llGetSubString(s,i+5,i+5);
        C = llGetSubString(s,i+8,i+8);
        D = llGetSubString(s,i+4,i+4);

        if (D == "8") {
            A = "0";
        } else if (D == "9") {
            A = "d";
        } else if (D == "a") {
            A = "f";
        }
        ret = ret + A + B + C;
    }
    return padDash(ret);
}

string generateLogicalID() {
    // this doesn't seem very high entropy, what to do...
    return llGetSubString(llStringToBase64(compressKey(llGenerateKey())), 0, 5);
}


#endif
