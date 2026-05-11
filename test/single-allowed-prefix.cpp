// RUN: %check_clang_tidy %s dollar-macro %t -- -config="{CheckOptions: [{key: dollar-macro.ignore-prefixes, value: 'TEST_'}]}"

// Compliant: starts with $
#define $COMPLIANT_MACRO 42

// Compliant: starts with allowed prefix TEST_
#define TEST_CASE_NAME 100
#define TEST_VALUE_MAX 999

// Non-compliant: starts with different prefix
#define MY_MACRO 42
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'MY_MACRO' should use $ prefix (e.g., $MY_MACRO) [dollar-macro]

#define DEBUG_FLAG 1
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'DEBUG_FLAG' should use $ prefix (e.g., $DEBUG_FLAG) [dollar-macro]
