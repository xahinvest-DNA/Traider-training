from __future__ import annotations

from typing import Any


def build_latest_trade_result_lines(journal_view: dict[str, Any]) -> list[str]:
    latest = journal_view["derived_review_output"]["latest_trade_result"]
    if latest is None:
        return ["Latest trade result: none", "No closed trades yet in current local session"]
    facets = latest["method_facets"]
    delta = latest["intent_delta"]
    completeness = latest["review_completeness"]
    review_sequence = latest["review_sequence"]
    rule_context = latest.get("review_rule_context", {})
    discipline_cue = latest.get("review_discipline_cue", {})
    discipline_badge = latest.get("review_discipline_badge", {})
    discipline_token = latest.get("review_discipline_token", {})
    discipline_marker = latest.get("review_discipline_marker", {})
    discipline_glyph = latest.get("review_discipline_glyph", {})
    discipline_sigil = latest.get("review_discipline_sigil", {})
    discipline_seal = latest.get("review_discipline_seal", {})
    discipline_crest = latest.get("review_discipline_crest", {})
    discipline_emblem = latest.get("review_discipline_emblem", {})
    discipline_reason = latest.get("review_discipline_reason", {})
    dataset_quality_link = latest.get("review_dataset_quality_link", {})
    review_evidence_status = latest.get("bill_williams_review_evidence_status") or "-"
    review_evidence_text = latest.get("bill_williams_review_evidence_text") or "-"
    review_follow_up_status = latest.get("bill_williams_review_evidence_follow_up_status") or "-"
    review_follow_up_text = latest.get("bill_williams_review_evidence_follow_up_text") or "-"
    digest_status = latest.get("current_trade_review_digest_status") or "-"
    digest_headline = latest.get("current_trade_review_digest_headline") or "-"
    digest_primary_gap = latest.get("current_trade_review_digest_primary_gap") or "-"
    digest_next_step = latest.get("current_trade_review_digest_next_step") or "-"
    missing_parts = ", ".join(completeness["missing_parts"]) or "none"
    recommended_order = " -> ".join(review_sequence["recommended_missing_order"]) or "none"
    return [
        f"Latest trade: {latest['trade_id']}",
        f"Outcome / review: {latest['outcome_label']} / {latest['review_status']}",
        f"PnL / cost: {latest['realised_pnl']:.5f} / {latest['total_trade_cost']:.5f}",
        f"Holding sec: {latest['holding_time_seconds']}",
        f"Review digest: {digest_status}",
        f"Digest headline: {digest_headline}",
        f"Digest primary gap: {digest_primary_gap}",
        f"Digest next step: {digest_next_step}",
        f"Setup / compliance: {latest['setup_tag'] or '-'} / {latest['compliance_label'] or '-'}",
        f"Intent delta: {delta['delta_status']}",
        f"Declared / reviewed: {delta['declared_setup_tag'] or '-'} / {delta['reviewed_setup_tag'] or '-'}",
        f"Review completeness: {completeness['completeness_status']} ({completeness['filled_part_count']}/{completeness['total_part_count']})",
        f"Next review field: {review_sequence['next_field'] or '-'}",
        f"Recommended order: {recommended_order}",
        f"Missing parts: {missing_parts}",
        f"Variant: {facets['setup_variant'] or '-'}",
        f"Entry/context: {facets['entry_timing_label'] or '-'} / {facets['market_context_label'] or '-'}",
        f"Exit/clarity: {facets['exit_quality_label'] or '-'} / {facets['review_clarity_label'] or '-'}",
        f"Notes / reviews: {latest['pre_trade_note_count']} / {latest['post_trade_review_count']}",
        f"Flags / violations: {latest['behavioral_flag_count']} / {latest['rule_violation_count']}",
        f"Rule context: {rule_context.get('context_status') or '-'}",
        f"Rule context text: {rule_context.get('context_text') or '-'}",
        f"Review discipline cue: {discipline_cue.get('cue_status') or '-'}",
        f"Discipline cue text: {discipline_cue.get('cue_text') or '-'}",
        f"Review discipline badge: {discipline_badge.get('badge_status') or '-'}",
        f"Discipline badge text: {discipline_badge.get('badge_text') or '-'}",
        f"Review discipline token: {discipline_token.get('token_status') or '-'}",
        f"Discipline token text: {discipline_token.get('token_text') or '-'}",
        f"Review discipline marker: {discipline_marker.get('marker_status') or '-'}",
        f"Discipline marker text: {discipline_marker.get('marker_text') or '-'}",
        f"Review discipline glyph: {discipline_glyph.get('glyph_status') or '-'}",
        f"Discipline glyph text: {discipline_glyph.get('glyph_text') or '-'}",
        f"Review discipline sigil: {discipline_sigil.get('sigil_status') or '-'}",
        f"Discipline sigil text: {discipline_sigil.get('sigil_text') or '-'}",
        f"Review discipline seal: {discipline_seal.get('seal_status') or '-'}",
        f"Discipline seal text: {discipline_seal.get('seal_text') or '-'}",
        f"Review discipline crest: {discipline_crest.get('crest_status') or '-'}",
        f"Discipline crest text: {discipline_crest.get('crest_text') or '-'}",
        f"Review discipline emblem: {discipline_emblem.get('emblem_status') or '-'}",
        f"Discipline emblem text: {discipline_emblem.get('emblem_text') or '-'}",
        f"Review discipline reason: {discipline_reason.get('reason_status') or '-'}",
        f"Discipline reason text: {discipline_reason.get('reason_text') or '-'}",
        f"Review dataset link: {dataset_quality_link.get('link_status') or '-'}",
        f"Review dataset link text: {dataset_quality_link.get('link_text') or '-'}",
        f"Review evidence: {review_evidence_status}",
        f"Review evidence text: {review_evidence_text}",
        f"Review evidence follow-up: {review_follow_up_status}",
        f"Review evidence next step: {review_follow_up_text}",
    ]


