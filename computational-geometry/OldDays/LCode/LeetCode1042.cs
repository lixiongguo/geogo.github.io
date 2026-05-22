using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class LeetCode1042 : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    class Edge
    {
        public Edge(int begin, int end, int weight)
        {
            this.Begin = begin;
            this.End = end;
            this.Weight = weight;
        }

        public int Begin { get; private set; }
        public int End { get; private set; }
        public int Weight { get; private set; }

        public override string ToString()
        {
            return string.Format(
              "Begin[{0}], End[{1}], Weight[{2}]",
              Begin, End, Weight);
        }
    }

    class Graph
    {
        private Dictionary<int, List<Edge>> _adjacentEdges
          = new Dictionary<int, List<Edge>>();

        public Graph(int vertexCount)
        {
            this.VertexCount = vertexCount;
        }

        public int VertexCount { get; private set; }

        public IEnumerable<int> Vertices
        {
            get
            {
                return _adjacentEdges.Keys;
            }
        }

        public IEnumerable<Edge> Edges
        {
            get
            {
                return _adjacentEdges.Values.SelectMany(e => e);
            }
        }

        public int EdgeCount
        {
            get
            {
                return this.Edges.Count();
            }
        }

        public void AddEdge(int begin, int end, int weight)
        {
            if (!_adjacentEdges.ContainsKey(begin))
            {
                var edges = new List<Edge>();
                _adjacentEdges.Add(begin, edges);
            }

            _adjacentEdges[begin].Add(new Edge(begin, end, weight));
        }

    }
}
