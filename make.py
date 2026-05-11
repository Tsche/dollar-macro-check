#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).parent.resolve()


LLVM_GIT_URL = "https://github.com/llvm/llvm-project"


CMAKE_CONFIG_DEFAULTS = {
    "CMAKE_BUILD_TYPE": "Release",
    "CMAKE_C_COMPILER": "clang",
    "CMAKE_CXX_COMPILER": "clang++",
    "LLVM_USE_LINKER": "lld",
    "LLVM_ENABLE_PROJECTS": "clang;clang-tools-extra",
    "LLVM_TARGETS_TO_BUILD": "host",
    "BUILD_SHARED_LIBS": "OFF",
}

PATCHES = [
    {
        "path": Path("clang-tools-extra") / "clang-tidy" / "CMakeLists.txt",
        "already_patched": "clangTidyDollarModule",
        "marker":          "set(ALL_CLANG_TIDY_CHECKS)",
        "replacement":     "add_subdirectory(dollar)\nset(ALL_CLANG_TIDY_CHECKS)\n  clangTidyDollarModule",
    },
    {
        "path": Path("clang-tools-extra") / "clang-tidy" / "ClangTidyForceLinker.h",
        "already_patched": "DollarModuleAnchorSource",
        "marker":           "} // namespace clang::tidy",
        "replacement":      "\n// This anchor is used to force the linker to link the DollarModule."
                            "\nextern volatile int DollarModuleAnchorSource;"
                            "\n[[maybe_unused]] static int DollarModuleAnchorDestination ="
                            "\n    DollarModuleAnchorSource;"
                            "\n} // namespace clang::tidy",
    },
]


def prompt(question: str, default: str = "yes") -> bool:
    choices = "Y/n" if default == "yes" else "y/N"
    reply = input(f"{question} [{choices}]: ").strip().lower()
    return reply != "n" if default == "yes" else reply == "y"


def check_tools(tools: list[str]) -> None:
    missing = [tool for tool in tools if not shutil.which(tool)]
    if missing:
        sys.exit("Error: missing required tools: " + ", ".join(missing))

def patch_file(path: Path, already_patched: str, marker: str, replacement: str) -> None:
    content = path.read_text()
    if already_patched in content:
        return
    if marker not in content:
        raise RuntimeError(f"Patch marker not found in {path}: {marker!r}")
    content = content.replace(marker, replacement)
    path.write_text(content)


def copy_extension(repo_root: Path, llvm_path: Path) -> None:
    dst = llvm_path / "clang-tools-extra" / "clang-tidy" / "dollar"
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(repo_root / "src" / "dollar", dst)


def ensure_llvm_repo(
    llvm_path: Path,
    *,
    branch: str | None,
    fresh: bool,
    non_interactive: bool,
) -> None:
    if llvm_path.exists() and fresh:
        # only allow deleting the default in-repo checkout unless the user explicitly confirms.
        default_path = (REPO_ROOT / "llvm-project").resolve()
        if llvm_path.resolve() != default_path and not non_interactive:
            ok = prompt(
                f"Delete existing LLVM repo at {llvm_path} and re-clone?", default="no"
            )
            if not ok:
                fresh = False
        if fresh:
            shutil.rmtree(llvm_path)

    if not llvm_path.exists():
        print(f"Cloning LLVM to {llvm_path}...")
        subprocess.check_call(["git", "clone", LLVM_GIT_URL, str(llvm_path)])

    if branch:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(llvm_path),
            capture_output=True,
            text=True,
            check=True,
        )
        current = result.stdout.strip()
        if current != branch:
            print(f"Current: {current}, Target: {branch}")
            if non_interactive or prompt("Switch branches?", default="no"):
                subprocess.check_call(["git", "fetch", "origin"], cwd=str(llvm_path))
                subprocess.check_call(["git", "checkout", branch], cwd=llvm_path)


def prepare_sources(llvm_path: Path) -> None:
    copy_extension(REPO_ROOT, llvm_path)
    for patch in PATCHES:
        patch['path'] = llvm_path / patch['path']
        patch_file(**patch)


def configure_cmake(build_dir: Path, llvm_path: Path, install_prefix: Path, reconfigure: bool) -> None:
    if not reconfigure and build_dir.exists():
        return

    print("Configuring CMake...")
    build_dir.mkdir(parents=True, exist_ok=True)
    cmake_args = ["cmake", "-S", str(llvm_path / "llvm"), "-B", str(build_dir), "-G", "Ninja"]
    for key, value in CMAKE_CONFIG_DEFAULTS.items():
        cmake_args.append(f"-D{key}={value}")
    cmake_args.append(f"-DCMAKE_INSTALL_PREFIX={str(install_prefix)}")
    subprocess.check_call(cmake_args)


def build_and_install(build_dir: Path) -> None:
    print("Building...")
    subprocess.check_call(["ninja", "-C", str(build_dir), "install"])


