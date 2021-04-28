"""
    Para esse trabalho cada celula tem o tamanho de 3.5m
    A velocidade maxima dos carros é de 17.5 m/s ou 63 km/h ou 5 celulas/s, esse valor foi escolhido para facilitar as contas
    e ser proximo do valor maximo real do BRT: 60km/h
    O veiculo tem o tamanho de 21 metros ou 6 celulas
"""
import random
import time

from math import floor
from copy import deepcopy 

# change this variables to modify simulation values
HIGHWAY_LENGHT = 6000 # 10.5 KM
MAX_VELOCITY = 5
VEHICLE_LENGHT = 6
VEHICLE_IGLE_TIME = 60 # 1 mim
STATION_LENGHT = 3 * VEHICLE_LENGHT
# if NEW_VEHICLE_DELAY = -1 read a file with name vehicles_timestamp to get time to arivel new vehicles
TIME_BETWEEN_STEPS = 0.5
#time in seconds to simulate
TIME_OF_SIMULATION = 3600
NEW_VEHICLE_DELAY = -1
SLOW_DOWN_PROBABILITY = 0.25
MUST_PRINT_RESULTS = True

# don't change this if you don't know what you're doing
RUNWAYS_LENGHT = 2
VEHICLE = 'VEHICLE'
STATION = 'STATION'
STATION_STOP = 'STOP'

class Vehicle:
    def __init__(self, velocity=0, x=None, y=None, stations=None, igle_time=None):
        self.velocity = velocity
        self.x = x
        self.y = y
        self.stations = stations or []
        self.igle_time = igle_time or VEHICLE_IGLE_TIME
        self.stoped = False
        self.await_to_get_in = False

    def __str__(self):
        return f'Ve [{self.x}][{self.y}] vel={self.velocity}'

    def __repr__(self):
        return self.__str__()

class Station:
    def __init__(self, x, y=1, lenght=STATION_LENGHT):
        self.x = x
        self.y = y
        self.lenght = lenght
        self.get_in_x = self.x + VEHICLE_LENGHT - 1
    
    def __repr__(self):
        return f'St {self.x} lenght:{self.lenght}'

def start_simulation():
    highway, old_highway, step, vehicles, stations = start_variabels()
    while must_exec(step):
        highway, old_highway, end_simulation = simulation_step(highway, old_highway, step, vehicles, stations)
        if MUST_PRINT_RESULTS:
            show_highway(highway, stations)
            time.sleep(TIME_BETWEEN_STEPS)      
        if end_simulation:
            break
        step += 1
    show_highway(highway, stations)

def start_variabels():
    random.seed(10000)
    vehicles = []
    stations = load_stations()
    highway = [
        [
            None for position in range(0, HIGHWAY_LENGHT)
        ] for runway in range(0, RUNWAYS_LENGHT)
    ]
    old_highway = deepcopy(highway)
    step = 1

    return highway, old_highway, step, vehicles, stations

def load_stations():
    stations = []
    with open('stations_locations.txt', 'r') as stations_file:
        for line in stations_file:
            stations.append(
                Station(x=int(line))
            )

    return tuple(stations)

def must_exec(step):
    must_continue = True
    if step >= TIME_OF_SIMULATION:
        must_continue = False

    return must_continue

def simulation_step(highway, old_highway, step, vehicles, stations):
    change_runway(highway, old_highway, vehicles, stations)
    move_vehicles(highway, old_highway, vehicles, stations)
    file_end = create_new_vehicles(highway, vehicles, step)
    end_simulation = False
    if file_end:
        end_simulation = True
    old_highway = deepcopy(highway)
    return highway, old_highway, end_simulation

# Change Runway

def change_runway(highway, old_highway, vehicles, stations):
    stations_index = get_stations_index(stations)
    for vehicle in vehicles:
        if vehicle.x in stations_index:
            move_on_station(vehicle, highway, old_highway, stations)

def move_on_station(vehicle, highway, old_highway, stations):
    station, station_index = get_station(vehicle.x, stations)
    if must_change_runway(vehicle, station, station_index):
        if can_change_runway(vehicle, station, old_highway):
            vehicle.await_to_get_in = False
            old_highway[vehicle.y][vehicle.x] = None
            highway[vehicle.y][vehicle.x] = None
            if vehicle.y == 0:
                vehicle.y = 1
            else:
                vehicle.y = 0
            old_highway[vehicle.y][vehicle.x] = vehicle
        else:
            vehicle.await_to_get_in = True
        
def get_station(x, stations):
    for station_index, station in enumerate(stations):
        if x >= station.x and x <= station.x + station.lenght - 1:
            return station, station_index + 1

def must_change_runway(vehicle, station, station_index):
    if vehicle.y == 0:
        return vehicle.x == station.x + VEHICLE_LENGHT - 1 and station_index in vehicle.stations
    else:
        return vehicle.x == station.x + station.lenght - 1

