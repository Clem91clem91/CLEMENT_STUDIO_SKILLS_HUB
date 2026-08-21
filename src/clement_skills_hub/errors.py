"""Typed fail-closed errors."""


class SkillsHubError(RuntimeError):
    """Base error for deterministic, user-actionable failures."""


class AuditContractError(SkillsHubError):
    """Audit evidence does not match the certified contract."""


class SourceIntegrityError(SkillsHubError):
    """A source path or source hash is unsafe or changed."""


class ImportPlanError(SkillsHubError):
    """Normalized import planning failed."""


class RepositoryValidationError(SkillsHubError):
    """Generated repository content is invalid."""


class TransactionError(SkillsHubError):
    """A transactional apply or rollback could not complete."""

