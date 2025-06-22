class Solution {
public:
    int subtractProductAndSum(int n) {
        int a = n;
        double product = 1;
        double sum = 0 ;
        int i;
        while (a!=0){
            i = a % 10;
            product = product * i;
            sum  = sum + i;
            a = a / 10;

        }
        int result = product - sum;
        return int(result);
        
    }
};