def build_timeline_preview_lines(journal_view: dict[str, Any], limit: int = 8) -> list[str]:
    timeline = journal_view["session_timeline"]
    lines = [f"Timeline items: {timeline['timeline_item_count']}"]
    for item in timeline["timeline_items"][-limit:]:
        trade_id = item.get("trade_id") or "-"
        lines.append(f"{item['timestamp']}  {item['title']}  trade={trade_id}")
    return lines


def build_history_status_lines(journal_view: dict[str, Any]) -> list[str]:
    derived = journal_view["derived_review_output"]
    timeline = journal_view["session_timeline"]
    latest = timeline["latest_timeline_item"]
    coverage = derived.get("review_field_coverage") or {}
    weak_spots = derived.get("review_weak_spots") or {}
    summary = journal_view["session_review_summary"]
    progress = summary.get("review_progress") or {}
    momentum = summary.get("review_momentum") or {}
    stability = summary.get("review_stability") or {}
    swings = summary.get("review_swings") or {}
    floor = summary.get("review_floor") or {}
    ceiling = summary.get("review_ceiling") or {}
    band = summary.get("review_band") or {}
    headroom = summary.get("review_headroom") or {}
    pressure = summary.get("review_pressure") or {}
    target = summary.get("review_target") or {}
    focus = summary.get("review_focus") or {}
    cue = summary.get("review_cue") or {}
    badge = summary.get("review_badge") or {}
    pill = summary.get("review_pill") or {}
    chip = summary.get("review_chip") or {}
    tag = summary.get("review_tag") or {}
    token = summary.get("review_token") or {}
    marker = summary.get("review_marker") or {}
    glyph = summary.get("review_glyph") or {}
    sigil = summary.get("review_sigil") or {}
    seal = summary.get("review_seal") or {}
    crest = summary.get("review_crest") or {}
    emblem = summary.get("review_emblem") or {}
    insignia = summary.get("review_insignia") or {}
    standard = summary.get("review_standard") or {}
    banner = summary.get("review_banner") or {}
    pennant = summary.get("review_pennant") or {}
    streamer = summary.get("review_streamer") or {}
    rule_context = summary.get("review_rule_context") or {}
    discipline_cue = summary.get("review_discipline_cue") or {}
    discipline_badge = summary.get("review_discipline_badge") or {}
    discipline_token = summary.get("review_discipline_token") or {}
    discipline_marker = summary.get("review_discipline_marker") or {}
    discipline_glyph = summary.get("review_discipline_glyph") or {}
    discipline_sigil = summary.get("review_discipline_sigil") or {}
    discipline_seal = summary.get("review_discipline_seal") or {}
    discipline_crest = summary.get("review_discipline_crest") or {}
    discipline_emblem = summary.get("review_discipline_emblem") or {}
    discipline_reason = summary.get("review_discipline_reason") or {}
    dataset_quality_link = summary.get("review_dataset_quality_link") or {}
    latest_evidence_status = summary.get("latest_bill_williams_review_evidence_status") or "-"
    latest_evidence_text = summary.get("latest_bill_williams_review_evidence_text") or "-"
    latest_follow_up_status = summary.get("latest_bill_williams_review_evidence_follow_up_status") or "-"
    latest_follow_up_text = summary.get("latest_bill_williams_review_evidence_follow_up_text") or "-"
    latest_trade_result = derived.get("latest_trade_result") or {}
    latest_review_sequence = latest_trade_result.get("review_sequence", {})
    weak_spot_fields = ", ".join(weak_spots.get("top_weak_spot_fields", [])) or "none"
    improved_fields = ", ".join(progress.get("improved_fields", [])) or "none"
    still_missing_fields = ", ".join(progress.get("still_missing_fields", [])) or "none"
    score_sequence = ", ".join(str(value) for value in momentum.get("score_sequence", [])) or "none"
    return [
        f"Closed trades: {derived['closed_trade_count']}",
        f"Reviewed / pending: {derived['reviewed_trade_count']} / {derived['pending_review_trade_count']}",
        f"Method-facet trades: {derived['trades_with_method_facets_count']}",
        f"Reviewed trades with BW evidence: {derived.get('reviewed_trades_with_bw_evidence_count', 0)}",
        f"Reviewed trades missing BW evidence: {derived.get('reviewed_trades_missing_bw_evidence_count', 0)}",
        f"Reviewed trades needing BW evidence follow-up: {derived.get('reviewed_trades_requiring_bw_evidence_follow_up_count', 0)}",
        f"Intent confirmed/refined/changed: {derived['intent_confirmed_count']} / {derived['intent_refined_count']} / {derived['intent_changed_count']}",
        f"Intent missing / review missing: {derived['intent_missing_count']} / {derived['review_missing_count']}",
        f"Review complete/partial/sparse: {derived['review_complete_count']} / {derived['review_partial_count']} / {derived['review_sparse_count']}",
        f"Latest next review field: {latest_review_sequence.get('next_field') or '-'}",
        f"Review weak spots: {weak_spot_fields}",
        f"Review progress: {progress.get('progress_status') or '-'}",
        f"Weak spots improved/still missing: {improved_fields} / {still_missing_fields}",
        f"Review momentum: {momentum.get('momentum_status') or '-'}",
        f"Momentum score sequence: {score_sequence}",
        f"Review stability: {stability.get('stability_status') or '-'}",
        f"Stability spread: {stability.get('score_spread') if stability.get('score_spread') is not None else '-'}",
        f"Review swings: {swings.get('swing_status') or '-'}",
        f"Max adjacent jump: {swings.get('max_adjacent_jump') if swings.get('max_adjacent_jump') is not None else '-'}",
        f"Review floor: {floor.get('floor_status') or '-'}",
        f"Min recent score: {floor.get('min_recent_score') if floor.get('min_recent_score') is not None else '-'}",
        f"Review ceiling: {ceiling.get('ceiling_status') or '-'}",
        f"Max recent score: {ceiling.get('max_recent_score') if ceiling.get('max_recent_score') is not None else '-'}",
        f"Review band: {band.get('band_status') or '-'}",
        f"Recent quality corridor: {band.get('corridor_label') or '-'}",
        f"Band width: {band.get('band_width') if band.get('band_width') is not None else '-'}",
        f"Review headroom: {headroom.get('headroom_status') or '-'}",
        f"Remaining headroom: {headroom.get('remaining_headroom') if headroom.get('remaining_headroom') is not None else '-'}",
        f"Review pressure: {pressure.get('pressure_status') or '-'}",
        f"Pressure target: {pressure.get('pressure_target') or '-'}",
        f"Review target: {target.get('target_status') or '-'}",
        f"Target field: {target.get('target_field') or '-'}",
        f"Review focus: {focus.get('focus_status') or '-'}",
        f"Focus label: {focus.get('focus_label') or '-'}",
        f"Review cue: {cue.get('cue_status') or '-'}",
        f"Cue text: {cue.get('cue_text') or '-'}",
        f"Review badge: {badge.get('badge_status') or '-'}",
        f"Badge text: {badge.get('badge_text') or '-'}",
        f"Review pill: {pill.get('pill_status') or '-'}",
        f"Pill text: {pill.get('pill_text') or '-'}",
        f"Review chip: {chip.get('chip_status') or '-'}",
        f"Chip text: {chip.get('chip_text') or '-'}",
        f"Review tag: {tag.get('tag_status') or '-'}",
        f"Tag text: {tag.get('tag_text') or '-'}",
        f"Review token: {token.get('token_status') or '-'}",
        f"Token text: {token.get('token_text') or '-'}",
        f"Review marker: {marker.get('marker_status') or '-'}",
        f"Marker text: {marker.get('marker_text') or '-'}",
        f"Review glyph: {glyph.get('glyph_status') or '-'}",
        f"Glyph text: {glyph.get('glyph_text') or '-'}",
        f"Review sigil: {sigil.get('sigil_status') or '-'}",
        f"Sigil text: {sigil.get('sigil_text') or '-'}",
        f"Review seal: {seal.get('seal_status') or '-'}",
        f"Seal text: {seal.get('seal_text') or '-'}",
        f"Review crest: {crest.get('crest_status') or '-'}",
        f"Crest text: {crest.get('crest_text') or '-'}",
        f"Review emblem: {emblem.get('emblem_status') or '-'}",
        f"Emblem text: {emblem.get('emblem_text') or '-'}",
        f"Review insignia: {insignia.get('insignia_status') or '-'}",
        f"Insignia text: {insignia.get('insignia_text') or '-'}",
        f"Review standard: {standard.get('standard_status') or '-'}",
        f"Standard text: {standard.get('standard_text') or '-'}",
        f"Review banner: {banner.get('banner_status') or '-'}",
        f"Banner text: {banner.get('banner_text') or '-'}",
        f"Review pennant: {pennant.get('pennant_status') or '-'}",
        f"Pennant text: {pennant.get('pennant_text') or '-'}",
        f"Review streamer: {streamer.get('streamer_status') or '-'}",
        f"Streamer text: {streamer.get('streamer_text') or '-'}",
        f"Review rule context: {rule_context.get('context_status') or '-'}",
        f"Rule context text: {rule_context.get('context_text') or '-'}",
        f"Review discipline cue: {discipline_cue.get('cue_status') or '-'}",
        f"Discipline cue text: {discipline_cue.get('cue_text') or '-'}",
        f"Review discipline badge: {discipline_badge.get('badge_status') or '-'}",
        f"Discipline badge text: {discipline_badge.get('badge_text') or '-'}",
        f"Review discipline token: {discipline_token.get('token_status') or '-'}",
        f"Discipline token text: {discipline_token.get('token_text') or '-'}",
        f"Review discipline marker: {discipline_marker.get('marker_status') or '-'}",
        f"Discipline marker text: {discipline_marker.get('marker_text') or '-'}",
        f"Review discipline glyph: {discipline_glyph.get('glyph_status') or '-'}",
        f"Discipline glyph text: {discipline_glyph.get('glyph_text') or '-'}",
        f"Review discipline sigil: {discipline_sigil.get('sigil_status') or '-'}",
        f"Discipline sigil text: {discipline_sigil.get('sigil_text') or '-'}",
        f"Review discipline seal: {discipline_seal.get('seal_status') or '-'}",
        f"Discipline seal text: {discipline_seal.get('seal_text') or '-'}",
        f"Review discipline crest: {discipline_crest.get('crest_status') or '-'}",
        f"Discipline crest text: {discipline_crest.get('crest_text') or '-'}",
        f"Review discipline emblem: {discipline_emblem.get('emblem_status') or '-'}",
        f"Discipline emblem text: {discipline_emblem.get('emblem_text') or '-'}",
        f"Review discipline reason: {discipline_reason.get('reason_status') or '-'}",
        f"Discipline reason text: {discipline_reason.get('reason_text') or '-'}",
        f"Review dataset link: {dataset_quality_link.get('link_status') or '-'}",
        f"Review dataset link text: {dataset_quality_link.get('link_text') or '-'}",
        f"Latest BW evidence: {latest_evidence_status}",
        f"Latest BW evidence text: {latest_evidence_text}",
        f"Latest BW evidence follow-up: {latest_follow_up_status}",
        f"Latest BW evidence next step: {latest_follow_up_text}",
        f"Coverage setup/compliance: {coverage.get('setup_tag_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)} / {coverage.get('compliance_label_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)}",
        f"Coverage entry/context: {coverage.get('entry_timing_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)} / {coverage.get('market_context_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)}",
        f"Coverage exit/clarity: {coverage.get('exit_quality_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)} / {coverage.get('review_clarity_coverage_count', 0)}/{coverage.get('total_reviewed_trades', 0)}",
        f"Timeline items: {timeline['timeline_item_count']}",
        f"Latest timeline event: {latest['title'] if latest else '-'}",
    ]