def install_clang_tidy(install_target: Path, llvm_install: Path) -> Path:
    if install_target.resolve() == llvm_install.resolve():
        return llvm_install / "bin" / "clang-tidy"

    src_clang_tidy = llvm_install / "bin" / "clang-tidy"
    if not src_clang_tidy.exists():
        raise RuntimeError(f"clang-tidy not found under LLVM install: {llvm_install}")

    dst_clang_tidy = install_target / "bin" / "clang-tidy"
    dst_clang_tidy.parent.mkdir(parents=True, exist_ok=True)
    if dst_clang_tidy.exists():
        dst_clang_tidy.unlink()
    shutil.copy2(src_clang_tidy, dst_clang_tidy)

    return dst_clang_tidy


def run_lit_tests(llvm_path: Path) -> None:
    env = dict(os.environ)
    env["DOLLAR_MACRO_LLVM_PATH"] = str(llvm_path)
    subprocess.check_call(["lit", "test"], cwd=REPO_ROOT, env=env)


@dataclass(frozen=True)
class ResolvedPaths:
    llvm_path: Path
    build_dir: Path
    llvm_install: Path
    install_target: Path


def resolve_paths(args: argparse.Namespace) -> ResolvedPaths:
    llvm_path = Path(args.llvm_path).expanduser()
    if not llvm_path.is_absolute():
        llvm_path = (REPO_ROOT / llvm_path).resolve()

    build_dir = Path(args.build_dir).expanduser() if args.build_dir else (llvm_path / "build")
    if not build_dir.is_absolute():
        build_dir = (REPO_ROOT / build_dir).resolve()

    llvm_install = (llvm_path / "install").resolve()

    install_target = Path(args.install_target).expanduser()
    if not install_target.is_absolute():
        install_target = (REPO_ROOT / install_target).resolve()

    return ResolvedPaths(
        llvm_path=llvm_path,
        build_dir=build_dir,
        llvm_install=llvm_install,
        install_target=install_target,
    )


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--llvm-path",
        default="llvm-project",
        help="Path to the llvm-project source checkout (default: ./llvm-project)",
    )
    parser.add_argument("--llvm-branch", help="LLVM branch/tag to checkout")
    parser.add_argument(
        "--build-dir",
        help="Build directory for LLVM (default: <llvm-path>/build)",
    )
    parser.add_argument(
        "--install-target",
        default="install",
        help="Where to install clang-tidy (default: ./install)",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Never prompt; use safe defaults",
    )


def cmd_prepare(paths: ResolvedPaths, args: argparse.Namespace) -> None:
    check_tools(["git"])
    ensure_llvm_repo(
        paths.llvm_path,
        branch=args.llvm_branch,
        fresh=bool(getattr(args, "fresh", False)),
        non_interactive=args.non_interactive,
    )
    prepare_sources(paths.llvm_path)


def cmd_build(paths: ResolvedPaths, args: argparse.Namespace) -> Path:
    check_tools(["cmake", "ninja", "git", "clang", "clang++"])
    ensure_llvm_repo(
        paths.llvm_path,
        branch=args.llvm_branch,
        fresh=False,
        non_interactive=args.non_interactive,
    )
    prepare_sources(paths.llvm_path)
    configure_cmake(
        paths.build_dir,
        paths.llvm_path,
        paths.llvm_install,
        reconfigure=bool(getattr(args, "reconfigure", False)),
    )
    build_and_install(paths.build_dir)

    print(f"Installing clang-tidy to {paths.install_target}...")
    try:
        installed = install_clang_tidy(paths.install_target, paths.llvm_install)
    except RuntimeError as e:
        sys.exit(f"Error: {e}")
    return installed


def cmd_test(paths: ResolvedPaths) -> None:
    check_tools(["lit"])
    run_lit_tests(paths.llvm_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and test the dollar-macro clang-tidy check")
    add_common_args(parser)
    parser.add_argument("--reconfigure", action="store_true", help="Re-run CMake configuration")
    parser.add_argument("--run-tests", action="store_true", help="Run tests after building")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test prompt after building")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Delete and re-clone the LLVM repo (only safe by default for ./llvm-project)",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("prepare", help="Clone/checkout LLVM, copy the check, and patch sources")
    subparsers.add_parser("build", help="Configure, build, and install clang-tidy")
    subparsers.add_parser("test", help="Run lit tests")
    subparsers.add_parser("all", help="prepare + build + (optional) test")

    args = parser.parse_args()
    if args.command is None:
        args.command = "all"

    paths = resolve_paths(args)

    if args.command == "prepare":
        cmd_prepare(paths, args)
        print("Done preparing sources.")
        return

    if args.command == "build":
        installed = cmd_build(paths, args)
        print(f"Done. clang-tidy: {installed}")
        return

    if args.command == "test":
        cmd_test(paths)
        return

    if args.command == "all":
        cmd_prepare(paths, args)
        installed = cmd_build(paths, args)

        if getattr(args, "run_tests", False):
            cmd_test(paths)
        elif not getattr(args, "skip_tests", False) and not args.non_interactive:
            if prompt("Run tests?", default="no"):
                cmd_test(paths)

        print(f"Done. clang-tidy: {installed}")
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

