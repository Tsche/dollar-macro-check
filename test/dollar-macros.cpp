// RUN: %check_clang_tidy %s dollar-macro %t --

#define NON_COMPLIANT_MACRO 42
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'NON_COMPLIANT_MACRO' should use $ prefix (e.g., $NON_COMPLIANT_MACRO) [dollar-macro]

#define NON_COMPLIANT_FNC_MACRO() 42
// CHECK-MESSAGES: :[[@LINE-1]]:9: warning: macro 'NON_COMPLIANT_FNC_MACRO' should use $ prefix (e.g., $NON_COMPLIANT_FNC_MACRO) [dollar-macro]

#define $COMPLIANT_MACRO 42
#define $COMPLIANT_FNC_MACRO() 42

#define _RESERVED_MACRO 1
#define __reserved_macro 1