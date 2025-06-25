class Solution:
    def findComplement(self, num: int) -> int:
        m = num
        mask = 0
        if num == 0:
            return 1
        while m != 0:
            mask = mask << 1 | 1
            m = m >> 1
        ans = (~num) & mask
        return ans



        