from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from engine import SimulationEngine

app = FastAPI(title="SLICE Interferometry PoC")
engine = SimulationEngine()

app.mount("/static", StaticFiles(directory="static"), name="static")

class ConfigModel(BaseModel):
    wavelength: float
    fov: float
    objects: List[Dict[str, Any]]
    telescopes: List[Dict[str, Any]]

class SpeedModel(BaseModel):
    speed: int

@app.post("/api/config")
def set_configuration(config: ConfigModel):
    engine.wavelength = config.wavelength
    engine.fov = config.fov
    engine.astronomical_objects = config.objects
    engine.telescopes_config = config.telescopes
    return {"status": "success"}

@app.post("/api/start")
def start_simulation():
    engine.start()
    return {"status": "running"}

@app.post("/api/pause")
def pause_simulation():
    engine.pause()
    return {"status": "paused"}

@app.post("/api/stop")
def stop_simulation():
    engine.stop()
    return {"status": "stopped"}

@app.post("/api/speed")
def set_speed(data: SpeedModel):
    engine.speed = data.speed
    return {"status": "speed updated"}

@app.get("/api/state")
def get_state():
    if engine.is_running:
        engine.step()
    return engine.get_state()

@app.get("/api/export")
def export_state():
    return {
        "wavelength": engine.wavelength,
        "fov": engine.fov,
        "objects": engine.astronomical_objects,
        "telescopes": engine.telescopes_config
    }

@app.post("/api/import")
def import_state(config: ConfigModel):
    engine.wavelength = config.wavelength
    engine.fov = config.fov
    engine.astronomical_objects = config.objects
    engine.telescopes_config = config.telescopes
    return {"status": "imported successfully"}