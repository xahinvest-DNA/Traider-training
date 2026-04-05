from __future__ import annotations

from typing import Any

from .transition_state import build_transition_state_view


def build_session_context_lines(journal_view: dict[str, Any]) -> list[str]:
    finalization = journal_view["session_finalization"]
    transition_state = build_transition_state_view(journal_view)
    recovery_text = transition_state["recovery_acknowledgment_text"]
    return [
        f"Session: {journal_view['session_id']}",
        f"Status: {journal_view['session_status']}",
        f"Mode: {journal_view['mode']}",
        f"Instrument: {journal_view['instrument_id']}",
        f"Timeframe: {journal_view['active_timeframe']}",
        f"Recovered: {'yes' if journal_view['recovered'] else 'no'}",
        f"Finalization: {finalization['finalization_status']}",
        f"Recovery follow-up: {recovery_text if recovery_text != 'none' else '-'}",
    ]


def build_trade_context_lines(trading_view: dict[str, Any], journal_view: dict[str, Any] | None = None) -> list[str]:
    last_execution = trading_view.get("last_execution_outcome")
    execution_label = last_execution["execution_type"] if last_execution else "none"
    dataset_quality = trading_view.get("dataset_quality_context") or {}
    plan_context = (journal_view or {}).get("current_trade_plan_context") or {}
    transition_state = build_transition_state_view(journal_view or {"session_finalization": {"is_session_finalized": False, "replay_running": False}, "session_review_summary": {}}, trading_view) if journal_view else None
    pending_trigger_price = trading_view.get("pending_stop_trigger_price")
    pending_stop_loss = trading_view.get("pending_stop_stop_loss")
    pending_take_profit = trading_view.get("pending_stop_take_profit")
    lines = [
        f"Lifecycle: {trading_view['lifecycle_state']}",
        f"Trade status: {trading_view['trade_status']}",
        f"Active trade: {'yes' if trading_view['active_trade_present'] else 'no'}",
        f"Trade lifecycle focus: {transition_state['lifecycle_label'] if transition_state else ('active_trade_open' if trading_view['active_trade_present'] else 'idle')}",
        f"Trade lifecycle text: {transition_state['lifecycle_text'] if transition_state else ('Active trade is open.' if trading_view['active_trade_present'] else 'No trade lifecycle is currently in progress.')}",
        f"Pending stop: {'yes' if trading_view.get('pending_stop_present') else 'no'}",
        f"Pending stop side: {trading_view.get('pending_stop_side') or '-'}",
        f"Pending stop trigger: {pending_trigger_price if pending_trigger_price is not None else '-'}",
        f"Pending stop status: {trading_view.get('pending_stop_status') or '-'}",
        f"Pending stop SL / TP: {pending_stop_loss if pending_stop_loss is not None else '-'} / {pending_take_profit if pending_take_profit is not None else '-'}",
        f"Pending stop result: {trading_view.get('latest_pending_stop_result') or '-'}",
        f"Side: {trading_view['trade_side'] or '-'}",
        f"Open volume: {trading_view['current_open_volume']}",
        f"Opened / closed volume: {trading_view.get('total_opened_volume', 0.0)} / {trading_view.get('total_closed_volume', 0.0)}",
        f"Trade partially closed: {'yes' if trading_view.get('trade_partially_closed') else 'no'}",
        f"Protection present: {'yes' if trading_view.get('protection_present') else 'no'}",
        f"Stop loss / take profit: {trading_view.get('current_stop_loss') if trading_view.get('current_stop_loss') is not None else '-'} / {trading_view.get('current_take_profit') if trading_view.get('current_take_profit') is not None else '-'}",
        f"Manual close available: {'yes' if trading_view['manual_close_available'] else 'no'}",
        f"Partial close available: {'yes' if trading_view.get('partial_close_available') else 'no'}",
        f"Last execution: {execution_label}",
        f"Last execution reason: {last_execution.get('reason') if last_execution else '-'}",
        f"Last close reason: {trading_view.get('last_close_reason') or '-'}",
    ]
    lines.extend(_build_plan_context_lines(plan_context))
    lines.extend([
        f"Dataset quality context: {dataset_quality.get('context_status') or '-'}",
        f"Dataset quality text: {dataset_quality.get('context_text') or '-'}",
    ])
    return lines