def can_change_runway(vehicle, station, highway):
    if vehicle.y == 0:
        min_range = station.get_in_x
        max_range = station.get_in_x + VEHICLE_LENGHT

        return not any(highway[1][min_range: max_range])
    else:
        bumper = vehicle.x - VEHICLE_LENGHT + 1

        min_range = bumper - MAX_VELOCITY
        if min_range < 0:
            min_range = 0
        max_range = vehicle.x + VEHICLE_LENGHT + 1
        if max_range > HIGHWAY_LENGHT:
            max_range = HIGHWAY_LENGHT

        can_change = False
        for near_by_vehicle in highway[0][min_range: max_range]:
            if near_by_vehicle and near_by_vehicle.x + near_by_vehicle.velocity < vehicle.x - VEHICLE_LENGHT:
                can_change = True
                break
        else:
            can_change = True

        return can_change

# Move vehicles

def move_vehicles(highway, old_highway, vehicles, stations):
    change_velocities(old_highway, vehicles, stations)
    vehicles_to_drop = []
    for vehicle in vehicles:
        highway[vehicle.y][vehicle.x] = None
        if vehicle.x + vehicle.velocity < HIGHWAY_LENGHT:
            vehicle.x = vehicle.x + vehicle.velocity
            if vehicle.stoped:
                vehicle.velocity = 0
            highway[vehicle.y][vehicle.x] = vehicle
        else:
            vehicles_to_drop.append(vehicle)

    for vehicle in vehicles_to_drop:
        vehicles.remove(vehicle)

def change_velocities(old_highway, vehicles, stations):
    for vehicle in vehicles:
        vehicle.velocity = move_rules(old_highway, vehicle, stations)

def move_rules(highway, vehicle, stations):
    if vehicle.y == 0:
        new_velocity = apply_highway_rules(vehicle, highway, stations)
    else:
        new_velocity = apply_station_rules(vehicle, highway, stations)

    return new_velocity

def apply_highway_rules(vehicle, highway, stations):
    old_velocity = vehicle.velocity
    vehicle_or_station, barrier_position = has_station_or_vehicle_near_by(vehicle, highway, stations)
    if vehicle.await_to_get_in:
        new_velocity = 0
    else:
        if vehicle_or_station == VEHICLE:
            new_velocity = rule_vehicle_near_by(vehicle, barrier_position)
        elif vehicle_or_station == STATION:
            new_velocity = rule_station_near_by(vehicle, barrier_position)
        else:
            chance = random_slow_down(old_velocity)
            if chance:
                new_velocity = old_velocity - 1
            elif old_velocity + 1 <= MAX_VELOCITY:
                new_velocity = old_velocity + 1
            else:
                new_velocity = old_velocity

    return new_velocity

def has_station_or_vehicle_near_by(vehicle, highway, stations):
    vehicle_or_station = None
    barrier_posistion = -1
    vehicle_near_by = get_near_by_vehicle_position(vehicle, highway)
    next_station = get_near_by_station(vehicle, stations)

    if vehicle_near_by == -1 and next_station != -1:
        vehicle_or_station = STATION
        barrier_posistion = next_station
    elif next_station == -1 and vehicle_near_by != -1:
        vehicle_or_station = VEHICLE
        barrier_posistion = vehicle_near_by
    elif next_station == -1 and vehicle_near_by == -1:
        vehicle_or_station = None
        barrier_posistion = -1
    elif vehicle_near_by - VEHICLE_LENGHT + 1 <= next_station:
        vehicle_or_station = VEHICLE
        barrier_posistion = vehicle_near_by
    else:
        vehicle_or_station = STATION
        barrier_posistion = next_station

    return vehicle_or_station, barrier_posistion

def get_near_by_vehicle_position(vehicle, highway):
    near_by_vehicle_position = -1
    colission_range = get_max_deslocation(vehicle) + VEHICLE_LENGHT
    end_of_range = colission_range if colission_range <= HIGHWAY_LENGHT else HIGHWAY_LENGHT
    for cell_index in range(vehicle.x + 1, end_of_range):
        cell = highway[vehicle.y][cell_index]
        if has_vehicle(cell):
            near_by_vehicle_position = cell_index
            break

    return near_by_vehicle_position

def get_near_by_station(vehicle, stations):
    near_by_station_position = -1
    next_station = get_next_station(vehicle, stations)
    get_in_range = get_max_deslocation(vehicle)
    
    if next_station and next_station.get_in_x <= get_in_range:
        near_by_station_position = next_station.get_in_x

    return near_by_station_position

def get_next_station(vehicle, stations):
    for index, station in enumerate(stations):
        if index + 1 in vehicle.stations and vehicle.x <= station.x:
            return station

def get_max_deslocation(vehicle):
    return vehicle.x + vehicle.velocity + 1

