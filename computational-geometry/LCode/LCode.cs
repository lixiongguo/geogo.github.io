using System.Collections;
using System.Collections.Generic;
using UnityEngine;

 struct Point
    {
       public int X;
       public int Y;
        public Point(int X, int Y)
        {
            this.X = X;
            this.Y = Y;
        }
    }
    struct vector
    {
        public int x;
        public int y;
    }
//测试用例
//输入：
//[[3,0],[4,0],[5,0],[6,1],[7,2],[7,3],[7,4],[6,5],[5,5],[4,5],[3,5],[2,5],[1,4],[1,3],[1,2],[2,1],[4,2],[0,3]]
//输出：
//[[3,0],[4,0],[5,0],[6,1],[7,2],[7,3],[7,4],[6,5],[5,5],[4,5],[3,5],[2,5],[1,4],[1,3],[1,2],[2,1],[0,3]]
//预期：
//[[7,4],[5,0],[7,3],[2,1],[5,5],[4,5],[3,5],[7,2],[1,2],[1,4],[4,0],[2,5],[6,1],[6,5],[0,3],[3,0]]
    private List<Point> calcConvexHull(List<Point> list)
    {
        List<Point> resPoint = new List<Point>();
        //查找最小坐标点
        int minIndex = 0;
        for (int i = 1; i < list.Count; i++)
        {
            if (list[i].Y < list[minIndex].Y)
            {
                minIndex = i;
            }
        }
        Point minPoint = list[minIndex];
        resPoint.Add(list[minIndex]);
        list.RemoveAt(minIndex);
        //坐标点排序
        list.Sort(
            delegate (Point p1, Point p2)
            {
                vector baseVec;
                baseVec.x = 1;
                baseVec.y = 0;

                vector p1Vec;
                p1Vec.x = p1.X - minPoint.X;
                p1Vec.y = p1.Y - minPoint.Y;

                vector p2Vec;
                p2Vec.x = p2.X - minPoint.X;
                p2Vec.y = p2.Y - minPoint.Y;

                double up1 = p1Vec.x * baseVec.x;
                double down1 = Math.Sqrt(p1Vec.x * p1Vec.x + p1Vec.y * p1Vec.y);

                double up2 = p2Vec.x * baseVec.x;
                double down2 = Math.Sqrt(p2Vec.x * p2Vec.x + p2Vec.y * p2Vec.y);


                double cosP1 = up1 / down1;
                double cosP2 = up2 / down2;

                if (cosP1 > cosP2)
                {
                    return -1;
                }
                else
                {
                    return 1;
                }
            }
            );
        resPoint.Add(list[0]);
        resPoint.Add(list[1]);
        for (int i = 2; i < list.Count; i++)
        {
            Point basePt = resPoint[resPoint.Count - 2];
            vector v1;
            v1.x = list[i - 1].X - basePt.X;
            v1.y = list[i - 1].Y - basePt.Y;

            vector v2;
            v2.x = list[i].X - basePt.X;
            v2.y = list[i].Y - basePt.Y;

            if (v1.x * v2.y - v1.y * v2.x < 0)
            {
                resPoint.RemoveAt(resPoint.Count - 1);
                while (true)
                {
                    Point basePt2 = resPoint[resPoint.Count - 2];
                    vector v12;
                    v12.x = resPoint[resPoint.Count - 1].X - basePt2.X;
                    v12.y = resPoint[resPoint.Count - 1].Y - basePt2.Y;
                    vector v22;
                    v22.x = list[i].X - basePt2.X;
                    v22.y = list[i].Y - basePt2.Y;
                    if (v12.x * v22.y - v12.y * v22.x < 0)
                    {
                        resPoint.RemoveAt(resPoint.Count - 1);
                    }
                    else
                    {
                        break;
                    }
                }
                resPoint.Add(list[i]);
            }
            else
            {
                resPoint.Add(list[i]);
            }
        }
        return resPoint;
    }
    public int[][] OuterTrees(int[][] points)
    {
        List<Point> tempPoints = new List<Point>();
        for (int i = 0; i < points.Length; i++)
        {
            Point point = new Point(points[i][0], points[i][1]);
            tempPoints.Add(point);
        }
        List<Point> resPoints = calcConvexHull(tempPoints);
        int[][] outPoints = new int[resPoints.Count][];
        for (int i = 0; i < resPoints.Count; i++)
        {
            int[] point = new int[2];
            point[0] = resPoints[i].X;
            point[1] = resPoints[i].Y;
            outPoints[i] = point;
        }
        return outPoints;
    }
