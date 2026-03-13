from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    risk_approval_threshold: float = float(os.getenv("RISK_APPROVAL_THRESHOLD", "0.7"))


settings = Settings()