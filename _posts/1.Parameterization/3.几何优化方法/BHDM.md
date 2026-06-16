The main contribution of this paper is the development of an un

derlying mathematical theory and algorithms for computing locally

injective harmonic and conformal planar mappings which are guar

anteed to have bounded amount of distortion.

**Definition 2.** *A continuously differentiable planar mapping*

*f* : Ω *⊂* C *→* C *is a* (*k, σ*

1

*, σ*

2

) *bounded distortion mapping if it*

*satisfies the following conditions*

0 *≤* *k*(*z*) *≤* *k <* 1 

*∀**z* *∈* Ω*,* 

(4a)

*σ*

1

(*z*) *≤* *σ*

1 

*<* *∞ ∀**z* *∈* Ω*,* 

(4b)

0 *< σ*

2 

*≤* *σ*

2

(*z*) 

*∀**z* *∈* Ω*,* 

(4c)

*where* *k*(*z*) *is the dilatation of* *f**,* *σ*

1

(*z*)*, σ*

2

(*z*) *are the singular*

*values of the Jacobian of* *f**, and* *k, σ*

1

*, σ*

2 

*are real constants.*

Equation (4a) asserts that *f* has bounded amount of conformal

distortion (*f* is called a quasiconformal mapping [Ahlfors 1966]).

Equations (4b) and (4c) bounds the maximal and minimal amount

of local stretch from above and below respectively. Together they

can be used to bound various measures of isometric distortion such

as max*{**σ*

1

(*z*)*,* 1*/σ*

2

(*z*)*}*.

**Observation 3.** *A* (*k, σ*

1

*, σ*

2

) *bounded distortion mapping* *f* *is lo*

*cally injective sense-preserving.*

*Proof.* From Equation (4c) we have that *σ*

2

(*z*) *>* 0, hence *|**f*

*z*

*| 6*=

*|**f*

*z*¯

*|*, so at every point in the domain *f* is either sense-preserving

(*|**f*

*z*

*|* *>* *|**f*

*z*¯

*|*) or sense-reversing (*|**f*

*z*

*|* *<* *|**f*

*z*¯

*|*). (4a) rules out *|**f*

*z*

*|* *<*

*|**f*

*z*¯

*|*.

The conditions in Definition 2 involve every point in the domain

of *f*. A natural question to raise is whether it is possible to refor

mulate these conditions solely in terms of the boundary behavior

of the mapping, in the special case that *f* is harmonic? The next

theorem addresses this question and provides alternative necessary

and sufficient conditions for a *harmonic* mapping to be a (*k, σ*

1

*, σ*

2

)

bounded distortion mapping.

**Theorem 4.** *A complex-valued harmonic mapping* *f* *defined on a*

*simply connected domain* Ω *is* (*k, σ*

1

*, σ*

2

) *bounded distortion if and*

*only if*

I *∂*Ω *f*

*0*

*z*

(

*z*

)

*f*

*z*

(

*z*

)

*dz* = 0*,* 

(5a)

0 *≤* *k*(*w*) *≤* *k <* 1 

*∀**w* *∈* *∂*Ω*,* 

(5b)

*σ*

1

(*w*) *≤* *σ*

1 

*<* *∞ ∀**w* *∈* *∂*Ω*,* 

(5c)

0 *< σ*

2 

*≤* *σ*

2

(*w*) 

*∀**w* *∈* *∂*Ω*,* 

(5d)

*Proof.* If *f* is harmonic (*k, σ*

1

*, σ*

2

) bounded distortion on a simply

connected domain, *f*

*z* 

is holomorphic (Corollary 1). Observation 3

asserts that *|**f*

*z*

*|* *>* *|**f*

*z*¯

*|* which imply that *f*

*z* 

does not vanish inside

Bounded Distortion Harmonic Mappings in the Plane • 73:3 

ACM Transactions on Graphics, Vol. 34, No. 4, Article 73, Publication Date: August 2015the domain (*f**z* = 0). By applying Cauchy’s argument principle to

