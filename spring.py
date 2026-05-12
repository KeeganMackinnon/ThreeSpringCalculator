from dataclasses import dataclass
from typing import Optional


@dataclass
class Spring:
    name: str
    rate: float       
    free_length: float      
    max_compression: Optional[float] = None  
    preload: float = 0.0      