from __future__ import annotations

BW_SETUP_TAGS = {
    "BW_1WM_LONG",
    "BW_1WM_SHORT",
    "BW_2WM_LONG",
    "BW_2WM_SHORT",
    "BW_3WM_LONG",
    "BW_3WM_SHORT",
    "BW_FRACTAL_LONG",
    "BW_FRACTAL_SHORT",
    "BW_AO_ADDON_LONG",
    "BW_AO_ADDON_SHORT",
    "BW_BALANCE_LINE_LONG",
    "BW_BALANCE_LINE_SHORT",
    "BW_MIXED_LONG",
    "BW_MIXED_SHORT",
    "BW_UNCLEAR",
}

BW_COMPLIANCE_LABELS = {
    "valid_setup",
    "weak_setup",
    "unconfirmed_setup",
    "late_entry",
    "early_entry",
    "add_on_valid",
    "add_on_invalid",
    "exit_by_rule",
    "exit_outside_rule",
    "unclear_setup",
    "not_bill_williams",
}

BW_REVIEW_TAGS = {
    "setup_clear",
    "setup_weak",
    "setup_unconfirmed",
    "setup_late",
    "setup_early",
    "setup_mixed",
    "setup_unclear",
    "not_bw_setup",
    "entry_precise",
    "entry_sloppy",
    "management_consistent",
    "management_inconsistent",
    "valid_add_on",
    "invalid_add_on",
    "exit_by_method",
    "exit_too_early",
    "exit_too_late",
    "exit_emotional",
    "alligator_supportive",
    "alligator_sleeping",
    "fractal_context_valid",
    "fractal_context_invalid",
    "ao_supportive",
    "ao_unsupportive",
    "timeframe_alignment_present",
    "timeframe_alignment_unclear",
}

BW_SETUP_VARIANTS = {
    "first_wise_man",
    "second_wise_man",
    "third_wise_man",
    "fractal_breakout",
    "ao_add_on",
    "balance_line_bounce",
    "mixed_context",
    "unclear_variant",
}

BW_ENTRY_TIMING_LABELS = {
    "timely_entry",
    "slightly_early_entry",
    "slightly_late_entry",
    "chased_entry",
    "unclear_entry_timing",
}

BW_MARKET_CONTEXT_LABELS = {
    "clean_context",
    "acceptable_context",
    "mixed_context",
    "weak_context",
    "unclear_context",
}

BW_EXIT_QUALITY_LABELS = {
    "disciplined_exit",
    "slightly_early_exit",
    "slightly_late_exit",
    "emotional_exit",
    "unclear_exit_quality",
}

BW_REVIEW_CLARITY_LABELS = {
    "high_clarity",
    "medium_clarity",
    "low_clarity",
    "needs_more_context",
}

BEHAVIORAL_FLAG_CODES = {
    "overtrading",
    "post_loss_revenge_trading",
    "averaging_down",
    "oversized_position",
    "impulsive_entry",
    "no_stop_entry",
    "premature_exit",
    "rule_violation_setup",
    "risk_escalation_after_win",
    "risk_escalation_after_loss",
    "holding_loser_too_long",
    "cost_blind_trading",
}

RULE_VIOLATION_CODES = {
    "bw_setup_missing_confirmation",
    "bw_entry_without_fractal_context",
    "bw_entry_against_alligator_context",
    "session_second_independent_trade_attempt",
    "execution_outside_session_rule",
    "invalid_position_size",
    "missing_stop_loss",
    "manual_plan_deviation",
    "exam_mode_backseek_attempt",
    "exam_mode_restart_attempt",
}

FLAG_SOURCES = {"manual", "derived", "hybrid"}
FLAG_SCOPES = {"session", "trade", "execution"}
FLAG_SEVERITIES = {"info", "warning", "high"}
VIOLATION_SOURCES = {"manual_review", "derived_rule_engine", "hybrid"}
VIOLATION_SCOPES = {"session", "trade", "execution"}
VIOLATION_SEVERITIES = {"soft", "hard"}


def _validate_membership(value: str | None, allowed: set[str], label: str) -> str | None:
    if value is None:
        return None
    if value not in allowed:
        raise ValueError(f"Unsupported {label}: {value}")
    return value


def validate_setup_tag(value: str | None) -> str | None:
    return _validate_membership(value, BW_SETUP_TAGS, "Bill Williams setupTag")


def validate_compliance_label(value: str | None) -> str | None:
    return _validate_membership(value, BW_COMPLIANCE_LABELS, "Bill Williams complianceLabel")


def validate_review_tags(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    normalized = tuple(values)
    invalid = [value for value in normalized if value not in BW_REVIEW_TAGS]
    if invalid:
        raise ValueError(f"Unsupported Bill Williams reviewTags: {', '.join(invalid)}")
    return normalized


def validate_review_setup_variant(value: str | None) -> str | None:
    return _validate_membership(value, BW_SETUP_VARIANTS, "Bill Williams review setupVariant")


def validate_entry_timing_label(value: str | None) -> str | None:
    return _validate_membership(value, BW_ENTRY_TIMING_LABELS, "Bill Williams review entryTimingLabel")


def validate_market_context_label(value: str | None) -> str | None:
    return _validate_membership(value, BW_MARKET_CONTEXT_LABELS, "Bill Williams review marketContextLabel")


def validate_exit_quality_label(value: str | None) -> str | None:
    return _validate_membership(value, BW_EXIT_QUALITY_LABELS, "Bill Williams review exitQualityLabel")


def validate_review_clarity_label(value: str | None) -> str | None:
    return _validate_membership(value, BW_REVIEW_CLARITY_LABELS, "Bill Williams review clarityLabel")


def validate_behavioral_flag_code(value: str) -> str:
    return _validate_membership(value, BEHAVIORAL_FLAG_CODES, "BehavioralFlag flagCode") or value


def validate_rule_violation_code(value: str) -> str:
    return _validate_membership(value, RULE_VIOLATION_CODES, "RuleViolation ruleCode") or value


def validate_flag_source(value: str) -> str:
    return _validate_membership(value, FLAG_SOURCES, "BehavioralFlag source") or value


def validate_flag_scope(value: str) -> str:
    return _validate_membership(value, FLAG_SCOPES, "BehavioralFlag scope") or value


def validate_flag_severity(value: str) -> str:
    return _validate_membership(value, FLAG_SEVERITIES, "BehavioralFlag severity") or value


def validate_violation_source(value: str) -> str:
    return _validate_membership(value, VIOLATION_SOURCES, "RuleViolation source") or value


def validate_violation_scope(value: str) -> str:
    return _validate_membership(value, VIOLATION_SCOPES, "RuleViolation scope") or value


def validate_violation_severity(value: str) -> str:
    return _validate_membership(value, VIOLATION_SEVERITIES, "RuleViolation severity") or value