def build_review_summary_lines(journal_view: dict[str, Any]) -> list[str]:
    summary = journal_view["session_review_summary"]
    latest_method_facets = summary.get("latest_method_facets") or {}
    latest_intent_delta = summary.get("latest_intent_delta") or {}
    latest_review_completeness = summary.get("latest_review_completeness") or {}
    latest_review_sequence = summary.get("latest_review_sequence") or {}
    weak_spots = summary.get("review_weak_spots") or {}
    review_progress = summary.get("review_progress") or {}
    review_momentum = summary.get("review_momentum") or {}
    review_stability = summary.get("review_stability") or {}
    review_swings = summary.get("review_swings") or {}
    review_floor = summary.get("review_floor") or {}
    review_ceiling = summary.get("review_ceiling") or {}
    review_band = summary.get("review_band") or {}
    review_headroom = summary.get("review_headroom") or {}
    review_pressure = summary.get("review_pressure") or {}
    review_target = summary.get("review_target") or {}
    review_focus = summary.get("review_focus") or {}
    review_cue = summary.get("review_cue") or {}
    review_badge = summary.get("review_badge") or {}
    review_pill = summary.get("review_pill") or {}
    review_chip = summary.get("review_chip") or {}
    review_tag = summary.get("review_tag") or {}
    review_token = summary.get("review_token") or {}
    review_marker = summary.get("review_marker") or {}
    review_glyph = summary.get("review_glyph") or {}
    review_sigil = summary.get("review_sigil") or {}
    review_seal = summary.get("review_seal") or {}
    review_crest = summary.get("review_crest") or {}
    review_emblem = summary.get("review_emblem") or {}
    review_insignia = summary.get("review_insignia") or {}
    review_standard = summary.get("review_standard") or {}
    review_banner = summary.get("review_banner") or {}
    review_pennant = summary.get("review_pennant") or {}
    review_streamer = summary.get("review_streamer") or {}
    review_rule_context = summary.get("review_rule_context") or {}
    review_discipline_cue = summary.get("review_discipline_cue") or {}
    review_discipline_badge = summary.get("review_discipline_badge") or {}
    review_discipline_token = summary.get("review_discipline_token") or {}
    review_discipline_marker = summary.get("review_discipline_marker") or {}
    review_discipline_glyph = summary.get("review_discipline_glyph") or {}
    review_discipline_sigil = summary.get("review_discipline_sigil") or {}
    review_discipline_seal = summary.get("review_discipline_seal") or {}
    review_discipline_crest = summary.get("review_discipline_crest") or {}
    review_discipline_emblem = summary.get("review_discipline_emblem") or {}
    review_discipline_reason = summary.get("review_discipline_reason") or {}
    review_dataset_quality_link = summary.get("review_dataset_quality_link") or {}
    latest_evidence_status = summary.get("latest_bill_williams_review_evidence_status") or "-"
    latest_evidence_text = summary.get("latest_bill_williams_review_evidence_text") or "-"
    latest_follow_up_status = summary.get("latest_bill_williams_review_evidence_follow_up_status") or "-"
    latest_follow_up_text = summary.get("latest_bill_williams_review_evidence_follow_up_text") or "-"
    latest_digest_status = summary.get("latest_current_trade_review_digest_status") or "not_applicable"
    latest_digest_headline = summary.get("latest_current_trade_review_digest_headline") or "-"
    latest_digest_primary_gap = summary.get("latest_current_trade_review_digest_primary_gap") or "-"
    latest_digest_next_step = summary.get("latest_current_trade_review_digest_next_step") or "-"
    dataset_quality = journal_view.get("dataset_quality_context") or {}
    coverage = summary.get("review_field_coverage") or {}
    completed_facets = sum(1 for value in latest_method_facets.values() if value)
    missing_parts = ", ".join(latest_review_completeness.get("missing_parts", [])) or "none"
    next_review_field = latest_review_sequence.get("next_field") or "-"
    weak_spot_fields = ", ".join(weak_spots.get("top_weak_spot_fields", [])) or "none"
    improved_fields = ", ".join(review_progress.get("improved_fields", [])) or "none"
    still_missing_fields = ", ".join(review_progress.get("still_missing_fields", [])) or "none"
    score_sequence = ", ".join(str(value) for value in review_momentum.get("score_sequence", [])) or "none"
    return [
        f"Summary status: {summary['summary_status']}",
        f"Closed trades: {summary['closed_trade_count']}",
        f"Reviewed trades: {summary['reviewed_trade_count']}",
        f"Pending review: {summary['pending_review_trade_count']}",
        f"Flags / violations: {summary['behavioral_flag_count']} / {summary['rule_violation_count']}",
        f"Snapshot-linked trades: {summary['trades_with_linked_chart_snapshots_count']}",
        f"Reviewed trades with BW evidence: {summary.get('reviewed_trades_with_bw_evidence_count', 0)}",
        f"Reviewed trades missing BW evidence: {summary.get('reviewed_trades_missing_bw_evidence_count', 0)}",
        f"Reviewed trades needing BW evidence follow-up: {summary.get('reviewed_trades_requiring_bw_evidence_follow_up_count', 0)}",
        f"Method-facet trades: {summary['trades_with_method_facets_count']}",
        f"Intent confirmed/refined/changed: {summary['intent_confirmed_count']} / {summary['intent_refined_count']} / {summary['intent_changed_count']}",
        f"Intent missing / review missing: {summary['intent_missing_count']} / {summary['review_missing_count']}",
        f"Review complete/partial/sparse: {summary['review_complete_count']} / {summary['review_partial_count']} / {summary['review_sparse_count']}",
        f"Coverage setup/compliance: {coverage.get('setup_tag_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)} / {coverage.get('compliance_label_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)}",
        f"Coverage entry/context: {coverage.get('entry_timing_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)} / {coverage.get('market_context_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)}",
        f"Coverage exit/clarity: {coverage.get('exit_quality_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)} / {coverage.get('review_clarity_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)}",
        f"Review weak spots: {weak_spot_fields}",
        f"Review progress: {review_progress.get('progress_status') or '-'}",
        f"Weak spots improved/still missing: {improved_fields} / {still_missing_fields}",
        f"Review momentum: {review_momentum.get('momentum_status') or '-'}",
        f"Momentum score sequence: {score_sequence}",
        f"Review stability: {review_stability.get('stability_status') or '-'}",
        f"Stability spread: {review_stability.get('score_spread') if review_stability.get('score_spread') is not None else '-'}",
        f"Review swings: {review_swings.get('swing_status') or '-'}",
        f"Max adjacent jump: {review_swings.get('max_adjacent_jump') if review_swings.get('max_adjacent_jump') is not None else '-'}",
        f"Review floor: {review_floor.get('floor_status') or '-'}",
        f"Min recent score: {review_floor.get('min_recent_score') if review_floor.get('min_recent_score') is not None else '-'}",
        f"Review ceiling: {review_ceiling.get('ceiling_status') or '-'}",
        f"Max recent score: {review_ceiling.get('max_recent_score') if review_ceiling.get('max_recent_score') is not None else '-'}",
        f"Review band: {review_band.get('band_status') or '-'}",
        f"Recent quality corridor: {review_band.get('corridor_label') or '-'}",
        f"Band width: {review_band.get('band_width') if review_band.get('band_width') is not None else '-'}",
        f"Review headroom: {review_headroom.get('headroom_status') or '-'}",
        f"Remaining headroom: {review_headroom.get('remaining_headroom') if review_headroom.get('remaining_headroom') is not None else '-'}",
        f"Review pressure: {review_pressure.get('pressure_status') or '-'}",
        f"Pressure target: {review_pressure.get('pressure_target') or '-'}",
        f"Review target: {review_target.get('target_status') or '-'}",
        f"Target field: {review_target.get('target_field') or '-'}",
        f"Review focus: {review_focus.get('focus_status') or '-'}",
        f"Focus label: {review_focus.get('focus_label') or '-'}",
        f"Review cue: {review_cue.get('cue_status') or '-'}",
        f"Cue text: {review_cue.get('cue_text') or '-'}",
        f"Review badge: {review_badge.get('badge_status') or '-'}",
        f"Badge text: {review_badge.get('badge_text') or '-'}",
        f"Review pill: {review_pill.get('pill_status') or '-'}",
        f"Pill text: {review_pill.get('pill_text') or '-'}",
        f"Review chip: {review_chip.get('chip_status') or '-'}",
        f"Chip text: {review_chip.get('chip_text') or '-'}",
        f"Review tag: {review_tag.get('tag_status') or '-'}",
        f"Tag text: {review_tag.get('tag_text') or '-'}",
        f"Review token: {review_token.get('token_status') or '-'}",
        f"Token text: {review_token.get('token_text') or '-'}",
        f"Review marker: {review_marker.get('marker_status') or '-'}",
        f"Marker text: {review_marker.get('marker_text') or '-'}",
        f"Review glyph: {review_glyph.get('glyph_status') or '-'}",
        f"Glyph text: {review_glyph.get('glyph_text') or '-'}",
        f"Review sigil: {review_sigil.get('sigil_status') or '-'}",
        f"Sigil text: {review_sigil.get('sigil_text') or '-'}",
        f"Review seal: {review_seal.get('seal_status') or '-'}",
        f"Seal text: {review_seal.get('seal_text') or '-'}",
        f"Review crest: {review_crest.get('crest_status') or '-'}",
        f"Crest text: {review_crest.get('crest_text') or '-'}",
        f"Review emblem: {review_emblem.get('emblem_status') or '-'}",
        f"Emblem text: {review_emblem.get('emblem_text') or '-'}",
        f"Review insignia: {review_insignia.get('insignia_status') or '-'}",
        f"Insignia text: {review_insignia.get('insignia_text') or '-'}",
        f"Review standard: {review_standard.get('standard_status') or '-'}",
        f"Standard text: {review_standard.get('standard_text') or '-'}",
        f"Review banner: {review_banner.get('banner_status') or '-'}",
        f"Banner text: {review_banner.get('banner_text') or '-'}",
        f"Review pennant: {review_pennant.get('pennant_status') or '-'}",
        f"Pennant text: {review_pennant.get('pennant_text') or '-'}",
        f"Review streamer: {review_streamer.get('streamer_status') or '-'}",
        f"Streamer text: {review_streamer.get('streamer_text') or '-'}",
        f"Review rule context: {review_rule_context.get('context_status') or '-'}",
        f"Rule context text: {review_rule_context.get('context_text') or '-'}",
        f"Review discipline cue: {review_discipline_cue.get('cue_status') or '-'}",
        f"Discipline cue text: {review_discipline_cue.get('cue_text') or '-'}",
        f"Review discipline badge: {review_discipline_badge.get('badge_status') or '-'}",
        f"Discipline badge text: {review_discipline_badge.get('badge_text') or '-'}",
        f"Review discipline token: {review_discipline_token.get('token_status') or '-'}",
        f"Discipline token text: {review_discipline_token.get('token_text') or '-'}",
        f"Review discipline marker: {review_discipline_marker.get('marker_status') or '-'}",
        f"Discipline marker text: {review_discipline_marker.get('marker_text') or '-'}",
        f"Review discipline glyph: {review_discipline_glyph.get('glyph_status') or '-'}",
        f"Discipline glyph text: {review_discipline_glyph.get('glyph_text') or '-'}",
        f"Review discipline sigil: {review_discipline_sigil.get('sigil_status') or '-'}",
        f"Discipline sigil text: {review_discipline_sigil.get('sigil_text') or '-'}",
        f"Review discipline seal: {review_discipline_seal.get('seal_status') or '-'}",
        f"Discipline seal text: {review_discipline_seal.get('seal_text') or '-'}",
        f"Review discipline crest: {review_discipline_crest.get('crest_status') or '-'}",
        f"Discipline crest text: {review_discipline_crest.get('crest_text') or '-'}",
        f"Review discipline emblem: {review_discipline_emblem.get('emblem_status') or '-'}",
        f"Discipline emblem text: {review_discipline_emblem.get('emblem_text') or '-'}",
        f"Review discipline reason: {review_discipline_reason.get('reason_status') or '-'}",
        f"Discipline reason text: {review_discipline_reason.get('reason_text') or '-'}",
        f"Review dataset link: {review_dataset_quality_link.get('link_status') or '-'}",
        f"Review dataset link text: {review_dataset_quality_link.get('link_text') or '-'}",
        f"Latest trade digest: {latest_digest_status}",
        f"Digest headline: {latest_digest_headline}",
        f"Digest primary gap: {latest_digest_primary_gap}",
        f"Digest next step: {latest_digest_next_step}",
        f"Latest BW evidence: {latest_evidence_status}",
        f"Latest BW evidence text: {latest_evidence_text}",
        f"Latest BW evidence follow-up: {latest_follow_up_status}",
        f"Latest BW evidence next step: {latest_follow_up_text}",
        f"Dataset quality context: {dataset_quality.get('context_status') or '-'}",
        f"Dataset quality text: {dataset_quality.get('context_text') or '-'}",
        f"Latest review status: {summary['latest_review_status'] or '-'}",
        f"Latest intent delta: {latest_intent_delta.get('delta_status') or '-'}",
        f"Latest completeness: {latest_review_completeness.get('completeness_status') or '-'}",
        f"Latest next review field: {next_review_field}",
        f"Latest missing review parts: {missing_parts}",
        f"Latest method facets filled: {completed_facets}/5",
    ]


