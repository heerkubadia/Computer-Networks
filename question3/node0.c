#include <stdio.h>
#include <string.h>

extern struct rtpkt {
  int sourceid;       /* id of sending router sending this pkt */
  int destid;         /* id of router to which pkt being sent 
                         (must be an immediate neighbor) */
  int mincost[4];    /* min cost to node 0 ... 3 */
  };

extern int TRACE;
extern int YES;
extern int NO;
extern float clocktime;
#define INFINITY 999

struct distance_table 
{
  int costs[4][4];
} dt0;


/* students to write the following two routines, and maybe some others */

int connection_costs0[4] = { 0,  1,  3, 7 };
struct rtpkt pkt0[4];
int min_cost_track_0[4];

int min_0 ( int a, int b ) { 
    if(a<b){
        return a;
    }
    return b;
}
int min_0_array ( int a[] ) {
    return min_0(min_0(min_0(a[0], a[1]), a[2]), a[3]);
}

void recalculate_min_costs_0(){
    //calculate the minimum cost to every other node
    for(int i=0;i<4;i++){
        min_cost_track_0[i] = min_0_array(dt0.costs[i]);
    }
}
void send_updated_pkt0() {
    // Prepare packets for each destination node
    for (int i = 0; i < 4; i++) {
        pkt0[i].sourceid = 0;
        pkt0[i].destid = i; // Assign destination IDs (including self for now)
        memcpy(pkt0[i].mincost, min_cost_track_0, sizeof(min_cost_track_0)); // Copy current min cost array
    }

    // Transmit packets to all neighboring nodes (excluding self)
    for (int i = 0; i < 4; i++) {
        if (i != 0) {  // Avoid sending packet to self
            tolayer2(pkt0[i]); // Simulate sending packet
            printf("Time %.3f: Node %d dispatches a packet to Node %d carrying mincosts: [%d  %d  %d  %d]\n",
                   clocktime, pkt0[i].sourceid, pkt0[i].destid,
                   pkt0[i].mincost[0], pkt0[i].mincost[1],
                   pkt0[i].mincost[2], pkt0[i].mincost[3]);
        }
    }
}


void evaluate_and_send_pkt0() {
    int previous_min_costs[4];
    memcpy(previous_min_costs, min_cost_track_0, sizeof(min_cost_track_0));
    
    int has_changed = 0;

    // Recompute the current minimum costs from updated distance table
    recalculate_min_costs_0();

    // Check if any of the minimum costs have changed
    for (int i = 0; i < 4; i++) {
        if (previous_min_costs[i] != min_cost_track_0[i]) {
            has_changed = 1;
            break;
        }
    }
    // If a change occurred, broadcast updated info to neighbors
    if (has_changed) {
        send_updated_pkt0();
    } else {
        printf("\nNo change in minimum costs. Skipping packet transmission.\n");
    }
}


void rtinit0() 
{
    printf("rtinit0() is triggered at time t=: %0.3f\n", clocktime);

    // Initialize the distance table with the direct link costs
    for (int row = 0; row < 4; row++) {
        for (int col = 0; col < 4; col++) {
            if (row == col)
                dt0.costs[row][col] = connection_costs0[row];  // direct link
            else
                dt0.costs[row][col] = INFINITY;  // unknown paths
        }
    }

    printdt0(&dt0);

    recalculate_min_costs_0();
    send_updated_pkt0();
}


void rtupdate0(rcvdpkt)
struct rtpkt *rcvdpkt;
{
    int sender_id = rcvdpkt->sourceid;
    int receiver_id = rcvdpkt->destid;
    int received_costs[4];

    for (int i = 0; i < 4; i++)
        received_costs[i] = rcvdpkt->mincost[i];

        printf("rtupdate0()  executed at time t = %.3f as node %d sent a packet containing (%d  %d  %d  %d)\n", clocktime, sender_id, received_costs[0], received_costs[1], received_costs[2], received_costs[3]);

    // Attempt to update the distance table with new cost info
    for (int i = 0; i < 4; i++) {
        int new_cost = dt0.costs[sender_id][sender_id] + received_costs[i];

        if (new_cost < INFINITY)
            dt0.costs[i][sender_id] = new_cost;
        else
            dt0.costs[i][sender_id] = INFINITY;
    }
    // Print the updated table and forward new cost if changes occurred
    printdt0(&dt0);
    evaluate_and_send_pkt0();
}


printdt0(dtptr)
  struct distance_table *dtptr;
  
{
  printf("                via     \n");
  printf("   D0 |    1     2    3 \n");
  printf("  ----|-----------------\n");
  printf("     1|  %3d   %3d   %3d\n",dtptr->costs[1][1],
	 dtptr->costs[1][2],dtptr->costs[1][3]);
  printf("dest 2|  %3d   %3d   %3d\n",dtptr->costs[2][1],
	 dtptr->costs[2][2],dtptr->costs[2][3]);
  printf("     3|  %3d   %3d   %3d\n",dtptr->costs[3][1],
	 dtptr->costs[3][2],dtptr->costs[3][3]);
}

printmincost0(){
    printf("Minimum cost from %d to other nodes are: %d %d %d %d\n", 0, min_cost_track_0[0], min_cost_track_0[1],
           min_cost_track_0[2], min_cost_track_0[3] );
}

void linkhandler0(linkid, newcost)
  int linkid, newcost;

/* called when cost from 0 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */
	
{
    int old_dist_linkid_to_others[4];
    for(int i=0;i<4;i++){
        old_dist_linkid_to_others[i] = dt0.costs[i][linkid] - dt0.costs[linkid][linkid];
    }

    int new_dist_0_to_linkid = newcost;

    for(int i=0;i<4;i++){
        dt0.costs[i][linkid] = new_dist_0_to_linkid + old_dist_linkid_to_others[i]; // = new_dist_0_to_i (0 to i via linkid)
    }

    printdt0(&dt0);

    evaluate_and_send_pkt0();
}