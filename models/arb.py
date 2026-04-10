from dataclasses import dataclass,field
from datetime import datetime
from models.odds import OddsLine

@dataclass
class ArbLeg:
    odds_line: OddsLine
    stake: float
    profit_if_wins: float

@dataclass
class ArbOpportunities:
    id:str
    legs: list[ArbLeg]
    implied_probability_sum: float
    profit_margin: float
    guaranteed_profit: float
    total_stake: float
    detected_at: datetime
    fired: bool = False
    fire_results: list[dict] = field(default_factory=list)

if __name__ == "__main__":
    from models.odds import OddsLine, OddsFormat, MarketType

    leg1 = ArbLeg(
        odds_line = OddsLine(
            book = "draftkings",
            event_id = "nba::Celtic__Heat::2026-04-09",
            sport = "nba",
            market_type = MarketType.MONEYLINE,
            outcome_label = "home",
            raw_odds = "+200",
            odds_format = OddsFormat.AMERICAN,
            decimal_odds = 3.0
        ),

        stake = 333.33,
        profit_if_wins = 666.67,
    )

    arb = ArbOpportunities(
        id = "Test-001",
        legs = [leg1],
        implied_probability_sum = 0.97,
        profit_margin = 0.03,
        guaranteed_profit = 30.0,
        total_stake = 1000.0,
        detected_at = datetime.utcnow(),
    )

    print(arb)