*f**z* we get

I

*∂*Ω

*f*

*0*

*z*

(

*z*

)

*f*

*z*

(

*z*

)

*dz* = 2*π*i*N,* 

(6)

where *N* is the number of zeros of *f**z*. Since *N* = 0, Equation (5a)

holds. Equations (5b),(5c), (5d) are satisfied simply because they

are the restriction of Equations (4a),(4b),(4c) from Definition 2 to

the boundary of the domain. The other direction is more compli

cated to prove and will rely on the following three small lemmas.

**Lemma 5.** *Conditions* (5a) *and* (5b) *imply condition* (4a)*.*

*Proof.* Condition (5a) implies that *f**z* = 0 and so the second

complex dilatation *ν**f* = *f f* *z*¯

*z*

is holomorphic (Section 3). Since

the modulus of a holomorphic function is a subharmonic function,

*|**ν**f* *|* = *k*(*z*) attains its maximum on *∂*Ω. Hence, bounding *k*(*z*)

from above by a constant *k* on the boundary (condition (5b)) im

plies that the same bound holds at every point in the domain (con

dition (4a)).

**Lemma 6.** *Condition* (5c) *imply condition* (4b)*.*

*Proof.* Using Corollary 1, we know that since *f* is harmonic, *f**z*

and *f**z*¯ are holomorphic. *|**f**z**|* and  *f**z*¯  = *|**f**z*¯*|* are subharmonic and

so is their sum *σ*1(*z*) = *|**f**z**|*+*|**f**z*¯*|* (Equation (3) left). Since *σ*1(*z*)

is subharmonic, its maximum is attained on the boundary and it is

sufficient to bound it on the boundary from above.

**Lemma 7.** *Conditions* (5a)*,* (5b)*, and* (5d) *together imply condi*

*tion* (4c)*.*

*Proof.* By using the same argument applied in the proof of Obser

vation 3, we know that, on the boundary, *|**f**z**|* *>* *|**f**z*¯*|*. Hence, the ex

pression for *σ*2(*w*) on the boundary simplifies to *|**f**z*(*w*)*|−|**f**z*¯(*w*)*|*

(Equation (3) right). Next we define an auxiliary function *ς*(*z*) =

