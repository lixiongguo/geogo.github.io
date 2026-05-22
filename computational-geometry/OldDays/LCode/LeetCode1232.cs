using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LeetCode1232 : MonoBehaviour
{
    public bool CheckStraightLine(int[][] coordinates)
    {
        if (coordinates.Length <= 2)
        {
            return true;
        }
        int x0 = coordinates[0][0];
        int y0 = coordinates[0][1];

        int x1 = coordinates[1][0];
        int y1 = coordinates[1][1];
        for (int i = 0; i < coordinates.Length; i++)
        {

            int[] coordinate = coordinates[i];
            int x = coordinate[0];
            int y = coordinate[1];
            if((y-y0)*(x - x1) - (x-x0)*(y-y1) != 0)
            {
                return false;
            }
        }
        return true;
    }


    private void Start()
    {
    }
}
