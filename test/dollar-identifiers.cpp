// RUN: %check_clang_tidy %s dollar-macro %t --

int foo = 3;  // ok
int $foo = 4; // reserved for macros
// CHECK-MESSAGES: :[[@LINE-1]]:5: warning: identifier '$foo' starts with '$', which is reserved for macros [dollar-macro]

void $bar() {}
// CHECK-MESSAGES: :[[@LINE-1]]:6: warning: identifier '$bar' starts with '$', which is reserved for macros [dollar-macro]

struct $baz {
  int $zab;
};
// CHECK-MESSAGES: :[[@LINE-3]]:8: warning: identifier '$baz' starts with '$', which is reserved for macros [dollar-macro]
// CHECK-MESSAGES: :[[@LINE-3]]:7: warning: identifier '$zab' starts with '$', which is reserved for macros [dollar-macro]

enum class $zoinks { $boings };
// CHECK-MESSAGES: :[[@LINE-1]]:12: warning: identifier '$zoinks' starts with '$', which is reserved for macros [dollar-macro]
// CHECK-MESSAGES: :[[@LINE-2]]:22: warning: identifier '$boings' starts with '$', which is reserved for macros [dollar-macro]
