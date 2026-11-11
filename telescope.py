import math
import numpy as np

class Telescope:
    def __init__(self, telescope_id: str, latitude: float, longitude: float):
        self.id = telescope_id
        self.latitude = latitude
        self.longitude = longitude

    def get_3d_position(self, moon_rotation_angle: float, moon_radius_km: float = 1737.4):
        lat_rad = math.radians(self.latitude)
        lon_rad = math.radians(self.longitude) + moon_rotation_angle

        x = moon_radius_km * math.cos(lat_rad) * math.cos(lon_rad)
        y = moon_radius_km * math.cos(lat_rad) * math.sin(lon_rad)
        z = moon_radius_km * math.sin(lat_rad)

        return np.array([x, y, z])