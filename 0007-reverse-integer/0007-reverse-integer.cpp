#include <climits> // For INT_MAX and INT_MIN

class Solution {
public:
    int reverse(int x) {
        int reversed_num = 0;
        
        while (x != 0) {
            int rem = x % 10;
            x /= 10;
            
            
            if (reversed_num > INT_MAX / 10 || (reversed_num == INT_MAX / 10 && rem > 7)) {
                return 0;
            }
            if (reversed_num < INT_MIN / 10 || (reversed_num == INT_MIN / 10 && rem < -8)) {
                return 0;
            }
            
            reversed_num = reversed_num * 10 + rem;
        }
        
        return reversed_num;
    }
};