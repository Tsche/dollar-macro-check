#pragma once
#include <clang-tidy/ClangTidyCheck.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>

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

  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;
  void registerPPCallbacks(const SourceManager &SM, Preprocessor *PP,
                           Preprocessor *ModuleExpanderPP) override;
  void storeOptions(ClangTidyOptions::OptionMap &Options) override;

private:
  std::string AllowedPrefixes;
};

} // namespace clang::tidy::dollar
