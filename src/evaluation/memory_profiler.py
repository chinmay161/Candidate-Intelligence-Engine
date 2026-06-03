import json
import psutil
import os
from typing import Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MemoryProfiler:
    """
    Measures memory usage metrics of the pipeline.
    """
    
    peak_memory_mb: float = 0.0
    average_memory_mb: float = 0.0
    memory_per_candidate: float = 0.0
    _measurements: list[float] = field(default_factory=list)
    _process: psutil.Process = field(default_factory=lambda: psutil.Process(os.getpid()))

    def snapshot(self) -> float:
        """Takes a memory snapshot in MB and returns it."""
        mem_info = self._process.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        self._measurements.append(mem_mb)
        
        if mem_mb > self.peak_memory_mb:
            self.peak_memory_mb = mem_mb
            
        return mem_mb

    def compute_metrics(self, num_candidates: int) -> None:
        """Computes average and per-candidate memory."""
        if self._measurements:
            self.average_memory_mb = sum(self._measurements) / len(self._measurements)
        
        if num_candidates > 0:
            self.memory_per_candidate = self.peak_memory_mb / num_candidates
        else:
            self.memory_per_candidate = 0.0

    def get_profile(self) -> Dict[str, float]:
        """Returns the memory profile dictionary."""
        return {
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "average_memory_mb": round(self.average_memory_mb, 2),
            "memory_per_candidate": round(self.memory_per_candidate, 4)
        }

    def save(self, output_dir: str = "reports") -> str:
        """Saves the memory profile to a JSON file."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "memory_profile.json"
        
        with open(output_path, "w") as f:
            json.dump(self.get_profile(), f, indent=2)
            
        return str(output_path)
