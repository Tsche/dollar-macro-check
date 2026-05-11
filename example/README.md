# Dollar-Macro Check Demo Project

This is a simple CMake project demonstrating the `dollar-macro` clang-tidy check.

## Overview

The `dollar-macro` check verifies that all user-defined macros are prefixed with a `$` symbol. This helps distinguish macros from regular code and follows a specific naming convention.

## Building

Make sure the custom clang-tidy install location is in your PATH.

```bash
mkdir build
cd build
cmake ..
make
```

## Running clang-tidy

To run clang-tidy with the dollar-macro check:

```bash
clang-tidy src/main.cpp -- -std=c++17
```

Or with the custom clang-tidy that includes the check:

```bash
/path/to/custom/clang-tidy src/main.cpp
```

## Expected Results

The `src/main.cpp` file contains:

- **Compliant macros**: `$ADD`, `$MULTIPLY`, `$MAX` - these start with `$` and will pass the check
- **Non-compliant macros**: `NON_COMPLIANT_MACRO`, `INVALID_SUM` - these don't start with `$` and will trigger warnings

## Configuration

The `.clang-tidy` file in this directory is configured to:
- Enable only the `dollar-macro` check
- Apply to all header files and source files
- Treat warnings as regular warnings (not errors)
