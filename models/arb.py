from dataclass import dataclass,field
from datetime import datetime
from models.odds import OddsLine

@dataclass
class ArbLeg:
    odds_line: OddsLine
    stake: float
    profit_if_win: float

@dataclass
class ArbOpportunity:
    id:str
    legs: list[ArbLeg]
    implied_margin: float
    profit_margin: float
    guarenteed_profit: float
    total_stake: float
    detected_at: datetime
    fired: bool = False
    fire_results: list[dict] = field(default_factory=list)
     