from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Sequence

from runtime_bootstrap import import_raw_dataset
from runtime_bootstrap.errors import DatasetImportError

from .controller import DesktopShellController


ASCII_TK_PYTHON = Path(r"C:\Python311\python.exe")
TK_FALLBACK_ENV = "TRADER_TRAINER_TK_FALLBACK"
_PENDING_STARTUP_SELECTION: "DesktopStartSelection | None" = None


@dataclass(frozen=True)
class DesktopLaunchConfig:
    dataset_handle: str
    storage_dir: Path
    replay_mode: str
    instrument_id: str | None = None
    market_profile: str = "FX/CFD"
    price_precision: int = 5
    timezone_canonical: str = "UTC"
    import_output_root: Path | None = None


@dataclass(frozen=True)
class DesktopStartPathOption:
    key: str
    label: str
    detail: str
    enabled: bool = True


@dataclass(frozen=True)
class DesktopStartSelection:
    key: str
    label: str
    detail: str
    selected_path: str | None = None


def build_default_launch_config(project_root: str | Path | None = None) -> DesktopLaunchConfig:
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parent.parent
    return DesktopLaunchConfig(
        dataset_handle=str(root / "runtime_bootstrap" / "fixtures" / "eurusd_sample"),
        storage_dir=root / "desktop_shell" / ".local_state",
        replay_mode="training",
    )


def parse_launch_args(argv: Sequence[str] | None = None, project_root: str | Path | None = None) -> DesktopLaunchConfig:
    defaults = build_default_launch_config(project_root=project_root)
    parser = argparse.ArgumentParser(description="Trader Trainer desktop shell")
    parser.add_argument("--dataset", default=defaults.dataset_handle, help="Path to normalized dataset directory or raw CSV/TSV/JSON tick file")
    parser.add_argument("--storage", default=str(defaults.storage_dir), help="Path to local storage directory")
    parser.add_argument("--mode", default=defaults.replay_mode, help="Replay mode for the desktop shell")
    parser.add_argument("--instrument", default=None, help="Instrument id override for raw dataset import")
    parser.add_argument("--profile", default=defaults.market_profile, help="Market profile override for raw dataset import")
    parser.add_argument("--precision", type=int, default=defaults.price_precision, help="Normalized price precision for raw dataset import")
    parser.add_argument("--timezone", default=defaults.timezone_canonical, help="Canonical timezone stored in imported normalized datasets")
    parser.add_argument("--import-output", default=None, help="Directory for auto-imported normalized datasets")
    args = parser.parse_args(list(argv) if argv is not None else None)
    return DesktopLaunchConfig(
        dataset_handle=str(args.dataset),
        storage_dir=Path(args.storage),
        replay_mode=str(args.mode),
        instrument_id=(str(args.instrument) if args.instrument else None),
        market_profile=str(args.profile),
        price_precision=int(args.precision),
        timezone_canonical=str(args.timezone),
        import_output_root=(Path(args.import_output) if args.import_output else None),
    )


def build_start_flow_options(config: DesktopLaunchConfig) -> list[DesktopStartPathOption]:
    dataset_label = _summarize_dataset_handle(config.dataset_handle)
    resume_available = has_local_session_state(config.storage_dir)
    resume_detail = (
        f"Resume the last local session from {config.storage_dir}."
        if resume_available
        else f"No recoverable local session found in {config.storage_dir} yet."
    )
    return [
        DesktopStartPathOption(
            key="open_prepared_dataset",
            label="Open prepared dataset",
            detail="Choose a normalized dataset folder, then enter the trainer workspace with a clean local session.",
        ),
        DesktopStartPathOption(
            key="import_raw_historical_data",
            label="Import raw historical data",
            detail="Choose a raw CSV/TSV/JSON tick file, import it, then enter the trainer workspace with a clean local session.",
        ),
        DesktopStartPathOption(
            key="start_new_session",
            label="Start new session",
            detail=f"Ignore saved local recovery and open a clean workspace session with the current dataset: {dataset_label}.",
        ),
        DesktopStartPathOption(
            key="resume_last_local_session",
            label="Resume last local session",
            detail=resume_detail,
            enabled=resume_available,
        ),
    ]