def apply_station_rules(vehicle, highway, stations):
    vehicle_near_by = get_near_by_vehicle_position(vehicle, highway)
    station, _ = get_station(vehicle.x, stations)
    old_velocity = vehicle.velocity

    if vehicle.stoped:
        if vehicle.igle_time > 0:
            vehicle.igle_time -= 1
            new_velocity = 0
        else:
            vehicle.igle_time = VEHICLE_IGLE_TIME
            vehicle.stoped = False
            new_velocity = 1
    else:
        vehicle_or_stop, barrier_position = has_vehicle_or_stop_near_by(vehicle, highway, stations)
        if vehicle_or_stop == VEHICLE:
            new_velocity = rule_vehicle_near_by(vehicle, barrier_position)
        elif vehicle_or_stop == STATION_STOP:
            new_velocity = rule_station_stop(vehicle, barrier_position)
        elif cant_move_in_station(vehicle, station):
            new_velocity = rule_station_end(vehicle, station)
        elif old_velocity + 1 <= MAX_VELOCITY:
            new_velocity = old_velocity + 1

    return new_velocity

def has_vehicle_or_stop_near_by(vehicle, highway, stations):
    vehicle_or_stop = None
    barrier_posistion = -1
    vehicle_near_by = get_near_by_vehicle_position(vehicle, highway)
    station_stop = get_near_by_stop(vehicle, stations)

    if vehicle_near_by == -1 and station_stop != -1:
        vehicle_or_stop = STATION_STOP
        barrier_posistion = station_stop
    elif station_stop == -1 and vehicle_near_by != -1:
        vehicle_or_stop = VEHICLE
        barrier_posistion = vehicle_near_by
    elif station_stop == -1 and vehicle_near_by == -1:
        vehicle_or_stop = None
        barrier_posistion = -1
    elif vehicle_near_by - VEHICLE_LENGHT + 1 <= station_stop:
        vehicle_or_stop = VEHICLE
        barrier_posistion = vehicle_near_by
    else:
        vehicle_or_stop = STATION_STOP
        barrier_posistion = station_stop

    return vehicle_or_stop, barrier_posistion

def rule_station_stop(vehicle, barrier_position):
    vehicle.stoped = True
    return barrier_position - vehicle.x

def get_near_by_stop(vehicle, stations):
    near_by_station_position = -1
    station, _ = get_station(vehicle.x, stations)
    get_in_range = get_max_deslocation(vehicle)
    stop_position = station.x - 1 + (floor(station.lenght/(2*VEHICLE_LENGHT)) + 1) * VEHICLE_LENGHT

    if stop_position <= get_in_range and vehicle.x < stop_position:
        near_by_station_position = stop_position

    return near_by_station_position

def rule_vehicle_near_by(vehicle, near_by_vehicle_position):
    return near_by_vehicle_position - vehicle.x - VEHICLE_LENGHT

def rule_station_near_by(vehicle, near_by_station_position):
    return near_by_station_position - vehicle.x

def random_slow_down(old_velocity):
    return SLOW_DOWN_PROBABILITY >= random.random() and old_velocity > 1

def cant_move_in_station(vehicle, station):
    return vehicle.x + vehicle.velocity + 1 > station.x + station.lenght - 1

def rule_station_end(vehicle, station):
    return station.x + station.lenght - 1 - vehicle.x

def has_vehicle(cell):
    return cell is not None


# utils
def create_new_vehicles(highway, vehicles, step):
    if NEW_VEHICLE_DELAY > 0:
        if step % NEW_VEHICLE_DELAY == 0:
            new_vehicle(highway, vehicles)
    else:
        return new_vehicle_from_file(highway, vehicles, step)

def new_vehicle_from_file(highway, vehicles, step):
    with open('vehicles_timestamp.txt', 'r') as vehicle_files:
        for line in vehicle_files:
            time_to_create, stations = line.split(' ')
            time_to_create = int(time_to_create)
            if step == time_to_create:
                stations = [int(x) for x in stations.split(',')]
                new_vehicle(highway, vehicles, stations=stations)
            elif time_to_create > step:
                break
        else:
            return True

def new_vehicle(highway, vehicles, where=0, stations=None):
    vehicles.append(
        Vehicle(velocity=1, x=where, y=0, stations=stations)
    )
    new_vehicle = vehicles[-1]
    highway[new_vehicle.y][new_vehicle.x] = new_vehicle

def show_highway(highway, stations):
    runway = highway[0]
    print('-', end='')
    for cell_index, cell in enumerate(runway):
        if cell:
            print(f'-{cell.velocity}-', end='')
        else:
            print(f'- -', end='')
    print('-\n')

    stations_index = get_stations_index(stations)

    runway = highway[1]
    for cell_index, cell in enumerate(runway):
        if cell_index in stations_index:
            if cell:
                print(f'-{cell.velocity}-', end='')
            else:
                print(f'- -', end='')
        else:
            print(f'   ', end='')
    print('\n')

def get_stations_index(stations):
    stations_index = []
    for station in stations:
        stations_index.extend(range(station.x, station.x + station.lenght))

    return stations_index


if __name__ == "__main__":
    start_simulation()