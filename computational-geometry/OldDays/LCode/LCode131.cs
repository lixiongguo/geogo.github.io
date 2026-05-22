using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LCode131 : MonoBehaviour
{
    public class ListNode
    {
        public int val;
        public ListNode next;
        public ListNode(int x) { val = x; }
     }
    public ListNode Partition(ListNode head, int x)
    {
        ListNode current = head;
        ListNode anotherPrev = null;
        ListNode anotherHead = null;
        ListNode prev = null;
        while (current != null)
        {
            if (current.val >= x)
            {
                if (anotherPrev == null)
                {
                    anotherHead = current;
                    anotherPrev = current;
                    if (prev == null)
                    {
                        head = head.next;
                    }
                    else
                    {
                        prev.next = current.next;
                    }
                }
                else
                {
                    anotherPrev.next = current;
                    anotherPrev = current;
                    if (prev == null)
                    {
                        head = head.next;
                    }
                    else
                    {
                        prev.next = current.next;
                    }
                }
                prev = current;
                current = current.next;
            }
            else
            {
                prev = current;
                current = current.next;
            }
        }
        prev.next = anotherHead;
        return head;
    }
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
