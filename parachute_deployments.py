def deploy_at_altitude_after_apogee(
    pressure, height, state_vector, altitude_deploy=100
):
    if state_vector[5] < 0:
        if height <= altitude_deploy:
            return True
    return False
