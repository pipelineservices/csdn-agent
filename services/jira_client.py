# services/jira_client.py

from __future__ import annotations
from typing import Dict, Any, List, Optional


class JiraClient:
    """
    Simple in-memory mock JIRA client.

    - No real HTTP calls
    - Issues live only in process memory
    """

    def __init__(self) -> None:
        self._issues: Dict[str, Dict[str, Any]] = {}
        self._counter: int = 1

    def create_issue(
        self,
        summary: str,
        description: str,
        severity: str = "medium",
        issue_type: str = "Incident",
    ) -> Dict[str, Any]:
        key = f"INC-{self._counter}"
        issue = {
            "id": str(self._counter),
            "key": key,
            "summary": summary,
            "description": description,
            "severity": severity,
            "type": issue_type,
            "status": "OPEN",
            "comments": [],
        }
        self._issues[key] = issue
        self._counter += 1
        return issue

    def add_comment(self, key: str, comment: str) -> Dict[str, Any]:
        issue = self._issues.get(key)
        if not issue:
            raise KeyError(f"Issue {key} not found in mock JIRA store")
        issue["comments"].append(comment)
        return issue

    def get_issue(self, key: str) -> Optional[Dict[str, Any]]:
        return self._issues.get(key)

    def list_issues(self) -> List[Dict[str, Any]]:
        return list(self._issues.values())


# Singleton instance used by the app
jira_client = JiraClient()
