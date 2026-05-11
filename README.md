

# Dollar-Macro Check

A clang-tidy check that enforces `$macros` to visually separate them from regular identifiers.


## Build Requirements

- CMake
- Ninja
- Clang/Clang++
- Python

## Building

### Quick Start

```bash
python make.py
```

This will:
1. Clone the LLVM project (if not present)
2. Apply necessary patches
3. Configure and build clang-tidy with the dollar-macro check
4. Install clang-tidy to `./install/bin/clang-tidy` (or `--install-target <prefix>`)

### Build Script Options

```bash
python make.py --llvm-branch llvmorg-22.1.5
python make.py --run-tests

python make.py prepare --llvm-path /path/to/llvm-project
python make.py build --llvm-path /path/to/llvm-project
python make.py test --llvm-path /path/to/llvm-project
```

### Manual Build

If you prefer to build manually, follow these steps:

1. Clone LLVM:
   ```bash
   git clone https://github.com/llvm/llvm-project llvm-project
   cd llvm-project
   ```

2. Copy the extension:
   ```bash
   cp -r ../src/dollar clang-tools-extra/clang-tidy/dollar
   ```

3. Patch clang-tidy sources
In `clang-tools-extra/clang-tidy/CMakeLists.txt` find the line `set(ALL_CLANG_TIDY_CHECKS)` and apply the following patch:
```diff
+add_subdirectory(dollar)
set(ALL_CLANG_TIDY_CHECKS)
+  clangTidyDollarModule
```

In `clang-tools-extra/clang-tidy/ClangTidyForceLinker.h` find the line `} // namespace clang::tidy` and insert the following code immediately prior to it
```cpp
// This anchor is used to force the linker to link the DollarModule.
extern volatile int DollarModuleAnchorSource;
[[maybe_unused]] static int DollarModuleAnchorDestination =
    DollarModuleAnchorSource;

```

4. Configure and build:
   ```bash
   cmake -S llvm -B build -G Ninja \
     -DCMAKE_BUILD_TYPE=Release \
     -DCMAKE_C_COMPILER=clang \
     -DCMAKE_CXX_COMPILER=clang++ \
     -DLLVM_USE_LINKER=lld \
     -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" \
     -DLLVM_TARGETS_TO_BUILD="host" \
     -DCMAKE_INSTALL_PREFIX=./install \
     -DBUILD_SHARED_LIBS=OFF
   
   ninja -C build install
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

Use `ignore-prefixes` to permit additional (comma-separated) prefixes. For example:
- `SOMELIB_` - Allow macros that already use the `SOMELIB_` prefix
- `BOOST_` - Allow macros that use Boost's `BOOST_` prefix

The check will suggest fixes for non-conforming macros. Reserved identifiers and system header macros are automatically excluded.

See [example/.clang-tidy](example/.clang-tidy) for a complete configuration example.

### Command Line

Run clang-tidy directly with the check:

```bash
./install/bin/clang-tidy -checks='dollar-macro' file.cpp
```

### Testing

The `test/` directory contains test cases demonstrating the check's behavior:

```bash
python make.py test
```

Or manually (you might need to add the clang-tidy install directory to PATH):

```bash
lit test/
```
