using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

namespace Assets.Scripts.Test
{
    class LCode179 :MonoBehaviour
    {
        public class LinkNode
        {
           public byte val;
           public LinkNode next;
        }
       
         bool DataLessThan(int a, int b)
        {
            LinkNode aHead = null;
            LinkNode bHead = null;
            int totalLength = 0;
            if (a == 0)
            {
                return true;
            }
            if (b == 0)
            {
                return false;
            }

            var tmpA = a;
            while (tmpA > 0)
            {
                var tmpNode = new LinkNode();
                tmpNode.val = (byte)(tmpA % 10);
                tmpNode.next = aHead;
                aHead = tmpNode;
                tmpA = tmpA / 10;
                totalLength++;
            }
            var tmpB = b;
            while (tmpB > 0)
            {
                var tmpNode = new LinkNode();
                tmpNode.val = (byte)(tmpB % 10);
                tmpNode.next = bHead;
                bHead = tmpNode;
                tmpB = tmpB / 10;
                totalLength++;
            }

            LinkNode aCurrent = aHead;
            LinkNode bCurrent = bHead;
            int cnt = 0;
            while (true)
            {

                if (aCurrent.val < bCurrent.val)
                {
                    return true;
                }
                else if (aCurrent.val > bCurrent.val)
                {
                    return false;
                }
                cnt++;
                if (cnt >= totalLength)
                {
                    return true;
                }
                if (aCurrent.next == null)
                {
                    aCurrent.next = bHead;
                    aCurrent = bHead;
                }
                else
                {
                    aCurrent = aCurrent.next;
                }
                if (bCurrent.next == null)
                {
                    bCurrent.next = aHead;
                    bCurrent = aHead;
                }
                else
                {
                    bCurrent = bCurrent.next;
                }
            }

            return true;
        }


        public  int[] QuickSort(int[] arr, int low, int high)
        {
           
            if (low >= high)
                return arr;
            int i = low;
            int j = high;
            int temp = arr[i];//基准值
            while (i < j)//从两端向中间扫描,跳出循环时i=j
            {
                //while (i < j && temp <= arr[j])//从右往左
                //    j--;
                //arr[i] = arr[j];
                //while (i < j && arr[i] <= temp)//从左往右
                //    i++;
                //arr[j] = arr[i];
                while (i < j && DataLessThan(temp, arr[j]))//从右往左
                    j--;
                arr[i] = arr[j];
                while (i < j && DataLessThan(arr[i], temp))//从左往右
                    i++;
                arr[j] = arr[i];
            }
            arr[i] = temp;// 基准值回归正确位置
            QuickSort(arr, low, i - 1);
            QuickSort(arr, i + 1, high);
            return arr;
        }
        bool CheckAllZero(int[] nums)
        {
            for (int i = 0; i < nums.Length; i++)
            {
                if (nums[i] != 0)
                {
                    return false;
                }
            }
            return true;
        }
        public string LargestNumber(int[] nums)
        {
            if (CheckAllZero(nums))
            {
                return "0";
            }
            QuickSort(nums,0, nums.Length-1);
            StringBuilder stringBuilder = new StringBuilder();
            for (int j = nums.Length - 1; j >= 0; j--)
            {
                stringBuilder.Append(nums[j]);
            }
            return stringBuilder.ToString();
        }
        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.M))
            {
                int[] testArr = new int[] { 0,0 };
                Debug.Log(LargestNumber(testArr));
            }
        }
    }
   
}
