from dataclasses import dataclass,field
from datetime import datatime
from enum import Enum

class OddsFormat(Enum):
    AMERICAN = "american"
    DECIMAL = "decimal"
    FRACTIONAL = "fractional"


class MarketType(Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    THREE_WAY = "threeway"

