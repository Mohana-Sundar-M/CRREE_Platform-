import psutil
import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crree")

class ResourceMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = 0
        self.start_cpu = 0

    def start(self):
        self.start_time = time.time()
        self.start_cpu = self.process.cpu_times().user + self.process.cpu_times().system

    def stop(self):
        end_time = time.time()
        end_cpu = self.process.cpu_times().user + self.process.cpu_times().system
        
        latency = (end_time - self.start_time) * 1000 # ms
        cpu_usage = (end_cpu - self.start_cpu) * 1000 # ms
        memory_usage = self.process.memory_info().rss / (1024 * 1024) # MB
        
        return {
            "latency_ms": latency,
            "cpu_time_ms": cpu_usage,
            "memory_mb": memory_usage
        }

monitor = ResourceMonitor()
