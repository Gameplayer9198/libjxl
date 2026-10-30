#!/usr/bin/env python
import re
import os
from pathlib import Path
from statistics import mean, median
from collections import Counter

def format_seconds(total_secs):
    """Convert total seconds to HH:MM:SS.ss string"""
    hours = int(total_secs // 3600)
    minutes = int((total_secs % 3600) // 60)
    seconds = total_secs % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:.2f}"

def main():
    log_files = ["~Jpeg-log.txt", "~PnGi-log.txt"]

    # Regex patterns
    pct_saved_pat = r'(\d+(?:\.\d+)?)\s*% saved'
    pct_larger_pat = r'(-?\d+(?:\.\d+)?)\s*% larger'  # allow optional negative already in text? safer: match any float
    wall_time_pat = r'Wall:\s*(\d+(?:\.\d+)?)\s*Sec'

    for log_path in log_files:
        if not os.path.isfile(log_path):
            print(f"Skipping '{log_path}': not found.")
            continue

        try:
            with open(log_path, "r") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading '{log_path}': {e}")
            continue

        # Extract percentage values
        saved_vals = [float(m) for m in re.findall(pct_saved_pat, text)]
        larger_vals = [float(m) for m in re.findall(pct_larger_pat, text)]

        # print(saved_vals)
        # print(larger_vals)

        all_values = saved_vals + [-v for v in larger_vals]

        # print(all_values)

        # Extract wall-clock times (seconds)
        wall_times = [float(m) for m in re.findall(wall_time_pat, text)]
        total_wall_sec = sum(wall_times)

        # print(wall_times)
        # print(total_wall_sec)

        # Format summary
        summary_lines = []

        if all_values:
            current_mean = mean(all_values)
            current_median = median(all_values)
            first_pass_results = {
                "mean": round(current_mean, 3),
                "median": round(current_median, 3)
            }

            rounded_vals = []
            for v in all_values:
                if v < 0:
                    rounded_vals.append(round(v, 1))
                else:
                    rounded_vals.append(int(round(v)))

            counter = Counter(rounded_vals)
            max_count = max(counter.values())
            modes = [val for val, cnt in counter.items() if cnt == max_count]
            mode_val = min(modes)

            summary_lines.append(f"Mean: {first_pass_results['mean']:.3f}% saved")
            summary_lines.append(f"Median: {first_pass_results['median']:.3f}% saved")
            summary_lines.append(f"Mode (rounded): {mode_val}%")
            summary_lines.append(f"(Compression values used: {len(all_values)} entries)")
        else:
            summary_lines.append("No percentage compression values found.")

        # Always include wall time (even if 0)
        summary_lines.append("")
        summary_lines.append(f"Total Wall Time: {total_wall_sec:.2f} sec → {format_seconds(total_wall_sec)}")

        # Write to file
        with open(log_path, "a") as f:
            f.write("\n--- Analysis Summary ---\n")
            for line in summary_lines:
                f.write(line + "\n")

        print(f"✅ Analysis complete for '{log_path}'. Summary appended.")

    if not any(os.path.isfile(p) for p in log_files):
        print("⚠️ No recognized log files found. Expected at least one of: Jpeg-log.txt, PnGi-log.txt")

if __name__ == "__main__":
    main()
