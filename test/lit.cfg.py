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
llvm_install = (llvm_path / "install").resolve()

check_clang_tidy = (llvm_path / "clang-tools-extra" / "test" / "clang-tidy" / "check_clang_tidy.py").resolve()
config.substitutions.append(
    ("%check_clang_tidy", "%s %s" % (python_exec, check_clang_tidy))
)

# Add clang-tidy to PATH
clang_tidy_bin = Path(os.environ.get("DOLLAR_MACRO_CLANG_TIDY_BIN", str(llvm_install / "bin"))).resolve()
if clang_tidy_bin.exists():
    config.environment["PATH"] = str(clang_tidy_bin) + os.pathsep + config.environment.get("PATH", "")

