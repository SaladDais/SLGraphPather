//start_unprocessed_text
/*// public domain / CC-0.

// example of how a script can ask the pathfinding object for a path
// should normally use an at_target + waypoint + llSetForce() locomotion or something.

// should match the ID in the object description of the node manager object we want
// to consult for pathing.
string NODE_MANAGER_NAME = "REPLACEME";
// how many seconds it should take to travel a meter away
float TRAVEL_S_PER_M = 0.5;

// say "I summon thee" to summon the object.

integer PATHFINDING_REQ_CHANNEL = -21461423;
integer PATHFINDING_RESP_CHANNEL = -21461424;

list gWaypoints;
vector gLastPos;
vector gDesiredPos;
float gHeightOffset;

vector waypointToPos(vector waypoint) {
    // waypoint pos -> pos we should move to
    // all waypoints are 0.5m high cubes with the bottom touching the ground
    // chances are this object is not a 0.5m high cube, so the position it
    // needs to be on z will be different.
    // Note that this only really makes sense when you mainly have paths along the ground.
    return <waypoint.x, waypoint.y, waypoint.z - 0.25 + gHeightOffset>;
}

vector posToWaypoint(vector pos) {
    // our pos -> approximate waypoint pos
    return <pos.x, pos.y, pos.z + 0.25 - gHeightOffset>;
}

goToNextWaypoint() {
    while (gWaypoints != []) {
        // consume a waypoint from the list
        gDesiredPos = waypointToPos((vector)llList2String(gWaypoints, 0));
        gWaypoints = llDeleteSubList(gWaypoints, 0, 0);

        // KFM uses relative positions, so calculate the offset to where we want to go
        vector diff = gDesiredPos - gLastPos;
        float travel_time = llVecDist(gLastPos, gDesiredPos) * TRAVEL_S_PER_M;

        // Just try the next waypoint immediately if we're exactly over this node already
        if (travel_time >= 0.001) {
            // don't actually use KFM to move to the next waypoint if it's very near,
            // llSetKeyframedMotion() doesn't accept travel times this short.
            // We'll just let the llSetRegionPos() in the timer() event move it.
            if (travel_time >= 0.1) {
                llSetKeyframedMotion([diff, travel_time], [KFM_DATA, KFM_TRANSLATION]);
            }
            llSetTimerEvent(travel_time);
            return;
        }
    }
    llSetTimerEvent(0.0);
}

default {
    state_entry() {
        // bottom corner of bounding box, coords relative to root center.
        vector min_corner = llList2Vector(llGetBoundingBox(llGetKey()), 0);
        // should be our height offset from the ground
        gHeightOffset = -min_corner.z;

        llSetLinkPrimitiveParamsFast(LINK_THIS, [PRIM_PHYSICS_SHAPE_TYPE, PRIM_PHYSICS_SHAPE_CONVEX]);
        llSetKeyframedMotion([ZERO_VECTOR, 0.15], [KFM_DATA, KFM_TRANSLATION]);
        llSitTarget(<0,0,1>, ZERO_ROTATION);
        llListen(PATHFINDING_RESP_CHANNEL, "", "", "");
        llListen(0, "", "", "I summon thee");
    }

    listen(integer channel, string name, key id, string msg) {
        if (channel == PATHFINDING_RESP_CHANNEL) {
            if (llGetOwnerKey(id) != llGetOwner())
                return;

            list params = llParseString2List(msg, [":"], []);
            string cmd = llList2String(params, 0);
            params = llDeleteSubList(params, 0, 0);
            if (cmd != "path") {
                return;
            }
            if (params == []) {
                llOwnerSay("Couldn't find a path!");
                return;
            }
            llOwnerSay((string)llGetTime());
            gLastPos = llGetPos();
            gWaypoints = params;
            goToNextWaypoint();
        } else if (channel == 0) {
            // Stop moving if we were already moving, we were just summoned.
            llSetKeyframedMotion([], [KFM_COMMAND, KFM_CMD_PAUSE]);
            llSetTimerEvent(0);
            // TODO: Should probably account for their height offset for ground targets.
            vector target_pos = llList2Vector(llGetObjectDetails(id, [OBJECT_POS]), 0);
            string resp_msg = "find_path_vectors:" + NODE_MANAGER_NAME + ":" + (string)posToWaypoint(llGetPos()) + ":" + (string)target_pos;
            llRegionSay(PATHFINDING_REQ_CHANNEL, resp_msg);
            llResetTime();
        }
    }

    timer() {
        llSetKeyframedMotion([], [KFM_COMMAND, KFM_CMD_PAUSE]);
        // Have to set position at each waypoint because keyframed motion can
        // be interrupted by a sitter or owner selecting the object.
        // Might be better to have keyframed motion only move in the general direction
        // of the target with a short time step and keep doing that in a timer until
        // the target is actually reached.
        llSetRegionPos(gDesiredPos);
        gLastPos = gDesiredPos;
        goToNextWaypoint();
    }
}
*/
//end_unprocessed_text
//nfo_preprocessor_version 0
//program_version LSL PyOptimizer v0.3.0beta
//mono