//输入：nums = [1,2,3,3,4,4,5,6], k = 4
//输出：true
//解释：数组可以分成[1, 2, 3, 4] 和[3, 4, 5, 6]。
//LCode1296


public bool IsPossibleDivide(int[] nums, int k)
{

}











public class LCode : MonoBehaviour
{


    //public double minAreaFreeRect(int[][] points)
    //{
    //    int N = points.length;
    //    Point[] A = new Point[N];
    //    for (int i = 0; i < N; ++i)
    //        A[i] = new Point(points[i][0], points[i][1]);

    //    Map<Integer, Map<Point, List<Point>>> seen = new HashMap();
    //    for (int i = 0; i < N; ++i)
    //        for (int j = i + 1; j < N; ++j)
    //        {
    //            // center is twice actual to keep integer precision
    //            Point center = new Point(A[i].x + A[j].x, A[i].y + A[j].y);

    //            int r2 = (A[i].x - A[j].x) * (A[i].x - A[j].x) + (A[i].y - A[j].y) * (A[i].y - A[j].y);
    //            if (!seen.containsKey(r2))
    //                seen.put(r2, new HashMap<Point, List<Point>>());
    //            if (!seen.get(r2).containsKey(center))
    //                seen.get(r2).put(center, new ArrayList<Point>());
    //            seen.get(r2).get(center).add(A[i]);
    //        }

    //    double ans = Double.MAX_VALUE;
    //    for (Map<Point, List<Point>> info: seen.values())
    //    {
    //        for (Point center: info.keySet())
    //        {  // center is twice actual
    //            List<Point> candidates = info.get(center);
    //            int clen = candidates.size();
    //            for (int i = 0; i < clen; ++i)
    //                for (int j = i + 1; j < clen; ++j)
    //                {
    //                    Point P = candidates.get(i);
    //                    Point Q = candidates.get(j);
    //                    Point Q2 = new Point(center);
    //                    Q2.translate(-Q.x, -Q.y);
    //                    double area = P.distance(Q) * P.distance(Q2);
    //                    if (area < ans)
    //                        ans = area;
    //                }
    //        }
    //    }

    //    return ans < Double.MAX_VALUE ? ans : 0;
    //}
}








//bool isPossibleDivide(vector<int>& nums, int k)
//{
//    map<int, int> s;
//    for (int num: nums)
//    {
//        ++s[num];
//    }
//    for (auto iter = s.begin(); iter != s.end(); ++iter)
//    {
//        int num = iter->first;
//        int occ = iter->second;
//        if (occ > 0)
//        {
//            auto it = next(iter);
//            for (auto i = 1; i < k; ++i, ++it)
//            {
//                if (it != s.end() && it->first == num + i && it->second >= occ)
//                {
//                    it->second -= occ;
//                }
//                else
//                {
//                    return false;
//                }
//            }
//        }
//    }
//    return true;
//}











//LCode1296
public bool ISDividible(int[] nums, int k)
{
    return false;
}







//LCode890
//输入：words = ["abc","deq","mee","aqq","dkd","ccc"], pattern = "abb"
//输出：["mee","aqq"]
//解释：
//"mee" 与模式匹配，因为存在排列 {a -> m, b -> e, ...}。
//"ccc" 与模式不匹配，因为 {a -> c, b -> c, ...} 不是排列。
//因为 a 和 b 映射到同一个字母。
public IList<string> FindAndReplacePattern(string[] words, string pattern)
    {
        IList<string> result_list = new List<string>();
        Dictionary<char, char> map = new Dictionary<char, char>();
        int charIdx = 0;
        for (int i = 0; i < pattern.Length; i++)
        {
            if (!map.ContainsKey(pattern[i]))
            {
                char std_char = (char)(charIdx + 'a');
                map[std_char] = pattern[i];
                charIdx++;
            }
        }
        foreach (string word in words)
        {
            for (int i = 0; i < word.Length; i++)
            {

            }
        }
        return null;
    }

    //tasks = [[1,2],[2,4],[4,8]]
    //输出：8
    //输入：tasks = [[1,3],[2,4],[10,11],[10,12],[8,9]]
    //输出：32
    //LCode1665
    public int MinimumEffort(int[][] tasks)
    {

    }


//输入: "abcabcbb"
//输出: 3 

//输入: "bbbbb"
//输出: 1

//输入: "pwwkew"
//输出: 3
//Offer48
public int LengthOfLongestSubstring(string s)
{
}

