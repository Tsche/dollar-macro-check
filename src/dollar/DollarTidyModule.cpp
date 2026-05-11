#include "../ClangTidy.h"
#include "../ClangTidyModule.h"
#include "DollarMacroCheck.h"

namespace clang::tidy {
namespace dollar {
namespace {

class DollarModule : public ClangTidyModule {
public:
  void addCheckFactories(ClangTidyCheckFactories &CheckFactories) override {
    CheckFactories.registerCheck<DollarMacroCheck>("dollar-macro");
  }
};

} // namespace

// Register the DollarModule using this statically initialized variable.
static ClangTidyModuleRegistry::Add<DollarModule>
    X("dollar-module", "Adds $identifier-related checks.");

} // namespace dollar

// This anchor is used to force the linker to link in the generated object file
// and thus register the DollarModule.
// NOLINTNEXTLINE(misc-use-internal-linkage)
volatile int DollarModuleAnchorSource = 0;

} // namespace clang::tidy
