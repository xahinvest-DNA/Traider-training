from __future__ import annotations

import json
import tkinter as tk
from tkinter import messagebox, ttk

from .authoring_surface import (
    build_authoring_status_lines,
    build_note_section_lines,
    build_review_section_lines,
    get_behavioral_flag_options,
    get_compliance_label_options,
    get_entry_timing_options,
    get_exit_quality_options,
    get_market_context_options,
    get_review_clarity_options,
    get_rule_violation_options,
    get_setup_tag_options,
    get_setup_variant_options,
)
from .chart_surface import (
    build_mid_price_line_points,
    build_replay_header_lines,
    build_tick_table_lines,
    flatten_canvas_points,
)
from .context_surface import (
    build_finalization_lines,
    build_latest_result_lines,
    build_review_summary_lines,
    build_session_context_lines,
    build_trade_context_lines,
)
from .control_surface import build_button_state_map, build_control_hint_lines
from .history_surface import (
    build_history_status_lines,
    build_latest_trade_result_lines,
    build_timeline_preview_lines,
)
from .workflow_surface import (
    build_action_feedback_lines,
    build_finalization_blocker_lines,
    build_workflow_guidance_lines,
)
from .controller import DesktopShellController


class TraderTrainerDesktopApp:
    def __init__(self, controller: DesktopShellController) -> None:
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Trader Trainer Desktop Shell")
        self.root.geometry("1480x980")

        self.note_setup_tag = tk.StringVar(value="BW_FRACTAL_LONG")
        self.note_thesis = tk.StringVar()
        self.note_risk_plan = tk.StringVar()
        self.note_snapshot_ref = tk.StringVar()
        self.review_setup_tag = tk.StringVar(value="BW_FRACTAL_LONG")
        self.review_compliance_label = tk.StringVar(value="valid_setup")
        self.review_setup_variant = tk.StringVar(value="fractal_breakout")
        self.review_entry_timing_label = tk.StringVar(value="timely_entry")
        self.review_market_context_label = tk.StringVar(value="clean_context")
        self.review_exit_quality_label = tk.StringVar(value="disciplined_exit")
        self.review_clarity_label = tk.StringVar(value="high_clarity")
        self.review_snapshot_ref = tk.StringVar()
        self.flag_code = tk.StringVar(value="premature_exit")
        self.violation_code = tk.StringVar(value="manual_plan_deviation")
        self.speed_value = tk.StringVar(value="1.0")
        self.pending_stop_trigger_value = tk.StringVar()
        self.initial_stop_loss_value = tk.StringVar()
        self.initial_take_profit_value = tk.StringVar()
        self.pending_note_snapshot_id: str | None = None
        self.pending_review_snapshot_ids: list[str] = []
        self.last_action_feedback: dict[str, str] | None = {
            "level": "info",
            "summary": "Desktop shell ready",
            "detail": "Local runtime bootstrapped successfully.",
        }
        self.control_buttons: dict[str, ttk.Button] = {}

        self._build_layout()
        self.refresh()

    def run(self) -> None:
        self.root.mainloop()

    def refresh(self) -> None:
        workspace = self.controller.get_workspace_view()
        replay_view = workspace["replay"]
        trading_view = workspace["trading"]
        journal_view = workspace["journal"]
        self._render_json(self.replay_text, replay_view)
        self._render_json(self.trading_text, trading_view)
        self._render_json(self.journal_text, journal_view)
        self._render_chart_surface(replay_view)
        self._render_control_surface(replay_view, trading_view, journal_view)
        self._render_context_surface(trading_view, journal_view)
        self._render_authoring_surface(journal_view)
        self._render_history_surface(journal_view)
        self._render_workflow_surface(replay_view, trading_view, journal_view)

    def _build_layout(self) -> None:
        root = self.root
        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        controls = ttk.Frame(root, padding=8)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew")

        button_specs = [
            ("play", "Play", self._action_play),
            ("pause", "Pause", self._action_pause),
            ("advance", "Advance", self._action_advance),
            ("buy", "Buy", self._action_buy),
            ("sell", "Sell", self._action_sell),
            ("buy_stop", "BuyStop", self._action_buy_stop),
            ("sell_stop", "SellStop", self._action_sell_stop),
            ("cancel_entry", "Cancel Entry", self._action_cancel_entry),
            ("close", "Close", self._action_close),
            ("finalize", "Finalize", self._action_finalize),
            ("force_finalize", "Force Finalize", self._action_force_finalize),
            ("acknowledge_recovery", "Review Warning", self._action_acknowledge_recovery),
        ]
        for index, (key, label, handler) in enumerate(button_specs):
            button = ttk.Button(controls, text=label, command=handler)
            button.grid(row=0, column=index, padx=4, pady=4)
            self.control_buttons[key] = button

        ttk.Label(controls, text="Speed").grid(row=0, column=len(button_specs), padx=(16, 4))
        ttk.Entry(controls, textvariable=self.speed_value, width=8).grid(row=0, column=len(button_specs) + 1, padx=4)
        speed_button = ttk.Button(controls, text="Set Speed", command=self._action_set_speed)
        speed_button.grid(row=0, column=len(button_specs) + 2, padx=4)
        self.control_buttons["set_speed"] = speed_button
        ttk.Label(controls, text="Stop trigger").grid(row=0, column=len(button_specs) + 3, padx=(16, 4))
        ttk.Entry(controls, textvariable=self.pending_stop_trigger_value, width=12).grid(row=0, column=len(button_specs) + 4, padx=4)
        ttk.Label(controls, text="Initial SL").grid(row=0, column=len(button_specs) + 5, padx=(12, 4))
        ttk.Entry(controls, textvariable=self.initial_stop_loss_value, width=12).grid(row=0, column=len(button_specs) + 6, padx=4)
        ttk.Label(controls, text="Initial TP").grid(row=0, column=len(button_specs) + 7, padx=(12, 4))
        ttk.Entry(controls, textvariable=self.initial_take_profit_value, width=12).grid(row=0, column=len(button_specs) + 8, padx=4)

        self.control_hint_label = ttk.Label(controls, justify="left", anchor="w")
        self.control_hint_label.grid(row=1, column=0, columnspan=len(button_specs) + 9, sticky="ew", pady=(6, 0))

        left_top = ttk.LabelFrame(root, text="Chart / Replay Surface", padding=8)
        left_top.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        left_top.columnconfigure(0, weight=1)
        left_top.rowconfigure(1, weight=1)
        self.chart_header = ttk.Label(left_top, justify="left", anchor="w")
        self.chart_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.chart_canvas = tk.Canvas(left_top, background="#10151c", highlightthickness=0)
        self.chart_canvas.grid(row=1, column=0, sticky="nsew")
        self.chart_canvas.bind("<Configure>", lambda _event: self.refresh())
        self.chart_footer = ttk.Label(left_top, justify="left", anchor="w")
        self.chart_footer.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        left_bottom = ttk.LabelFrame(root, text="Session / Trade Context Surface", padding=8)
        left_bottom.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        left_bottom.columnconfigure(0, weight=1)
        left_bottom.columnconfigure(1, weight=1)
        for row in range(3):
            left_bottom.rowconfigure(row, weight=1)

        self.session_context_label = ttk.Label(left_bottom, justify="left", anchor="nw")
        self.session_context_label.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 6))
        self.trade_context_label = ttk.Label(left_bottom, justify="left", anchor="nw")
        self.trade_context_label.grid(row=0, column=1, sticky="nsew", pady=(0, 6))
        self.review_summary_label = ttk.Label(left_bottom, justify="left", anchor="nw")
        self.review_summary_label.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 6))
        self.finalization_label = ttk.Label(left_bottom, justify="left", anchor="nw")
        self.finalization_label.grid(row=1, column=1, sticky="nsew", pady=(0, 6))
        self.latest_result_label = ttk.Label(left_bottom, justify="left", anchor="nw")
        self.latest_result_label.grid(row=2, column=0, columnspan=2, sticky="nsew")

        right_top = ttk.LabelFrame(root, text="Workflow / Review Surface", padding=8)
        right_top.grid(row=1, column=1, sticky="nsew", padx=(0, 8), pady=8)
        for column in range(2):
            right_top.columnconfigure(column, weight=1)
        right_top.rowconfigure(3, weight=1)

        self.workflow_guidance_label = ttk.Label(right_top, justify="left", anchor="w")
        self.workflow_guidance_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self.blocker_status_label = ttk.Label(right_top, justify="left", anchor="w")
        self.blocker_status_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self.action_feedback_label = ttk.Label(right_top, justify="left", anchor="w")
        self.action_feedback_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self._build_note_review_form(right_top)

        right_bottom = ttk.Notebook(root)
        right_bottom.grid(row=2, column=1, sticky="nsew", padx=(0, 8), pady=(0, 8))

        history_frame = ttk.Frame(right_bottom, padding=8)
        history_frame.columnconfigure(0, weight=1)
        for row in range(3):
            history_frame.rowconfigure(row, weight=1)
        self.history_status_label = ttk.Label(history_frame, justify="left", anchor="nw")
        self.history_status_label.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        self.latest_trade_result_label = ttk.Label(history_frame, justify="left", anchor="nw")
        self.latest_trade_result_label.grid(row=1, column=0, sticky="nsew", pady=(0, 6))
        self.timeline_preview_label = ttk.Label(history_frame, justify="left", anchor="nw")
        self.timeline_preview_label.grid(row=2, column=0, sticky="nsew")
        right_bottom.add(history_frame, text="History / Timeline")

        journal_frame = ttk.Frame(right_bottom, padding=8)
        journal_frame.columnconfigure(0, weight=1)
        journal_frame.rowconfigure(0, weight=1)
        self.journal_text = tk.Text(journal_frame, wrap="none")
        self.journal_text.grid(row=0, column=0, sticky="nsew")
        self.journal_text.configure(state="disabled")
        right_bottom.add(journal_frame, text="Journal / Result")

        replay_frame = ttk.Frame(right_bottom, padding=8)
        replay_frame.columnconfigure(0, weight=1)
        replay_frame.rowconfigure(0, weight=1)
        self.replay_text = tk.Text(replay_frame, wrap="none")
        self.replay_text.grid(row=0, column=0, sticky="nsew")
        self.replay_text.configure(state="disabled")
        right_bottom.add(replay_frame, text="Replay State")

        trading_frame = ttk.Frame(right_bottom, padding=8)
        trading_frame.columnconfigure(0, weight=1)
        trading_frame.rowconfigure(0, weight=1)
        self.trading_text = tk.Text(trading_frame, wrap="none")
        self.trading_text.grid(row=0, column=0, sticky="nsew")
        self.trading_text.configure(state="disabled")
        right_bottom.add(trading_frame, text="Trading State")

    def _build_note_review_form(self, parent: ttk.LabelFrame) -> None:
        self.authoring_status_label = ttk.Label(parent, justify="left", anchor="w")
        self.authoring_status_label.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        note_frame = ttk.LabelFrame(parent, text="PreTradeNote", padding=8)
        note_frame.grid(row=4, column=0, sticky="nsew", padx=(0, 4))
        note_frame.columnconfigure(0, weight=1)
        note_frame.rowconfigure(1, weight=1)

        self.note_status_label = ttk.Label(note_frame, justify="left", anchor="w")
        self.note_status_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.note_text = tk.Text(note_frame, height=7, wrap="word")
        self.note_text.grid(row=1, column=0, sticky="nsew", pady=2)
        ttk.Label(note_frame, text="Setup tag").grid(row=2, column=0, sticky="w")
        self.note_setup_combo = ttk.Combobox(note_frame, textvariable=self.note_setup_tag, values=get_setup_tag_options())
        self.note_setup_combo.grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Label(note_frame, text="Thesis summary").grid(row=4, column=0, sticky="w")
        ttk.Entry(note_frame, textvariable=self.note_thesis).grid(row=5, column=0, sticky="ew", pady=2)
        ttk.Label(note_frame, text="Risk plan").grid(row=6, column=0, sticky="w")
        ttk.Entry(note_frame, textvariable=self.note_risk_plan).grid(row=7, column=0, sticky="ew", pady=2)
        ttk.Label(note_frame, text="Chart snapshot ref").grid(row=8, column=0, sticky="w")
        ttk.Entry(note_frame, textvariable=self.note_snapshot_ref).grid(row=9, column=0, sticky="ew", pady=2)
        buttons_note = ttk.Frame(note_frame)
        buttons_note.grid(row=10, column=0, sticky="ew", pady=(6, 0))
        buttons_note.columnconfigure(0, weight=1)
        buttons_note.columnconfigure(1, weight=1)
        buttons_note.columnconfigure(2, weight=1)
        self.note_add_button = ttk.Button(buttons_note, text="Add Note", command=self._action_add_note)
        self.note_add_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(buttons_note, text="Mark Pre Snapshot", command=self._action_capture_note_snapshot).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(buttons_note, text="Clear", command=self._clear_note_form).grid(row=0, column=2, sticky="ew")

        review_frame = ttk.LabelFrame(parent, text="PostTradeReview", padding=8)
        review_frame.grid(row=4, column=1, sticky="nsew", padx=(4, 0))
        review_frame.columnconfigure(0, weight=1)
        review_frame.rowconfigure(1, weight=1)

        self.review_status_label = ttk.Label(review_frame, justify="left", anchor="w")
        self.review_status_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.review_text = tk.Text(review_frame, height=7, wrap="word")
        self.review_text.grid(row=1, column=0, sticky="nsew", pady=2)
        ttk.Label(review_frame, text="Setup tag").grid(row=2, column=0, sticky="w")
        self.review_setup_combo = ttk.Combobox(review_frame, textvariable=self.review_setup_tag, values=get_setup_tag_options())
        self.review_setup_combo.grid(row=3, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Compliance label").grid(row=4, column=0, sticky="w")
        self.review_compliance_combo = ttk.Combobox(review_frame, textvariable=self.review_compliance_label, values=get_compliance_label_options())
        self.review_compliance_combo.grid(row=5, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Setup variant").grid(row=6, column=0, sticky="w")
        self.review_setup_variant_combo = ttk.Combobox(review_frame, textvariable=self.review_setup_variant, values=get_setup_variant_options())
        self.review_setup_variant_combo.grid(row=7, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Entry timing").grid(row=8, column=0, sticky="w")
        self.review_entry_timing_combo = ttk.Combobox(review_frame, textvariable=self.review_entry_timing_label, values=get_entry_timing_options())
        self.review_entry_timing_combo.grid(row=9, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Market context").grid(row=10, column=0, sticky="w")
        self.review_market_context_combo = ttk.Combobox(review_frame, textvariable=self.review_market_context_label, values=get_market_context_options())
        self.review_market_context_combo.grid(row=11, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Exit quality").grid(row=12, column=0, sticky="w")
        self.review_exit_quality_combo = ttk.Combobox(review_frame, textvariable=self.review_exit_quality_label, values=get_exit_quality_options())
        self.review_exit_quality_combo.grid(row=13, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Review clarity").grid(row=14, column=0, sticky="w")
        self.review_clarity_combo = ttk.Combobox(review_frame, textvariable=self.review_clarity_label, values=get_review_clarity_options())
        self.review_clarity_combo.grid(row=15, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Chart snapshot ref").grid(row=16, column=0, sticky="w")
        ttk.Entry(review_frame, textvariable=self.review_snapshot_ref).grid(row=17, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Behavioral flag").grid(row=18, column=0, sticky="w")
        self.flag_combo = ttk.Combobox(review_frame, textvariable=self.flag_code, values=get_behavioral_flag_options())
        self.flag_combo.grid(row=19, column=0, sticky="ew", pady=2)
        ttk.Label(review_frame, text="Rule violation").grid(row=20, column=0, sticky="w")
        self.violation_combo = ttk.Combobox(review_frame, textvariable=self.violation_code, values=get_rule_violation_options())
        self.violation_combo.grid(row=21, column=0, sticky="ew", pady=2)
        buttons_review = ttk.Frame(review_frame)
        buttons_review.grid(row=22, column=0, sticky="ew", pady=(6, 0))
        for idx in range(5):
            buttons_review.columnconfigure(idx, weight=1)
        self.review_add_button = ttk.Button(buttons_review, text="Add Review", command=self._action_add_review)
        self.review_add_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.flag_add_button = ttk.Button(buttons_review, text="Add Flag", command=self._action_add_flag)
        ttk.Button(buttons_review, text="Mark Review Snapshot", command=self._action_capture_review_snapshot).grid(row=0, column=1, sticky="ew", padx=4)
        self.flag_add_button.grid(row=0, column=2, sticky="ew", padx=4)
        self.violation_add_button = ttk.Button(buttons_review, text="Add Violation", command=self._action_add_violation)
        self.violation_add_button.grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Button(buttons_review, text="Clear", command=self._clear_review_form).grid(row=0, column=4, sticky="ew", padx=(4, 0))

    def _render_chart_surface(self, replay_view: dict) -> None:
        chart_context = replay_view["chart_context"]
        header_lines = build_replay_header_lines(replay_view)
        current_tick = chart_context["current_tick"]
        header_lines.append(f"Current tick: bid={current_tick['bid']:.5f} ask={current_tick['ask']:.5f} mid={current_tick['mid']:.5f}")
        self.chart_header.configure(text="\n".join(header_lines))
        self.chart_footer.configure(text="\n".join(build_tick_table_lines(chart_context)))

        width = max(320, self.chart_canvas.winfo_width())
        height = max(220, self.chart_canvas.winfo_height())
        points = build_mid_price_line_points(chart_context["recent_points"], width=width, height=height)
        self.chart_canvas.delete("all")
        self.chart_canvas.create_rectangle(0, 0, width, height, outline="", fill="#10151c")
        self.chart_canvas.create_text(12, 12, anchor="nw", text="Mid-price trace", fill="#d7e3f4", font=("TkDefaultFont", 10, "bold"))
        if not points:
            self.chart_canvas.create_text(width / 2, height / 2, text="Not enough replay points yet", fill="#8aa0b8")
            return

        last_x, last_y = points[-1]
        self.chart_canvas.create_line(*flatten_canvas_points(points), fill="#4fc3f7", width=2, smooth=True)
        self.chart_canvas.create_oval(last_x - 4, last_y - 4, last_x + 4, last_y + 4, fill="#ffb74d", outline="")
        self.chart_canvas.create_line(16, height - 16, width - 16, height - 16, fill="#33485f")
        self.chart_canvas.create_line(16, 24, 16, height - 16, fill="#33485f")

    def _render_control_surface(self, replay_view: dict, trading_view: dict, journal_view: dict) -> None:
        button_state_map = build_button_state_map(replay_view, trading_view, journal_view)
        self.control_hint_label.configure(text="\n".join(build_control_hint_lines(button_state_map)))
        for key, button in self.control_buttons.items():
            button.configure(state="normal" if button_state_map[key] else "disabled")
        self.note_add_button.configure(state="normal" if button_state_map["add_note"] else "disabled")
        self.review_add_button.configure(state="normal" if button_state_map["add_review"] else "disabled")
        self.flag_add_button.configure(state="normal" if button_state_map["add_flag"] else "disabled")
        self.violation_add_button.configure(state="normal" if button_state_map["add_violation"] else "disabled")

    def _render_context_surface(self, trading_view: dict, journal_view: dict) -> None:
        self.session_context_label.configure(text="\n".join(build_session_context_lines(journal_view)))
        self.trade_context_label.configure(text="\n".join(build_trade_context_lines(trading_view, journal_view)))
        self.review_summary_label.configure(text="\n".join(build_review_summary_lines(journal_view)))
        self.finalization_label.configure(text="\n".join(build_finalization_lines(journal_view)))
        self.latest_result_label.configure(text="\n".join(build_latest_result_lines(journal_view)))

    def _render_authoring_surface(self, journal_view: dict) -> None:
        self.authoring_status_label.configure(text="\n".join(build_authoring_status_lines(journal_view)))
        note_lines = build_note_section_lines(journal_view)
        note_lines.append(f"Next note snapshot: {self.pending_note_snapshot_id or '-'}")
        self.note_status_label.configure(text="\n".join(note_lines))
        review_lines = build_review_section_lines(journal_view)
        review_lines.append(f"Next review snapshot: {', '.join(self.pending_review_snapshot_ids) or '-'}")
        self.review_status_label.configure(text="\n".join(review_lines))

    def _render_history_surface(self, journal_view: dict) -> None:
        self.history_status_label.configure(text="\n".join(build_history_status_lines(journal_view)))
        self.latest_trade_result_label.configure(text="\n".join(build_latest_trade_result_lines(journal_view)))
        self.timeline_preview_label.configure(text="\n".join(build_timeline_preview_lines(journal_view)))

    def _render_workflow_surface(self, replay_view: dict, trading_view: dict, journal_view: dict) -> None:
        self.workflow_guidance_label.configure(text="\n".join(build_workflow_guidance_lines(replay_view, trading_view, journal_view)))
        self.blocker_status_label.configure(text="\n".join(build_finalization_blocker_lines(journal_view)))
        self.action_feedback_label.configure(text="\n".join(build_action_feedback_lines(self.last_action_feedback, journal_view)))

    def _render_json(self, widget: tk.Text, payload: dict) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", json.dumps(payload, indent=2, ensure_ascii=False))
        widget.configure(state="disabled")

    def _get_text(self, widget: tk.Text) -> str:
        return widget.get("1.0", tk.END).strip()

    def _set_text(self, widget: tk.Text, value: str = "") -> None:
        widget.delete("1.0", tk.END)
        if value:
            widget.insert("1.0", value)

    @staticmethod
    def _parse_optional_float(value: str) -> float | None:
        stripped = value.strip()
        if not stripped:
            return None
        return float(stripped)

    def _clear_entry_inputs(self) -> None:
        self.pending_stop_trigger_value.set("")
        self.initial_stop_loss_value.set("")
        self.initial_take_profit_value.set("")

    def _clear_note_form(self) -> None:
        self._set_text(self.note_text)
        self.note_thesis.set("")
        self.note_risk_plan.set("")
        self.note_snapshot_ref.set("")
        self.pending_note_snapshot_id = None

    def _clear_review_form(self) -> None:
        self._set_text(self.review_text)
        self.review_setup_variant.set("fractal_breakout")
        self.review_entry_timing_label.set("timely_entry")
        self.review_market_context_label.set("clean_context")
        self.review_exit_quality_label.set("disciplined_exit")
        self.review_clarity_label.set("high_clarity")
        self.review_snapshot_ref.set("")
        self.pending_review_snapshot_ids = []

    def _run_action(self, action, success_summary: str) -> None:
        try:
            action()
            self.last_action_feedback = {
                "level": "info",
                "summary": success_summary,
                "detail": "Desktop shell refreshed from current runtime projections.",
            }
            self.refresh()
        except Exception as exc:  # pragma: no cover - UI path
            self.last_action_feedback = {
                "level": "error",
                "summary": success_summary,
                "detail": str(exc),
            }
            self.refresh()
            messagebox.showerror("Trader Trainer", str(exc))

    def _action_play(self) -> None:
        self._run_action(self.controller.play, "Replay started")

    def _action_pause(self) -> None:
        self._run_action(self.controller.pause, "Replay paused")

    def _action_advance(self) -> None:
        self._run_action(self.controller.advance_frame, "Replay advanced by one frame")

    def _action_set_speed(self) -> None:
        self._run_action(lambda: self.controller.set_speed(float(self.speed_value.get() or "1.0")), f"Replay speed set to {self.speed_value.get() or '1.0'}x")

    def _action_buy(self) -> None:
        def submit() -> None:
            self.controller.buy_market(
                stop_loss=self._parse_optional_float(self.initial_stop_loss_value.get()),
                take_profit=self._parse_optional_float(self.initial_take_profit_value.get()),
            )
            self._clear_entry_inputs()

        self._run_action(submit, "BuyMarket submitted")

    def _action_sell(self) -> None:
        def submit() -> None:
            self.controller.sell_market(
                stop_loss=self._parse_optional_float(self.initial_stop_loss_value.get()),
                take_profit=self._parse_optional_float(self.initial_take_profit_value.get()),
            )
            self._clear_entry_inputs()

        self._run_action(submit, "SellMarket submitted")

    def _action_buy_stop(self) -> None:
        def submit() -> None:
            self.controller.buy_stop(
                trigger_price=float(self.pending_stop_trigger_value.get() or "0"),
                stop_loss=self._parse_optional_float(self.initial_stop_loss_value.get()),
                take_profit=self._parse_optional_float(self.initial_take_profit_value.get()),
            )
            self._clear_entry_inputs()

        self._run_action(submit, "BuyStop submitted")

    def _action_sell_stop(self) -> None:
        def submit() -> None:
            self.controller.sell_stop(
                trigger_price=float(self.pending_stop_trigger_value.get() or "0"),
                stop_loss=self._parse_optional_float(self.initial_stop_loss_value.get()),
                take_profit=self._parse_optional_float(self.initial_take_profit_value.get()),
            )
            self._clear_entry_inputs()

        self._run_action(submit, "SellStop submitted")

    def _action_cancel_entry(self) -> None:
        self._run_action(self.controller.cancel_pending_entry, "Pending stop cancelled")

    def _action_close(self) -> None:
        self._run_action(self.controller.manual_close, "Manual close requested")

    def _action_finalize(self) -> None:
        self._run_action(self.controller.finalize_session, "Standard finalization requested")

    def _action_force_finalize(self) -> None:
        self._run_action(lambda: self.controller.finalize_session(force=True), "Force finalization requested")

    def _action_acknowledge_recovery(self) -> None:
        self._run_action(self.controller.acknowledge_recovery_context, "Reopened warning reviewed")

    def _action_add_note(self) -> None:
        def submit() -> None:
            self.controller.create_pre_trade_note(
                content=self._get_text(self.note_text) or "Desktop note",
                setup_tag=self.note_setup_tag.get() or None,
                thesis_summary=self.note_thesis.get() or None,
                risk_plan=self.note_risk_plan.get() or None,
                chart_snapshot_ref=self.pending_note_snapshot_id,
            )
            self._clear_note_form()

        self._run_action(submit, "PreTradeNote saved")

    def _action_add_review(self) -> None:
        def submit() -> None:
            self.controller.create_post_trade_review(
                content=self._get_text(self.review_text) or "Desktop review",
                setup_tag=self.review_setup_tag.get() or None,
                compliance_label=self.review_compliance_label.get() or None,
                setup_variant=self.review_setup_variant.get() or None,
                entry_timing_label=self.review_entry_timing_label.get() or None,
                market_context_label=self.review_market_context_label.get() or None,
                exit_quality_label=self.review_exit_quality_label.get() or None,
                review_clarity_label=self.review_clarity_label.get() or None,
                chart_snapshot_refs=tuple(self.pending_review_snapshot_ids),
            )
            self._clear_review_form()

        self._run_action(submit, "PostTradeReview saved")

    def _action_add_flag(self) -> None:
        self._run_action(lambda: self.controller.create_behavioral_flag(self.flag_code.get() or "premature_exit"), f"BehavioralFlag saved: {self.flag_code.get() or 'premature_exit'}")

    def _action_add_violation(self) -> None:
        self._run_action(lambda: self.controller.create_rule_violation(self.violation_code.get() or "manual_plan_deviation"), f"RuleViolation saved: {self.violation_code.get() or 'manual_plan_deviation'}")











    def _action_capture_note_snapshot(self) -> None:
        self._capture_snapshot(
            artifact_ref=self.note_snapshot_ref.get().strip() or "snapshots/desktop/pre-entry-context.png",
            snapshot_role="pre_entry_context",
            success_summary="Pre-entry chart snapshot saved",
            assign_to_note=True,
        )

    def _action_capture_review_snapshot(self) -> None:
        self._capture_snapshot(
            artifact_ref=self.review_snapshot_ref.get().strip() or "snapshots/desktop/review-context.png",
            snapshot_role="review_context",
            success_summary="Review chart snapshot saved",
            assign_to_note=False,
        )

    def _capture_snapshot(
        self,
        artifact_ref: str,
        snapshot_role: str,
        success_summary: str,
        assign_to_note: bool,
    ) -> None:
        try:
            workspace = self.controller.create_chart_snapshot(
                artifact_ref=artifact_ref,
                snapshot_role=snapshot_role,
            )
            snapshot = workspace["journal"].get("last_chart_snapshot") or {}
            snapshot_id = snapshot.get("snapshot_id")
            if assign_to_note:
                self.pending_note_snapshot_id = snapshot_id
            elif snapshot_id:
                self.pending_review_snapshot_ids = [snapshot_id]
            self.last_action_feedback = {
                "level": "info",
                "summary": success_summary,
                "detail": f"Snapshot {snapshot_id or '-'} is ready for the next {'note' if assign_to_note else 'review'}.",
            }
            self.refresh()
        except Exception as exc:  # pragma: no cover - UI path
            self.last_action_feedback = {
                "level": "error",
                "summary": success_summary,
                "detail": str(exc),
            }
            self.refresh()
            messagebox.showerror("Trader Trainer", str(exc))
