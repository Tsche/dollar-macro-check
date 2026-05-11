// RUN: %check_clang_tidy %s dollar-macro %t -- -config="{CheckOptions: [{key: dollar-macro.ignore-prefixes, value: 'MY_,YOUR_'}]}"

// Compliant: starts with $
#define $COMPLIANT_MACRO 42

// Compliant: starts with allowed prefix MY_
#define MY_ALLOWED_MACRO 42

// Compliant: starts with allowed prefix YOUR_
#define YOUR_ALLOWED_MACRO 42

// Non-compliant: doesn't start with $ or allowed prefixes
#define NON_COMPLIANT_MACRO 42
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'NON_COMPLIANT_MACRO' should use $ prefix (e.g., $NON_COMPLIANT_MACRO) [dollar-macro]

// Non-compliant: starts with different prefix
#define OTHER_MACRO 42
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'OTHER_MACRO' should use $ prefix (e.g., $OTHER_MACRO) [dollar-macro]
