#!/usr/bin/env python

# Copyright (c) 2021 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Example script to generate traffic in the simulation"""

import glob
import os
import sys
import time
import json
import msvcrt

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from carla import VehicleLightState as vls

import argparse
import logging
from numpy import random


# def camera_move(camera, move_location):
#     camera.

def traffic_light_change(traffic_light, now_time):
    now_state = traffic_light["traffic_light"].state
    if now_state == carla.TrafficLightState.Red:
        if traffic_light["change_time"] + traffic_light["red_time"] < now_time:
            traffic_light["traffic_light"].set_state(carla.TrafficLightState.Green)
        else: return traffic_light["change_time"]
    elif now_state == carla.TrafficLightState.Green:
        if traffic_light["change_time"] + traffic_light["green_time"] < now_time:
            traffic_light["traffic_light"].set_state(carla.TrafficLightState.Yellow)
        else: return traffic_light["change_time"]
    if now_state == carla.TrafficLightState.Yellow:
        if traffic_light["change_time"] + traffic_light["yellow_time"] < now_time:
            traffic_light["traffic_light"].set_state(carla.TrafficLightState.Red)
        else: return traffic_light["change_time"]
    
    return now_time

def get_all_traffic_light(traffic_lights, traffic_guide_lights):
    return traffic_lights + traffic_guide_lights

def random_route():
    path_list = ["Straight", "Left", "Right"]
    return random.choice(path_list)

def vehicle_state(vehicle):
    print(vehicle.get_control())
    # print(vehicle.get_physics_control())

def route_(i, randam_seed):
    route_randam = random
    route_randam.seed(randam_seed)
    route_path = []
    if i == 0:
        route_path.append("Straight")
        # route_path.append(random.choice(["Right", "Left"]))
        route_path.append(route_randam.choice(["Straight", "Left"], p=[0.75,0.25]))
        route_path.append("Straight")
    elif i == 1:
        # route_path.append("Straight")
        # route_path.append(random.choice(["Straight", "Left"]))
        # route_path.append(random.choice(["Right", "Left"]))
        route_path.append(route_randam.choice(["Right", "Straight"], p=[0.25,0.75]))
        route_path.append("Straight")
    elif i == 2: 
        route_path.append("Straight")
        # route_path.append(random.choice(["Right", "Straight"]))
        route_path.append(route_randam.choice(["Right", "Left"]))
        route_path.append("Straight")
    return route_path

def spawn_judge(vehicle_x, vehicle_y, spawn_x, spawn_y):
    x_diff = 0
    y_diff = 0
    if vehicle_x > spawn_x:
        x_diff = vehicle_x -spawn_x
    else:
        x_diff = spawn_x -vehicle_x

    if vehicle_y > spawn_y:
        y_diff = vehicle_y -spawn_y
    else:
        y_diff = spawn_y -vehicle_y

    if x_diff >= 10 or y_diff >= 10:
        return True
    
    return False

def vehicle_set_route(traffic_manager, vehicle, path):
    traffic_manager.set_route(vehicle, path)
    vehicle.set_autopilot()
    return

def spawn_vehicle(world, vehicles, transform, random_seed):
    blueprint_random = random
    blueprint_color_random = random
    blueprint_random.seed(random_seed + 1)
    blueprint = blueprint_random.choice(vehicles)
    blueprint_color_random.seed()
    # blueprint = blueprint_random.choice(vehicles)
    if blueprint.has_attribute('color'):
        color = blueprint_color_random.choice(blueprint.get_attribute('color').recommended_values)
        # if n == 0:
        # color = blueprint.get_attribute('color').recommended_values[2]
        blueprint.set_attribute('color', color)
    if blueprint.has_attribute('driver_id'):
        driver_id = blueprint_random.choice(blueprint.get_attribute('driver_id').recommended_values)
        blueprint.set_attribute('driver_id', driver_id)

    return world.try_spawn_actor(blueprint, transform)
    # print()

