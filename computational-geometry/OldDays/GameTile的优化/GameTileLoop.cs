using System.Collections.Generic;
using UnityEngine;
using Utils;
using GOGUI;
using UnityEngine.UI;

namespace GOEGame
{
    public delegate void OnupdateItem(GameObject obj, int currentDataIndex);
    /// <summary>
    /// 循环利用的通用容器控件
    /// </summary>
    public class GameTileLoop : GameTile
    {
        private ScrollRect m_scrollRect;
        /// <summary>每个Item的边距</summary>
        private Vector2 m_itemSpacing;
        /// <summary>每个格子的大小（Size + Spacing）</summary>
        private Vector2 m_GridSize;
        /// <summary>每个格子的单向大小（垂直是y, 水平是x）</summary>
        float m_GridSizeOne;
        /// <summary>可视区域内Item的列数</summary>
        private int m_viewItemColCount = 1;
        /// <summary>可视区域内Item的行数</summary>
        private int m_viewItemRowCount = 1;
        /// <summary>行数*列数</summary>
        private int m_viewItemCount;
        /// <summary>是否是垂直滚动方式，否则是水平滚动</summary>
        private bool m_isVertical;
        /// <summary>scrowview的widget</summary>
        private RectTransform m_content;
        /// <summary>布局方式</summary>
        private LayoutGroup m_LayoutGroup;
        /// <summary>边距</summary>
        private RectOffset m_oldPadding;
        /// <summary>数据数组渲染的起始下标(从0开始)</summary>
        private int m_startRowOrCol;
        /// <summary>上一次数据数组渲染的起始下标(从0开始)</summary>
        private int last_startRowOrCol;
        /// <summary>Panel面板的初始位置</summary>
        Vector2 panelPos;
        /// <summary>第一个元素的位置只设置一次就好</summary>
        bool haveSetStartPos = false;
        /// <summary>第一个元素的位置</summary>
        Vector2 itemStartPos = Vector2.zero;
        /// <summary>第一个元素的渲染值只设置一次就好</summary>
        bool haveFindStartSibling = false;
        /// <summary>第一个元素的渲染值</summary>
        int itemStartSibling;
        /// <summary>第一个元素和第二个元素的x差， 第一行元素和第二行元素的y差</summary>
        Vector2 itemAddPos = Vector2.zero;
        /// <summary>更新内容, GameObject obj当前Template,  int currentDataIndex当前数据位置</summary>
        public OnupdateItem onUpdateItem;
        /// <summary>从上到下或者从左到右</summary>
        public bool IsUpToDownOrLeftToRight = true;
        //可见区域长度
        private float ViewSpace;
        /// <summary>拉到最底部时候开始的行（列）（从0开始的下标）</summary>
        int showBottomStartRowOrCol;
        /// <summary>当前数据量显示所需要的所有行（列）数</summary>
        int totalRowOrCol;
        /// <summary>可视区域可以显示的行（列）数</summary>
        int viewRowOrCol;
        /// <summary>数据量个数</summary>
        int dataCount;
        /// <summary>在下一帧设置为true</summary>
        bool canScrowRectMove = false;
        /// <summary>比实际增加几行或者几列</summary>
        public int addRowOrCol = 1;
        /// <summary>可以显示的行或者列</summary>
        int canShowRowOrCol = 0;

        Vector2 GetPosByIndex(int index)
        {
            return itemStartPos + new Vector2((index % m_viewItemColCount) * itemAddPos.x, (index / m_viewItemColCount) * itemAddPos.y);
        }

        List<RectTransform> lastChildOrderList = new List<RectTransform>();

        public new int ChildCount
        {
            get
            {
                if (childList.Count > 0 && !childList[0])
                {
                    childListDirty = true;
                }
                if (childListDirty)
                {
                    childListDirty = false;
                    childList.Clear();
                    lastChildOrderList.Clear();
                    for (int i = 0; i < ContainerTransform.childCount; i++)
                    {
                        var t = ContainerTransform.GetChild(i);
                        if (t == poolTransform)
                            continue;
                        if (t.gameObject == template)
                        {
                            continue;
                        }
                        t.gameObject.SetActive(true);
                        childList.Add(t.GetComponent<RectTransform>());
                    }
                    if (childList.Count > 0 && !haveFindStartSibling)
                    {
                        haveFindStartSibling = true;
                        itemStartSibling = childList[0].GetSiblingIndex();
                    }
                    int start = itemStartSibling;
                    for (int i = 0; i < childList.Count; ++i)
                    {
                        //设置一下渲染顺序
                        childList[i].SetSiblingIndex(start);
                        lastChildOrderList.Add(childList[i]);
                        ++start;
                    }
                }
                return childList.Count;
            }
        }

