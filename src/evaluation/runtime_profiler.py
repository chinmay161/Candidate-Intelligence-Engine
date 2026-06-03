import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RuntimeProfiler:
    """
    Measures time spent in different phases of the pipeline.
    """
    
    profiles: Dict[str, float] = field(default_factory=lambda: {
        "jd_parsing_time": 0.0,
        "candidate_parsing_time": 0.0,
        "feature_extraction_time": 0.0,
        "matching_time": 0.0,
        "ranking_time": 0.0,
        "reasoning_time": 0.0,
        "submission_time": 0.0,
        "total_runtime": 0.0
    })
    
    _start_times: Dict[str, float] = field(default_factory=dict)
    
    def start(self, phase: str) -> None:
        """Starts timing a specific phase."""
        self._start_times[phase] = time.perf_counter()
        
    def stop(self, phase: str) -> None:
        """Stops timing a specific phase and records the elapsed time."""
        if phase in self._start_times:
            elapsed = time.perf_counter() - self._start_times.pop(phase)
            self.profiles[phase] += elapsed
            
    def record_total(self, total_time: float) -> None:
        """Records the total runtime."""
        self.profiles["total_runtime"] = total_time

    def get_profile(self) -> Dict[str, float]:
        """Returns the profile dictionary."""
        return self.profiles

    def save(self, output_dir: str = "reports") -> str:
        """Saves the runtime profile to a JSON file."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "runtime_profile.json"
        
        with open(output_path, "w") as f:
            json.dump(self.profiles, f, indent=2)
            
        return str(output_path)
