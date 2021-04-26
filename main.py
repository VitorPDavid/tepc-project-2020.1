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
STATION_LENGHT = 4 # 12
MAX_VELOCITY = 4 # 5
VEHICLE_LENGHT = 2 # 6
RUNWAYS_LENGHT = 2
# if NEW_VEHICLE_DELAY = -1 read a file with name vehicles_timestamp to get time to arivel new vehicles
NEW_VEHICLE_DELAY = -1 #5
SLOW_DOWN_PROBABILITY = 0.3
MUST_PRINT_RESULTS = True

class Vehicle:
    def __init__(self, velocity=0, x=None, y=None):
        self.velocity = velocity
        self.x = x
        self.y = y

    def __str__(self):
        return f'{self.velocity}'

    def __repr__(self):
        return self.__str__()

class Station:
    def __init__(self, x, y=1, tam=STATION_LENGHT):
        self.x = x
        self.y = y
        self.tam = tam
    
    def __repr__(self):
        return f'St {self.x} lenght:{self.tam}'

def start_simulation():
    highway, old_highway, step, vehicles, stations = start_variabels()
    while must_exec(step):
        highway, old_highway = simulation_step(highway, old_highway, step, vehicles, stations)
        if MUST_PRINT_RESULTS:
            show_highway(highway, stations)
        step += 1
        time.sleep(2)
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
    change_velocities(old_highway, vehicles, stations)
    move_vehicles(highway, old_highway, vehicles, stations)
    create_new_vehicles(highway, vehicles, step)
    old_highway = deepcopy(highway)
    return highway, old_highway

def change_velocities(old_highway, vehicles, stations):
    for vehicle in vehicles:
        vehicle.velocity = get_new_velocity(old_highway, vehicle.y, vehicle.x)

def get_new_velocity(highway, runway_index, cell_index):
    cell = highway[runway_index][cell_index]

    other_vehicle_position = -1

    vehicle_move_range = cell_index + cell.velocity + 1 + VEHICLE_LENGHT
    end_of_range = vehicle_move_range if vehicle_move_range < HIGHWAY_LENGHT else HIGHWAY_LENGHT
    for index in range(cell_index + 1, end_of_range):
        range_cell = highway[runway_index][index]
        if must_check_cell(range_cell):
            other_vehicle_position = index
    
    return apply_rules(highway, runway_index, cell_index, other_vehicle_position)

def must_check_cell(cell):
    return cell and cell.velocity != 0

def apply_rules(highway, runway_index, cell_index, other_vehicle_position):
    old_velocity = highway[runway_index][cell_index].velocity

    if other_vehicle_position != -1:
        new_velocity = other_vehicle_position - cell_index - VEHICLE_LENGHT
    else:
        chance = random_slow_down(old_velocity)
        if chance:
            new_velocity = old_velocity - 1
        elif other_vehicle_position == -1 and old_velocity + 1 <= MAX_VELOCITY:
            new_velocity = old_velocity + 1
        else:
            new_velocity = old_velocity

    return new_velocity

def random_slow_down(old_velocity):
    return SLOW_DOWN_PROBABILITY >= random.random() and old_velocity > 1

def move_vehicles(highway, old_highway, vehicles, stations):
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

def create_new_vehicles(highway, vehicles, step):
    if NEW_VEHICLE_DELAY > 0:
        if step % NEW_VEHICLE_DELAY == 0:
            new_vehicle(highway, vehicles)
    else:
        new_vehicle_from_file(highway, vehicles, step)

def new_vehicle_from_file(highway, vehicles, step):
    with open('vehicles_timestamp.txt', 'r') as vehicle_files:
        for line in vehicle_files:
            line = int(line)
            if step == line:
                new_vehicle(highway, vehicles)
            elif line > step:
                break

def new_vehicle(highway, vehicles, where=0):
    vehicles.append(
        Vehicle(velocity=1, x=where, y=0)
    )
    new_vehicle = vehicles[-1]
    highway[new_vehicle.y][new_vehicle.x] = new_vehicle

def show_highway(highway, stations):
    runway = highway[0]
    for cell_index, cell in runway.items():
        if cell:
            print(f'-{cell.velocity}-', end='')
        else:
            print(f'-0-', end='')
    print('\n')

    stations_index = []
    for station in stations:
        stations_index.extend(range(station.x, station.x + station.tam))

    runway = highway[1]
    for cell_index, cell in runway.items():
        if cell_index in stations_index:
            if cell:
                print(f'-{cell.velocity}-', end='')
            else:
                print(f'-0-', end='')
        else:
            print(f'   ', end='')
    print('\n')

if __name__ == "__main__":
    start_simulation()