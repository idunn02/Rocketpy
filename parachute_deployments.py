class ParachuteDeployer:
    def __init__(self, altitude_deploy_after_apogee=0, time_after_apogee=0):
        self.apogee = 0
        self.apogee_reached = False
        self.time_at_apogee = 0
        self.altitude_deploy_after_apogee = altitude_deploy_after_apogee
        self.time_after_apogee = time_after_apogee

    def update_apogee_status(self, height, curr_time):
        if not self.apogee_reached:
            if height > self.apogee:
                self.apogee = height
            else:
                self.apogee_reached = True
                self.time_at_apogee = curr_time

    def deploy_at_altitude_after_apogee(self, height, curr_time):
        self.update_apogee_status(height, curr_time)
        return self.apogee_reached and height <= self.altitude_deploy_after_apogee

    def deploy_after_time_after_apogee(self, height, curr_time):
        self.update_apogee_status(height, curr_time)
        return (
            self.apogee_reached
            and (curr_time - self.time_at_apogee) >= self.time_after_apogee
        )

    def set_deployment_criteria(self, criteria):
        if criteria == "deploy_at_altitude_after_apogee":
            return self.deploy_at_altitude_after_apogee
        elif criteria == "deploy_after_time_after_apogee":
            return self.deploy_after_time_after_apogee
        else:
            raise ValueError("Invalid deployment criteria specified.")
