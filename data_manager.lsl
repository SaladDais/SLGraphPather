// responsible for long-term storage of node<->node relations
// also responsible for calculation of optimal paths in response to path queries

#include "shared.inc.lsl"


#define NODE_STRIDE 2
#define NODE_ID_OFFSET 0
#define NODE_POS_OFFSET 1

#define EDGE_STRIDE 4
#define EDGE_SRC_IDX_OFFSET 0
#define EDGE_DST_IDX_OFFSET 2
// distance from src->dst is the weight of the edge.
#define EDGE_DIST_OFFSET 3

#define MAX_DIST 9999999.9

// src_idx, "", dst_idx, dist
// "" gives us a boundary for llListFindList to work correctly.
// Essentially, we treat this as a Map[src_node_idx, List[Pair[distance, dst_node_idx]]]
// for quick lookups of neighbor data
list gWeightedEdges;


// node id, node position
list gNodes;
// ORed together indices into gNodes list
list gNodeRelations;


dumpNodeDetails() {
    integer i;
    integer len = llGetListLength(gNodes);
    llOwnerSay("gNodes:");
    for(i=0; i<len; i+=NODE_STRIDE) {
        llOwnerSay(llList2String(gNodes, i + NODE_ID_OFFSET) + ": "
            + llList2String(gNodes, i + NODE_POS_OFFSET));
    }

    len = llGetListLength(gNodeRelations);
    llOwnerSay("NODE RELATIONS:");
    for(i=0; i<len; ++i) {
        integer rel = llList2Integer(gNodeRelations, i);
        llOwnerSay(llList2String(gNodes, UNPACK_REL_SRC(rel)) + ": "
            + llList2String(gNodes, UNPACK_REL_DST(rel)));
    }
}


calculateEdgeWeights() {
    gWeightedEdges = [];
    integer i;
    integer len = llGetListLength(gNodeRelations);
    for(i=0; i<len; ++i) {
        integer rel = llList2Integer(gNodeRelations, i);
        string src = llList2String(gNodes, UNPACK_REL_SRC(rel));
        string dst = llList2String(gNodes, UNPACK_REL_DST(rel));
        integer src_idx = llListFindList(gNodes, [src]);
        integer dst_idx = llListFindList(gNodes, [dst]);
        float dist = llVecDist(
            llList2Vector(gNodes, src_idx + NODE_POS_OFFSET),
            llList2Vector(gNodes, dst_idx + NODE_POS_OFFSET)
        );
        gWeightedEdges += [src_idx / NODE_STRIDE, "", dst_idx / NODE_STRIDE, dist];
    }
    // sorted by src_idx
    gWeightedEdges = llListSort(gWeightedEdges, EDGE_STRIDE, TRUE);
}

// https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Pseudocode
list dijkstraFindPath(integer src_idx, integer dst_idx) {
    if (src_idx == dst_idx) {
        return [src_idx];
    }

    integer src = src_idx / NODE_STRIDE;
    integer dst = dst_idx / NODE_STRIDE;
    // shortest distance from source->vertex
    list dist;
    // idx of best previous path to vertex
    list prev;
    // bool, whether vertex is used in shortest path from src
    // Performs better than using `Q` as a queue because we need
    // to check membership very often no matter what, and llList2Integer()
    // is faster than llListFindList.
    list consumed;
    // num of verts
    integer V = llGetListLength(gNodes) / NODE_STRIDE;
    // num of unique edges
    integer edges_len = llGetListLength(gWeightedEdges);

    integer i;
    for (i = 0; i < V; i++) {
        // dist[v] ← INFINITY
        dist += [MAX_DIST];
        // prev[v] ← UNDEFINED
        prev += [-1];
        // add v to Q
        consumed += [FALSE];
    }

    // dist[source] ← 0
    dist = llListReplaceList(dist, [0.0], src, src);

    // Candidate node under consideration for path
    integer u;

    // while Q is not empty:
    // (not empty check is below, where we check `consumed` membership)
    while (TRUE) {
        // u ← vertex in Q with min dist[u]
        {
            float min_dist = MAX_DIST;
            integer v;
            for (v = 0; v < V; v++) {
                float cur_dist = llList2Float(dist, v);
                if (cur_dist <= min_dist) {
                    if (!llList2Integer(consumed, v)) {
                        min_dist = cur_dist;
                        u = v;
                    }
                }
            }
            // No unconsumed items in Q
            if (min_dist == MAX_DIST) {
                // Maybe unreachable? Islands in the graph?
                return [];
            }
        }

        if (u == dst) {
            // We only care about the ideal path from src->dst, not the distance src->*.
            // We can quit early if we found the path to dst.
            // walk the prev node list in reverse order to reconstruct
            // the best path from src to dst
            list path;
            while(u != -1) {
                path = [u * NODE_STRIDE] + path;
                u = llList2Integer(prev, u);
            }
            return path;
        }
        // remove u from Q
        consumed = llListReplaceList(consumed, [TRUE], u, u);

        // for each neighbor v of u
        // this finds the start index where edges stemming from u begin
        integer adj_start = llListFindList(gWeightedEdges, [u, ""]);
        for(i=adj_start; i<edges_len; i+=EDGE_STRIDE) {
            // Processed the last node reachable from u
            if (llList2Integer(gWeightedEdges, i + EDGE_SRC_IDX_OFFSET) != u)
                jump next;
            // is v still in Q?
            integer v = llList2Integer(gWeightedEdges, i + EDGE_DST_IDX_OFFSET);
            if (!llList2Integer(consumed, v)) {
                float u_dist = llList2Float(dist, u);
                // length(u, v)
                float edge_dist = llList2Float(gWeightedEdges, i + EDGE_DIST_OFFSET);
                // alt ← dist[u] + length(u, v)
                float alt = u_dist + edge_dist;
                // if alt < dist[v]:
                if (alt < llList2Float(dist, v)) {
                    // dist[v] ← alt
                    dist = llListReplaceList(dist, [alt], v, v);
                    // prev[v] ← u
                    prev = llListReplaceList(prev, [u], v, v);
                }
            }
        }
        @next;
    }

    // This line shouldn't be reachable but we need a return
    return [];
}


