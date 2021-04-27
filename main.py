"""
    Para esse trabalho cada celula tem o tamanho de 3.5m
    A velocidade maxima dos carros é de 17.5 m/s ou 63 km/h ou 5 celulas/s, esse valor foi escolhido para facilitar as contas
    e ser proximo do valor maximo real do BRT: 60km/h
    O veiculo tem o tamanho de 21 metros ou 6 celulas
"""
import random
import time

from copy import deepcopy 

HIGHWAY_LENGHT = 50 # 6000
MAX_VELOCITY = 4 # 5
VEHICLE_LENGHT = 2 # 6
VEHICLE_IGLE_TIME = 5
STATION_LENGHT = 3 * VEHICLE_LENGHT
RUNWAYS_LENGHT = 2
# if NEW_VEHICLE_DELAY = -1 read a file with name vehicles_timestamp to get time to arivel new vehicles
NEW_VEHICLE_DELAY = -1 #5
SLOW_DOWN_PROBABILITY = 0.25
MUST_PRINT_RESULTS = True

# veiculos passando as estações 2 e 3 direto
# veiculo n esta parando na pista principal quando n tem espaco na estacao
# veiculos saindo da estacao estao com prioridade

class Vehicle:
    def __init__(self, velocity=0, x=None, y=None, stations=None, igle_time=None):
        self.velocity = velocity
        self.x = x
        self.y = y
        self.stations = stations or []
        self.igle_time = igle_time or VEHICLE_IGLE_TIME
        self.stoped = False

    def __str__(self):
        return f'{self.velocity}'

    def __repr__(self):
        return self.__str__()

class Station:
    def __init__(self, x, y=1, lenght=STATION_LENGHT):
        self.x = x
        self.y = y
        self.lenght = lenght
    
    def __repr__(self):
        return f'St {self.x} lenght:{self.lenght}'

def start_simulation():
    highway, old_highway, step, vehicles, stations = start_variabels()
    while must_exec(step):
        highway, old_highway = simulation_step(highway, old_highway, step, vehicles, stations)
        if MUST_PRINT_RESULTS:
            show_highway(highway, stations)
        step += 1
        time.sleep(1)
    show_highway(highway)

def start_variabels():
    random.seed(10000)
    vehicles = []
    stations = load_stations()
    highway = {
        runway: {
            position: None for position in range(0, HIGHWAY_LENGHT)
        } for runway in range(0, RUNWAYS_LENGHT)
    }
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
    if step >= 100:
        must_continue = False

    return must_continue

def simulation_step(highway, old_highway, step, vehicles, stations):
    change_runway(highway, old_highway, vehicles, stations)
    move_vehicles(highway, old_highway, vehicles, stations)
    create_new_vehicles(highway, vehicles, step)
    old_highway = deepcopy(highway)
    return highway, old_highway

def change_runway(highway, old_highway, vehicles, stations):
    stations_index = get_stations_index(stations)
    for vehicle in vehicles:
        if vehicle.x in stations_index:
            move_on_station(vehicle, highway, old_highway, stations)

def move_on_station(vehicle, highway, old_highway, stations):
    station = get_station(vehicle.x, stations)
    if must_change_runway(vehicle, station, old_highway):
        old_highway[vehicle.y][vehicle.x] = None
        highway[vehicle.y][vehicle.x] = None
        if vehicle.y == 0:
            vehicle.y = 1
        else:
            vehicle.y = 0
        old_highway[vehicle.y][vehicle.x] = vehicle

def get_station(x, stations):
    for station in stations:
        if x >= station.x and x <= station.x + station.lenght - 1:
            return station

def must_change_runway(vehicle, station, highway):
    return (
        (vehicle.x == station.x + VEHICLE_LENGHT - 1
         and highway[1][vehicle.x] is None)
        or (vehicle.x == station.x + station.lenght - 1
         and highway[0][vehicle.x] is None
         and vehicle.stoped == False)
    )



def move_vehicles(highway, old_highway, vehicles, stations):
    change_velocities(old_highway, vehicles, stations)
    vehicles_to_drop = []
    for vehicle in vehicles:
        highway[vehicle.y][vehicle.x] = None
        if vehicle.x + vehicle.velocity < HIGHWAY_LENGHT:
            vehicle.x = vehicle.x + vehicle.velocity
            highway[vehicle.y][vehicle.x] = vehicle
        else:
            vehicles_to_drop.append(vehicle)

    for vehicle in vehicles_to_drop:
        vehicles.remove(vehicle)