        /// <summary>
        /// 设置当前数据量
        /// </summary>
        private int DataCount
        {
            set
            {
                if (value < 0)
                {
                    value = 0;
                }
                dataCount = value;
                if (m_isVertical)
                {
                    if (value % m_viewItemColCount == 0)
                    {
                        totalRowOrCol = value / m_viewItemColCount;
                    }
                    else
                    {
                        totalRowOrCol = value / m_viewItemColCount + 1;
                    }
                }
                else
                {
                    if (value % m_viewItemRowCount == 0)
                    {
                        totalRowOrCol = value / m_viewItemRowCount;
                    }
                    else
                    {
                        totalRowOrCol = value / m_viewItemRowCount + 1;
                    }
                }
                showBottomStartRowOrCol = Mathf.Max(0, totalRowOrCol - viewRowOrCol);
                canScrowRectMove = true;
                last_startRowOrCol = -100000;
                if(nextFrameIndex >= 0)
                {
                    ScrollTo(nextFrameIndex);
                }
                ScorwRectMove(Vector2.zero);
            }
        }
        /// <summary>设置m_GridSize和m_GridSizeOne</summary>
        Vector2 SetGridSize
        {
            set
            {
                m_GridSize = value;
                m_GridSizeOne = m_isVertical ? value.y : value.x;
            }
        }
        /// <summary>设置扩展</summary>
        void ExpandPadding()
        {
            int frontSpace = 0;
            int behindSpace = 0;
            if (IsUpToDownOrLeftToRight)
            {
                frontSpace = Mathf.CeilToInt(m_startRowOrCol * m_GridSizeOne);
                behindSpace = Mathf.CeilToInt(Mathf.Max(0, m_GridSizeOne * showBottomStartRowOrCol - frontSpace));
            }
            else
            {
                behindSpace = Mathf.CeilToInt(m_startRowOrCol * m_GridSizeOne);
                frontSpace = Mathf.CeilToInt(Mathf.Max(0, m_GridSizeOne * showBottomStartRowOrCol - behindSpace));
            }
            if (m_isVertical)
            {
                m_LayoutGroup.padding = new RectOffset(m_oldPadding.left, m_oldPadding.right, m_oldPadding.top + frontSpace, m_oldPadding.bottom + behindSpace);
            }
            else
            {
                m_LayoutGroup.padding = new RectOffset(m_oldPadding.left + frontSpace, m_oldPadding.right + behindSpace, m_oldPadding.top, m_oldPadding.bottom);
            }
        }

        void HandleItem(RectTransform rect, int dataIndex)
        {
            Debug.Log("Handle  : " + dataIndex);
            rect.anchoredPosition = GetPosByIndex(dataIndex);
            if (dataIndex < dataCount)
            {
                onUpdateItem(rect.gameObject, dataIndex);
                rect.gameObject.SetActive(true);
            }
            else
            {
                rect.gameObject.SetActive(false);
            }
        }

        int nextFrameIndex = -1;
        /// <summary>
        /// 在调用此方法的时候确定  VisibleInHierarchy == true
        /// 定位到第几行或者第几列, 在显示区域的层数， 在最底或者最高， 其他在可见的第一层
        /// </summary>
        /// <param name="index">下标(从0开始)</param>
        public void ScrollTo(int index)
        {
            if (canScrowRectMove)
            {
                int rowOrCol = 1;
                if (m_isVertical)
                {
                    rowOrCol = (index / m_viewItemColCount + 1);
                }
                else
                {
                    rowOrCol = (index / m_viewItemRowCount + 1);
                }
                rowOrCol = Mathf.Min(rowOrCol, totalRowOrCol);
                if (rowOrCol < canShowRowOrCol)
                {
                    m_content.anchoredPosition = panelPos;
                }
                else
                {
                    int maxMin = totalRowOrCol - canShowRowOrCol;
                    if (maxMin < 0)
                    {
                        m_content.anchoredPosition = panelPos;
                    }
                    else if (rowOrCol > maxMin)
                    {
                        SetPos(totalRowOrCol, ViewSpace);
                    }
                    else
                    {
                        SetPos(rowOrCol - canShowRowOrCol / 2);
                    }
                }
                nextFrameIndex = -1;
            }
            else
            {
                nextFrameIndex = index;
            }
        }

