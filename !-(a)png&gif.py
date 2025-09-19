import os
import subprocess
from pathlib import Path
import sys

def main():
    # Create output directory if it doesn't exist
    output_dir = "Conversion-2"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PNG and GIF files in current directory
    current_dir = Path('.')
    files = list(current_dir.glob("*.png")) + list(current_dir.glob("*.gif"))
    
    # Open log file for writing
    with open('~PnGi-log.txt', 'w') as log_file:
        for file_path in files:
            print(f"\nConverting: {file_path.name}")
            log_file.write(f"Converting: {file_path.name}\n")
            
            # Define output path
            output_name = file_path.stem + '.jxl'
            output_path = os.path.join(output_dir, output_name)
            
            # Build cjxl command
            cmd = [
                "cjxl.exe",
                str(file_path),
                output_path,
                "--num_threads=16",
                "--modular_palette_colors=2048",
                "--brotli_effort=11",
                "--gaborish=0",
                "-m", "1",
                "-d", "0.0",
                "-e", "8",
                "-I", "100",
                "-E", "4",
                "-v"
            ]
            
            # Execute command with real-time output capture
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Combine stderr and stdout
                    text=True,
                    bufsize=1
                )
                
                # Read output in real-time (both stdout and stderr)
                while True:
                    output = process.stdout.readline()
                    if output == '':
                        break
                    sys.stdout.write(output)  # Write to console
                    sys.stdout.flush()       # Ensure immediate display
                    log_file.write(output)   # Write to log file
                    log_file.flush()         # Ensure immediate write
                    
                process.wait()
                
                print(f"Completed: {file_path.name} -> {output_path}")
                log_file.write(f"\n")
                log_file.flush()
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                log_file.write(f"Error processing {file_path.name}: {e}\n")
                log_file.flush()
    
    print("\nAll conversions completed!")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