//nums = [1,3,-1,-3,5,3,6,7], k = 3
//[3,3,5,5,6,7]
public int[] MaxSlidingWindow(int[] nums, int k)
    {

    }
//给你一个仅由大写英文字母组成的字符串，你可以将任意位置上的字符替换成另外的字符，总共可最多替换 k次。在执行上述操作后，找到包含重复字母的最长子串的长度。

//注意：字符串长度 和 k 不会超过104。



//示例 1：

//输入：s = "ABAB", k = 2
//输出：4
//解释：用两个'A'替换为两个'B',反之亦然。
//示例 2：

//输入：s = "AABABBA", k = 1
//输出：4
//解释：
//将中间的一个'A'替换为'B',字符串变为 "AABBBBA"。
//子串 "BBBB" 有最长重复字母, 答案为 4。
public int CharacterReplacement(string s, int k)
    {

    }

//nums = [1,2,4,3], limit = 4 
//1
//LCode1674
public int MinMoves(int[] nums, int limit)
{
    Dictionary<int, List<int>> dic = new Dictionary<int, List<int>>();
    for (int i = 0; i <= (nums.Length -1 )/2; i++)
    {
        int j = nums.Length - 1 - i;
        int sum_i = nums[i] + nums[j];
        if (!dic.ContainsKey(sum_i))
        {
            List<int> list = new List<int>();
            dic.Add(sum_i, list);
        }
        dic[sum_i].Add(i);
    }
    int max_num = 0;
    foreach (var item in dic)
    {
        if (item.Value.Count > max_num)
        {
           max_num = item.Key;
        }
    }
    int move = nums.Length - max_num;
    return move;
}
//LCode85
//输入：matrix = [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]
//输出：6
public int MaximalRectangle(char[][] matrix)
{

}

//public int maximalRectangle(char[][] matrix)
//{
//    int m = matrix.length;
//    if (m == 0)
//    {
//        return 0;
//    }
//    int n = matrix[0].length;
//    int[][] left = new int[m][n];

//    for (int i = 0; i < m; i++)
//    {
//        for (int j = 0; j < n; j++)
//        {
//            if (matrix[i][j] == '1')
//            {
//                left[i][j] = (j == 0 ? 0 : left[i][j - 1]) + 1;
//            }
//        }
//    }

//    int ret = 0;
//    for (int i = 0; i < m; i++)
//    {
//        for (int j = 0; j < n; j++)
//        {
//            if (matrix[i][j] == '0')
//            {
//                continue;
//            }
//            int width = left[i][j];
//            int area = width;
//            for (int k = i - 1; k >= 0; k--)
//            {
//                width = Math.min(width, left[k][j]);
//                area = Math.max(area, (i - k + 1) * width);
//            }
//            ret = Math.max(ret, area);
//        }
//    }
//    return ret;
//}


//LCode1011
//weights = [1,2,3,4,5,6,7,8,9,10], D = 5
//15
public int ShipWithinDays(int[] weights, int D)
{

}

//LCode140
public IList<string> WordBreak(string s, IList<string> wordDict)
{
    List<String>[] dp = new List<String>[s.Length + 1];
    List<String> initial = new List<String>();
    initial.Add("");
    dp[0] = initial;
    for (int i = 1; i <= s.Length; i++)
    {
        List<String> list = new List<String>();
        for (int j = 0; j < i; j++)
        {
            if (dp[j].Count > 0 && wordDict.Contains(s.Substring(j, i - j)))
            {
                foreach (string l in dp[j])
                {
                    list.Add(l + (l.Equals("") ? "" : " ") + s.Substring(j, i - j));
                }
            }
        }
        dp[i] = list;
    }
    return dp[s.Length];
}


public class PriorityQueue<T> where T : IComparable<T>
{
    readonly List<T> _data;

    public PriorityQueue()
    {
        this._data = new List<T>();
    }

    public void enqueue(T item)
    {
        this._data.Add(item);
        int ci = this._data.Count - 1; // child index; start at end
        while (ci > 0)
        {
            int pi = (ci - 1) / 2; // parent index
            if (this._data[ci].CompareTo(this._data[pi]) >= 0)
            {
                break; // child item is larger than (or equal) parent so we're done
            }

            T tmp = this._data[ci];
            this._data[ci] = this._data[pi];
            this._data[pi] = tmp;
            ci = pi;
        }
    }

