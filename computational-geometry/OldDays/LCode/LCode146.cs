using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LCode146 : MonoBehaviour
{
    struct IntPair
    {
       public int key;
       public int value;
        public IntPair(int key, int value)
        {
            this.key = key;
            this.value = value;
        }
    }
    public class LRUCache
    {
        LinkedList<IntPair> _list ;
        Dictionary<int, LinkedListNode<IntPair>> _dic;
        int _capacity;
        public LRUCache(int capacity)
        {
            _capacity = capacity;
            _list = new LinkedList<IntPair>();
            _dic = new Dictionary<int, LinkedListNode<IntPair>>();
        }

        public int Get(int key)
        {
            
            if (!_dic.ContainsKey(key))
            {
                Debug.Log("-1");
                return -1;
            }
            else
            {
                LinkedListNode<IntPair> node = _dic[key];
                IntPair pair = node.Value;
                int ret_val = pair.value;
                _list.Remove(pair);
                _list.AddLast(pair);
                Debug.Log(pair.value);

                return ret_val;

            }
        }

        public void Put(int key, int value)
        {
            if (!_dic.ContainsKey(key))
            {
                LinkedListNode<IntPair> node = new LinkedListNode<IntPair>(new IntPair(key,value));
                _list.AddLast(node);
                _dic.Add(key, node);
                if (_list.Count <= _capacity)
                {

                }
                else
                {
                    int toRmvKey = _list.First.Value.key;
                    _dic.Remove(toRmvKey);
                    _list.RemoveFirst();
                }
            }
            else
            {
                LinkedListNode<IntPair> node = _dic[key];
                _list.Remove(node.Value);
                node.Value = new IntPair(key, value);
                _list.AddLast(node.Value);
            }
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.L))
        {
            LRUCache cache = new LRUCache(2);
            cache.Put(2, 1);
            cache.Put(1, 1);
            cache.Put(2, 3);
            cache.Put(4, 1);
            cache.Get(1);
            cache.Get(2);

        }
    }
}
