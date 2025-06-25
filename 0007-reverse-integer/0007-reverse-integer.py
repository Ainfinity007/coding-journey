class Solution:
    def reverse(self, x: int) -> int:
        neg = 0
        if x < 0:
            neg = 1
        rev = 0
        x = abs(x)

        while (x!=0):
            if rev > ((2**31-1)//10) or rev < ((2**(-31))//10):
                return 0
            digit = x % 10
            rev = rev * 10 + digit
            x = x // 10
        if neg == 1 :
            rev = -rev
        return rev
        