    public T dequeue()
    {
        // assumes pq is not empty; up to calling code
        int li = this._data.Count - 1; // last index (before removal)
        T frontItem = this._data[0]; // fetch the front
        this._data[0] = this._data[li];
        this._data.RemoveAt(li);

        --li; // last index (after removal)
        int pi = 0; // parent index. start at front of pq
        while (true)
        {
            int ci = pi * 2 + 1; // left child index of parent
            if (ci > li)
            {
                break; // no children so done
            }

            int rc = ci + 1; // right child
            if (rc <= li && this._data[rc].CompareTo(this._data[ci]) < 0)
            {
                // if there is a rc (ci + 1), and it is smaller than left child, use the rc instead
                ci = rc;
            }

            if (this._data[pi].CompareTo(this._data[ci]) <= 0)
            {
                break; // parent is smaller than (or equal to) smallest child so done
            }

            T tmp = this._data[pi];
            this._data[pi] = this._data[ci];
            this._data[ci] = tmp; // swap parent and child
            pi = ci;
        }

        return frontItem;
    }

    public T peek()
    {
        T frontItem = this._data[0];
        return frontItem;
    }

    public int count
    {
        get { return this._data.Count; }
    }

    public override string ToString()
    {
        string s = "";
        for (int i = 0; i < this._data.Count; ++i)
        {
            s += this._data[i] + " ";
        }

        s += "count = " + this._data.Count;
        return s;
    }

    public bool isConsistent()
    {
        // is the heap property true for all data?
        if (this._data.Count == 0)
        {
            return true;
        }

        int li = this._data.Count - 1; // last index
        for (int pi = 0; pi < this._data.Count; ++pi)
        {
            // each parent index
            int lci = 2 * pi + 1; // left child index
            int rci = 2 * pi + 2; // right child index

            if (lci <= li && this._data[pi].CompareTo(this._data[lci]) > 0)
            {
                return false; // if lc exists and it's greater than parent then bad.
            }

            if (rci <= li && this._data[pi].CompareTo(this._data[rci]) > 0)
            {
                return false; // check the right child too.
            }
        }

        return true; // passed all checks
    }
}

public class NewBehaviourScript : MonoBehaviour
{



    //输入：nums = [1,2,3,3,4,4,5,6], k = 4
    //输出：true
    //解释：数组可以分成[1, 2, 3, 4] 和[3, 4, 5, 6]。

    public class Sorter : IComparer<int>
    {
        public int Compare(int x, int y)
        {
            return x - y;
        }
    }
    public bool IsPossibleDivide(int[] nums, int k)
    {
        SortedDictionary<int, int> map = new SortedDictionary<int, int>(new Sorter());
        foreach (int num in nums)
        {
            if (!map.ContainsKey(num))
            {
                map.Add(num, 1);
            }
            else
            {
                map[num]++;
            }
        }
        var enumerator = map.GetEnumerator();
        for (int index = 0; index < map.Keys.Count; index++)
        {
            int num = enumerator.Current.Key;
            int occ = enumerator.Current.Value;
            if (occ > 0)
            {
                for (int i = 1; i <= k; i++)
                {
                    if (map.ContainsKey(num + i) && map[num + i] >= occ)
                    {
                        map[num + i] -= occ;
                    }
                    else
                    {
                        return false;
                    }
                }
            }
            enumerator.MoveNext();
        }
        return true;
    }


    // Start is called before the first frame update
    void Start()
    {
        Debug.Log(IsPossibleDivide(new int[] { 1, 2, 3, 3, 4, 4, 5, 6 }, 4));
    }



    //    public int[] maxSlidingWindow(int[] nums, int k)
    //    {
    //        int n = nums.length;
    //        PriorityQueue<int[]> pq = new PriorityQueue<int[]>(new Comparator<int[]>()
    //        {
    //            public int compare(int[] pair1, int[] pair2)
    //        {
    //            return pair1[0] != pair2[0] ? pair2[0] - pair1[0] : pair2[1] - pair1[1];
    //        }
    //    });
    //        for (int i = 0; i<k; ++i) {
    //            pq.offer(new int[]{nums[i], i
    //});
    //        }
    //        int[] ans = new int[n - k + 1];
    //      ans[0] = pq.peek()[0];
    //        for (int i = k; i<n; ++i) {
    //            pq.offer(new int[]{nums[i], i});
    //            while (pq.peek()[1] <= i - k) {
    //                pq.poll();
    //            }
    //            ans[i - k + 1] = pq.peek()[0];
    //        }
    //        return ans;
    //    }


    //public int[] maxSlidingWindow(int[] nums, int k) {
    //    PriorityQueue<int[]> pq = new PriorityQueue<int[]>();

    //}
}