*σ*2*/* *|**f**z*(*z*)*|*+*k*(*z*), which is well defined on Ω since *f**z* = 0. From

Lemma 5 we have that *k*(*z*) is subharmonic. Since *f**z*(*z*) is holo

morphic, so is 1*/f**z*(*z*). It follows that 1*/* *|**f**z*(*z*)*|* is subharmonic

and since *σ*2 is a positive constant, *ς*(*z*) is also subharmonic. Equa

tion (5d) can be written as *σ*2 *≤ |**f**z*(*w*)*| − |**f**z*¯(*w*)*|*. Dividing both

sides of the inequality by *|**f**z*(*w*)*|* and further manipulating we get

*σ*2

*|**f**z*(*w*)*|*

+

*|**f**z*¯(*w*)*|*

*|**f**z*(*w*)*|*

*≤* 1*,* 

(7)

where the left hand side is simply *ς*(*w*). The subharmonicity of *ς*

is then used to show that *ς*(*z*) is bounded by 1 in the *entire* domain.

By reversing the manipulations that led to Equation (7) we obtain

*σ*2 *≤ |**f**z*(*z*)*| − |**f**z*¯(*z*)*|* = *σ*2(*z*) which concludes the proof of the

lemma.

Finally, since Lemmas 5, 6, and 7 show that conditions (4a),

(4b), and (4c) are satisfied, the harmonic mapping *f* is (*k, σ*1*, σ*2)

bounded distortion and the theorem is proved.

Equipped with Theorem 4, we are now ready to design an algorithm

for computing (*k, σ*1*, σ*2) bounded distortion harmonic mappings



**5 Optimization**

In order to perform interactive shape deformation, we use the point

to-point (P2P) user metaphor. The user controls the deformation by

manipulating the target position of a small amount of points located

inside or on the boundary of the domain. In addition, the user pre

scribes the bounds 0 *≤* *k <* 1, 

0 *< σ*2 *≤* *σ*1 and a numerical op

timization problem is solved in order to find an optimal (*k, σ*1*, σ*2)

bounded distortion harmonic mapping.





**5.1 Discretization**

To discretize the space of harmonic mappings, it will be conve

nient to represent *f* as Φ + Ψ, where Φ and Ψ are both holo

morphic (Equation (1)). We represent holomorphic functions by

using the Cauchy complex barycentric coordinates [Weber et al.

2009] which are derived by discretizing the boundary of the do

main using a polygonal shape (a so-called cage) and computing the

Cauchy transform [Bell 1992] of a piecewise linear trial function.

Let P =ˆ *{**z*1*, z*2*, ..., z**n**}*, 

*z**j* *∈* C be the vertices of a simply con

nected planar polygon (the cage), oriented counterclockwise (see

Figure 2 for notations).

Using the discrete Cauchy transform [Weber et al. 2009], Φ and Ψ

are represented as

Φ(*z*) =

*n*

X

*j*=1

*C**j* (*z*)*ϕ**j* *,* 

Ψ(*z*) =

*n*

X

*j*=1

*C**j* (*z*)*ψ**j* *,* 

(8)

where *C**j* (*z*) is the *j* *th* holomorphic Cauchy barycentric coordi

nate associated with vertex *z**j* and *ϕ**j* *, ψ**j* are complex coefficients.

*C**j* (*z*) and its first and second complex derivatives, *C**j* *0* (*z*), *C**j* *00* (*z*),

possess a rather simple closed-form expressions (see Appendix A).

For any choice of the coefficients *ϕ**j* *, ψ**j* , the mapping *f* is har

monic and its derivatives

*f**z*(*z*) = Φ*0* (*z*) =

*n*

X

*j*=1

*C**j* *0* (*z*)*ϕ**j* *,*

*f**z*¯(*z*) = Ψ*0* (*z*) =

*n*

X

*j*=1

*C**j* *0* (*z*)*ψ**j* *,*

(9)

are holomorphic and anti-holomorphic respectively, and can be eas

ily evaluated at any point *z* inside the domain using a straightfor

ward formula.

**5.2 Convexification**

Harmonicity of *f* is a built-in property of the subspace we chose.

Based on Theorem 4, we design a numerical optimization proce

dure that requires setting inequality constraints *only at the bound*

*ary* of the domain. However, both the conditions of Definition 2 and

Theorem 4 pose a challenge for numerical optimization since they

are nonconvex. To alleviate this difficulty, we adapt the effective

convexification approach of [Lipman 2012] to the complex setting.

This is done by substituting the *nonconvex* constraints of Theorem

4 with (maximal) *convex* constraints that imply the nonconvex ones.

The convexified constraints are then enforced efficiently by using a

Second Order Cone Program (SOCP) solver.

Let us start by expressing condition (5c) explicitly

*|**f**z*(*w*)*|* + *|**f**z*¯(*w*)*| ≤* *σ*1



Fortunately, this constraint is already convex. The convexification

of the rest of the constraints is done by introducing an auxiliary

function *θ*. Let *θ*(*w*) : *∂*Ω *→* R be a continuous real-valued func

tion defined on the boundary of the domain. For each selection of

*θ*(*w*) a different maximal convex subspace of the full nonconvex

space is chosen. By maximality of the subspace we mean that there

is no other convex subspace that strictly contains it. For now, as

sume that *θ* is chosen arbitrarily. The geometric interpretation of *θ*

and a strategy on how to choose it is given in Section 5.3.

Condition (5d) is expressed explicitly by

*σ*2 *≤ |**f**z*(*w*)*| − |**f**z*¯(*w*)*|* *,* 

(11)

and is replaced by the following second order convex cone con

straint

*|**f**z*¯(*w*)*| ≤* Re  *f**z*(*w*)ei*θ*(*w*) *−* *σ*2*.* 

(12)

The above constraint defines a maximal convex subset that is con

tained in the nonconvex set defined by Equation (11). The fact that

Equation (12) implies Equation (11) follows from

Re  *f**z*(*w*)ei*θ*(*w*) *≤*  

 

*f**z*(*w*)ei*θ*(*w*)

 

= *|**f**z*(*w*)*|* *,* 

(13)

where the left inequality is due to the fact that the modulus of

any complex number is no less than its real (and imaginary) part.

The maximality follows by using the same arguments used in [Lip

man 2012] or [Poranne and Lipman 2014] and is omitted here for

brevity.

Next, we handle condition (5b) and rearrange it to take the follow

ing explicit form

*|**f**z*¯(*w*)*| ≤* *k* *|**f**z*(*w*)*|* *.* 

(14)

The second order convex cone constraint substitute for Equation

(14) is given by

*|**f**z*¯(*w*)*| ≤* *k*Re  *f**z*(*w*)ei*θ*(*w*) *,* 

(15)

which also defines a maximal convex subset. Containment is easily

proved by multiplying both sides of the inequality (13) by the (non

negative) constant *k* such that we have

*|**f**z*¯(*w*)*| ≤* *k*Re  *f**z*(*w*)ei*θ*(*w*) *≤* *k* *|**f**z*(*w*)*|* *.*

As a regularization term we use the ARAP energy [Liu et al. 2008]

EARAP = 1

2

Z (*σ*1 *−* 1)2 + (*σ*2 *−* 1)2 *da.* 

(16)

A simple calculation shows that if *f* is locally injective sense

preserving, the ARAP energy can be expressed by

EARAP = Z (*|**f**z**| −* 1)2 + *|**f**z*¯*|* 2 *da.* 

(17)

As this energy is nonconvex, we approximate it using the following

quadratic functional in the spirit of [Poranne and Lipman 2014]

Z



*f**z*e i*θ* *−* 1



2

\+ *|**f**z*¯*|* 2 *da.* 

(18)

It remains to deal with the nonlinear condition of Equation (5a).

Without this condition, Theorem 4 cannot be applied. This is ex

plained in detail in Section 6.4



**5.3 The Algorithm**

In order to deform a domain Ω, bounded by a polygonal shape P,

we compute an outward offset polygon, denoted as the cage Pˆ. This

is done in order to avoid the singularities of the Cauchy’s coordi

nates on the boundary. The barycentric coordinates and their deriva

tives are computed with respect to Pˆ but are evaluated only on or

inside P (during a preprocessing step). We typically use an offset

of 0*.*1% of the overall length of P.

We then sample the boundary P uniformly with various densities to

obtain the sets *M*, *A*, and *B*. The set *M* is used in order to approx

imate the ARAP energy. *A* is a set of samples where (potentially)

the convex constraints are being enforced. *B* is used in the process

of evaluating the global bounds on distortion (Section 6). Finally,

the user defines the set *P* that contains the deformation handles, by

selecting small amount of points, on or inside P.

The algorithm also maintains three active sets: *A* *k* , *A* *σ*1 , and *A* *σ*2

that are initialized with the vertices of P. *θ* is initialized to 0. The

user sets the parameters *σ*1*, σ*2*, k* that bounds the distortion and the

interaction begins. In order to deform the shape, the user relocates

the points in *P* from their original positions *r**j* to their target posi

tions *q**j* and the following SOCP is solved

min

*ϕ,ψ*

EARAP + *λ* EP2P

*s.t. ψ*1 = 0*,*

*∀**p* *∈ A**k*

*|**f**z*¯(*p*)*| ≤* *k*Re  *f**z*(*p*)ei*θ*(*p*) *,*

*∀**p* *∈ A**σ*1

*|**f**z*(*p*)*|* + *|**f**z*¯(*p*)*| ≤* *σ*1*,*

*∀**p* *∈ A**σ*2

*|**f**z*¯(*p*)*| ≤* Re  *f**z*(*p*)ei*θ*(*p*) *−* *σ*2*,*

(19)

where the equality constraint is needed in order to nail down the

constant degree of freedom of the representation *f* = Φ + Ψ.

EARAP is obtained by approximating the integral in Equation (18)

with the following quadratic function

EARAP =

1

*|M|*

*|M|*

X

*j*=1





*f**z*(*p**j* )ei*θ*(*p**j* ) *−* 1



2

\+ *|**f**z*¯(*p**j* )*|* 2 *,* (20)

where the samples *p**j* *∈ M* are taken on the boundary alone.

Adding samples to the interior is also possible but we have not

noticed any improvement in the results. Positional constraints are

enforced softly using the following energy term

EP2P =

*|P|*

X

*j*=1

*|**f*(*r**j* ) *−* *q**j* *|* 2 *.* 

(21)

Switching to hard positional constraints is easily done by replac

ing EP2P with linear equality constraints *f*(*r**j* ) = *q**j* , but is less

preferable as it may hamper the feasibility of the constrained opti

mization.

While the convex optimization in equation (19) is always feasible,

the mapping it produces is only guaranteed to have bounded amount

of distortion at a finite number of points (where the inequality con

straints are enforced). Hence, the obtained solution must be val

idated by computing *global* distortion bounds (the validation pro

cess is explained in detail in Section 6). Once the solution is vali

dated, we update the function *θ*(*w*) (this defines a different convex

subspace) and the convex optimization is re-solved. This is repeated

till the energy cannot be further reduced. Convergence typically re

quires 1-3 iterations. In each iteration, *θ*(*w*) is set to *−* arg *f* ˜*z*(*w*)

where *f* ˜*z* is our best estimate for the unknown *f**z*. We then have



e

i*θ* 

= *|**f* ˜*z**|**/f* ˜*z* and the expression Re  *f**z*e i*θ* , that repetitively ap

