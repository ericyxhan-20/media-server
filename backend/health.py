from fastapi import APIRouter
import psutil
from datetime import datetime

router = APIRouter()

def disk_usage():
    disk = psutil.disk_usage('/')
    return {
        "total": disk.total / (1024 ** 3),  # Convert bytes to GB
        "used": disk.used / (1024 ** 3),
        "free": disk.free / (1024 ** 3),
        "percent": disk.percent
    }

def ram_usage():
    ram = psutil.virtual_memory()
    return {
        "total": ram.total / (1024 ** 3),  # Convert bytes to GB
        "available": ram.available / (1024 ** 3),
        "used": ram.used / (1024 ** 3),
        "percent": ram.percent
    }

def cpu_usage():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(logical=True)
    }

@router.get("/health")
def health():
    # Perform all health checks
    disk = disk_usage()
    ram = ram_usage()
    cpu = cpu_usage()
    
    return {
        "status": "Healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "disk": disk,
        "ram": ram,
        "cpu": cpu
    }