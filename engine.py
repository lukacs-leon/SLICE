from telescope import Telescope
from correlator import Correlator
import numpy as np

class SimulationEngine:
    def __init__(self):
        self.is_running = False
        self.time_step = 0
        self.speed = 1
        self.wavelength = 1.0e-6
        self.fov = 10.0
        self.astronomical_objects = [
            {"type": "star", "x": 1.0, "y": 1.0, "temp": 8000, "size": 1.2},
            {"type": "gas_cloud", "x": -2.0, "y": -1.5, "temp": 4000, "size": 2.0}
        ]
        self.telescopes_config = [
            {"id": "T1", "lat": 15.0, "lon": 30.0},
            {"id": "T2", "lat": -20.0, "lon": -40.0},
            {"id": "T3", "lat": 45.0, "lon": -10.0}
        ]
        
        self.correlator = Correlator(grid_size=64)
        self.moon_rotation_angle = 0.0

    def start(self):
        self.is_running = True

    def pause(self):
        self.is_running = False

    def stop(self):
        self.is_running = False
        self.time_step = 0
        self.moon_rotation_angle = 0.0

    def step(self):
        if not self.is_running:
            return
        
        step_increment = max(1, self.speed // 10) if self.speed >= 1000 else max(1, self.speed)
        self.time_step += step_increment
        
        rot_step = 0.002 * self.speed
        self.moon_rotation_angle += rot_step

    def get_state(self):
        telescopes = [Telescope(t["id"], t["lat"], t["lon"]) for t in self.telescopes_config]
        
        # Összesített bázistávolság (Total Baseline) kiszámítása a 3D pozíciókból
        total_baseline_km = 0.0
        if len(telescopes) >= 2:
            positions = [t.get_3d_position(self.moon_rotation_angle) for t in telescopes]
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = np.linalg.norm(positions[i] - positions[j])
                    total_baseline_km += dist

        sky_map = self.correlator.generate_sky_map(self.astronomical_objects, self.wavelength, self.fov)
        uv_count, uv_cov, reconstructed = self.correlator.compute_interferometry(sky_map, telescopes, self.moon_rotation_angle, self.wavelength)

        return {
            "is_running": self.is_running,
            "time_step": self.time_step,
            "speed": self.speed,
            "moon_rotation_angle": self.moon_rotation_angle,
            "sky_map": sky_map.tolist() if isinstance(sky_map, np.ndarray) else sky_map,
            "uv_coverage": uv_cov,
            "reconstructed_map": reconstructed,
            "uv_coverage_count": uv_count,
            "telescopes": self.telescopes_config,
            "objects": self.astronomical_objects,
            "telescope_count": len(self.telescopes_config),
            "total_baseline_km": round(total_baseline_km, 2)
        }