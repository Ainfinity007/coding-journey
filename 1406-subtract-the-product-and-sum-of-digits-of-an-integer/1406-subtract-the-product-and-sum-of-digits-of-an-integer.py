class Solution:
    def subtractProductAndSum(self, n: int) -> int:
        a = n
        prod = 1
        sum = 0

        while (a!=0):
            i = a % 10
            
            prod = prod * i
            sum = sum + i
            a = a // 10
        res = prod - sum
        return int(res)
        
        