def build_finalization_lines(journal_view: dict[str, Any], trading_view: dict[str, Any] | None = None) -> list[str]:
    finalization = journal_view["session_finalization"]
    transition_state = build_transition_state_view(journal_view, trading_view)
    pending_ids = ", ".join(finalization["pending_review_trade_ids"]) or "none"
    return [
        f"Finalized: {'yes' if finalization['is_session_finalized'] else 'no'}",
        f"Reason: {finalization['finalization_reason'] or '-'}",
        f"Replay running: {'yes' if finalization['replay_running'] else 'no'}",
        f"Trade lifecycle in progress: {transition_state['lifecycle_label']}",
        f"Lifecycle text: {transition_state['lifecycle_text']}",
        f"Pending review ids: {pending_ids}",
        f"Can finalize: {'yes' if finalization['can_finalize_without_force'] else 'no'}",
        f"Can force finalize: {'yes' if finalization['can_finalize_with_force'] else 'no'}",
        f"Finalization dataset link: {transition_state['finalization_link_status']}",
        f"Finalization dataset text: {transition_state['finalization_link_text']}",
        f"Recovery follow-up: {transition_state['recovery_acknowledgment_text'] if transition_state['recovery_acknowledgment_text'] != 'none' else '-'}",
    ]


def build_latest_result_lines(journal_view: dict[str, Any], trading_view: dict[str, Any] | None = None) -> list[str]:
    latest_trade_result = journal_view["derived_review_output"]["latest_trade_result"]
    if latest_trade_result is None:
        if trading_view and trading_view.get("trade_partially_closed"):
            last_execution = trading_view.get("last_execution_outcome") or {}
            return [
                "Latest result: active trade is partially closed",
                f"Remaining open volume: {trading_view.get('current_open_volume', 0.0)}",
                f"Realized PnL so far: {trading_view.get('realised_pnl', 0.0)}",
                f"Last execution: {last_execution.get('execution_type') or '-'}",
            ]
        return ["Latest result: no closed trades yet"]
    facets = latest_trade_result["method_facets"]
    delta = latest_trade_result["intent_delta"]
    completeness = latest_trade_result["review_completeness"]
    review_sequence = latest_trade_result["review_sequence"]
    review_rule_context = latest_trade_result.get("review_rule_context", {})
    review_discipline_cue = latest_trade_result.get("review_discipline_cue", {})
    review_discipline_badge = latest_trade_result.get("review_discipline_badge", {})
    review_discipline_token = latest_trade_result.get("review_discipline_token", {})
    review_discipline_marker = latest_trade_result.get("review_discipline_marker", {})
    review_discipline_glyph = latest_trade_result.get("review_discipline_glyph", {})
    review_discipline_sigil = latest_trade_result.get("review_discipline_sigil", {})
    review_discipline_seal = latest_trade_result.get("review_discipline_seal", {})
    review_discipline_crest = latest_trade_result.get("review_discipline_crest", {})
    review_discipline_emblem = latest_trade_result.get("review_discipline_emblem", {})
    review_discipline_reason = latest_trade_result.get("review_discipline_reason", {})
    review_dataset_quality_link = latest_trade_result.get("review_dataset_quality_link", {})
    review_evidence_status = latest_trade_result.get("bill_williams_review_evidence_status") or "-"
    review_evidence_text = latest_trade_result.get("bill_williams_review_evidence_text") or "-"
    review_follow_up_status = latest_trade_result.get("bill_williams_review_evidence_follow_up_status") or "-"
    review_follow_up_text = latest_trade_result.get("bill_williams_review_evidence_follow_up_text") or "-"
    digest_status = latest_trade_result.get("current_trade_review_digest_status") or "not_applicable"
    digest_headline = latest_trade_result.get("current_trade_review_digest_headline") or "-"
    digest_primary_gap = latest_trade_result.get("current_trade_review_digest_primary_gap") or "-"
    digest_next_step = latest_trade_result.get("current_trade_review_digest_next_step") or "-"
    plan_context = latest_trade_result.get("current_trade_plan_context") or {}
    dataset_quality = journal_view.get("dataset_quality_context") or {}
    missing_parts = ", ".join(completeness["missing_parts"]) or "none"
    recommended_order = " -> ".join(review_sequence["recommended_missing_order"]) or "none"
    return [
        f"Latest trade: {latest_trade_result['trade_id']}",
        f"Outcome: {latest_trade_result['outcome_label']}",
        f"PnL: {latest_trade_result['realised_pnl']}",
        f"Holding seconds: {latest_trade_result['holding_time_seconds']}",
        f"Close reason: {latest_trade_result['close_reason'] or '-'}",
        f"Protection present: {'yes' if latest_trade_result.get('has_initial_trade_protection') else 'no'}",
        f"Stop loss / take profit: {latest_trade_result.get('stop_loss') if latest_trade_result.get('stop_loss') is not None else '-'} / {latest_trade_result.get('take_profit') if latest_trade_result.get('take_profit') is not None else '-'}",
        f"Declared plan: {'present' if plan_context.get('plan_present') else 'absent'}",
        f"Declared setup: {plan_context.get('declared_setup_tag') or '-'}",
        f"Thesis summary: {plan_context.get('thesis_summary') or '-'}",
        f"Risk plan: {plan_context.get('risk_plan') or '-'}",
        f"Setup: {latest_trade_result['setup_tag'] or '-'}",
        f"Compliance: {latest_trade_result['compliance_label'] or '-'}",
        f"Intent delta: {delta['delta_status']}",
        f"Declared/reviewed: {delta['declared_setup_tag'] or '-'} / {delta['reviewed_setup_tag'] or '-'}",
        f"Review completeness: {completeness['completeness_status']} ({completeness['filled_part_count']}/{completeness['total_part_count']})",
        f"Next review field: {review_sequence['next_field'] or '-'}",
        f"Recommended order: {recommended_order}",
        f"Missing review parts: {missing_parts}",
        f"Variant: {facets['setup_variant'] or '-'}",
        f"Entry/context: {facets['entry_timing_label'] or '-'} / {facets['market_context_label'] or '-'}",
        f"Exit/clarity: {facets['exit_quality_label'] or '-'} / {facets['review_clarity_label'] or '-'}",
        f"Rule context: {review_rule_context.get('context_status') or '-'}",
        f"Rule context text: {review_rule_context.get('context_text') or '-'}",
        f"Review discipline cue: {review_discipline_cue.get('cue_status') or '-'}",
        f"Discipline cue text: {review_discipline_cue.get('cue_text') or '-'}",
        f"Review discipline badge: {review_discipline_badge.get('badge_status') or '-'}",
        f"Discipline badge text: {review_discipline_badge.get('badge_text') or '-'}",
        f"Review discipline token: {review_discipline_token.get('token_status') or '-'}",
        f"Discipline token text: {review_discipline_token.get('token_text') or '-'}",
        f"Review discipline marker: {review_discipline_marker.get('marker_status') or '-'}",
        f"Discipline marker text: {review_discipline_marker.get('marker_text') or '-'}",
        f"Review discipline glyph: {review_discipline_glyph.get('glyph_status') or '-'}",
        f"Discipline glyph text: {review_discipline_glyph.get('glyph_text') or '-'}",
        f"Review discipline sigil: {review_discipline_sigil.get('sigil_status') or '-'}",
        f"Discipline sigil text: {review_discipline_sigil.get('sigil_text') or '-'}",
        f"Review discipline seal: {review_discipline_seal.get('seal_status') or '-'}",
        f"Discipline seal text: {review_discipline_seal.get('seal_text') or '-'}",
        f"Review discipline crest: {review_discipline_crest.get('crest_status') or '-'}",
        f"Discipline crest text: {review_discipline_crest.get('crest_text') or '-'}",
        f"Review discipline emblem: {review_discipline_emblem.get('emblem_status') or '-'}",
        f"Discipline emblem text: {review_discipline_emblem.get('emblem_text') or '-'}",
        f"Review discipline reason: {review_discipline_reason.get('reason_status') or '-'}",
        f"Discipline reason text: {review_discipline_reason.get('reason_text') or '-'}",
        f"Review dataset link: {review_dataset_quality_link.get('link_status') or '-'}",
        f"Review dataset link text: {review_dataset_quality_link.get('link_text') or '-'}",
        f"Review digest: {digest_status}",
        f"Digest headline: {digest_headline}",
        f"Digest primary gap: {digest_primary_gap}",
        f"Digest next step: {digest_next_step}",
        f"Review evidence: {review_evidence_status}",
        f"Review evidence text: {review_evidence_text}",
        f"Review evidence follow-up: {review_follow_up_status}",
        f"Review evidence next step: {review_follow_up_text}",
        f"Dataset quality context: {dataset_quality.get('context_status') or '-'}",
        f"Dataset quality text: {dataset_quality.get('context_text') or '-'}",
        f"Review status: {latest_trade_result['review_status']}",
    ]



def _build_plan_context_lines(plan_context: dict[str, Any] | None) -> list[str]:
    if plan_context is None or not plan_context:
        return []
    return [
        f"Declared plan: {'present' if plan_context.get('plan_present') else 'absent'}",
        f"Declared setup: {plan_context.get('declared_setup_tag') or '-'}",
        f"Thesis summary: {plan_context.get('thesis_summary') or '-'}",
        f"Risk plan: {plan_context.get('risk_plan') or '-'}",
    ]




