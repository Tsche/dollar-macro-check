# pyright: reportUndefinedVariable=false
# -*- Python -*-

import os
import sys
import shlex
from pathlib import Path
from typing import Any

import lit.formats

from lit.llvm import llvm_config

# Provided by lit at runtime.
config: Any

# Configuration file for the 'lit' test runner.

config.name = "dollar-macro tests"

# testFormat: The test format to use to interpret tests.
# We prefer the lit internal shell which provides a better user experience on
# failures and is faster unless the user explicitly disables it with
# LIT_USE_INTERNAL_SHELL=0 env var.
use_lit_shell = True
lit_shell_env = os.environ.get("LIT_USE_INTERNAL_SHELL")
if lit_shell_env:
    use_lit_shell = lit.util.pythonize_bool(lit_shell_env)

config.test_format = lit.formats.ShTest(not use_lit_shell)

# suffixes: A list of file extensions to treat as test files.
config.suffixes = [
    ".cpp",
]

config.excludes = []

# test_source_root: The root path where tests are located.
config.test_source_root = str(Path(__file__).parent.resolve())

# test_exec_root: The root path where tests should be run.
config.test_exec_root = str((Path(config.test_source_root) / "build").resolve())


python_exec = shlex.quote(sys.executable)
config.substitutions.append(("%python", python_exec))

test_root = Path(config.test_source_root).resolve()

llvm_path = Path(os.environ.get("DOLLAR_MACRO_LLVM_PATH", str(test_root.parent / "llvm-project"))).resolve()
plugin_install = test_root.parent / "install"

clang_tidy_bin = Path(os.environ.get("DOLLAR_MACRO_CLANG_TIDY_BIN", str(llvm_path / "install" / "bin"))).resolve()
if not (clang_tidy_bin / "clang-tidy").exists():
    clang_tidy_bin = (llvm_path / "build" / "bin").resolve()
check_clang_tidy = (llvm_path / "clang-tools-extra" / "test" / "clang-tidy" / "check_clang_tidy.py").resolve()

path = str(clang_tidy_bin) + os.pathsep + config.environment.get("PATH", "")
if clang_tidy_bin.exists():
    config.environment["PATH"] = str(clang_tidy_bin) + os.pathsep + config.environment.get("PATH", "")

config.substitutions.append(
    ("%check_clang_tidy", 
        f"{python_exec} {check_clang_tidy} --load={plugin_install / 'lib' / 'dollar_macros.so'}")
)

