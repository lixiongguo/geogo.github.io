using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

//new int[]{
//new int[]{1,0,0,0,1,1,0,1,0,0,0,1,0,0,0},
//new int[]{0,1,0,0,1,0,1,0,0,0,0,0,0,0,0},
//new int[]{0,0,1,0,1,0,0,0,0,0,0,0,1,1,0},
//new int[]{0,0,0,1,0,0,0,0,0,0,0,1,1,1,0},
//new int[]{1,1,1,0,1,0,0,0,0,0,1,0,0,0,0},
//new int[]{1,0,0,0,0,1,0,0,0,1,0,0,0,0,0},
//new int[]{0,1,0,0,0,0,1,0,1,0,0,0,0,0,0},
//new int[]{1,0,0,0,0,0,0,1,0,0,0,0,0,0,0},
//new int[]{0,0,0,0,0,0,1,0,1,0,0,0,0,0,1},
//new int[]{0,0,0,0,0,1,0,0,0,1,0,0,0,0,0},
//new int[]{0,0,0,0,1,0,0,0,0,0,1,0,0,1,0},
//new int[]{1,0,0,1,0,0,0,0,0,0,0,1,1,0,0},
//new int[]{0,0,1,1,0,0,0,0,0,0,0,1,1,0,0},
//new int[]{0,0,1,1,0,0,0,0,0,0,1,0,0,1,0},
//new int[]{0,0,0,0,0,0,0,0,1,0,0,0,0,0,1}}

    

class LCode200 : MonoBehaviour
{
    class Node
    {
        public int nodeIdx;
        public Node p;
    }
    void LinkBack(Node[][] nodes,char[][] grid,int x, int y)
    {
        Node node = new Node();
        node.nodeIdx = y * nodes.Length + x;
        nodes[x][y] = node;
        node.p = node;
        if (x == 0 && y == 0)
        {

        }
        else if (x == 0 && y > 0)
        {
            if (grid[x][y - 1] == '1')
            {
                Union(nodes[x][y - 1], nodes[x][y]);
            }
        }
        else if (x > 0 && y == 0)
        {
            if (grid[x - 1][y] == '1')
            {
                Union(nodes[x - 1][y], nodes[x][y]);
            }
        }
        else //x>0 y>0
        {
            if (grid[x - 1][y] == '1')
            {
                Union(nodes[x - 1][y], nodes[x][y]);
            }
            if (grid[x][y - 1] == '1')
            {
                Union(nodes[x][y-1], nodes[x][y]);
            }
        }
    }
    void Union(Node nodeA, Node nodeB)
    {
        while (nodeA.p != nodeA)
        {
            nodeA = nodeA.p;
        }
        while (nodeB.p != nodeB)
        {
            nodeB = nodeB.p;
        }
        if (nodeA.nodeIdx < nodeB.nodeIdx)
        {
            nodeB.p = nodeA.p;
        }
        else
        {
            nodeA.p = nodeB.p;
        }
    }
 
    public int NumIslands(char[][] grid)
    {
        int N = grid.Length;
        Node[][] nodes = new Node[N][];
        for (int i = 0; i < N; i++)
        {
            for (int j = 0; j < N; j++)
            {
                LinkBack(nodes,grid, i, j);
            }

        }
        int cnt = 0;
        for (int i = 0; i < N; i++)
        {
            for (int j = 0; j < N; j++)
            {
                if (nodes[i][j].p == nodes[i][j])
                    cnt++;
            }
        }
          
        return cnt;
    }
    private void Start()
    {
        int[][] M = new int[][]{
            new int[]{1,0,0,0,1,1,0,1,0,0,0,1,0,0,0},
            new int[]{0,1,0,0,1,0,1,0,0,0,0,0,0,0,0},
            new int[]{0,0,1,0,1,0,0,0,0,0,0,0,1,1,0},
            new int[]{0,0,0,1,0,0,0,0,0,0,0,1,1,1,0},
            new int[]{1,1,1,0,1,0,0,0,0,0,1,0,0,0,0},
            new int[]{1,0,0,0,0,1,0,0,0,1,0,0,0,0,0},
            new int[]{0,1,0,0,0,0,1,0,1,0,0,0,0,0,0},
            new int[]{1,0,0,0,0,0,0,1,0,0,0,0,0,0,0},
            new int[]{0,0,0,0,0,0,1,0,1,0,0,0,0,0,1},
            new int[]{0,0,0,0,0,1,0,0,0,1,0,0,0,0,0},
            new int[]{0,0,0,0,1,0,0,0,0,0,1,0,0,1,0},
            new int[]{1,0,0,1,0,0,0,0,0,0,0,1,1,0,0},
            new int[]{0,0,1,1,0,0,0,0,0,0,0,1,1,0,0},
            new int[]{0,0,1,1,0,0,0,0,0,0,1,0,0,1,0},
            new int[]{0,0,0,0,0,0,0,0,1,0,0,0,0,0,1}
        };
    }
}

