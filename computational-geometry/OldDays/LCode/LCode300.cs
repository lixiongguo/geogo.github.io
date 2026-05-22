using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Assets.Scripts.Test
{
    /*
     * 给定一个无序的整数数组，找到其中最长上升子序列的长度。

示例:

输入: [10,9,2,5,3,7,101,18]
输出: 4 
解释: 最长的上升子序列是 [2,3,7,101]，它的长度是 4。

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/longest-increasing-subsequence
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。
    **
    * 
    * 
    * */
    class LCode300
    {
        public int LengthOfLIS(int[] nums)
        {
            if (nums == null || nums.Length ==0) return 0;
            int[] s = new int[nums.Length];
            s[0] = 1;
            for (int i = 1; i < nums.Length; i++)
            {
                int tmp = 0;
                for (int j = 0; j < i; j++)
                {
                    if (nums[i] >= nums[j] && s[j] >tmp)
                    {
                        tmp = s[j];
                    }
                }
                s[i] = tmp+1;
            }
            int maxlength = 0;
            for (int i = 0; i < nums.Length; i++)
            {
                if (s[i] > maxlength)
                {
                    maxlength = s[i];
                }
            }
            return s[nums.Length-1];
        }
    }
}
