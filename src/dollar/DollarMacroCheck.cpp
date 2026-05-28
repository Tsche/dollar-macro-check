#include "DollarMacroCheck.h"
#include <clang/Basic/Diagnostic.h>
#include <clang/Basic/DiagnosticIDs.h>
#include <clang/Basic/IdentifierTable.h>
#include <clang/Lex/MacroInfo.h>
#include <clang/Lex/PPCallbacks.h>
#include <clang/Lex/Preprocessor.h>
#include <llvm/ADT/STLExtras.h>
#include <llvm/ADT/StringRef.h>

namespace clang::tidy::dollar {

class MacroDollarIdentPPCallbacks : public PPCallbacks {
public:
  MacroDollarIdentPPCallbacks(DollarMacroCheck *Check, const Preprocessor *PP,
                              const std::string &AllowedPrefixes)
      : Check(Check), PP(PP), AllowedPrefixes(AllowedPrefixes) {
    llvm::SmallVector<StringRef, 8> Prefixes;
    StringRef(AllowedPrefixes).split(Prefixes, ",");
    for (const auto &Prefix : Prefixes)
      AllowedPrefixList.push_back(Prefix.trim());
  }

  void MacroDefined(const Token &MacroNameTok,
                    const MacroDirective *MD) override {
    // Skip predefined macros
    if (MD->getMacroInfo()->isBuiltinMacro())
      return;

    // Skip macros from system headers
    const SourceManager &SM = PP->getSourceManager();
    if (SM.isInSystemHeader(MacroNameTok.getLocation()))
      return;

    auto *Identifier = MacroNameTok.getIdentifierInfo();
    StringRef MacroName = Identifier->getName();

    // Skip reserved identifiers
    if (Identifier->isReserved(PP->getLangOpts()) !=
        ReservedIdentifierStatus::NotReserved)
      return;

    // Check if macro starts with $ or is in allowed prefix list
    if (MacroName.starts_with("$") || isAllowedPrefix(MacroName))
      return;

    // Emit a diagnostic
    SourceRange MacroRange(
        MacroNameTok.getLocation(),
        MacroNameTok.getLocation().getLocWithOffset(MacroName.size() - 1));

    Check->diag(MacroNameTok.getLocation(),
                "macro '%0' should use $ prefix (e.g., $%0)")
        << MacroName
        << FixItHint::CreateReplacement(MacroRange, "$" + MacroName.str());
  }

private:
  DollarMacroCheck *Check;
  const Preprocessor *PP;
  StringRef AllowedPrefixes;
  llvm::SmallVector<StringRef, 8> AllowedPrefixList;

  bool isAllowedPrefix(StringRef MacroName) const {
    return llvm::any_of(AllowedPrefixList, [=](StringRef Prefix) {
      return !Prefix.empty() && MacroName.starts_with(Prefix);
    });
  }
};

void DollarMacroCheck::registerPPCallbacks(const SourceManager &SM,
                                           Preprocessor *PP,
                                           Preprocessor *ModuleExpanderPP) {
  PP->addPPCallbacks(
      std::make_unique<MacroDollarIdentPPCallbacks>(this, PP, AllowedPrefixes));
}

void DollarMacroCheck::storeOptions(ClangTidyOptions::OptionMap &Options) {
  ClangTidyCheck::storeOptions(Options);
}

} // namespace clang::tidy::dollar
