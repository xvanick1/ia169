/* Homework 02b:

 Implement the following program and prove its correctness using Dafny:
 https://rise4fun.com/Dafny

*/

// You can add some auxiliary variables 
// but do not change the code computing a, b, and x.

method Multiply(N: int, M: nat) returns (R: int)
  ensures R == M*N;
  requires N>=0 && M>=0;
{
  var a := N;
  var b := M;
  var x := 0;

  while (b > 0)
  invariant b >= 0;
  //invariant M*N == (M - b) * N;
  invariant M*N == x + a*b;
  decreases b;
  {
    while (b % 10 != 0)
    invariant b >= 0;
    //invariant M*N == (M - b) * N + (N - a);
    invariant M*N == x + a*b;
    decreases b
    {
      x := x + a;
      b := b - 1;
    }
    a := 10 * a;
    b := b / 10;
  }
  R := x;
}