        void SetPos(int index, float height = 0)
        {
            float space = 0;
            if (IsUpToDownOrLeftToRight)
            {
                space = m_GridSizeOne;
            }
            else
            {
                space = -m_GridSizeOne;
                height = -height;
            }
            if (m_isVertical)
            {
                m_content.anchoredPosition = new Vector2(panelPos.x, panelPos.y - height + index * space);
            }
            else
            {
                m_content.anchoredPosition = new Vector2(panelPos.x - height + index * space, panelPos.y);
            }
        }

        Vector2 currentPos = Vector2.zero;
        /// <summary>
        /// childList 比如原来是   0 1；2 3； 4 5向上移动了两行， 变成  2 3； 4 5； 0 1
        /// </summary>
        /// <param name="data"></param>
        void ScorwRectMove(Vector2 data)
        {
            if (dataCount <= 0) return;
            int count = ChildCount;
            if (count <= 0 || !canScrowRectMove) return;
            currentPos = m_content.anchoredPosition;
            float currentOffset = 0;
            if (m_isVertical)
            {
                if (IsUpToDownOrLeftToRight)
                {
                    if (currentPos.y >= panelPos.y)
                        currentOffset = currentPos.y - panelPos.y;
                }
                else
                {
                    if (currentPos.y <= panelPos.y)
                        currentOffset = panelPos.y - currentPos.y;
                }
            }
            else
            {
                if (IsUpToDownOrLeftToRight)
                {
                    if (currentPos.x <= panelPos.x)
                        currentOffset = panelPos.x - currentPos.x;
                }
                else
                {
                    if (currentPos.x >= panelPos.x)
                        currentOffset = currentPos.x - panelPos.x;
                }
            }
            //垂直算出来的是行，水平算出来的是列
            m_startRowOrCol = Mathf.Min(Mathf.FloorToInt(currentOffset / m_GridSizeOne), showBottomStartRowOrCol);
            if (last_startRowOrCol != m_startRowOrCol)
            {
                int moveRowOrCol = m_startRowOrCol - last_startRowOrCol;
                if (Mathf.Abs(moveRowOrCol) >= viewRowOrCol)
                {
                    int dataStartIndex = m_startRowOrCol * m_viewItemColCount;
                    for (int i = 0; i < count; ++i, ++dataStartIndex)
                    {
                        HandleItem(childList[i], dataStartIndex);
                    }
                }
                else if (moveRowOrCol > 0)
                {
                    //不用更新的Item
                    int currentChildStart = 0;
                    int lastOrderStrat = moveRowOrCol * 1;
                    int totalCount = (viewRowOrCol - moveRowOrCol) * 1;
                    for (int i = 0; i < totalCount; ++i)
                    {
                        childList[currentChildStart] = lastChildOrderList[lastOrderStrat];
                        ++currentChildStart;
                        ++lastOrderStrat;
                    }
                    //以下是要更新的Item
                    int dataStartIndex = (last_startRowOrCol + viewRowOrCol) * 1;
                    lastOrderStrat = 0;
                    totalCount = moveRowOrCol * 1;
                    for (int i = 0; i < totalCount; ++i)
                    {
                        childList[currentChildStart] = lastChildOrderList[lastOrderStrat];
                        childList[currentChildStart].SetAsLastSibling(); //设置渲染顺序 
                       // HandleItem(childList[currentChildStart], dataStartIndex);
                        ++currentChildStart;
                        ++lastOrderStrat;
                        ++dataStartIndex;
                    }
                }
                else
                {
                    moveRowOrCol = -moveRowOrCol;
                    //不用更新的Item
                    int currentChildStart = moveRowOrCol * 1;
                    int lastOrderStrat = 0;
                    int totalCount = (viewRowOrCol - moveRowOrCol) * 1;
                    for (int i = 0; i < totalCount; ++i)
                    {
                        childList[currentChildStart] = lastChildOrderList[lastOrderStrat];
                        ++currentChildStart;
                        ++lastOrderStrat;
                    }
                    //以下是要更新的Item
                    int dataEndIndex = last_startRowOrCol * 1 - 1;
                    currentChildStart = moveRowOrCol * 1 - 1;
                    lastOrderStrat = viewRowOrCol * 1 - 1;
                    totalCount = moveRowOrCol * 1;
                    for (int i = 0; i < totalCount; ++i)
                    {
                        childList[currentChildStart] = lastChildOrderList[lastOrderStrat];
                        childList[currentChildStart].SetSiblingIndex(itemStartSibling);//设置渲染顺序
                       // HandleItem(childList[currentChildStart], dataEndIndex);
                        --currentChildStart;
                        --lastOrderStrat;
                        --dataEndIndex;
                    }
                }
                //更新当前存储的列表
                for (int i = 0; i < count; ++i)
                {
                    lastChildOrderList[i] = childList[i];
                }
                ExpandPadding();
                last_startRowOrCol = m_startRowOrCol;
            }
        }

