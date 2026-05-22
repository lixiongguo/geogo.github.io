using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LCode427 : MonoBehaviour
{
    //X X X X
    //X O O X
    //X X O X
    //X O X X

    //X X X X
    //X X X X
    //X X X X
    //X O X X
    class Node
    {
       public int x, y;
       public bool isChecked;
        public bool isO;
       public Node nodeParent;
    }
    public void Solve(char[][] board)
    {
        int N = board.Length;
        bool[][] visited = new bool[N][];
        Queue<Node> nodes = new Queue<Node>();
        for (int i = 0; i < N; i++)
        {
            for (int j = 0; j < N; j++)
            {
                if (board[i][j] == 'O')
                {
                    bfs(board, i, j);
                }
            }
        }
    }
    void bfs(char[][] board, int i, int j,Queue<Node> nodes)
    {
        nodes.Clear();
        Node node = new Node();
        node.x = i;
        node.y = j;
        node.isChecked = false;
        nodes.Enqueue(node);
        while (nodes.Count > 0)
        {
            node =  nodes.Dequeue();
            int N = board.Length - 1;
            int N2 = board[0].Length - 1;
            if (node.x == 0 || node.x == N - 1 || node.y == 0 || node.y == N2 - 1)
            {
                node.isChecked = true;
            }

        }
    }
    bool dfs(char[][] board, int i, int j)
    {
        int N = board.Length;
        if (i == 0 || i == N - 1 || j == 0 || j == N - 1)
        {
            board[i][j] = '*';
            return true;
        }
        else
        {
            bool down = (board[i + 1][j] == '*')|| ((board[i + 1][j] == 'O') && dfs(board, i + 1, j));
            if (down)
            {
                board[i + 1][j] = '*';
                board[i][j] = '*';
                return true;
            }
            bool right = (board[i][j + 1] == '*') || ((board[i][j+1] == 'O') && dfs(board, i, j+1));
            if (right)
            {
                board[i][j + 1] = '*';
                board[i][j] = '*';
                return true;
            }
            bool up = (board[i-1][j] == '*') ||((board[i-1][j] == 'O') && dfs(board, i-1, j));
            if (up)
            {
                board[i - 1][j] = '*';
                board[i][j] = '*';
                return true;
            }
            bool left = (board[i][j-1] == '*') || ((board[i][j - 1] == 'O') && dfs(board, i, j - 1));
            if (left)
            {
                board[i][j - 1] = '*';
                board[i][j] = '*';
                return true;
            }
            board[i][j] = 'X';
            return false;
        }
    }




    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.K))
        {
            //char[][] board = new char[][] {
            //    new char[4]{'X', 'X', 'X', 'X'},
            //    new char[4]{'X', 'O', 'O', 'X'},
            //    new char[4]{'X', 'X', 'O', 'X'},
            //    new char[4]{'X', 'O', 'X', 'X'},
            //};
            //Solve(board);
            //int N = board.Length;
            //for (int i = 0; i < N; i++)
            //{
            //    string str = "";
            //    for (int j = 0; j < N; j++)
            //    {
            //        str += board[i][j] + "  ";
            //    }
            //    Debug.Log(str);
            //}
            int[][] matrix = new int[][] {
                new int[]{1,3,5,7},
                 new int[]{10,11,16,20},
                   new int[]{23,30,34,50}
            };
            Debug.Log(SearchMatrix(matrix, 11));
        }
       
    }
}
