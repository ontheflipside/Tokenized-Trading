from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class AgentConfig:
    raw: dict

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AgentConfig":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            return cls(raw=yaml.safe_load(f))

    @property
    def watchlist(self) -> list[dict]:
        return self.raw.get("watchlist", [])

    @property
    def report_directory(self) -> Path:
        return Path(self.raw.get("agent", {}).get("report_directory", "reports"))

    @property
    def kraken_base(self) -> str:
        return self.raw.get("kraken", {}).get("public_api_base", "https://api.kraken.com/0/public")

    @property
    def orderbook_depth(self) -> int:
        return int(self.raw.get("kraken", {}).get("orderbook_depth", 25))
