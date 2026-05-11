#include <iostream>

// Compliant: macro starts with $
#define $ADD(a, b) ((a) + (b))
#define $MULTIPLY(a, b) ((a) * (b))
#define $MAX(a, b) ((a) > (b) ? (a) : (b))

// Non-compliant: macro doesn't start with $
#define NON_COMPLIANT_MACRO 42
#define INVALID_SUM(x, y) ((x) + (y))

int main() {
    int x = $ADD(5, 3);
    int y = $MULTIPLY(x, 2);
    int z = $MAX(x, y);
    
    int invalid = NON_COMPLIANT_MACRO;
    int sum = INVALID_SUM(10, 20);
    
    std::cout << "x = " << x << std::endl;
    std::cout << "y = " << y << std::endl;
    std::cout << "z = " << z << std::endl;
    std::cout << "invalid = " << invalid << std::endl;
    std::cout << "sum = " << sum << std::endl;
    
    return 0;
}
