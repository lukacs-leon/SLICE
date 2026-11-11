import numpy as np

class Correlator:
    def __init__(self, grid_size: int = 64):
        self.grid_size = grid_size

    def generate_sky_map(self, astronomical_objects: list, wavelength: float, fov: float):
        size = self.grid_size
        x = np.linspace(-fov / 2, fov / 2, size)
        y = np.linspace(-fov / 2, fov / 2, size)
        X, Y = np.meshgrid(x, y)
        
        sky_map = np.zeros((size, size))

        for obj in astronomical_objects:
            ox = obj.get("x", 0.0)
            oy = obj.get("y", 0.0)
            temperature = obj.get("temp", 6000.0)
            size_scale = obj.get("size", 1.0)
            obj_type = obj.get("type", "star")

            if obj_type == "star":
                intensity = (temperature / 1000.0) * np.exp(-((X - ox)**2 + (Y - oy)**2) / (2 * (0.8 * size_scale)**2))
                sky_map += intensity
            elif obj_type == "gas_cloud":
                intensity = (temperature / 5000.0) * np.exp(-((X - ox)**2 / (2 * (2.0 * size_scale)**2) + (Y - oy)**2 / (2 * (1.0 * size_scale)**2)))
                sky_map += intensity
            elif obj_type == "planet":
                mask = ((X - ox)**2 + (Y - oy)**2) < (0.8 * size_scale)**2
                sky_map[mask] += temperature / 2000.0
            elif obj_type == "galaxy":
                ellip = ((X - ox)**2 / (3.0 * size_scale)) + ((Y - oy)**2 / (1.0 * size_scale))
                intensity = (temperature / 3000.0) * np.exp(-ellip)
                sky_map += intensity

        return sky_map

    def compute_interferometry(self, sky_map: np.ndarray, telescopes: list, moon_rotation_angle: float, wavelength: float):
        size = self.grid_size
        
        visibilities = np.fft.fft2(sky_map)
        visibilities = np.fft.fftshift(visibilities)

        uv_coverage = np.zeros((size, size), dtype=float)
        uv_coverage_count = 0

        if len(telescopes) >= 2:
            positions = [t.get_3d_position(moon_rotation_angle) for t in telescopes]
            
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    baseline = positions[i] - positions[j] # km
                    
                    # Optimalizált skálázás a grid mérethez
                    u = int(size / 2 + (baseline[0] / 50.0))
                    v = int(size / 2 + (baseline[1] / 50.0))
                    
                    if 0 <= u < size and 0 <= v < size:
                        uv_coverage[v, u] = 1.0
                        inv_u, inv_v = size - 1 - u, size - 1 - v
                        if 0 <= inv_u < size and 0 <= inv_v < size:
                            uv_coverage[inv_v, inv_u] = 1.0
                        uv_coverage_count += 1

        # Ha esetleg még nincsenek fedésben, tegyünk bele egy kis alapmintát, hogy ne legyen üres a kép
        if uv_coverage_count == 0:
            uv_coverage[int(size/2), int(size/2)] = 1.0

        sampled_vis = visibilities * uv_coverage
        reconstructed = np.abs(np.fft.ifft2(np.fft.ifftshift(sampled_vis)))

        max_val = np.max(reconstructed)
        if max_val > 0:
            reconstructed = reconstructed / max_val

        return uv_coverage_count, uv_coverage.tolist(), reconstructed.tolist()