# 車両生成
def spawn_vehicle_list(world, route_seed, spawn_points, vehicles, traffic_manager, traffic_volume_pattern):
    now_time = world.get_snapshot().timestamp.elapsed_seconds
    route_random = random
    route_random.seed(route_seed)
    route_random_list = route_random.randint(0, 100, len(spawn_points))

    # if now_time < spawn_time + 10 * 2.5:
    #     return spawn_time, None
    
    # print("-----SpawnVehicle-----\n")

    vehicle_list = []
    
    # if now_time < traffic_volume_pattern[2]["spawn_time"] + traffic_volume_pattern[2]["traffic_volume"]:
    #     return now_time, None
    # vehicle = spawn_vehicle(world, random.choice(vehicles), spawn_points[2])
    # vehicle_set_route(traffic_manager, vehicle, route_(2    ))
    # vehicle_list.append(vehicle)
    # traffic_volume_pattern[2]["spawn_time"] = now_time
    # traffic_volume_pattern[2]["latast_spawn_vehicle"] = vehicle
    for i, spawn_point in enumerate(spawn_points):
        if now_time < traffic_volume_pattern[i]["SpawnTime"] + (1 / (traffic_volume_pattern[i]["TrafficVolume"] / 3600)):
            continue
        if "latast_spawn_vehicle" in traffic_volume_pattern[i]:
            try:
                vehicle_x = traffic_volume_pattern[i]["latast_spawn_vehicle"].get_transform().location.x
                vehicle_y = traffic_volume_pattern[i]["latast_spawn_vehicle"].get_transform().location.y
            except RuntimeError as e:
                print(e)
                traffic_volume_pattern[i].pop("latast_spawn_vehicle")
                continue
            spawn_x = spawn_point.location.x
            spawn_y = spawn_point.location.y
            # print("vehicle transform: ")
            # print(traffic_volume_pattern[i]["latast_spawn_vehicle"].get_transform().location.x)
            # print("spawn transform  : ")
            # print(spawn_point.location)
            if not spawn_judge(vehicle_x, vehicle_y, spawn_x, spawn_y):
                continue

        vehicle = spawn_vehicle(world, vehicles, spawn_point, route_random_list[i])
        vehicle_set_route(traffic_manager, vehicle, route_(i, route_random_list[i]))
        vehicle_list.append(vehicle)
        traffic_volume_pattern[i]["SpawnTime"] = now_time
        traffic_volume_pattern[i]["latast_spawn_vehicle"] = vehicle
    return now_time, vehicle_list

def pattern_cycle(list_len, i):
    i += 1
    if i >= list_len:
        i = 0
    return i

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []

