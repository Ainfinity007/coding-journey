class Solution {
public:
    int hammingWeight(int n) {
       double  count = 0;
        for (int i=n;i!=0;i>>=1){
            if ((i & 1) == 1){
                count++;
            }
        }
        return int(count);
    }
};