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
} dt2;


/* students to write the following two routines, and maybe some others */

int connection_costs2[4] = { 3,  1,  0, 2 };
struct rtpkt pkt2[4];
int min_cost_track_2[4];

int min_2 ( int a, int b ) { 
    if(a<b){
        return a;
    }
    return b;
}
int min_2_array ( int a[] ) {
    return min_2(min_2(min_2(a[0], a[1]), a[2]), a[3]);
}

void recalculate_min_costs_2() {
    //calculate the minimum cost to every other node
    for(int i=0;i<4;i++){
        min_cost_track_2[i] = min_2_array(dt2.costs[i]);
    }
}

void send_updated_pkt2() {
    // Prepare packets for each destination node
    for(int i=0;i<4;i++) {
        pkt2[i].sourceid = 2;
        pkt2[i].destid = i; // Assign destination IDs (including self for now)
        memcpy(pkt2[i].mincost, min_cost_track_2, sizeof(min_cost_track_2));
    }
     // Transmit packets to all neighboring nodes (excluding self)
    for(int i=0;i<4;i++) {
        if(i!=2) { // Avoid sending packet to self
            tolayer2(pkt2[i]);
            printf("Time %.3f: Node %d dispatches a packet to Node %d carrying mincosts: [%d  %d  %d  %d]\n",
                clocktime, pkt2[i].sourceid, pkt2[i].destid,
                pkt2[i].mincost[0], pkt2[i].mincost[1],
                pkt2[i].mincost[2], pkt2[i].mincost[3]);
        }
    }
}

void evaluate_and_send_pkt2() {
    int previous_min_costs[4];
    memcpy(previous_min_costs, min_cost_track_2, sizeof(min_cost_track_2));
    
    int has_changed = 0;

    // Recompute the current minimum costs from updated distance table
    recalculate_min_costs_2();

    // Check if any of the minimum costs have changed
    for (int i = 0; i < 4; i++) {
        if (previous_min_costs[i] != min_cost_track_2[i]) {
            has_changed = 1;
            break;
        }
    }
    // If a change occurred, broadcast updated info to neighbors
    if (has_changed == 1) {   
        send_updated_pkt2();
    }
    else{
    printf("\nNo change in minimum costs. Skipping packet transmission.\n");
    }
}

void rtinit2() 
{
    printf("rtinit2() is triggered at time t=: %0.3f\n", clocktime);

    // Initialize the distance table with the direct link costs
    for(int row=0;row<4;row++){
        for(int col=0;col<4;col++){
            if(row==col)
                dt2.costs[row][col] = connection_costs2[row]; //direct link
            else
                dt2.costs[row][col] = INFINITY; //unknown paths
        }
    }
    printdt2(&dt2);
    recalculate_min_costs_2();
    send_updated_pkt2();
}


void rtupdate2(rcvdpkt)
  struct rtpkt *rcvdpkt;
  
{
    int sender_id = rcvdpkt->sourceid;
    int receiver_id = rcvdpkt->destid;
    int received_costs[4];

    for(int j= 0; j<4;j++)
        received_costs[j] =  rcvdpkt->mincost[j];

        printf("rtupdate0()  executed at time t = %.3f as node %d sent a packet containing (%d  %d  %d  %d)\n", clocktime, sender_id, received_costs[0], received_costs[1], received_costs[2], received_costs[3]);

    // Attempt to update the distance table with new cost info
    for(int i=0;i<4;i++){
        int new_cost = dt2.costs[sender_id][sender_id] + received_costs[i]; 

        if(new_cost<INFINITY)
            dt2.costs[i][sender_id] = new_cost;
        else
            dt2.costs[i][sender_id] = INFINITY;
    }

    // Print the updated table and forward new cost if changes occurred
    printdt2(&dt2);
    evaluate_and_send_pkt2();

}


printdt2(dtptr)
  struct distance_table *dtptr;
  
{
  printf("                via     \n");
  printf("   D2 |    0     1    3 \n");
  printf("  ----|-----------------\n");
  printf("     0|  %3d   %3d   %3d\n",dtptr->costs[0][0],
	 dtptr->costs[0][1],dtptr->costs[0][3]);
  printf("dest 1|  %3d   %3d   %3d\n",dtptr->costs[1][0],
	 dtptr->costs[1][1],dtptr->costs[1][3]);
  printf("     3|  %3d   %3d   %3d\n",dtptr->costs[3][0],
	 dtptr->costs[3][1],dtptr->costs[3][3]);
}

printmincost2(){
    printf("Minimum cost from %d to other nodes are: %d %d %d %d\n", 2, min_cost_track_2[0], min_cost_track_2[1],
           min_cost_track_2[2], min_cost_track_2[3] );
}