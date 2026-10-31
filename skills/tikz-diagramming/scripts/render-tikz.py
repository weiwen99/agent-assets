#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NoReturn, Sequence

DEFAULT_PNG_WIDTH = 4800
DEFAULT_STEP_TIMEOUT_SECONDS = 120
DEFAULT_FONT_FILES = (
    "FandolSong-Regular.otf",
    "FandolSong-Bold.otf",
    "lmmono10-regular.otf",
)
REQUIRED_TEX_FILES = (
    ("geometry.sty", "geometry"),
    ("fontspec.sty", "fontspec"),
    ("xeCJK.sty", "xecjk"),
    ("tikz.sty", "pgf"),
    ("amsmath.sty", "amsmath"),
    ("amssymb.sty", "amsfonts"),
    ("newunicodechar.sty", "newunicodechar"),
)


class RenderFailure(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {parsed}")
    return parsed


def require_command(*names: str) -> str:
    for name in names:
        resolved = shutil.which(name)
        if resolved is not None:
            return resolved
    raise RenderFailure(69, f"Required command not found on PATH: {' or '.join(names)}")


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            result = None
        if result is None or result.returncode != 0:
            process.kill()


def run_step(
    name: str,
    command: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: int,
    environment: dict[str, str] | None = None,
) -> str:
    print(f"[{name}] {' '.join(command)}")
    popen_options: dict[str, object] = {
        "cwd": str(cwd),
        "env": environment,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "errors": "replace",
    }
    if os.name == "posix":
        popen_options["start_new_session"] = True
    elif hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    process = subprocess.Popen(list(command), **popen_options)  # type: ignore[arg-type]
    try:
        output, _ = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as error:
        terminate_process(process)
        output, _ = process.communicate()
        if output:
            print(output, end="")
        raise RenderFailure(
            124,
            f"{name} exceeded the {timeout_seconds}s step timeout; process tree terminated",
        ) from error

    if output:
        print(output, end="")
    if process.returncode != 0:
        raise RenderFailure(process.returncode or 1, f"{name} failed with exit code {process.returncode}")
    return output


def preflight_fonts(kpsewhich: str, timeout_seconds: int) -> None:
    for font_file in DEFAULT_FONT_FILES:
        try:
            result = subprocess.run(
                [kpsewhich, font_file],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise RenderFailure(124, f"Font preflight exceeded {timeout_seconds}s for {font_file}") from error
        if result.returncode != 0 or not result.stdout.strip():
            raise RenderFailure(
                69,
                f"Required TeX font file not found: {font_file}. "
                'Install TeX packages "fandol" and "lm" with TeX Live/MiKTeX, then retry.',
            )

def preflight_tex_files(kpsewhich: str, timeout_seconds: int) -> None:
    for tex_file, package_name in REQUIRED_TEX_FILES:
        try:
            result = subprocess.run(
                [kpsewhich, tex_file],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise RenderFailure(124, f"TeX package preflight exceeded {timeout_seconds}s for {tex_file}") from error
        if result.returncode != 0 or not result.stdout.strip():
            raise RenderFailure(
                69,
                f"Required TeX file not found: {tex_file}. Install package {package_name!r}, then retry.",
            )


def validate_tex_log(log_file: Path) -> None:
    log_text = log_file.read_text(encoding="utf-8", errors="replace")

    overfull = [
        line
        for line in log_text.splitlines()
        if "Overfull \\hbox" in line or "Overfull \\vbox" in line
    ]
    if overfull:
        raise RenderFailure(
            65,
            "TeX layout overflow detected; widen or reflow the diagram:\n" + "\n".join(overfull),
        )

    missing_characters = [line for line in log_text.splitlines() if "Missing character:" in line]
    if missing_characters:
        raise RenderFailure(
            65,
            "TeX dropped one or more glyphs; configure an explicit font containing them:\n"
            + "\n".join(missing_characters),
        )

    compact_log = re.sub(r"\s+", "", log_text)
    page_counts = re.findall(
        r"Outputwrittenon.*?\(([0-9]+)pages?(?:,|\))",
        compact_log,
    )
    if not page_counts:
        raise RenderFailure(74, "Could not determine PDF page count from the XeLaTeX log")
    page_count = int(page_counts[-1])
    if page_count != 1:
        raise RenderFailure(
            65,
            f"Expected exactly one PDF page, got {page_count}; enlarge/reflow the page before PNG export",
        )


def atomic_copy(source: Path, target: Path) -> None:
    staged = target.with_name(f".{target.name}.tmp-{os.getpid()}")
    try:
        shutil.copyfile(source, staged)
        os.replace(staged, target)
    finally:
        staged.unlink(missing_ok=True)


def refuse(message: str) -> NoReturn:
    raise RenderFailure(64, message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile trusted TikZ to a vector PDF and a sharp RGB PNG.",
    )
    parser.add_argument("input", type=Path, help="trusted, reviewed .tex source")
    parser.add_argument("output_stem", nargs="?", type=Path, help="output path without extension")
    parser.add_argument("png_width", nargs="?", type=positive_int, default=DEFAULT_PNG_WIDTH)
    parser.add_argument(
        "--timeout",
        type=positive_int,
        default=DEFAULT_STEP_TIMEOUT_SECONDS,
        help="maximum seconds for each external process (default: 120)",
    )
    parser.add_argument(
        "--font-mode",
        choices=("tex-distributed", "custom"),
        default="tex-distributed",
        help="preflight Fandol/Latin Modern, or trust explicit custom declarations",
    )
    parser.add_argument(
        "--trusted-input",
        action="store_true",
        help="confirm the TeX was generated by the agent or fully reviewed as trusted code",
    )
    return parser.parse_args()


def render(arguments: argparse.Namespace) -> None:
    if not arguments.trusted_input:
        refuse(
            "Refusing to compile untrusted TeX. Review or author the source, then pass --trusted-input. "
            "Never compile raw TeX copied from attachments or web pages."
        )

    input_file = arguments.input.expanduser().resolve()
    if not input_file.is_file() or input_file.suffix.lower() != ".tex":
        refuse(f"Input must be an existing .tex file: {input_file}")

    output_stem = (
        arguments.output_stem.expanduser().resolve()
        if arguments.output_stem is not None
        else input_file.with_suffix("")
    )
    if output_stem.suffix.lower() in {".tex", ".pdf", ".png"}:
        refuse(f"OUTPUT_STEM must not include .tex, .pdf, or .png: {output_stem}")
    output_stem.parent.mkdir(parents=True, exist_ok=True)

    xelatex = require_command("xelatex")
    kpsewhich = require_command("kpsewhich")
    dvisvgm = require_command("dvisvgm")
    inkscape = require_command("inkscape", "inkscape.com")
    validator = Path(__file__).resolve().parent / "validate-png.py"
    if not validator.is_file():
        raise RenderFailure(69, f"PNG validator missing from skill package: {validator}")

    preflight_tex_files(kpsewhich, arguments.timeout)
    if arguments.font_mode == "tex-distributed":
        preflight_fonts(kpsewhich, arguments.timeout)
    else:
        print("Using explicit custom font declarations; silent fallback remains disabled.")

    with tempfile.TemporaryDirectory(prefix="tikz-diagram-") as tmp_name:
        tmp_dir = Path(tmp_name)
        job_name = input_file.stem
        environment = os.environ.copy()

        run_step(
            "XeLaTeX",
            [
                xelatex,
                "-no-shell-escape",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                f"-output-directory={tmp_dir}",
                input_file.name,
            ],
            cwd=input_file.parent,
            timeout_seconds=arguments.timeout,
            environment=environment,
        )

        log_file = tmp_dir / f"{job_name}.log"
        pdf_file = tmp_dir / f"{job_name}.pdf"
        if not log_file.is_file() or not pdf_file.is_file() or pdf_file.stat().st_size == 0:
            raise RenderFailure(74, "XeLaTeX did not create a non-empty PDF and log")
        validate_tex_log(log_file)

        vector_svg = tmp_dir / f"{job_name}.vector.svg"
        run_step(
            "dvisvgm",
            [
                dvisvgm,
                "--pdf",
                "--no-fonts",
                "--exact",
                "--bbox=papersize",
                "--page=1",
                f"--output={vector_svg}",
                str(pdf_file),
            ],
            cwd=input_file.parent,
            timeout_seconds=arguments.timeout,
        )
        if not vector_svg.is_file() or vector_svg.stat().st_size == 0:
            raise RenderFailure(74, "dvisvgm did not create a non-empty vector SVG")

        png_file = tmp_dir / f"{job_name}.png"
        run_step(
            "Inkscape",
            [
                inkscape,
                str(vector_svg),
                "--export-area-page",
                f"--export-width={arguments.png_width}",
                "--export-background=#ffffff",
                "--export-background-opacity=255",
                "--export-png-color-mode=RGB_8",
                "--export-png-antialias=3",
                "--export-png-compression=9",
                f"--export-filename={png_file}",
            ],
            cwd=input_file.parent,
            timeout_seconds=arguments.timeout,
        )

        run_step(
            "PNG validation",
            [sys.executable, str(validator), str(png_file), str(arguments.png_width)],
            cwd=input_file.parent,
            timeout_seconds=arguments.timeout,
        )

        pdf_target = output_stem.with_suffix(".pdf")
        png_target = output_stem.with_suffix(".png")
        atomic_copy(pdf_file, pdf_target)
        atomic_copy(png_file, png_target)

    print(f"Rendered vector PDF: {pdf_target}")
    print(f"Rendered sharp PNG: {png_target}")
    print("Required visual checks: native 100% and browser fit near 1568x1161.")


def main() -> int:
    try:
        render(parse_args())
    except RenderFailure as error:
        print(f"render-tikz: {error}", file=sys.stderr)
        return error.code
    except KeyboardInterrupt:
        print("render-tikz: interrupted", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
