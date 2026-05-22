using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LCode850 : MonoBehaviour
{
    struct IntervalPoint
    {
        public int value;
        public int idx;
        public bool startOrEnd;
        public IntervalPoint(int value, int idx,bool startOrEnd)
        {
            this.value = value;
            this.idx = idx;
            this.startOrEnd = startOrEnd;
        }
    }
    void QuickSort(List<IntervalPoint> arr, int low, int high, int[][] intervals)
    {

        if (low >= high)
            return;
        int i = low;
        int j = high;
        IntervalPoint temp = arr[i];//基准值
        while (i < j)//从两端向中间扫描,跳出循环时i=j
        {
            while (i < j && LessThan(temp, arr[j], intervals))//从右往左
                j--;
            arr[i] = arr[j];
            while (i < j && LessThan(arr[i], temp, intervals))//从左往右
                i++;
            arr[j] = arr[i];
        }
        arr[i] = temp;// 基准值回归正确位置
        QuickSort(arr, low, i - 1, intervals);
        QuickSort(arr, i + 1, high, intervals);
    }
    bool LessThan(IntervalPoint a, IntervalPoint b, int[][] intervals)
    {
        return a.value - b.value <=0;
    }
    public int MergeV(int[][] intervals ,HashSet<int> idxes)
    {
        List<int[]> newIntervals = new List<int[]>();
        HashSet<int> intervalIdx = new HashSet<int>();
        List<IntervalPoint> points = new List<IntervalPoint>();
        foreach (int idx in idxes)
        {
            int start = intervals[idx][1];
            int end = intervals[idx][3];
            if (start != end)
            {
                points.Add(new IntervalPoint(start, idx, true));
                points.Add(new IntervalPoint(end, idx, false));
            }
        }
        QuickSort(points, 0, points.Count - 1, intervals);
        for (int i= 0; i < points.Count;i++)
        {
            int j = i;
            while (j < points.Count-1 && points[j].value == points[j + 1].value) j++;
            for (int k = i; k <= j; k++)
            {
                if (points[k].startOrEnd)
                {
                    intervalIdx.Add(points[k].idx);
                }
            }
            for (int k = i; k <= j; k++)
            {
                if (!points[k].startOrEnd)
                {
                    intervalIdx.Remove(points[k].idx);
                }
            }
            if (intervalIdx.Count != 1 && j != points.Count-1)
            {
                return -2;
            }
            i = j;
        }
        return points[points.Count - 1].value - points[0].value;
    }
    public bool MergeU(int[][] intervals)
    {
        List<int[]> newIntervals = new List<int[]>();
        HashSet<int> intervalIdx = new HashSet<int>();
        List<IntervalPoint> points = new List<IntervalPoint>();
        for (int i = 0; i < intervals.Length; i++)
        {
            int idx = i;
            int start = intervals[idx][0];
            int end = intervals[idx][2];
            if (start != end)
            {
                points.Add(new IntervalPoint(start, i, true));
                points.Add(new IntervalPoint(end, i, false));
            }
        }
        QuickSort(points, 0, points.Count - 1, intervals);
        int valV = -1;
        int lastValV = -1;
        for (int i = 0; i < points.Count; i++)
        {
            int j = i;
            while (j < points.Count-1 && points[j].value == points[j + 1].value) j++;
            for (int k = i; k <= j; k++)
            {
                if (points[k].startOrEnd)
                {
                    intervalIdx.Add(points[k].idx);
                }
            }
            for (int k = i; k <= j; k++)
            {
                if (!points[k].startOrEnd)
                {
                    intervalIdx.Remove(points[k].idx);
                }
            }
            if (intervalIdx.Count == 0)
            {
                if (j < intervalIdx.Count - 1)
                    return false;
                else
                    return true;
            }
            valV = MergeV(intervals, intervalIdx);
            if (valV == -2)
            {
                return false;
            }
            if (lastValV != -1 && valV != lastValV)
            {
                return false;
            }
         
            lastValV = valV;
           
        }
        return true;
    }
    public bool IsRectangleOver(int[][] rectangles)
    {
       return  MergeU(rectangles);
    }

    //public int MergeIntervalLength(int[][] intervals)
    //{
    //    int[][] mergedIntervals = Merge(intervals);
    //    int length = 0;
    //    for (int i = 0; i < mergedIntervals.Length; i++)
    //    {
    //        length += mergedIntervals[i][1] - mergedIntervals[i][0];
    //    }
    //    return length;
    //}


    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.K))
        {
            int[][] intervals = new int[][]{
            new int[]{ 1, 1, 2, 3 }
            ,new int[]{ 1, 3, 2, 4 }
             ,new int[]{ 3, 1, 4, 2 }
              ,new int[]{ 3, 2, 4, 4 }
        };
            bool merged = IsRectangleOver(intervals);
            Debug.Log(merged);
        }
        

    }
}