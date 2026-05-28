from dataclasses import dataclass, field
from typing import Any


@dataclass
class MCPToolResult:
    tool_name: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self):
        return {
            "tool_name": self.tool_name,
            "data": self.data,
            "error": self.error,
        }
