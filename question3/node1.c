#include <stdio.h>
#include<string.h>

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
} dt1;


/* students to write the following two routines, and maybe some others */

int connection_costs1[4] = { 1,  0,  1, 999};
struct rtpkt pkt1[4];
int min_cost_track_1[4];

int min_1 ( int a, int b ) {
     if(a<b){
        return a;
     }
     return b;
}
int min_1_array ( int a[] ) {
    return min_1(min_1(min_1(a[0], a[1]), a[2]), a[3]);
}

void recalculate_min_costs_1(){
    //calculate the minimum cost to every other node
    for(int i=0;i<4;i++){
        min_cost_track_1[i] = min_1_array(dt1.costs[i]);
    }
}

void send_updated_pkt1(){
    // Prepare packets for each destination node
    for(int i=0;i<4;i++) {
        pkt1[i].sourceid = 1;
        pkt1[i].destid = i;// Assign destination IDs (including self for now)
        memcpy(pkt1[i].mincost, min_cost_track_1, sizeof(min_cost_track_1));// Copy current min cost array
    }
    // Transmit packets to all neighboring nodes (excluding self)
    for(int i=0;i<3;i++) { //No packet sent to last node 
        if(i!=1) {            // Avoid sending packet to self
            tolayer2(pkt1[i]); // Simulate sending packet
            printf("Time %.3f: Node %d dispatches a packet to Node %d carrying mincosts: [%d  %d  %d  %d]\n",
                clocktime, pkt1[i].sourceid, pkt1[i].destid,
                pkt1[i].mincost[0], pkt1[i].mincost[1],
                pkt1[i].mincost[2], pkt1[i].mincost[3]);
        }
    }
}

void evaluate_and_send_pkt1() {
    int previous_min_costs[4];
    memcpy(previous_min_costs, min_cost_track_1, sizeof(min_cost_track_1));
    int has_changed = 0;

    // Recompute the current minimum costs from updated distance table
    recalculate_min_costs_1();

    // Check if any of the minimum costs have changed
    for (int i = 0; i < 4; i++) {
        if (previous_min_costs[i] != min_cost_track_1[i]) {
            has_changed = 1;
        }
    }
    // If a change occurred, broadcast updated info to neighbors
    if (has_changed == 1) {    //min cost changed, so send new packets
        send_updated_pkt1();
    }
    else{
    printf("\nNo change in minimum costs. Skipping packet transmission.\n");
    }
}

void rtinit1() 
{
  printf("rtinit1() is triggered at time t=: %0.3f\n", clocktime);

  // Initialize the distance table with the direct link costs
  for(int row=0;row<4;row++){
    for(int col=0;col<4;col++){
      if(row==col)
        dt1.costs[row][col] = connection_costs1[row];// direct link
      else
        dt1.costs[row][col] = INFINITY;//unknown paths
    }
  }
  printdt1(&dt1);

    recalculate_min_costs_1();
    send_updated_pkt1();
}


void rtupdate1(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
    int sender_id = rcvdpkt->sourceid;
    int receiver_id = rcvdpkt->destid;
    int received_costs[4];
    for(int i= 0; i<4;i++)
        received_costs[i] =  rcvdpkt->mincost[i];

    printf("rtupdate1() executed at time t=: %0.3f as node %d sent a packet containing (%d  %d  %d  %d)\n", clocktime, sender_id,
        received_costs[0], received_costs[1], received_costs[2],received_costs[3]);

    // Attempt to update the distance table with new cost info
    for(int i=0;i<4;i++){
        int new_cost = dt1.costs[sender_id][sender_id] + received_costs[i];   //use the already calculated min_cost_track_1 path to all node
      
        if(new_cost<INFINITY)
            dt1.costs[i][sender_id] = new_cost;
        else
            dt1.costs[i][sender_id] = INFINITY;
    }
    // Print the updated table and forward new cost if changes occurred
    printdt1(&dt1);
    evaluate_and_send_pkt1();
}


printdt1(dtptr)
  struct distance_table *dtptr;
  
{
  printf("             via   \n");
  printf("   D1 |    0     2 \n");
  printf("  ----|-----------\n");
  printf("     0|  %3d   %3d\n",dtptr->costs[0][0], dtptr->costs[0][2]);
  printf("dest 2|  %3d   %3d\n",dtptr->costs[2][0], dtptr->costs[2][2]);
  printf("     3|  %3d   %3d\n",dtptr->costs[3][0], dtptr->costs[3][2]);

}

printmincost1(){
    printf("Minimum cost from %d to other nodes are: %d %d %d %d\n", 1, min_cost_track_1[0], min_cost_track_1[1],
           min_cost_track_1[2], min_cost_track_1[3] );
}

void linkhandler1(linkid, newcost)
int linkid, newcost;   
/* called when cost from 1 to linkid changes from current value to newcost*/
/* You can leave this routine empty if you're an undergrad. If you want */
/* to use this routine, you'll need to change the value of the LINKCHANGE */
/* constant definition in prog3.c from 0 to 1 */
	
{
    int old_dist_linkid_to_others[4];
    for(int i=0;i<4;i++){
        old_dist_linkid_to_others[i] = dt1.costs[i][linkid] - dt1.costs[linkid][linkid];
    }

    int new_dist_0_to_linkid = newcost;

    for(int i=0;i<4;i++){
        dt1.costs[i][linkid] = new_dist_0_to_linkid + old_dist_linkid_to_others[i]; // = new_dist_1_to_i (1 to i via linkid)
    }

    printdt1(&dt1);
    evaluate_and_send_pkt1();
}