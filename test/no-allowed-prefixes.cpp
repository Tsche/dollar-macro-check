// RUN: %check_clang_tidy %s dollar-macro %t -- -config="{CheckOptions: [{key: dollar-macro.ignore-prefixes, value: ''}]}"

// Compliant: starts with $
#define $COMPLIANT_MACRO 42
#define $ANOTHER_COMPLIANT 100

// Non-compliant: starts with any other prefix (no other prefixes allowed)
#define MY_MACRO 42
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'MY_MACRO' should use $ prefix (e.g., $MY_MACRO) [dollar-macro]

#define PREFIX_VALUE 99
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'PREFIX_VALUE' should use $ prefix (e.g., $PREFIX_VALUE) [dollar-macro]

#define SIMPLE_MACRO 1
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'SIMPLE_MACRO' should use $ prefix (e.g., $SIMPLE_MACRO) [dollar-macro]