list gWaypoints;
vector gLastPos = <0, 0, 0>;
vector gDesiredPos = <0, 0, 0>;
float gHeightOffset = 0;

vector waypointToPos(vector waypoint)
{
    return <waypoint.x, waypoint.y, ((float)-0.25) + waypoint.z + gHeightOffset>;
}

vector posToWaypoint(vector pos)
{
    return <pos.x, pos.y, 0.25 + pos.z + -gHeightOffset>;
}

goToNextWaypoint()
{
    while (gWaypoints != [])
    {
        gDesiredPos = waypointToPos((vector)llList2String(gWaypoints, 0));
        gWaypoints = llDeleteSubList(gWaypoints, 0, 0);
        vector diff = gDesiredPos - gLastPos;
        float travel_time = llVecDist(gLastPos, gDesiredPos) * 0.5;
        if (!(travel_time < 0.001))
        {
            if (!(travel_time < 0.1))
            {
                llSetKeyframedMotion((list)diff + travel_time, (list)2 + 2);
            }
            llSetTimerEvent(travel_time);
            return;
        }
    }
    llSetTimerEvent(((float)0));
}

default
{
    state_entry()
    {
        vector min_corner = llList2Vector(llGetBoundingBox(llGetKey()), 0);
        gHeightOffset = -min_corner.z;
        llSetLinkPrimitiveParamsFast(((integer)-4), (list)30 + 2);
        llSetKeyframedMotion((list)<((float)0), ((float)0), ((float)0)> + 0.15, (list)2 + 2);
        llSitTarget(<((float)0), ((float)0), ((float)1)>, <((float)0), ((float)0), ((float)0), ((float)1)>);
        llListen(((integer)-21461424), "", "", "");
        llListen(0, "", "", "I summon thee");
    }

    listen(integer channel, string name, key id, string msg)
    {
        if (channel ^ ((integer)-21461424))
        {
            if (!channel)
            {
                llSetKeyframedMotion([], (list)0 + 2);
                llSetTimerEvent(0);
                vector target_pos = llList2Vector(llGetObjectDetails(id, (list)3), 0);
                string resp_msg = "find_path_vectors:REPLACEME:" + (string)posToWaypoint(llGetPos()) + ":" + (string)target_pos;
                llRegionSay(((integer)-21461423), resp_msg);
                llResetTime();
            }
        }
        else
        {
            if (!(llGetOwnerKey(id) == llGetOwner()))
                return;
            list params = llParseString2List(msg, (list)":", []);
            string cmd = llList2String(params, 0);
            params = llDeleteSubList(params, 0, 0);
            if (!(cmd == "path"))
            {
                return;
            }
            if (params == [])
            {
                llOwnerSay("Couldn't find a path!");
                return;
            }
            llOwnerSay((string)llGetTime());
            gLastPos = llGetPos();
            gWaypoints = params;
            goToNextWaypoint();
        }
    }

    timer()
    {
        llSetKeyframedMotion([], (list)0 + 2);
        llSetRegionPos(gDesiredPos);
        gLastPos = gDesiredPos;
        goToNextWaypoint();
    }
}
