/* Homework 02a:

 Implement the following program and prove its correctness using Dafny:
 https://rise4fun.com/Dafny

*/

function sum(A: array<int>, Length:int): int
  decreases Length
  requires 0 <= Length <= A.Length
  reads A
{
  if Length == 0 then 0 else
  if A[Length-1] % 2 == 0 then sum(A, Length-1) + A[Length-1] else sum(A, Length-1)
}

function product(A: array<int>, Length:int): int
  decreases Length
  requires 0 <= Length <= A.Length
  reads A
{
  if Length == 0 then 1 else
  if A[Length-1] % 2 == 1 then product(A, Length-1) * A[Length-1] else product(A, Length-1)
}

method compute(A: array<int>) returns (E: int, O: int, M: int)
  requires 0 < A.Length
  ensures E == sum(A, A.Length)
  ensures O == product(A, A.Length)
	ensures forall k :: 0 < k < A.Length ==> M >= A[k]
	ensures exists k :: 0 < k < A.Length ==> M == A[k]
  // Implement this method such that: 
  //  - E is the sum of all even numbers of A
  //  - O is the product of all odd numbers of A
  //  - M is the maximal number of A
  // When A is an empty array, the result should be (0, 1, 8).
  // Yes, M for an empty array should be 8 (there is no -infty in Dafny).
  // Add invariants, ensures, requires, (functions)... s.t. Dafny can prove the correctness.
  //the quantifier has the form 'exists x :: A ==> B', which most often is a typo for 'exists x :: A && B'; if you think otherwise, rewrite as 'exists x :: (A ==> B)' or 'exists x :: !A || B' to suppress this warningDafny VSCode
{ 
  var index := 0;
  E := 0;
  O := 1;
  M := 8;
  if A.Length == 0{
    return;
  }
  M := A[0];
	while index < A.Length
    decreases A.Length - index
		invariant 0 <= index <= A.Length
		invariant forall k :: 0 <= k < index ==> M >= A[k]
    invariant E == sum(A, index)
    invariant O == product(A, index)
	{
    if A[index] % 2 == 0 {
      E := E + A[index];
    }
    else{
      O := O*A[index];
    }
		if A[index] >= M { M := A[index]; }
		index := index + 1;
	}
  return E, O, M;
}

