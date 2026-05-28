#!/usr/bin/env python3
"""Build the Dollar Macro Check clang-tidy plugin."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.resolve()


def run_command(cmd):
    """Run a command, exit on failure."""
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"Failed: {' '.join(cmd)}")


def check_llvm(llvm_src, llvm_build):
    """Check if LLVM source and build exist."""
    llvm_src = Path(llvm_src).resolve()
    llvm_build = Path(llvm_build).resolve()
    
    if not (llvm_src / "llvm" / "CMakeLists.txt").exists():
        sys.exit(f"LLVM source not found at {llvm_src}")
    
    if not (llvm_build / "lib" / "cmake" / "llvm").exists():
        sys.exit(f"LLVM not built at {llvm_build}\nPlease build LLVM first")
    
    return llvm_src, llvm_build


def main():
    parser = argparse.ArgumentParser(description="Build the Dollar Macro Check plugin")
    parser.add_argument("--llvm-src", default=str(REPO_ROOT / "llvm-project"),
                        help="Path to LLVM source (default: ./llvm-project)")
    parser.add_argument("--llvm-build", help="Path to LLVM build (default: <llvm-src>/build)")
    parser.add_argument("--build-dir", default=str(REPO_ROOT / "build"),
                        help="Plugin build directory (default: ./build)")
    parser.add_argument("--install-dir", default=str(REPO_ROOT / "install"),
                        help="Installation directory (default: ./install)")
    parser.add_argument("--clean", action="store_true", help="Clean build before building")
    parser.add_argument("-j", type=int, default=4, help="Parallel jobs (default: 4)")
    
    args = parser.parse_args()
    
    llvm_src = Path(args.llvm_src).resolve()
    llvm_build = Path(args.llvm_build or (llvm_src / "build")).resolve()
    build_dir = Path(args.build_dir).resolve()
    install_dir = Path(args.install_dir).resolve()
    
    llvm_src, llvm_build = check_llvm(llvm_src, llvm_build)
    
    if args.clean and build_dir.exists():
        shutil.rmtree(build_dir)
    
    build_dir.mkdir(parents=True, exist_ok=True)
    install_dir.mkdir(parents=True, exist_ok=True)
    
    run_command([
        "cmake", "-B", str(build_dir), "-S", str(REPO_ROOT), "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        f"-DLLVM_SRC_DIR={llvm_src}",
        f"-DLLVM_BUILD_DIR={llvm_build}",
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
    ])
    
    run_command(["ninja", "-C", str(build_dir), "-j", str(args.j)])
    run_command(["ninja", "-C", str(build_dir), "install"])
    
    plugin = next(install_dir.glob("lib/dollar_macros.*"), None)
    if plugin:
        clang_tidy = llvm_build / "bin" / "clang-tidy"
        if clang_tidy.exists():
            print(f"Run: {clang_tidy} --load={plugin} -checks=dollar-macro <file>")


if __name__ == "__main__":
    main()
