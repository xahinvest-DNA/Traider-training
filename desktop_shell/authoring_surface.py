from __future__ import annotations

from runtime_bootstrap.bill_williams import (
    BEHAVIORAL_FLAG_CODES,
    BW_COMPLIANCE_LABELS,
    BW_ENTRY_TIMING_LABELS,
    BW_EXIT_QUALITY_LABELS,
    BW_MARKET_CONTEXT_LABELS,
    BW_REVIEW_CLARITY_LABELS,
    BW_SETUP_TAGS,
    BW_SETUP_VARIANTS,
    RULE_VIOLATION_CODES,
)


def get_setup_tag_options() -> list[str]:
    return sorted(BW_SETUP_TAGS)


def get_compliance_label_options() -> list[str]:
    return sorted(BW_COMPLIANCE_LABELS)


def get_setup_variant_options() -> list[str]:
    return sorted(BW_SETUP_VARIANTS)


def get_entry_timing_options() -> list[str]:
    return sorted(BW_ENTRY_TIMING_LABELS)


def get_market_context_options() -> list[str]:
    return sorted(BW_MARKET_CONTEXT_LABELS)


def get_exit_quality_options() -> list[str]:
    return sorted(BW_EXIT_QUALITY_LABELS)


def get_review_clarity_options() -> list[str]:
    return sorted(BW_REVIEW_CLARITY_LABELS)


def get_behavioral_flag_options() -> list[str]:
    return sorted(BEHAVIORAL_FLAG_CODES)


def get_rule_violation_options() -> list[str]:
    return sorted(RULE_VIOLATION_CODES)


def build_authoring_status_lines(journal_view: dict) -> list[str]:
    summary = journal_view["session_review_summary"]
    pending_trade_id = journal_view["review_pending_trade_id"] or "none"
    latest_method_facets = summary.get("latest_method_facets") or {}
    last_snapshot = journal_view.get("last_chart_snapshot") or {}
    completed_facets = sum(1 for value in latest_method_facets.values() if value)
    return [
        f"Pending review trade: {pending_trade_id}",
        f"Chart snapshots: {journal_view['chart_snapshot_count']}",
        f"Notes / reviews: {journal_view['pre_trade_note_count']} / {journal_view['post_trade_review_count']}",
        f"Flags / violations: {journal_view['behavioral_flag_count']} / {journal_view['rule_violation_count']}",
        f"Summary status: {summary['summary_status']}",
        f"Latest method facets filled: {completed_facets}/5",
        f"Latest snapshot: {last_snapshot.get('snapshot_role') or '-'} / {last_snapshot.get('artifact_ref') or '-'}",
    ]


def build_note_section_lines(journal_view: dict) -> list[str]:
    last_note = journal_view["last_pre_trade_note"]
    if last_note is None:
        return ["Last note: none", "Create a bounded pre-trade intent note before entry when useful"]
    return [
        f"Last note id: {last_note['note_id']}",
        f"Last note setup: {last_note.get('setup_tag') or '-'}",
        f"Last note trade link: {last_note.get('trade_id') or 'session-only'}",
        f"Last note snapshot: {last_note.get('chart_snapshot_ref') or '-'}",
    ]


def build_review_section_lines(journal_view: dict) -> list[str]:
    last_review = journal_view["last_post_trade_review"]
    if last_review is None:
        return ["Last review: none", "Create a bounded post-trade review after close when available"]
    review_snapshot_refs = list(last_review.get("chart_snapshot_refs") or [])
    return [
        f"Last review id: {last_review['review_id']}",
        f"Last review setup: {last_review.get('setup_tag') or '-'}",
        f"Last review compliance: {last_review.get('compliance_label') or '-'}",
        f"Last review variant: {last_review.get('setup_variant') or '-'}",
        f"Last review entry/context: {last_review.get('entry_timing_label') or '-'} / {last_review.get('market_context_label') or '-'}",
        f"Last review exit/clarity: {last_review.get('exit_quality_label') or '-'} / {last_review.get('review_clarity_label') or '-'}",
        f"Last review snapshots: {', '.join(review_snapshot_refs) or '-'}",
    ]
