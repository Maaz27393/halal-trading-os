import os
import json
import logging
from typing import Dict

logger = logging.getLogger("ChartinkAuthSessionProvider")

class ChartinkAuthSessionProvider:
    """
    Manages local session cookies securely within the peripheral ecosystem.
    Parses standard browser export JSON lists into requests-compatible cookies.
    """
    def __init__(self):
        self.session_file = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem\\Canonical Universe\\chartink_session.json"

    def load_session_cookies(self) -> Dict[str, str]:
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Handle list format from Cookie Editor extensions
                    cookie_dict = {}
                    if isinstance(data, list):
                        for cookie in data:
                            if "name" in cookie and "value" in cookie:
                                cookie_dict[cookie["name"]] = cookie["value"]
                    elif isinstance(data, dict):
                        cookie_dict = data

                    logger.info(f"Successfully loaded {len(cookie_dict)} session cookie(s) from local store.")
                    return cookie_dict
            except Exception as e:
                logger.warning(f"Failed to load session cookies file: {e}")
        else:
            logger.warning(f"Session file not found at: {self.session_file}")
        return {}