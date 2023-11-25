import argparse
import subprocess
import pathlib

import sys
import os

DESKTOP_ENTRY_TEMPLATE=["[Desktop Entry]", "Name={}", "Exec={}", "Icon={}", "Type={}", "Terminal={}"]

def entryFile(args):
    entry = DESKTOP_ENTRY_TEMPLATE.copy()
    entry[1] = args.name
    entry[2] = str(args.executable)
    if args.icon is not None:
        entry[3] = str(args.icon)
    else:
        if args.executable.suffix == ".AppImage":
            subprocess.run(["chmod", "+x", str(args.executable)])
            subprocess.run([str(args.executable), "--appimage-extract"])
        entry.pop(3)
    entry[4] = args.type
    entry[5] = str(args.terminal)
    return entry.join("\n")

GLOBAL_PATH=pathlib.Path("/usr/share/applications/")
LOCAL_PATH=pathlib.Path(pathlib.Path.home(), "/.local/share/applications/")

parser = argparse.ArgumentParser("dem", description="Desktop Entry Maker")

parser.add_argument("-e", "--executable", type=pathlib.Path, required=True)
parser.add_argument("-n", "--name", type=str, required=True)
parser.add_argument("-i", "--icon", type=pathlib.Path)
parser.add_argument("-T", "--type", type=str, default="Application")
parser.add_argument("-t", "--terminal", action="store_true")
parser.add_argument("--global", dest="global_", action="store_true")
parser.add_argument("--install-mime", action="store_true")

args = parser.parse_args()

if __name__ == "__main__":
    # subprocess.Popen(
    #     ["xdg-mime", "install", "--novendor", args.executable]
    # )
    if not args.executable.is_file():
        print(f"{str(args.executable)} is not a file")
        sys.exit(1)

    if args.executable.exists():
        if not args.icon.exists():
            print("Icon not found")
            sys.exit(1)

        entry = entryFile(args)
        _path = GLOBAL_PATH if args.global_ else LOCAL_PATH
        path: pathlib.Path = _path / os.path.splitext(args.executable.name)[0] + ".desktop"
        if args.global_:
            print("Requesting sudo...")
            subprocess.run(["sudo", "echo", "\n".join(entry), ">", str(path)], shell=True)
        else:
            print(f"Writing to {str(path)}")
            path.write_text(entry)
        
        if args.install_mime:
            subprocess.run(["xdg-mime", "install", "--novendor", args.executable])
            print(f"To uninstall the mime type, run: xdg-mime uninstall --novendor {str(args.executable)}")
            sys.exit(0)
    else:       
        print("Executable not found")
        sys.exit(1)