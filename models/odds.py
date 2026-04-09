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

@dataclass
class Oddsline:
    book: str #Draftkings,Fanduel,Betmgm, Caesars
    event_id: str   
    sport: str  #NBA, NFL, NBA, NHL
    market_type: MarketType
    outcome_label: str  #Home, Away, Over, Under, Draw
    raw_odds: str   #Original string scraped as e.g. -110
    odds_format: OddsFormat
    decimal_oods: float
    scraped_at: datetime = field(defulat_factory = datetime.utcnow)
    bet_url = str = ""

