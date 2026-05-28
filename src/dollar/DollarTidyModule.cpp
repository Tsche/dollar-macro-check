#include "DollarMacroCheck.h"
#include "clang-tidy/ClangTidyModule.h"

namespace clang::tidy {
namespace dollar {
class DollarModule : public ClangTidyModule {
public:
  void addCheckFactories(ClangTidyCheckFactories &CheckFactories) override {
    CheckFactories.registerCheck<DollarMacroCheck>("dollar-macro");
  }
};
} // namespace dollar

static ClangTidyModuleRegistry::Add<dollar::DollarModule>
    X("dollar-module", "Adds $identifier-related checks.");

// This anchor is used to force the linker to link in the generated object file
// and thus register the module.
// NOLINTNEXTLINE(misc-use-internal-linkage)
volatile int DollarModuleAnchorSource = 0;

} // namespace clang::tidy
