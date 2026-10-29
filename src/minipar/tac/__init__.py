from .generator import TACGenerator
from .instructions import TACClass, TACFunction, TACInstr, TACProgram
from .interface import ITACGenerator

__all__ = ["ITACGenerator", "TACGenerator", "TACProgram", "TACFunction", "TACClass", "TACInstr"]
