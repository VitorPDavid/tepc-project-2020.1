#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define LANE_LENGTH 20
#define LANES_COUNT 2
#define VEHICLES_COUNT 20
#define TIME_STEPS 10
#define EMPTY -1
#define ABSENT -1
#define SPEED_MAX 5

struct Vehicle_{
    int speed;
    int lane;
    int position;
};

typedef struct Vehicle_ Vehicle;

Vehicle* start_vehicles(); //starts the vehicles with random speed (cell/sec) and their lane and positions with ABSENT
int** start_lanes(); //at the beginning, all cells in lanes are EMPTY
void random_case(Vehicle*, int**); //the vehicles are distributed among the lanes, at differente positions
void update_rules(Vehicle*, int**); //calculating the new speed and the new position of each vehicle following the NaSch model's rules
void update_data(Vehicle*, int**, int, int); //update the vehicle and lane data, based on the new speed and position calculated
int is_vehicle_outofbounds(Vehicle* vehicle); //check if the vehicle already reached the end of the lane
void print_vehicles(Vehicle*);
void print_lanes(int**);
void free_vehicles(Vehicle*);
void free_lanes(int**);

int main(){
    srand(time(0));
    Vehicle* vehicle = start_vehicles();
    int** lane = start_lanes();

    random_case(vehicle, lane);
    print_vehicles(vehicle);
    print_lanes(lane);

    for(int i = 0; i < TIME_STEPS; i++)
    {
        update_rules(vehicle, lane);
        print_lanes(lane);
    }

    free_vehicles(vehicle);
    free_lanes(lane);

    return 0;
}

//starts the vehicles with random speed (cell/sec) and their lane and positions with ABSENT
Vehicle* start_vehicles(){
    Vehicle* vehicle = (Vehicle*) malloc(sizeof(Vehicle) * VEHICLES_COUNT);

    for(int i = 0; i < VEHICLES_COUNT; i++)
    {
        vehicle[i].speed = rand() % (SPEED_MAX + 1);
        vehicle[i].lane = ABSENT;
        vehicle[i].position = ABSENT;
    }

    return vehicle;
}

//at the beginning, all cells in lanes are EMPTY
int** start_lanes(){
    int** lane = (int**) malloc(sizeof(int*) * LANES_COUNT);

    for(int i = 0; i < LANES_COUNT; i++)
    {
        lane[i] = (int*) malloc(sizeof(int) * LANE_LENGTH);
    }

    for(int i = 0; i < LANES_COUNT; i++)
    {
        for(int j = 0; j < LANE_LENGTH; j++)
        {
            lane[i][j] = EMPTY;
        }
    }

    return lane;
}

//the vehicles are distributed among the lanes, at differente positions
void random_case(Vehicle* vehicle, int** lane){
    int rand_lane;
    int rand_position;

    for(int i = 0; i < VEHICLES_COUNT; i++)
    {
        do{
            rand_lane = rand() % LANES_COUNT;
            rand_position = rand() % LANE_LENGTH;
        } while(lane[rand_lane][rand_position] != -1);

        vehicle[i].lane = rand_lane;
        vehicle[i].position = rand_position;

        lane[rand_lane][rand_position] = vehicle[i].speed;
    }
}

//calculating the new speed and the new position of each vehicle following the NaSch model's rules
void update_rules(Vehicle* vehicle, int** lane){
    int new_speed;
    int new_position;
    int probability;
    int distance;

    for(int i = 0; i < VEHICLES_COUNT; i++)
    {
        if(is_vehicle_outofbounds(&(vehicle[i])))
        {
            continue;
        }

        new_speed = vehicle[i].speed;
        probability = rand() % 100;

        //rule_1: new speed by acceleration
        new_speed = new_speed + 1 < SPEED_MAX ? new_speed + 1 : SPEED_MAX;

        //rule 2: new speed by probability
        if(probability < 50)
            new_speed--;

        //rule 3: new speed by vehicles distance
        if(vehicle[i].position < LANE_LENGTH - 1)
        {
            distance = -1;

            for(int position = vehicle[i].position + 1; position < LANE_LENGTH; position++)
            {
                if(lane[vehicle[i].lane][position] != -1)
                {
                    distance = position - vehicle[i].position;
                    break;
                }
            }

            if(distance != -1)
            {
                new_speed = new_speed > distance ? distance : new_speed;
            }
        }

        //rule 4: new position by new speed
        new_position = vehicle[i].position + new_speed;

        //printf("Antes %d %d %d\n", vehicle[i].speed, vehicle[i].lane, vehicle[i].position);

        update_data(&(vehicle[i]), lane, new_speed, new_position);

        //printf("Depois %d %d %d\n", vehicle[i].speed, vehicle[i].lane, vehicle[i].position);
    }
}

//update the vehicle and lane data, based on the new speed and position calculated
void update_data(Vehicle* vehicle, int** lane, int new_speed, int new_position){
    lane[vehicle->lane][vehicle->position] = -1;

    if(new_position > LANE_LENGTH - 1)
    {
        vehicle->speed = -1;
        vehicle->lane = -1;
        vehicle->position = -1;
    }
    else
    {
        vehicle->speed = new_speed;
        vehicle->position = new_position;
        lane[vehicle->lane][vehicle->position] = vehicle->speed;
    }
}

//check if the vehicle already reached the end of the lane
int is_vehicle_outofbounds(Vehicle* vehicle)
{
    if(vehicle->speed == -1 && vehicle->lane == -1 && vehicle->position == -1)
    {
        return 1;
    }

    return 0;
}

void print_vehicles(Vehicle* vehicle){
    for(int i = 0; i < VEHICLES_COUNT; i++)
    {
        printf("[%d] speed: %d | lane: %d | position: %d\n", i, vehicle[i].speed, vehicle[i].lane, vehicle[i].position);
    }
}

void print_lanes(int** lane){
    for(int i = 0; i < LANES_COUNT; i++)
    {
        printf("[%d] ", i);

        for(int j = 0; j < LANE_LENGTH; j++)
        {
            if(lane[i][j] == -1)
            {
                printf(". ");
            }
            else
            {
                printf("%d ", lane[i][j]);
            }
        }

        printf("\n");
    }
}

void free_vehicles(Vehicle* vehicle){
    free(vehicle);
}

void free_lanes(int** lane){
    for(int i = 0; i < LANES_COUNT; i++)
    {
        free(lane[i]);
    }

    free(lane);
}