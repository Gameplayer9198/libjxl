#!/usr/bin/env python3
import subprocess
from pathlib import Path
import sys

# ================= CONFIGURATION =================
# File extensions to process
EXTENSIONS = {".jpg", ".jpeg"}

# Output directory
OUT_DIR = Path("Conversion")

# Literal log file name
LOG_FILE = "~Jpeg-log.txt"

# /usr/bin/time format string
TIME_FORMAT = "Wall: %e Sec\nUser: %U CPU-sec\nKernel: %S CPU-sec\nPercent CPU Usage: %P\nMaximum resident set size: %M KB"

# ./cjxl arguments
CJXL_ARGS = [
    "--num_threads=16",
    "--brotli_effort=11",
    "--gaborish=0",
    "--allow_jpeg_reconstruction=0",
    "-j", "1",
    "-d", "0.0",
    "-e", "8",
    "-v"
]
# =================================================

def main():
    # Create output directory if it doesn't exist
    OUT_DIR.mkdir(exist_ok=True)

    # Open log file (overwrite each run; change mode to "a" to append)
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        # Scan current working directory 1. Collect matching files
        files = [
            src for src in Path.cwd().glob("*")
            if src.is_file() and src.suffix.lower() in EXTENSIONS
        ]

        # 2. Sort by file size: largest first
        files.sort(key=lambda p: p.stat().st_size, reverse=True)

        # 3. Process in sorted order
        for src in files:
            dst = OUT_DIR / (src.stem + ".jxl")

            # Build command: /usr/bin/time -f "..." ./cjxl [args] input output
            cmd = [
                "/usr/bin/time",
                "-f", TIME_FORMAT,
                "./cjxl",
                *CJXL_ARGS,
                str(src),
                str(dst)
            ]

            header = f"\nProcessing: {src.name} -> {dst.name}"
            print(header)
            log.write(header + "\n")
            sys.stdout.flush()
            log.flush()

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Merge time stats with cjxl output
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )

                # Stream output line-by-line in real time
                for line in iter(proc.stdout.readline, ""):
                    print(line, end="")
                    log.write(line)
                    sys.stdout.flush()
                    log.flush()

                proc.wait()
                if proc.returncode != 0:
                    msg = f"Warning: cjxl exited with code {proc.returncode} for {src.name}\n"
                    print(msg, end="")
                    log.write(msg)

            except FileNotFoundError:
                msg = "Error: /usr/bin/time or ./cjxl not found. Ensure they are installed and executable.\n"
                print(msg, end="")
                log.write(msg)
                break
            except Exception as e:
                msg = f"Error processing {src.name}: {e}\n"
                print(msg, end="")
                log.write(msg)

# Final prompt
    print("\nAll done.")
    try:
        input("Press Enter to Exit/Close...")
    except (EOFError, KeyboardInterrupt):
        # Graceful fallback if run non-interactively or via automation
        pass

if __name__ == "__main__":
    main()
