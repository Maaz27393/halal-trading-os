"""
Point-in-Time Shariah Universe Filter.
Ensures symbols tested on a given historical date match the approved compliance list valid for that specific time period.
"""
from datetime import datetime

class PointInTimeUniverse:
    def __init__(self, compliance_records: list[dict]):
        # compliance_records format: [{symbol, valid_from, valid_to, is_shariah}]
        self.records = compliance_records

    def is_eligible(self, symbol: str, evaluation_date: datetime) -> bool:
        for rec in self.records:
            if rec['symbol'] == symbol:
                if rec['valid_from'] <= evaluation_date <= rec['valid_to']:
                    return rec['is_shariah']
        return False
