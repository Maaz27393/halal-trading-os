from .source import HistoricalBars

class AcquisitionValidator:
    @staticmethod
    def validate(bars: HistoricalBars) -> bool:
        """Enforce S4.1 acquisition integrity rules (empty checks, duplicates)."""
        if bars.dataframe is None or bars.dataframe.empty:
            raise ValueError("Acquisition rejected: Received empty historical dataset.")
        
        if "Date" in bars.dataframe.columns and bars.dataframe["Date"].duplicated().any():
            raise ValueError("Acquisition rejected: Duplicate dates detected in historical sequence.")
            
        return True
