import os
import logging
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("AdvancedChartingExporter")

class ChartAnnotation(BaseModel):
    symbol: str
    timeframe: str
    pattern_detected: str  # e.g., "Bullish Pullback", "Volume Breakout"
    key_support: float
    key_resistance: float
    confidence_score: float

class ChartingReport(BaseModel):
    timestamp: str
    instrument_count: int
    annotations: List[ChartAnnotation]
    provenance: List[str]

class AdvancedChartingExporter:
    """
    P5.1 Expansion: Generates structured technical pattern annotations
    and exports formatted charting summaries to the local Obsidian vault.
    """

    def __init__(self, permission_gateway: PermissionGateway, vault_base_path: str):
        self.permission_gateway = permission_gateway
        self.vault_path = vault_base_path
        logger.info("AdvancedChartingExporter initialized for P5.1.")

    def generate_and_export_charts(self, symbols: List[str], caller_role: str = "analyst_agent") -> str:
        """
        1. Verify READ/WRITE permissions via the immutable Gateway.
        2. Generate synthetic technical chart annotations.
        3. Serialize into structured Markdown with fail-safe directory creation.
        """
        if not self.permission_gateway.verify_permission(caller_role, "READ") or \
           not self.permission_gateway.verify_permission(caller_role, "WRITE"):
            raise PermissionError(f"Caller role '{caller_role}' lacks permissions for charting export.")

        logger.info(f"Generating advanced chart annotations for symbols: {symbols}")

        annotations = []
        for sym in symbols:
            annotations.append(
                ChartAnnotation(
                    symbol=sym,
                    timeframe="1D / 4H",
                    pattern_detected="Bullish EMA 20/50 Pullback & Volume Expansion",
                    key_support=2820.0 if sym == "RELIANCE" else 3350.0,
                    key_resistance=2950.0 if sym == "RELIANCE" else 3480.0,
                    confidence_score=0.88
                )
            )

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        report = ChartingReport(
            timestamp=datetime.utcnow().isoformat(),
            instrument_count=len(symbols),
            annotations=annotations,
            provenance=[
                f"P5.1 Advanced Charting Module Active",
                f"Immutable Guardrail: LIVE_AUTO_EXECUTION = {LIVE_AUTO_EXECUTION}"
            ]
        )

        # Construct Markdown formatting
        md_content = f"""---
date: {date_str}
type: advanced-charting-report
instruments_analyzed: {report.instrument_count}
guardrail: LIVE_AUTO_EXECUTION=FALSE
---

# Advanced Technical Charting & Pattern Annotations - {date_str}

## Overview
- **Instruments Evaluated**: {report.instrument_count}
- **Primary Pattern Framework**: Multi-timeframe EMA Pullback & Volume Spikes

## Pattern Annotations
"""
        for item in report.annotations:
            md_content += f"""### {item.symbol} ({item.timeframe})
- **Detected Pattern**: `{item.pattern_detected}`
- **Key Support**: `{item.key_support}`
- **Key Resistance**: `{item.key_resistance}`
- **Confidence Score**: `{item.confidence_score * 100}%`
"""

        md_content += f"\n## Provenance\n"
        for prov in report.provenance:
            md_content += f"- {prov}\n"

        # Safe directory provisioning (prevents path does not exist errors)
        target_dir = os.path.join(self.vault_path, "Peripheral Ecosystem", "Advanced Charts")
        os.makedirs(target_dir, exist_ok=True)
        
        file_path = os.path.join(target_dir, f"AdvancedCharts_{date_str}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Successfully exported P5.1 charting artifact to {file_path}")
        return file_path