def has_local_session_state(storage_dir: str | Path) -> bool:
    return (Path(storage_dir) / "local_runtime_state.json").exists()


def reset_local_session_state(storage_dir: str | Path) -> None:
    storage_path = Path(storage_dir) / "local_runtime_state.json"
    if storage_path.exists():
        storage_path.unlink()


def resolve_start_selection(
    config: DesktopLaunchConfig,
    selection_key: str,
    selected_path: str | Path | None = None,
) -> tuple[DesktopLaunchConfig, DesktopStartSelection]:
    selected = Path(selected_path) if selected_path is not None else None
    if selection_key == "open_prepared_dataset":
        if selected is None:
            raise ValueError("Prepared dataset path is required for open_prepared_dataset.")
        resolved_config = replace(config, dataset_handle=str(selected))
        reset_local_session_state(resolved_config.storage_dir)
        return resolved_config, DesktopStartSelection(
            key=selection_key,
            label="Open prepared dataset",
            detail="Entered workspace from an explicit prepared dataset choice.",
            selected_path=str(selected),
        )
    if selection_key == "import_raw_historical_data":
        if selected is None:
            raise ValueError("Raw dataset path is required for import_raw_historical_data.")
        resolved_config = replace(config, dataset_handle=str(selected))
        reset_local_session_state(resolved_config.storage_dir)
        return resolved_config, DesktopStartSelection(
            key=selection_key,
            label="Import raw historical data",
            detail="Entered workspace from an explicit raw import choice.",
            selected_path=str(selected),
        )
    if selection_key == "start_new_session":
        reset_local_session_state(config.storage_dir)
        return config, DesktopStartSelection(
            key=selection_key,
            label="Start new session",
            detail="Entered workspace from an explicit clean-session choice.",
            selected_path=None,
        )
    if selection_key == "resume_last_local_session":
        return config, DesktopStartSelection(
            key=selection_key,
            label="Resume last local session",
            detail="Entered workspace from an explicit local-session resume choice.",
            selected_path=None,
        )
    raise ValueError(f"Unsupported start selection: {selection_key}")


def build_controller_from_start_selection(
    config: DesktopLaunchConfig,
    selection_key: str,
    selected_path: str | Path | None = None,
) -> tuple[DesktopShellController, DesktopStartSelection]:
    resolved_config, selection = resolve_start_selection(config, selection_key, selected_path=selected_path)
    return build_controller_from_launch_config(resolved_config), selection


def resolve_dataset_handle(config: DesktopLaunchConfig) -> str:
    dataset_path = Path(config.dataset_handle)
    if dataset_path.is_file():
        output_root = config.import_output_root or (config.storage_dir / ".imports")
        imported = import_raw_dataset(
            dataset_path,
            output_root,
            instrument_id=config.instrument_id,
            market_profile=config.market_profile,
            price_precision=config.price_precision,
            timezone_canonical=config.timezone_canonical,
        )
        return str(imported)
    return str(dataset_path)


def build_controller_from_launch_config(config: DesktopLaunchConfig) -> DesktopShellController:
    return DesktopShellController(
        dataset_handle=resolve_dataset_handle(config),
        storage_dir=config.storage_dir,
        replay_mode=config.replay_mode,
    )


def launch_desktop_app(controller: DesktopShellController, startup_selection: DesktopStartSelection | None = None) -> None:
    from .tk_app import TraderTrainerDesktopApp

    active_selection = startup_selection if startup_selection is not None else _PENDING_STARTUP_SELECTION
    TraderTrainerDesktopApp(controller, startup_selection=active_selection).run()