list pathToIDs(list path) {
    list path_new;
    integer i;
    integer len = llGetListLength(path);
    for(i=0; i<len; ++i) {
        path_new += [llList2String(gNodes, llList2Integer(path, i) + NODE_ID_OFFSET)];
    }
    path = [];
    return path_new;
}

list pathToVectors(list path) {
    list path_new;
    integer i;
    integer len = llGetListLength(path);
    for(i=0; i<len; ++i) {
        path_new += [llList2Vector(gNodes, llList2Integer(path, i) + NODE_POS_OFFSET)];
    }
    path = [];
    return path_new;
}


integer findClosestAccessibleNode(vector pos, key caster_key) {
    // find the closest node reachable from `pos` that doesn't
    // require passing through an obstruction according to llCastRay().
    integer i;
    integer len = llGetListLength(gNodes);
    // list of (distance_from_pos << 16) | node_idx
    list points;

    for(i=0; i<len; i+=NODE_STRIDE) {
        vector diff = llList2Vector(gNodes, i + NODE_POS_OFFSET) - pos;
        // disfavor nodes with large z differences from pos
        // depending on your use-case you may not want this.
        diff.z *= 2.0;
        // put the distance in the high bits so list will be sorted by dist
        points += [((integer)llVecDist(ZERO_VECTOR, diff) << 16) | i];
    }
    points = llListSort(points, 1, TRUE);

    // no accessibility check if caster_key is null, return early
    if (caster_key == NULL_KEY)
        // pick off just the index of the closest point
        return llList2Integer(points, 0) & 0xFFff;

    len = llGetListLength(points);
    for(i=0; i<len && i<5; ++i) {
        integer point = llList2Integer(points, i);
        integer node_idx = point & 0xFFff;
        // distance between src and node is below 2m, no need for raycast
        if ((point >> 16) < 2) {
            return node_idx;
        }
        vector node_pos = llList2Vector(gNodes, node_idx + NODE_POS_OFFSET);
        list cast_data = llCastRay(
            // slightly above the floor so we don't detect minor obstructions on the floor
            pos + <0,0,0.5>,
            node_pos + <0,0,0.5>,
            [
                // 2 max hits because we expect one our rays might intersect with the
                // object that requested the cast, we want to know about collisions with
                // anything _else_.
                RC_MAX_HITS, 2,
                // We can shove our way through physical shit and agents :)
                RC_REJECT_TYPES, RC_REJECT_PHYSICAL | RC_REJECT_LAND | RC_REJECT_AGENTS,
                RC_DATA_FLAGS, RC_GET_ROOT_KEY
            ]
        );
        integer j;
        integer num_hits = llList2Integer(cast_data, -1);
        // < 0 == error code
        if (num_hits >= 0) {
            for(j=0; j<num_hits; ++j) {
                // intersected with something that wasn't the caster's key
                if (llList2Key(cast_data, j * 2) != caster_key) {
                    jump next;
                }
            }
            return node_idx;
        }
        @next;
    }
    // raycast keeps failing for whatever reason, just return closest point.
    return llList2Integer(points, 0) & 0xFFff;
}