pears in our convexified constraints, becomes a good approximation

to the expression *|**f**z**|*. This is desirable since the only difference

between the full nonconvex constraints (Equations (11) and (14))

and the convex ones (Equations (12) and (15)) is the substitution

of Re  *f**z*e i*θ* with *|**f**z**|*. In practice, we start with *f* ˜*z* = 0 (corre

sponds to the identity mapping) and update this estimate in further

iterations by using the solution *f**z* obtained in the previous iteration.

This also ensures that the optimization at each iteration is feasible.

In order to reduce the computation time of the optimization (19), we

use an active set approach where the main idea is to add inequality

constraints only where they are actually needed. In contrast to [Po

ranne and Lipman 2014] that uses a single active set, we noticed

that it is quite rare for more than one type of constraint to be vio

lated simultaneously and that maintaining three active sets leads to

significant reduction in the total number of active constraints. Be

fore a new iteration begins, we evaluate *k*(*p*), *σ*1(*p*), and *σ*2(*p*) on

all points *p* *∈ A* and add any point that violates the user bounds

*k*, *σ*1, and *σ*2 to its corresponding active set *A* *k* , *A* *σ*1 , and *A* *σ*2 .

In addition, we find the *local* extrema points (maxima for *k*(*p*) and

*σ*1(*p*), and minima for *σ*2(p)) and add points which are relatively

close to violate the bounds. For example, if *k*(*p**i*) is a local maxima

(i.e. *k*(*p**i*) *> k*(*p**i**−*1) and *k*(*p**i*) *> k*(*p**i*+1)) and *k*(*p**i*) *>* 0*.*95*k*,

we add *p**i* to the active set *A* *k* (and similarly for *σ*1(*p*)). If *σ*2(*p**i*)

is a local minima and *σ*2(*p**i*) *<* 1*.*15*σ*2, we add *p**i* to the active set

*A* *σ*2 . On the other hand, any point *p* in the active sets for which

the distortion goes sufficiently low is removed (we use thresholds

of 0*.*945*k*, 0*.*945*σ*1, and 1*.*2*σ*2)
