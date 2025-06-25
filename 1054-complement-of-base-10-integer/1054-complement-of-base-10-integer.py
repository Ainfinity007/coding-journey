class Solution:
    def bitwiseComplement(self, n: int) -> int:
        mask = 0
        m=n
        if n==0:
            return 1
        while m!=0:
            mask = mask << 1 | 1
            m = m >> 1
        ans = (~n) & mask
        return ans
        