from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from contracts.context_contracts import ContextRequest, ProviderResult
from providers.base_provider import ContextProvider


class ObsidianProvider(ContextProvider):
    """
    Read-only adapter around the existing Retrieval V3.6 CLI.

    The existing retrieval engine remains the source of retrieval behavior.
    This adapter only translates ContextRequest -> CLI request and normalizes
    the JSON response into ProviderResult.
    """

    name = "obsidian"

    def __init__(
        self,
        retrieval_script: str | Path,
        python_executable: str = sys.executable,
        timeout_seconds: int = 120,
    ):
        self.retrieval_script = Path(retrieval_script)
        self.python_executable = python_executable
        self.timeout_seconds = timeout_seconds

    def capabilities(self) -> List[str]:
        return [
            "markdown_retrieval",
            "vault_search",
            "knowledge_retrieval",
            "retrieval_v36",
        ]

    def health(self) -> bool:
        return self.retrieval_script.exists() and self.retrieval_script.is_file()

    def retrieve(self, request: ContextRequest) -> ProviderResult:
        if not self.retrieval_script.exists():
            return ProviderResult(
                provider=self.name,
                status="UNAVAILABLE",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "obsidian_retrieval_v36",
                    "path": str(self.retrieval_script),
                },
                errors=[f"Retrieval script not found: {self.retrieval_script}"],
            )

        command = [
            self.python_executable,
            str(self.retrieval_script),
            "/json",
            request.user_query,
        ]

        # Ensure UTF-8 encoding for Windows subprocess execution to prevent cp1252 charmap errors
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                cwd=str(self.retrieval_script.parent),
                env=env,
                check=False,
            )

        except subprocess.TimeoutExpired:
            return ProviderResult(
                provider=self.name,
                status="TIMEOUT",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "obsidian_retrieval_v36",
                    "path": str(self.retrieval_script),
                },
                errors=[
                    f"Retrieval exceeded {self.timeout_seconds} seconds."
                ],
            )

        except OSError as exc:
            return ProviderResult(
                provider=self.name,
                status="ERROR",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "obsidian_retrieval_v36",
                    "path": str(self.retrieval_script),
                },
                errors=[str(exc)],
            )

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()

        if completed.returncode != 0:
            return ProviderResult(
                provider=self.name,
                status="ERROR",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "obsidian_retrieval_v36",
                    "path": str(self.retrieval_script),
                },
                errors=[
                    f"Retrieval exited with code {completed.returncode}.",
                    stderr,
                ] if stderr else [
                    f"Retrieval exited with code {completed.returncode}."
                ],
            )

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            return ProviderResult(
                provider=self.name,
                status="ERROR",
                query=request.user_query,
                content={},
                provenance={
                    "source_type": "obsidian_retrieval_v36",
                    "path": str(self.retrieval_script),
                },
                errors=[
                    f"Retrieval returned non-JSON output: {exc}",
                    stdout[:1000],
                ],
            )

        return ProviderResult(
            provider=self.name,
            status="SUCCESS",
            query=request.user_query,
            content=payload,
            provenance={
                "source_type": "obsidian_retrieval_v36",
                "path": str(self.retrieval_script),
                "retrieval_version": payload.get(
                    "retrieval_version",
                    "unknown",
                ),
                "read_only": True,
            },
            metadata={
                "return_code": completed.returncode,
                "stderr_present": bool(stderr),
            },
        )
