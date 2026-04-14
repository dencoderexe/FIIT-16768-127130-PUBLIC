from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass(frozen=True)
class Command:
    key: str                                        # unique identifier of the command (used internally)
    name: str                                       # human-readable name (for UI display)
    description: str
    template: str                                   # base command template with placeholders (formatted later)
    steps: List[str] = field(default_factory=list)  # ordered list of execution steps for progress tracking
    
    defaults: Dict[str, object] = field(default_factory=dict)   # default argument values (merged with user input)
    optionals: Dict[str, str] = field(default_factory=dict)     # optional CLI arguments mapping: {arg_name: flag}
    link_output_to_input_arg: Optional[str] = None              # optional: link output file next to this input argument (input file)
    msi_threshold: Optional[float] = None                       # optional: msi detection threshold

@dataclass(frozen=True)
class Tool:
    key: str                                        # unique identifier of the tool (used internally)
    name: str
    description: str
    dir: str                                        # directory where the tool is located
    commands: Dict[str, Command] = field(default_factory=dict)  # available commands for this tool