        protected override void OnInit()
        {
            base.OnInit();
            //记录下m_itemSpacing的大小
            Vector2 m_itemSize = Vector2.zero;
            m_LayoutGroup = gameObject.GetComponent<LayoutGroup>();
            if (m_LayoutGroup is GridLayoutGroup)
            {
                var gridGroup = m_LayoutGroup as GridLayoutGroup;
                m_itemSize = gridGroup.cellSize;
                m_itemSpacing = gridGroup.spacing;
            }
            else
            {
                LayoutElement layOut = template.GetComponent<LayoutElement>();
                if (layOut == null)
                {
                    m_itemSize = new Vector2(100, 100);
                }
                else
                {
                    float width = layOut.minWidth;
                    if (width <= 0)
                    {
                        width = layOut.preferredWidth;
                    }
                    float height = layOut.preferredHeight;
                    if (height <= 0)
                    {
                        height = layOut.minHeight;
                    }
                    m_itemSize = new Vector2(width, height);
                }
                if (m_LayoutGroup is HorizontalLayoutGroup)
                {
                    m_itemSpacing = new Vector2((m_LayoutGroup as HorizontalLayoutGroup).spacing, 0);
                }
                else
                {
                    m_itemSpacing = new Vector2(0, (m_LayoutGroup as VerticalLayoutGroup).spacing);
                }
            }
            m_oldPadding = m_LayoutGroup.padding;
            SetGridSize = m_itemSize + m_itemSpacing;
        }
        public override void OnHide()
        {
            Events.Common.NextFrameExecute -= NextFrameRun;
            dataCount = 0;
            base.OnHide();
        }

        public override void Clear()
        {
            base.Clear();
            dataCount = 0;
        }
        /// <summary>
        /// 外部调用增加一条数据
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <returns></returns>
        public void AddOneData<T>()
           where T : GameUIComponent, new()
        {
            InitM_ScrowRect();
            ++dataCount;
            if (ChildCount >= m_viewItemCount)
            {
                DataCount = dataCount;
            }
            else
            {
                Events.Common.NextFrameExecute += NextFrameRun;
                AddChild_T<T>();
            }
        }
        /// <summary>
        /// 外部调用的减少一条数据
        /// </summary>
        /// <returns></returns>
        public void RemoveOneData()
        {
            if (dataCount <= 0) return;
            InitM_ScrowRect();
            --dataCount;
            if (dataCount >= m_viewItemCount)
            {
                DataCount = dataCount;
            }
            else
            {
                int count = ChildCount;
                if (count > 0)
                {
                    RemoveChildByIndex(count - 1);
                    Events.Common.NextFrameExecute += NextFrameRun;
                }
            }
        }

