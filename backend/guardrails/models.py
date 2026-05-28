from dataclasses import dataclass, field


@dataclass
class GuardrailResult:
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    blocked_reason: str | None = None

    def to_dict(self):
        return {
            "passed": self.passed,
            "warnings": self.warnings,
            "blocked_reason": self.blocked_reason,
        }
