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
        "--config", type=str, required=True, help="Path to the JSON configuration file"
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="./sims_output",
        help="Directory where output files will be saved. Default is './sims_output'",
    )

    return parser.parse_args()


def add_fins(fin_type, fin_config, rocket):
    fins_args = {
        "n": fin_config["number"],
        "root_chord": fin_config["root_chord"],
        "tip_chord": fin_config["tip_chord"],
        "span": fin_config["span"],
        "position": fin_config["position"],
    }

    if "cant_angle" in fin_config:
        fins_args["cant_angle"] = fin_config["cant_angle"]
    if "airfoil" in fin_config:
        fins_args["airfoil"] = fin_config["airfoil"]

    if fin_type == "trapezoidal":
        return rocket.add_trapezoidal_fins(**fins_args)
    elif fin_type == "elliptical":
        return rocket.add_elliptical_fins(**fins_args)
    else:
        raise ValueError(f"Unsupported fin type: {fin_type}")


def main():

    args = parse_args()

    with open(args.config, "r") as file:
        config = json.load(file)

    # setting up the Environment
    ## converting date string to datetime object
    launch_date_string = config["environment"]["launch_date"]
    launch_time_num = config["environment"]["launch_time"]  # time given in UTC
    launch_date = datetime.datetime.strptime(launch_date_string, "%Y-%m-%d")

    env_args = {
        "latitude": config["environment"]["location"]["latitude"],
        "longitude": config["environment"]["location"]["longitude"],
        "elevation": config["environment"]["location"]["elevation"],
    }

    ## only add 'datum' if it's provided as to not fuck up defaults
    if "datum" in config["environment"]:
        env_args["datum"] = config["environment"]["datum"]

    env = Environment(**env_args)
    env.set_date(
        (launch_date.year, launch_date.month, launch_date.day, launch_time_num)
    )
    env.set_atmospheric_model(
        type=config["environment"]["atmospheric_data_type"],
        file=config["environment"]["atmospheric_data_url"],
    )

    # setting up the Solid Motor
    motor_args = {
        "nozzle_radius": config["solid_motor"]["nozzle_radius"],
        "dry_mass": config["solid_motor"]["dry_mass"],
        "dry_inertia": config["solid_motor"]["dry_inertia"],
        "thrust_source": config["solid_motor"]["thrust_source"],
        "grain_number": config["solid_motor"]["grain_number"],
        "grain_separation": config["solid_motor"]["grain_separation"],
        "grain_density": config["solid_motor"]["grain_density"],
        "grain_outer_radius": config["solid_motor"]["grain_outer_diameter"] / 2,
        "grain_initial_inner_radius": config["solid_motor"][
            "grain_initial_inner_diameter"
        ]
        / 2,
        "grain_initial_height": config["solid_motor"]["grain_initial_height"],
        "grains_center_of_mass_position": config["solid_motor"][
            "grains_center_of_mass_position"
        ],
        "center_of_dry_mass_position": config["solid_motor"][
            "center_of_dry_mass_position"
        ],
        "coordinate_system_orientation": config["solid_motor"][
            "coordinate_system_orientation"
        ],
    }

    ## similar to before, conditionally add optional parameters
    if "nozzle_position" in config["solid_motor"]:
        motor_args["nozzle_position"] = config["solid_motor"]["nozzle_position"]
    if "throat_radius" in config["solid_motor"]:
        motor_args["throatRadius"] = config["solid_motor"]["throat_radius"]
    if "interpolation_method" in config["solid_motor"]:
        motor_args["interpolationMethod"] = config["solid_motor"][
            "interpolation_method"
        ]
    if "burn_time" in config["solid_motor"]:
        motor_args["burn_time"] = config["solid_motor"]["burn_time"]
    if "reshape_thrust_curve" in config["solid_motor"]:
        motor_args["reshape_thrust_curve"] = config["solid_motor"][
            "reshape_thrust_curve"
        ]

    motor = SolidMotor(**motor_args)

    # setting up the Rocket
    rocket_args = {
        "radius": config["rocket"]["radius"],
        "mass": config["rocket"]["mass"],
        "inertia": config["rocket"]["inertia"],
        "power_off_drag": config["rocket"]["power_off_drag"],
        "power_on_drag": config["rocket"]["power_on_drag"],
        "center_of_mass_without_motor": config["rocket"][
            "center_of_mass_without_motor"
        ],
        "coordinate_system_orientation": config["rocket"][
            "coordinate_system_orientation"
        ],
    }

    rocket = Rocket(**rocket_args)
    rocket.add_motor(motor, position=["rocket"]["motor_position"])

    ## adding rail buttons
    rail_buttons = rocket.set_rail_buttons(
        upper_button_position=["rocket"]["rail_buttons"]["upper_rail_button"],
        lower_button_position=["rocket"]["rail_buttons"]["lower_rail_button"],
        angular_position=["rocket"]["rail_buttons"]["angular position"],
    )

    nose_cone = rocket.add_nose(
        length=config["rocket"]["aerodynamics"]["nose_length"],
        kind=["rocket"]["aerodynamics"]["nose_type"],
        position=["rocket"]["aerodynamics"]["nose_position"],
    )

    fin_type = config["rocket"]["aerodynamics"]["fins"]["fin_type"]
    fin_config = config["rocket"]["aerodynamics"]["fins"]
    fin_set = add_fins(fin_type, fin_config, rocket)

    rocket.add_tail(
        top_radius=config["rocket"]["aerodynamics"]["tail"]["top_radius"],
        bottom_radius=config["rocket"]["aerodynamics"]["tail"]["bottom_radius"],
        length=config["rocket"]["aerodynamics"]["tail"]["length"],
        position=config["rocket"]["aerodynamics"]["tail"]["position"],
    )

    for parachute in config["rocket"]["parachutes"]:
        rocket.addParachute(
            name=parachute["name"],
            cdS=parachute["cd_s"],
            trigger=parachute["trigger"],
            samplingRate=parachute["sampling_rate"],
            lag=parachute["lag"],
            noise=parachute["noise"],
        )

    test_flight = Flight(rocket, env, inclination=85, heading=0)

    test_flight.allInfo()

    # test_flight.plot()