def change_velocities(old_highway, vehicles, stations):
    for vehicle in vehicles:
        vehicle.velocity = get_new_velocity(old_highway, vehicle, stations)

def get_new_velocity(highway, vehicle, stations):
    next_vehicle_position = -1
    vehicle_move_range = vehicle.x + vehicle.velocity + VEHICLE_LENGHT  + 1
    end_of_range = vehicle_move_range if vehicle_move_range < HIGHWAY_LENGHT else HIGHWAY_LENGHT
    for index in range(vehicle.x + 1, end_of_range):
        range_cell = highway[vehicle.y][index]
        if must_check_cell(range_cell):
            next_vehicle_position = index
            break

    return apply_rules(highway, vehicle, next_vehicle_position, stations)

def must_check_cell(cell):
    return cell is not None

def apply_rules(highway, vehicle, next_vehicle_position, stations):
    if vehicle.y == 0:
        new_velocity = apply_in_highway_rules(highway, vehicle, next_vehicle_position, stations)
    else:
        new_velocity = apply_in_station_rules(highway, vehicle, next_vehicle_position, stations)

    return new_velocity

def apply_in_highway_rules(highway, vehicle, next_vehicle_position, stations):
    old_velocity = vehicle.velocity
    station = get_next_station(vehicle, stations)

    if station:
        new_velocity = rule_station_near_by(vehicle, station)
    elif next_vehicle_position != -1:
        new_velocity = rule_vehicle_near_by(vehicle, next_vehicle_position)
    else:
        chance = random_slow_down(old_velocity)
        if chance:
            new_velocity = old_velocity - 1
        elif old_velocity + 1 <= MAX_VELOCITY:
            new_velocity = old_velocity + 1
        else:
            new_velocity = old_velocity
    
    return new_velocity

def apply_in_station_rules(highway, vehicle, next_vehicle_position, stations):
    old_velocity = vehicle.velocity
    station = get_station(vehicle.x, stations)

    if vehicle.stoped:
        if vehicle.igle_time > 0:
            vehicle.igle_time -= 1
            new_velocity = 0
        else:
            vehicle.igle_time = VEHICLE_IGLE_TIME
            vehicle.stoped = False
            new_velocity = 0
    else:
        if next_vehicle_position != -1:
            new_velocity = rule_vehicle_near_by(vehicle, next_vehicle_position)
        else:
            if cant_move_in_station(vehicle, station):
                new_velocity = rule_station_end(vehicle, station)
            elif old_velocity + 1 <= MAX_VELOCITY:
                new_velocity = old_velocity + 1
            
    
    return new_velocity

def get_next_station(vehicle, stations):
    
    for index, station in enumerate(stations):
        if (index + 1 in vehicle.stations
            and vehicle.x <= station.x
            and vehicle.x + vehicle.velocity + 1 >= station.x + VEHICLE_LENGHT - 1):
            return station

def rule_vehicle_near_by(vehicle, next_vehicle_position):
    return next_vehicle_position - vehicle.x - VEHICLE_LENGHT

def rule_station_near_by(vehicle, station):
    return station.x + VEHICLE_LENGHT - 1 - vehicle.x

def random_slow_down(old_velocity):
    return SLOW_DOWN_PROBABILITY >= random.random() and old_velocity > 1

def cant_move_in_station(vehicle, station):
    return vehicle.x + vehicle.velocity + 1 > station.x + station.lenght - 1

def rule_station_end(vehicle, station):
    vehicle.stoped = True
    station_end = station.x + station.lenght - 1
    return station_end - vehicle.x



def create_new_vehicles(highway, vehicles, step):
    if NEW_VEHICLE_DELAY > 0:
        if step % NEW_VEHICLE_DELAY == 0:
            new_vehicle(highway, vehicles)
    else:
        new_vehicle_from_file(highway, vehicles, step)

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

def new_vehicle(highway, vehicles, where=0, stations=None):
    vehicles.append(
        Vehicle(velocity=1, x=where, y=0, stations=stations)
    )
    new_vehicle = vehicles[-1]
    highway[new_vehicle.y][new_vehicle.x] = new_vehicle



def show_highway(highway, stations):
    runway = highway[0]
    print('-', end='')
    for cell_index, cell in runway.items():
        if cell:
            print(f'-{cell.velocity}-', end='')
        else:
            print(f'- -', end='')
    print('-\n')

    stations_index = get_stations_index(stations)

    runway = highway[1]
    for cell_index, cell in runway.items():
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