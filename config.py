import os
from dataclasses import dataclass,field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BookCredentials:
    username: str
    password: str


@dataclass
class Config:
    scrape_interval_seconds: int = 30
    headless: bool = True
    use_stealth: bool = True
    requrest_timeout_ms: int = 15000
    min_action_delay_ms: int = 800
    max_action_delay_ms: int = 2500
    min_profit_margin: float = 0.01
    max_profit_margin: float = 10000.0
    max_strake_per_leg: float = 500.0
    discord_webhook_url: str | None = None
    alert_cooldown_seconds: int = 300
    autofire_enables: bool = False
    autofire_confirm_threshold: float = 0.02
    dashboard_host: str = "0.0.0.0"
    dashbord_port: int = 8000
    credentials: dict[str, BookCredentials] = field(default_factory = dict)

def load_config() -> Config:
    credentials = {}
    for book in ["draftkings","fanduel","betmgm","caesars"]:
        user = os.getenv(f"{book.upper()}_USERNAME","")
        pw = os.getenv(f"{book.upper()}_PASSWORD","")
        if user and pw:
            credentials[book] = BookCredentials(username=user, password=pw)

    return Config(
        scrape_interval_seconds = int(os.getenv("SCRAOE_INTERVAL_SECONDS",30)),
        headless=os.getenv("HEADLESS","true").lower() == "true",
        use_stealth=os.getenv("USE_STEALTH","true").lower() == "true",
        min_profit_margin=float(os.getenv("MIN_PROFIT_MARGIN", 0.01)),
        total_bankroll=float(os.getenv("TOTAL_BANKROLL", 10000)),
        max_stake_per_leg=float(os.getenv("MAX_STAKE_PER_LEG", 500)),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
        alert_cooldown_seconds=int(os.getenv("ALERT_COOLDOWN_SECONDS", 300)),
        autofire_enabled=os.getenv("AUTOFIRE_ENABLED", "false").lower() == "true",
        autofire_confirm_threshold=float(os.getenv("AUTOFIRE_CONFIRM_THRESHOLD", 0.02)),
        dashboard_host=os.getenv("DASHBOARD_HOST", "0.0.0.0"),
        dashboard_port=int(os.getenv("DASHBOARD_PORT", 8000)),
        credentials=credentials,
    )
