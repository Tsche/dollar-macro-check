

# Dollar-Macro Check

A clang-tidy check that enforces `$macros` to visually separate them from regular identifiers.

With this check enabled, you will get warnings if you try to define a macro without prefixing its name with a `$`. Likewise, you will get a warning if you use a regular identifier that starts with `$`.

## Build Requirements

- CMake 3.20+
- Ninja
- Clang/Clang++
- Pre-built LLVM and Clang

## Building

### Quick Start with Build Script

```bash
python build-plugin.py
```

This configures and builds the plugin, installing it to `./install/lib/dollar_macros.so`.

**Note:** Requires LLVM to be pre-built at `./llvm-project/build/` (or specify with `--llvm-build`).

### Using CMake Directly

```bash
# Configure
cmake -B build -S . \
  -DLLVM_SRC_DIR=./llvm-project \
  -DLLVM_BUILD_DIR=./llvm-project/build \
  -DCMAKE_INSTALL_PREFIX=./install

# Build
ninja -C build

# Install
ninja -C build install
```

### Custom Paths

```bash
python build-plugin.py \
  --llvm-src /path/to/llvm-project \
  --llvm-build /path/to/llvm-project/build \
  --install-dir ./install
```

## Usage

### Configuration

Add the check to your `.clang-tidy` configuration:

```yaml
Checks: 'dollar-macro'
CheckOptions:
  - key: dollar-macro.ignore-prefixes
    value: 'SOMELIB_,BOOST_'
```

Use `ignore-prefixes` to permit additional (comma-separated) prefixes:
- `SOMELIB_` - Allow macros that use the `SOMELIB_` prefix
- `BOOST_` - Allow macros that use Boost's `BOOST_` prefix

Reserved identifiers and system header macros are automatically excluded.

See [example/.clang-tidy](example/.clang-tidy) for a complete configuration example.

### Command Line

Run clang-tidy with the plugin:

```bash
clang-tidy --load=/path/to/dollar_macros.so -checks='dollar-macro' file.cpp
```

### Testing

The `test/` directory contains test cases demonstrating the check's behavior:

```bash
lit test/
```
