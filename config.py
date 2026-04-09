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
    

