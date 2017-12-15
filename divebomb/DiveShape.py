
from enum import Enum
class DiveShape(Enum):
    """
    DiveShape is an enumeration for classifying dives.
    
    """
    def __str__(self):
        return str(self.value)

    SQUARE = 'square'
    VSHAPE = 'v-shape'
    USHAPE = 'u-shape'
    WSHAPE = 'w-shape'
    LEFTSKEW = 'left'
    RIGHTSKEW = 'right'
    OTHER = 'other'
    UNKNOWN = 'unkown'
    SURFACE = 'surface'
    WIGGLE = 'wiggle'
    FLAT = 'flat'
    SHALLOW = 'shallow'
