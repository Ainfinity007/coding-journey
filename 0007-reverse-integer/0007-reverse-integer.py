class Solution(object):
    def reverse(self, x):
        sign = -1 if x < 0 else 1
        x_abs = abs(x)
        reversed_num = 0
        
        while x_abs > 0:
            reversed_num = reversed_num * 10 + x_abs % 10
            x_abs //= 10
        
        reversed_num *= sign
        
        
        if reversed_num < -2**31 or reversed_num > 2**31 - 1:
            return 0
        
        return reversed_num