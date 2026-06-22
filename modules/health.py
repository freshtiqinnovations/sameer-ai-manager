import psutil, shutil

def health_report():
    disk = shutil.disk_usage("/")
    ram = psutil.virtual_memory()

    return f"""
🟢 SAMEER AI MANAGER HEALTH

CPU: {psutil.cpu_percent()}%
RAM: {ram.percent}%
DISK: {round(disk.used/disk.total*100,2)}%

TOTAL RAM: {round(ram.total/1024/1024/1024,2)} GB
FREE RAM: {round(ram.available/1024/1024/1024,2)} GB

AUTO MODE: ACTIVE
SERVER: HEALTHY
"""
import psutil, shutil

def health_report():
    total, used, free = shutil.disk_usage("/")
    ram = psutil.virtual_memory()

    return f"""
🟢 SERVER HEALTH

CPU: {psutil.cpu_percent()}%
RAM: {ram.percent}%
DISK: {used // (2**30)}GB / {total // (2**30)}GB
FREE: {free // (2**30)}GB
"""
