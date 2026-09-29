from pathlib import Path
from .source import HistoricalBars

class StagingManager:
    def __init__(self, staging_dir: Path):
        self.staging_dir = Path(staging_dir)
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def stage_bars(self, bars: HistoricalBars, overwrite: bool = False) -> Path:
        file_path = self.staging_dir / f"{bars.symbol.upper()}_{bars.start_date}_{bars.end_date}.csv"
        if file_path.exists() and not overwrite:
            raise FileExistsError(f"Staged file already exists and overwrite=False: {file_path}")
        bars.dataframe.to_csv(file_path, index=False)
        return file_path