def prompt_start_selection(config: DesktopLaunchConfig) -> DesktopStartSelection | None:
    import tkinter as tk
    from tkinter import filedialog, ttk

    options = build_start_flow_options(config)
    result: dict[str, str | None] = {"key": None, "selected_path": None}

    root = tk.Tk()
    root.title("Enter Trainer Workspace")
    root.geometry("760x340")
    root.resizable(False, False)

    container = ttk.Frame(root, padding=16)
    container.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    ttk.Label(container, text="Choose how to enter the desktop trainer workspace", justify="left", anchor="w").grid(row=0, column=0, sticky="ew")
    ttk.Label(
        container,
        text=f"Current dataset: {_summarize_dataset_handle(config.dataset_handle)} | Storage: {config.storage_dir}",
        justify="left",
        anchor="w",
    ).grid(row=1, column=0, sticky="ew", pady=(4, 12))

    def choose(option: DesktopStartPathOption) -> None:
        selected_path: str | None = None
        if option.key == "open_prepared_dataset":
            selected_path = filedialog.askdirectory(
                title="Open prepared dataset",
                initialdir=str(Path(config.dataset_handle).parent if Path(config.dataset_handle).exists() else Path.cwd()),
                mustexist=True,
            )
            if not selected_path:
                return
        elif option.key == "import_raw_historical_data":
            selected_path = filedialog.askopenfilename(
                title="Import raw historical data",
                initialdir=str(Path(config.dataset_handle).parent if Path(config.dataset_handle).exists() else Path.cwd()),
                filetypes=[("Raw market data", "*.csv *.tsv *.json"), ("All files", "*.*")],
            )
            if not selected_path:
                return
        result["key"] = option.key
        result["selected_path"] = selected_path
        root.destroy()

    for index, option in enumerate(options, start=2):
        frame = ttk.LabelFrame(container, text=option.label, padding=10)
        frame.grid(row=index, column=0, sticky="ew", pady=(0, 8))
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text=option.detail, justify="left", anchor="w").grid(row=0, column=0, sticky="ew", padx=(0, 8))
        button = ttk.Button(frame, text=option.label, command=lambda current=option: choose(current))
        button.grid(row=0, column=1, sticky="e")
        if not option.enabled:
            button.configure(state="disabled")

    ttk.Button(container, text="Cancel", command=root.destroy).grid(row=len(options) + 2, column=0, sticky="e", pady=(8, 0))
    root.mainloop()

    key = result["key"]
    if not key:
        return None
    _, selection = resolve_start_selection(config, str(key), selected_path=result["selected_path"])
    return selection


def format_launch_failure_message(config: DesktopLaunchConfig, exc: Exception) -> str:
    from .readiness import build_readiness_snapshot, format_readiness_report

    readiness_report = format_readiness_report(build_readiness_snapshot(config))
    return (
        "Desktop shell could not start a Tk GUI in the current environment.\n"
        f"Reason: {exc}\n"
        "A non-GUI readiness snapshot is shown below so work can continue while Tk/Tcl is fixed.\n\n"
        f"{readiness_report}"
    )




def _looks_like_tk_environment_error(exc: Exception) -> bool:
    message = str(exc)
    return "Tcl" in message or "Tk" in message or "init.tcl" in message


def _try_relaunch_with_ascii_tk_python(argv: Sequence[str] | None = None) -> bool:
    if os.environ.get(TK_FALLBACK_ENV) == "1":
        return False
    if not ASCII_TK_PYTHON.exists():
        return False
    if Path(sys.executable).resolve() == ASCII_TK_PYTHON.resolve():
        return False

    env = os.environ.copy()
    env[TK_FALLBACK_ENV] = "1"
    command = [str(ASCII_TK_PYTHON), "-m", "desktop_shell", *(list(argv) if argv is not None else [])]
    subprocess.Popen(command, cwd=str(Path(__file__).resolve().parent.parent), env=env)
    return True


def run_desktop_shell(argv: Sequence[str] | None = None) -> None:
    config = parse_launch_args(argv=argv)
    try:
        selection = prompt_start_selection(config)
        if selection is None:
            return
        controller, resolved_selection = build_controller_from_start_selection(
            config,
            selection.key,
            selected_path=selection.selected_path,
        )
        global _PENDING_STARTUP_SELECTION
        _PENDING_STARTUP_SELECTION = resolved_selection
        launch_desktop_app(controller)
        _PENDING_STARTUP_SELECTION = None
    except DatasetImportError:
        raise
    except Exception as exc:
        if _looks_like_tk_environment_error(exc):
            if _try_relaunch_with_ascii_tk_python(argv):
                return
            raise SystemExit(format_launch_failure_message(config, exc)) from None
        raise


def _summarize_dataset_handle(dataset_handle: str | Path) -> str:
    path = Path(dataset_handle)
    if path.name:
        return path.name
    return str(path)
