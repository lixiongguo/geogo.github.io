using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LeetCode46 : MonoBehaviour
{

    //public IList<IList<int>> Permute(int[] nums)
    //{
    //    IList<IList<int>> list = new List<IList<int>>();
    //    int tail = nums.Length - 1;
    //    for (int i = 0; i < tail; i++)
    //    {
    //        Swap(nums, i, tail);
    //        int tailNum = nums[tail];
    //        DoPermute(nums,nums.Length-1 ,list, tailNum);
    //        for (int j = 0; j < list.Count; j++)
    //        {
    //            list[i].Add(tailNum);
    //        }
    //    }
    //  //  list.Add(subList);
    //    return list;
    //}
    //void Swap(int[] nums, int i, int j)
    //{
    //    if (i == j) return;
    //    var tmp = nums[i];
    //    nums[i] = nums[j];
    //    nums[j] = tmp;
    //}
    //public void DoPermute(int[] nums, int length, IList<IList<int>> list,int lastNum)
    //{
    //    if (length == 0)
    //    {
    //        IList<int> subList = new List<int>();
    //        subList.Add(lastNum);
    //        list.Add(subList);
    //    }
    //    else
    //    {
    //        int tail = length - 1;
    //        for (int i = 0; i < tail; i++)
    //        {
    //            Swap(nums, i, tail);
    //            int tailNum = nums[tail];
    //            IList<IList<int>> childlist = DoPermute(nums, tail, list, tailNum);
    //            for (int k = 0; k < childlist.Count; k++)
    //            {
    //                childlist[k];
    //            }
    //            list.Add(childlist);
    //            for (int j = 0; j < list.Count; j++)
    //            {
    //                list[i].Add(lastNum);
    //            }
    //        }
    //    }
    //}

    //// Update is called once per frame
    //void Update()
    //{
        
    //}
}
