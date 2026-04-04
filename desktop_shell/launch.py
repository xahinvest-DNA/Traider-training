from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from runtime_bootstrap import import_raw_dataset
from runtime_bootstrap.errors import DatasetImportError

from .controller import DesktopShellController


ASCII_TK_PYTHON = Path(r"C:\Python311\python.exe")
TK_FALLBACK_ENV = "TRADER_TRAINER_TK_FALLBACK"


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


def launch_desktop_app(controller: DesktopShellController) -> None:
    from .tk_app import TraderTrainerDesktopApp

    TraderTrainerDesktopApp(controller).run()


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
        controller = build_controller_from_launch_config(config)
        launch_desktop_app(controller)
    except DatasetImportError:
        raise
    except Exception as exc:
        if _looks_like_tk_environment_error(exc):
            if _try_relaunch_with_ascii_tk_python(argv):
                return
            raise SystemExit(format_launch_failure_message(config, exc)) from None
        raise
