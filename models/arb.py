from dataclass import dataclass,field
from datetime import datetime
from models.odds import OddsLine

@dataclass
class ArbLeg:
    odds_line: OddsLine
    stake: float
    profit_if_win: float

