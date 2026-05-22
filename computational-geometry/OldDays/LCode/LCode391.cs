using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LCode391 : MonoBehaviour
{
    class RecPoint
    {
      public  int x, y;
      public  int idx;
        public bool startOrEnd;
    }
    public bool IsRectangleCover(int[][] rectangles)
    {
        int totalRects = rectangles.Length;
        List<RecPoint> recPoints = new List<RecPoint>();
        HashSet<int> CurrentIdxs = new HashSet<int>();
        for (int i = 0; i < totalRects; i++)
        {
            RecPoint recStartPoint = new RecPoint();
            recStartPoint.x = rectangles[i][0];
            recStartPoint.y = rectangles[i][1];
            recStartPoint.idx = i;
            recStartPoint.startOrEnd = true;
            RecPoint recEndPoint = new RecPoint();
            recEndPoint.x = rectangles[i][2];
            recEndPoint.y = rectangles[i][3];
            recEndPoint.idx = i;
            recStartPoint.startOrEnd = false;
            recPoints.Add(recStartPoint);
            recPoints.Add(recEndPoint);
        }
        recPoints.Sort((RecPoint a, RecPoint b) => {return (a.x - b.x); });
        int maxY = 0, minY = 0;
        for (int i = 0; i < recPoints.Count; i++)
        {
            int cur_idx = recPoints[i].idx;
            if (!CurrentIdxs.Contains(cur_idx))
            {
                if (recPoints[i].x > recPoints[i - 1].x)
                {
                    if (recPoints[i].y > maxY || recPoints[i].y < minY) //是否Y坐标有延申?
                    {
                        return false;
                    }
                }
                else  //recPoints[i].x == recPoints[i - 1].x
                {
                    if (recPoints[i].y > maxY)
                    {
                        maxY = recPoints[i].y;
                    }
                    else if (recPoints[i].y < minY)
                    {
                        minY = recPoints[i].y;
                    }
                }
                //Y坐标是否能构成区间?
                CurrentIdxs.Add(cur_idx);
            }
            else
            {
                CurrentIdxs.Remove(cur_idx);
            }
        }
        return false;
    }
    bool JudgelineSegment(int[][] rectangles ,HashSet<int> idXs)
    {
        return false;
    }
    bool JudgelineSegment(int[][] ys)
    {
        return false;
    }
    // Update is called once per frame
    void Update()
    {
        
    }
   
}
