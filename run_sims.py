import json
import datetime
import pandas
import requests
import argparse

from parachute_deployments import *

from rocketpy import Environment, SolidMotor, Rocket, Flight

# TODO: Implement a means of taking the longitude and laitude data from json to figure out which weather station
#          should be used to get sounding air data, this may be farther down the line since you could easily go to the site
#           yourself and get the data (https://weather.uwyo.edu/upperair/sounding.html)






def parse_args():
    """
    Parses command-line arguments
    """
    parser = argparse.ArgumentParser(description="Rocket Simulation using RocketPy")

    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help="Path to the JSON configuration file"
    )

    parser.add_argument(
        '--output_dir',
        type=str,
        default='./sims_output',
        help="Directory where output files will be saved. Default is './sims_output'"
    )

    return parser.parse_args()

def main():
    
    args = parse_args()
    
    with open(args.config, 'r') as file:
        config = json.load(file)


    env = Environment(
        railLength=5.2,
        latitude=config['environment']['location']['latitude'],
        longitude=config['environment']['location']['longitude'],
        elevation=config['environment']['location']['elevation'],
        date=(config['environment']['launch_date'], config['environment']['launch_time']),
        datum=config['environment']['datum']
    )

    motor = SolidMotor(
        thrustSource=config['solid_motor']['thrust_source'],
        burnOut=config['solid_motor']['burn_time'],
        grainNumber=config['solid_motor']['grain_number'],
        grainSeparation=config['solid_motor']['grain_separation'],
        grainDensity=config['solid_motor']['grain_density'],
        grainOuterRadius=config['solid_motor']['grain_outer_diameter'] / 2,
        grainInitialInnerRadius=config['solid_motor']['grain_initial_inner_diameter'] / 2,
        grainInitialHeight=config['solid_motor']['grain_initial_height'],
        nozzleRadius=config['solid_motor']['nozzle_radius'],
        throatRadius=config['solid_motor']['throat_radius'],
        interpolationMethod='linear'
    )

    rocket = Rocket(
        motor=motor,
        radius=config['rocket']['radius'],
        mass=config['rocket']['mass'],
        inertia=config['rocket']['inertia'],
        distanceRocketNozzle=config['solid_motor']['nozzle_position'],
        distanceRocketPropellant=-0.12
    )

    rocket.addNose(length=config['rocket']['aerodynamics']['nose_length'])
    rocket.addFins(
        n=config['rocket']['aerodynamics']['fins']['number'],
        rootChord=config['rocket']['aerodynamics']['fins']['root_chord'],
        tipChord=config['rocket']['aerodynamics']['fins']['tip_chord'],
        span=config['rocket']['aerodynamics']['fins']['span'],
        cantAngle=config['rocket']['aerodynamics']['fins']['cant_angle'],
        airfoil=config['rocket']['aerodynamics']['fins']['airfoil']
    )
    rocket.addTail(
        topRadius=config['rocket']['aerodynamics']['tail']['top_radius'],
        bottomRadius=config['rocket']['aerodynamics']['tail']['bottom_radius'],
        length=config['rocket']['aerodynamics']['tail']['length']
    )

    for parachute in config['rocket']['parachutes']:
        rocket.addParachute(
            name=parachute['name'],
            cdS=parachute['cd_s'],
            trigger=parachute['trigger'],
            samplingRate=parachute['sampling_rate'],
            lag=parachute['lag'],
            noise=parachute['noise']
        )

    test_flight = Flight(rocket, env, inclination=85, heading=0)
    
    test_flight.allInfo()

    # test_flight.plot()