def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=30,
        type=int,
        help='Number of vehicles (default: 30)')
    argparser.add_argument(
        '-w', '--number-of-walkers',
        metavar='W',
        default=10,
        type=int,
        help='Number of walkers (default: 10)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filterv',
        metavar='PATTERN',
        default='vehicle.*',
        help='Filter vehicle model (default: "vehicle.*")')
    argparser.add_argument(
        '--generationv',
        metavar='G',
        default='All',
        help='restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='Filter pedestrian type (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '--generationw',
        metavar='G',
        default='2',
        help='restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='Port to communicate with TM (default: 8000)')
    argparser.add_argument(
        '--asynch',
        action='store_true',
        help='Activate asynchronous mode execution')
    argparser.add_argument(
        '--hybrid',
        action='store_true',
        help='Activate hybrid mode for Traffic Manager')
    argparser.add_argument(
        '-s', '--seed',
        metavar='S',
        type=int,
        help='Set random device seed and deterministic mode for Traffic Manager')
    argparser.add_argument(
        '--seedw',
        metavar='S',
        default=0,
        type=int,
        help='Set the seed for pedestrians module')
    argparser.add_argument(
        '--car-lights-on',
        action='store_true',
        default=False,
        help='Enable automatic car light management')
    argparser.add_argument(
        '--hero',
        action='store_true',
        default=False,
        help='Set one of the vehicles as hero')
    argparser.add_argument(
        '--respawn',
        action='store_true',
        default=False,
        help='Automatically respawn dormant vehicles (only in large maps)')
    argparser.add_argument(
        '--no-rendering',
        action='store_true',
        default=False,
        help='Activate no rendering mode')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    settings_file_name = "Set.json"

    settings_file = open(settings_file_name)
    scenario_settings = json.load(settings_file)
    pattern_change_time = scenario_settings["TrafficVolumeChangeTime"]
    traffic_volume_pattern = scenario_settings["TrafficVolumePattern"]
    advance_speed = scenario_settings["CarlaWorldAdvanceSpeed"]
    # print(scenario_settings)
    route_random = random
    route_random.seed(0)
    route_random_list = route_random.randint(0, 100, 50)
    route_random_list_int = 0
    # print(route_random_list)

    

    vehicles_list = []
    walkers_list = []
    all_id = []
    
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    try:
        world = client.get_world()

        traffic_manager = client.get_trafficmanager(args.tm_port)
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        if args.respawn:
            traffic_manager.set_respawn_dormant_vehicles(True)
        if args.hybrid:
            traffic_manager.set_hybrid_physics_mode(True)
            traffic_manager.set_hybrid_physics_radius(70.0)
        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)

        settings = world.get_settings()
        if not args.asynch:
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.01 * advance_speed
            else:
                synchronous_master = False
        else:
            print("You are currently in asynchronous mode. If this is a traffic simulation, \
            you could experience some issues. If it's not working correctly, switch to synchronous \
            mode by using traffic_manager.set_synchronous_mode(True)")

        if args.no_rendering:
            settings.no_rendering_mode = True
        world.apply_settings(settings)

        blueprints = get_actor_blueprints(world, args.filterv, args.generationv)

        if args.safe:
            blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
            blueprints = [x for x in blueprints if not x.id.endswith('microlino')]
            blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
            blueprints = [x for x in blueprints if not x.id.endswith('cybertruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('t2')]
            blueprints = [x for x in blueprints if not x.id.endswith('sprinter')]
            blueprints = [x for x in blueprints if not x.id.endswith('firetruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('ambulance')]

        blueprints = sorted(blueprints, key=lambda bp: bp.id)

        spawn_points = world.get_map().get_spawn_points()
        # print(len(spawn_points))
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        # --------------
        # Spawn vehicles
        # --------------
        vehicles = []
        batch = []
        # hero = args.hero
        # for vehicle in blueprints:
        #     print(vehicle)
            # vehicles.append(vehicle)
        vehicles.append(blueprints[0])
        vehicles.append(blueprints[1])
        vehicles.append(blueprints[2])
        # vehicles.append(blueprints[3]) # crossbike
        vehicles.append(blueprints[4])
        vehicles.append(blueprints[5]) # truck
        # vehicles.append(blueprints[6]) # firetruck
        vehicles.append(blueprints[7])
        vehicles.append(blueprints[8])
        # vehicles.append(blueprints[9]) # crossbike
        vehicles.append(blueprints[10])
        # vehicles.append(blueprints[11]) #police
        # vehicles.append(blueprints[12]) #police
        # vehicles.append(blueprints[13]) #truck
        # vehicles.append(blueprints[14]) #taxi
        vehicles.append(blueprints[15])
        # vehicles.append(blueprints[16]) #crossbike
        vehicles.append(blueprints[17]) #bike
        # vehicles.append(blueprints[18]) #amelica
        vehicles.append(blueprints[19]) #bike
        vehicles.append(blueprints[20])
        vehicles.append(blueprints[21])
        vehicles.append(blueprints[22])
        vehicles.append(blueprints[23])
        # vehicles.append(blueprints[24]) #wagon
        # vehicles.append(blueprints[25]) #future
        vehicles.append(blueprints[26])
        vehicles.append(blueprints[27])
        vehicles.append(blueprints[28])
        vehicles.append(blueprints[29])
        vehicles.append(blueprints[30])
        vehicles.append(blueprints[31])
        # vehicles.append(blueprints[32]) #?
        vehicles.append(blueprints[33])
        vehicles.append(blueprints[34])
        # vehicles.append(blueprints[35]) #autobike
        vehicles.append(blueprints[36]) #bus
        vehicles.append(blueprints[37]) #bus
        vehicles.append(blueprints[38]) #bike

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Set automatic vehicle lights update if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)

        # Example of how to use Traffic Manager parameters
        traffic_manager.global_percentage_speed_difference(30.0)

        # --------------
        # TrafficLight Setting
        # --------------
        actors = world.get_actors()
        traffic_lights = []
        traffic_guide_lights = []
        world.freeze_all_traffic_lights(True)
        start_time = world.get_snapshot().timestamp.elapsed_seconds
        for actor in actors:
            # print(actor.id)
            # print(type(actor))

            # if type(actor) is carla.libcarla.Camera:
            #     print(actor.id)
            if type(actor) is carla.libcarla.TrafficLight:
                # print(actor.id)
                if actor.id == 7:
                    traffic_guide_lights.append({
                        "traffic_light": actor,
                        "first_state": carla.TrafficLightState.Red,
                        "red_time": 26.0,
                        "green_time": 36.0,
                        "yellow_time": 3.0,
                        "change_time": start_time
                    })
                    actor.set_state(carla.TrafficLightState.Red)
                elif actor.id == 6:
                    traffic_guide_lights.append({
                        "traffic_light": actor,
                        "first_state": carla.TrafficLightState.Green,
                        "red_time": 53.0,
                        "green_time": 9.0,
                        "yellow_time": 3.0,
                        "change_time": start_time + 7
                    })
                    actor.set_state(carla.TrafficLightState.Green)
                elif actor.id == 3:
                    traffic_lights.append({
                        "traffic_light": actor,
                        "first_state": carla.TrafficLightState.Green,
                        "red_time": 43.0,
                        "green_time": 19.0,
                        "yellow_time": 3.0,
                        "change_time": start_time + 12
                    })
                    actor.set_state(carla.TrafficLightState.Green)
                elif actor.id == 2:
                    traffic_lights.append({
                        "traffic_light": actor,
                        "first_state": carla.TrafficLightState.Red,
                        "red_time": 28.0,
                        "green_time": 34.0,
                        "yellow_time": 3.0,
                        "change_time": start_time + 9
                    })
                    actor.set_state(carla.TrafficLightState.Red)
                elif actor.id == 4:
                    traffic_lights.append({
                        "traffic_light": actor,
                        "first_state": carla.TrafficLightState.Green,
                        "red_time": 43.0,
                        "green_time": 19.0,
                        "yellow_time": 3.0,
                        "change_time": start_time + 12
                    })
                    actor.set_state(carla.TrafficLightState.Green)
                elif actor.id == 5:
                    traffic_lights.append({
                        "traffic_light": actor,
                        "first_state": carla.TrafficLightState.Red,
                        "red_time": 28.0,
                        "green_time": 34.0,
                        "yellow_time": 3.0,
                        "change_time": start_time + 9
                    })
                    actor.set_state(carla.TrafficLightState.Red)


        spawn_time = world.get_snapshot().timestamp.elapsed_seconds
        traffic_volume_pattern_int = 0
        for trafffic_volume in traffic_volume_pattern[traffic_volume_pattern_int]:
            trafffic_volume["spawn_time"] = spawn_time

        traffic_volume_pattern_length = len(traffic_volume_pattern)
        start_time = time.time()
        # print(start_time)
        # print(traffic_volume_pattern_length)

        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

            now_time = time.time()
            if (start_time + pattern_change_time <= now_time and traffic_volume_pattern_length > 1) or (msvcrt.kbhit() and msvcrt.getch() == b' '):
                print("----------reset----------")
                actors = world.get_actors()
                vehicle_list = []
                for actor in actors:
                    # print(type(actor))
                    if type(actor) == carla.libcarla.Vehicle:
                        # print(actor.id)
                        vehicle_list.append(actor)
                client.apply_batch([carla.command.DestroyActor(x.id) for x in vehicle_list])
                # vehicles_list.clear()
                traffic_volume_pattern_int = pattern_cycle(traffic_volume_pattern_length, traffic_volume_pattern_int)
                start_time = now_time
                route_random_list_int = 0
                light_start_time = world.get_snapshot().timestamp.elapsed_seconds
                traffic_guide_lights.clear()
                traffic_lights.clear()

                for actor in actors:
                    # print(actor.id)
                    # print(type(actor))

                    # if type(actor) is carla.libcarla.Camera:
                    #     print(actor.id)
                    if type(actor) is carla.libcarla.TrafficLight:
                        # print(actor.id)
                        if actor.id == 7:
                            traffic_guide_lights.append({
                                "traffic_light": actor,
                                "first_state": carla.TrafficLightState.Red,
                                "red_time": 26.0,
                                "green_time": 36.0,
                                "yellow_time": 3.0,
                                "change_time": light_start_time
                            })
                            actor.set_state(carla.TrafficLightState.Red)
                        elif actor.id == 6:
                            traffic_guide_lights.append({
                                "traffic_light": actor,
                                "first_state": carla.TrafficLightState.Green,
                                "red_time": 53.0,
                                "green_time": 9.0,
                                "yellow_time": 3.0,
                                "change_time": light_start_time + 7
                            })
                            actor.set_state(carla.TrafficLightState.Green)
                        elif actor.id == 3:
                            traffic_lights.append({
                                "traffic_light": actor,
                                "first_state": carla.TrafficLightState.Green,
                                "red_time": 43.0,
                                "green_time": 19.0,
                                "yellow_time": 3.0,
                                "change_time": light_start_time + 12
                            })
                            actor.set_state(carla.TrafficLightState.Green)
                        elif actor.id == 2:
                            traffic_lights.append({
                                "traffic_light": actor,
                                "first_state": carla.TrafficLightState.Red,
                                "red_time": 28.0,
                                "green_time": 34.0,
                                "yellow_time": 3.0,
                                "change_time": light_start_time + 9
                            })
                            actor.set_state(carla.TrafficLightState.Red)
                        elif actor.id == 4:
                            traffic_lights.append({
                                "traffic_light": actor,
                                "first_state": carla.TrafficLightState.Green,
                                "red_time": 43.0,
                                "green_time": 19.0,
                                "yellow_time": 3.0,
                                "change_time": light_start_time + 12
                            })
                            actor.set_state(carla.TrafficLightState.Green)
                        elif actor.id == 5:
                            traffic_lights.append({
                                "traffic_light": actor,
                                "first_state": carla.TrafficLightState.Red,
                                "red_time": 28.0,
                                "green_time": 34.0,
                                "yellow_time": 3.0,
                                "change_time": light_start_time + 9
                            })
                            actor.set_state(carla.TrafficLightState.Red)


            elapsed_seconds = world.get_snapshot().timestamp.elapsed_seconds

            # for traffic_guide_light in traffic_guide_lights:
            #     traffic_guide_light["change_time"] = traffic_light_change(traffic_guide_light ,elapsed_seconds)

            for traffic_light in get_all_traffic_light(traffic_lights, traffic_guide_lights):
                traffic_light["change_time"] = traffic_light_change(traffic_light ,elapsed_seconds)
            
            spawn_time, spawn_actor = spawn_vehicle_list(world, route_random_list[route_random_list_int], spawn_points, vehicles, traffic_manager, traffic_volume_pattern[traffic_volume_pattern_int])
            if len(spawn_actor) == 0:
                continue
            vehicles_list.extend(spawn_actor)
            route_random_list_int = pattern_cycle(len(route_random_list), route_random_list_int)
        
            # for vehicle in vehicles_list:
            #     vehicle_state(vehicle)

    finally:

        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)

        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x.id) for x in vehicles_list])

        # stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(all_id), 2):
            all_actors[i].stop()

        print('\ndestroying %d walkers' % len(walkers_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        time.sleep(0.5)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
