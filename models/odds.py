from dataclasses import dataclass,field
from datetime import datetime
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
class OddsLine:
    book: str #Draftkings,Fanduel,Betmgm, Caesars
    event_id: str   
    sport: str  #NBA, NFL, NBA, NHL
    market_type: MarketType
    outcome_label: str  #Home, Away, Over, Under, Draw
    raw_odds: str   #Original string scraped as e.g. -110
    odds_format: OddsFormat
    decimal_odds: float
    scraped_at: datetime = field(default_factory = datetime.utcnow)
    bet_url = str = ""

@dataclass
class MarketSnapshot:
    event_id: str
    market_type: MarketType
    lines: list[OddsLine]
    snapshot_at: datetime = field(default_factory=datetime.utcnow)

if __name__ == "__main__":
    line = OddsLine(
        book = "draftkings",
        event_id="nba::boston_celtics__miami_heat::2026-04-09",
        sport="nba",
        market_type=MarketType.MONEYLINE,
        outcome_label="home",
        raw_odds="-110",
        odds_format=OddsFormat.AMERICAN,
        decimal_odds=1.909,

    )
    print(line)