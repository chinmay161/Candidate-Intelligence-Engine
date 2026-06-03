from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class BottleneckAnalyzer:
    """
    Analyzes runtime profiles to identify bottlenecks.
    """
    
    def analyze(self, profile: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyzes the runtime profile and returns bottleneck metrics.
        """
        total_time = profile.get("total_runtime", 0.0)
        if total_time <= 0:
            total_time = sum(v for k, v in profile.items() if k != "total_runtime")
            
        if total_time <= 0:
            return {
                "largest_runtime_component": None,
                "runtime_percentage": 0.0,
                "ranked_phases": []
            }
            
        # Filter out total_runtime for component analysis
        components = {k: v for k, v in profile.items() if k != "total_runtime"}
        
        ranked_phases = sorted(components.items(), key=lambda item: item[1], reverse=True)
        
        largest_component = ranked_phases[0][0] if ranked_phases else None
        largest_runtime = ranked_phases[0][1] if ranked_phases else 0.0
        
        return {
            "largest_runtime_component": largest_component,
            "runtime_percentage": round((largest_runtime / total_time) * 100, 2) if total_time > 0 else 0.0,
            "ranked_phases": [
                {
                    "phase": phase,
                    "runtime": runtime,
                    "percentage": round((runtime / total_time) * 100, 2)
                }
                for phase, runtime in ranked_phases
            ]
        }
