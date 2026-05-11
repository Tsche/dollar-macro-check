#pragma once
#include "../ClangTidyCheck.h"

namespace clang::tidy::dollar {

/// FIXME: Write a short description.
///
/// For the user-facing documentation see:
/// https://clang.llvm.org/extra/clang-tidy/checks/readability/require-dollar-macros.html
class DollarMacroCheck : public ClangTidyCheck {
public:
  DollarMacroCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context),
        AllowedPrefixes(Options.get("ignore-prefixes", "")) {}

  bool isLanguageVersionSupported(const LangOptions &LangOpts) const override {
    return LangOpts.CPlusPlus;
  }

  void registerPPCallbacks(const SourceManager &SM, Preprocessor *PP,
                           Preprocessor *ModuleExpanderPP) override;
  void storeOptions(ClangTidyOptions::OptionMap &Options) override;

private:
  std::string AllowedPrefixes;
};

} // namespace clang::tidy::dollar
