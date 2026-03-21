from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass(frozen=True)
class Command:
    key: str
    name: str
    description: str
    template: str
    steps: List[str] = field(default_factory=list)
    
    defaults: Dict[str, object] = field(default_factory=dict)
    optionals: Dict[str, str] = field(default_factory=dict)
    link_output_to_input_arg: Optional[str] = None

@dataclass(frozen=True)
class Tool:
    key: str
    name: str
    description: str
    dir: str
    commands: Dict[str, Command] = field(default_factory=dict)