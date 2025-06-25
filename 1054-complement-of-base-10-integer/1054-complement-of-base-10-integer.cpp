#include <bitset>
#include <string>
#include <algorithm>
#include <cmath>

using namespace std;

class Solution {
public:
    int bitwiseComplement(int n) {
        // Handle edge case: n = 0
        if (n == 0) return 1;
        
        string bin = "";
        int original_n = n;  // Keep original for bit counting
        
        // Extract and flip bits
        while (n != 0) {
            if ((n & 1) == 1) {
                bin.push_back('0');  // 1 becomes 0
            } else {
                bin.push_back('1');  // 0 becomes 1
            }
            n = n >> 1;
        }
        
        reverse(bin.begin(), bin.end());
        
        // More efficient conversion without pow()
        int result = 0;
        for (char c : bin) {
            result = result * 2 + (c - '0');
        }
        
        return result;
    }
};