        /// <summary>
        /// 因为ShowUI的时候  activeInHierarchy为false， 所以GetComponentInParent不可用
        /// </summary>
        public int InitM_ScrowRect()
        {
            canScrowRectMove = false;
            nextFrameIndex = -1;
            if (m_scrollRect != null) return m_viewItemCount;
            if (Widget.gameObject.activeInHierarchy)
            {
                m_scrollRect = Widget.GetComponentInParent<ScrollRect>();
            }
            else
            {
                m_scrollRect = Widget.parent.GetComponent<ScrollRect>();
            }
            RectTransform m_tranScrollRect = m_scrollRect.GetComponent<RectTransform>();
            m_content = m_scrollRect.content;
            panelPos = m_content.anchoredPosition;
            m_isVertical = m_scrollRect.vertical;
            float height = m_GridSize.y;
            float width = m_GridSize.x;
            if (m_isVertical) //垂直排列
            {
                ViewSpace = m_tranScrollRect.rect.height;
                canShowRowOrCol = Mathf.CeilToInt(ViewSpace / height);
                m_viewItemRowCount = canShowRowOrCol + addRowOrCol;
                if (width <= 0)
                    width = m_tranScrollRect.rect.width;
                m_viewItemColCount = 1;// Mathf.Max(1, Mathf.FloorToInt(m_tranScrollRect.rect.width / width));
                viewRowOrCol = m_viewItemRowCount;
            }
            else
            {
                ViewSpace = m_tranScrollRect.rect.width;
                if (height <= 0)
                    height = m_tranScrollRect.rect.height;
                m_viewItemRowCount = 1;// Mathf.Max(1, Mathf.FloorToInt(m_tranScrollRect.rect.height / height));
                canShowRowOrCol = Mathf.CeilToInt(ViewSpace / width);
                m_viewItemColCount = canShowRowOrCol + addRowOrCol;
                viewRowOrCol = m_viewItemColCount;
            }
            m_viewItemCount = m_viewItemRowCount * m_viewItemColCount;
            m_scrollRect.onValueChanged.AddListener(ScorwRectMove);
            return m_viewItemCount;
        }

        /// <summary>
        /// 因为ContentSizeFitter的RectTransForm下一帧有用
        /// </summary>
        void NextFrameRun()
        {
            int count = ChildCount;
            if (count <= 0)
            {
                return;
            }
            if (childList[0].rect.size == Vector2.zero)
            {
                Events.Common.NextFrameExecute += NextFrameRun;
                return;
            }
            SetGridSize = childList[0].rect.size + m_itemSpacing;
            if (!haveSetStartPos)
            {
                haveSetStartPos = true;
                itemStartPos = childList[0].anchoredPosition;
            }
            if (count > 1)
            {
                itemAddPos.x = (childList[1].anchoredPosition.x - itemStartPos.x);
            }
            if (count > m_viewItemColCount)
            {
                itemAddPos.y = (childList[m_viewItemColCount].anchoredPosition.y - itemStartPos.y);
            }
            DataCount = dataCount;
        }

        /// <summary>
        /// 内部EnsureSize使用的AddChild
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <returns></returns>
        protected virtual T AddChild_T<T>()
          where T : GameUIComponent, new()
        {
            GameObject go = AddChild();
            T res = go.ToGameUIComponent() as T;
            if (res != null)
                return res;
            res = Make<T>(go);
            EventTriggerListener lis = EventTriggerListener.Get(go);
            lis.parameter = res;
            return res;
        }
        public new void EnsureSize<T>(int realDataCount)
            where T : GameUIComponent, new()
        {
            InitM_ScrowRect();
            int count = Mathf.Min(realDataCount, m_viewItemCount);
            int cur = ChildCount;
            //if (cur != count)
            //    Visible = false;
            if (cur < count)
            {
                int diff = count - cur;
                for (int i = 0; i < diff; i++)
                {
                    AddChild_T<T>();
                }
            }
            else
            {
                int diff = cur - count;
                for (int i = 0; i < diff; i++)
                    RemoveChildByIndex(0);
            }
            //if (!Visible)
            //    Visible = true;
            SetEnsureSizeLoop(realDataCount);
        }
        public void SetEnsureSizeLoop(int realDataCount)
        {
            dataCount = realDataCount;
            Events.Common.NextFrameExecute += NextFrameRun;
        }
    }
}