integer nodeRefToIdx(string node_ref, key caster_key) {
    // could either be a node name or a specific position
    if ((vector)node_ref == ZERO_VECTOR) {
        return llListFindList(gNodes, [node_ref]);
    } else {
        return findClosestAccessibleNode((vector)node_ref, caster_key);
    }
}


default {
    link_message(integer sender_num, integer num, string str, key id) {
        if (num == IPC_INIT_SAVE_INWORLD_STATE) {
            // node manager script is about to start sending new graph data
            gNodes = [];
            gNodeRelations = [];
            gWeightedEdges = [];
        } else if (num == IPC_FINISH_SAVE_INWORLD_STATE) {
            calculateEdgeWeights();
            llOwnerSay("Graph state saved");
        } else if (num == IPC_SAVE_NODE) {
            gNodes += [str, (vector)((string)id)];
        } else if (num == IPC_SAVE_RELATION) {
            gNodeRelations += PACK_RELATION(
                llListFindList(gNodes, [str]),
                llListFindList(gNodes, [(string)id])
            );
        } else if (num == IPC_REQUEST_RESTORE_FROM_DATA) {
            // node manager is requesting we send our view of the graph
            integer i;
            integer len = llGetListLength(gNodes);
            for(i=0; i<len; i+=NODE_STRIDE) {
                string node_id = llList2String(gNodes, i + NODE_ID_OFFSET);
                vector node_pos = llList2Vector(gNodes, i + NODE_POS_OFFSET);
                llMessageLinked(LINK_THIS, IPC_RESTORE_NODE, node_id, (key)((string)node_pos));
                // message queueing limits...
                if ((i % 25) == 0)
                    llSleep(0.5);
            }
            len = llGetListLength(gNodeRelations);
            for(i=0; i<len; ++i) {
                integer rel = llList2Integer(gNodeRelations, i);
                llMessageLinked(
                    LINK_THIS,
                    IPC_RESTORE_RELATION,
                    llList2String(gNodes, UNPACK_REL_SRC(rel)),
                    (key)llList2String(gNodes, UNPACK_REL_DST(rel))
                );
                // message queueing limits...
                if ((i % 25) == 0)
                    llSleep(0.5);
            }
            llMessageLinked(LINK_THIS, IPC_FINISH_RESTORE_FROM_DATA, "", NULL_KEY);
        } else if (num == IPC_REQUEST_PATH || num == IPC_REQUEST_PATH_VECTORS
          || num == IPC_REQUEST_PATH_FROM_VECTORS) {
            list path;
            list params = llParseString2List(str, [":"], []);

            integer src_idx = nodeRefToIdx(llList2String(params, 0), id);
            integer dst_idx = nodeRefToIdx(llList2String(params, 1), NULL_KEY);
            vector src_pos = (vector)llList2String(params, 0);

            if (src_idx != -1 && dst_idx != -1 && llGetListLength(gWeightedEdges)) {
                path = dijkstraFindPath(src_idx, dst_idx);
                if (num == IPC_REQUEST_PATH) {
                    path = pathToIDs(path);
                } else {
                    path = pathToVectors(path);
                    // src was a vector, see if we can elide the first node in the
                    // path, we may already be on the path from node1 to node2 in the
                    // path due to the way we do pos->node snapping. Otherwise we may
                    // end up with a path that has us walking "backwards" to the start
                    // node to then continue along the same path we were on to begin with
                    if (src_pos != ZERO_VECTOR && llGetListLength(path) >= 2) {
                        vector node1_pos = llList2Vector(path, 0);
                        vector node2_pos = llList2Vector(path, 1);
                        vector ideal_dir = llVecNorm(node2_pos - node1_pos);
                        vector src_dir = llVecNorm(node2_pos - src_pos);
                        // comparison of direction of travel from node1 to node2 in comparison
                        // to the direction from our position to node2
                        float dir_diff = llRot2Angle(llRotBetween(ideal_dir, src_dir));
                        if (dir_diff < 0.25) {
                            // directions of travel from node1->node2 and src_pos->node2 are
                            // very similar, elide node1.
                            // TODO: raycast as well?
                            path = llDeleteSubList(path, 0, 0);
                        }
                    }
                }
            }
            llMessageLinked(LINK_THIS, IPC_PATH_RESPONSE, llDumpList2String(path, ":"), id);
        }
    }
}
