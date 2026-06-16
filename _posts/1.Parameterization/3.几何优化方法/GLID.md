4 HARMONIC MAPS ON MULTIPLY-CONNECTED

DOMAINS

As mentioned in the Introduction, our work generalizes existing

techniques that are designed for simply-connected domains to

multiply-connected domains. We base our construction on the

following theorem which we prove in Appendix A.

Theorem 4.1 (Harmonic Decomposition). *Let* Ω *be a multiply*

*connected planar domain with* *N* *holes* *K*1, . . . ,*K**N* *, and choose* *N*

*arbitrary points* *ρ**i* *in* *K**i* *. Then, any harmonic map* *f* : Ω → C *can*

*be represented as:*

*f* (*z*) = Φ˜ (*z*) + Ψ˜ (*z*) +

*N*

Õ

*i*=1

*ω**i* ln |*z* − *ρ**i* | , 

(3)

*where* Φ˜ , Ψ˜ : Ω → C *are holomorphic functions, and* *ω*1, . . . ,*ω**N* *are*

*some complex coefficients.*

The harmonic decomposition (3) is unique up to an additive com

plex constant that can be chosen by setting e.g. Ψ˜ (*z*0) = 0 for an

arbitrary point *z*0 ∈ Ω. Theorem 4.1 extends a similar result for

simply-connected domains for which the summation term in (3) is

missing (c.f. [Duren 2004] Section 1.2). While Φ˜ (*z*) + Ψ˜ (*z*) is still har

monic on multiply-connected domains, the additional summation

term is essential to represent certain harmonic maps and without it,

the representation is incomplete.

4.1 Locally Injective Harmonic Maps

The main theoretical result in [Chen and Weber 2015] is a boundary

value characterization of the injectivity and the conformal-and

isometric distortion of planar harmonic maps on simply-connected

domains. We generalize this result to the multiply-connected case

(see Appendix B for the proof):

Theorem 4.2 (Bounded Distortion). *A planar harmonic map* *f* :

Ω → C *on a multiply-connected domain with exterior boundary curve*

*γ*0 *oriented counterclockwise and interior boundary curves* *γ*1 · · ·*γ**N*

*oriented clockwise, is locally injective with an upper bound* **k** ∈ [0, 1)

*on the conformal distortion, a lower bound* **σ****2** > 0 *on the small*

*singular value of the Jacobian, and an upper bound* **σ****1** < ∞ *on the*

*large singular value at every point* *z* *in* Ω *if and only if:*

∮ *γ*0 *f f* *z z* ′ ( ( *w w* ) ) *dw* + Õ *i N* =1 ∮ *γ**i* *f f* *z z* ′ ( ( *w w* ) ) *dw* = 0, 

(4a)

0 ≤ *k*(*w*) ≤ **k** 

∀*w* ∈ ∂Ω, 

(4b)

*σ*1(*w*) ≤ **σ****1** 

∀*w* ∈ ∂Ω, 

(4c)

**σ****2** ≤ *σ*2(*w*) 

∀*w* ∈ ∂Ω. 

(4d)

Intuitively, Theorem 4.2 states that in order to induce global dis

tortion bounds, it is sufficient to bound the distortion of a harmonic

map on the *boundary* curves *γ**i* as long as (4a) holds. The boundary

integral condition (4a) is equivalent to the condition that *f**z* is non

vanishing throughout the domain. Namely that *f**z* (*z*) , 0 (Appendix

B). In contrast to the simply-connected domain, the integral over

the exterior boundary *γ*0 may be nonzero. This gives rise to maps

which are not regular homotopic to the identity map but can still

be locally injective (see Figure 3).

As opposed to [Chen and Weber 2015], our deformation algorithm

does not *explicitly* impose user-defined bounds **k**,**σ****1**,**σ****2** on the

distortion. Instead, we favor an overall lower *average* distortion. By

using energies that become infinite when the map degenerates at

a boundary point, a finite bound on distortion is naturally formed

on the boundary. Theorem 4.2 then assures that this bound is also

global. At each iteration, our algorithm certifies the map as locally

injective by verifying that (4a) holds, as well as the following:

|*f**z* (*w*)| > |*f**z*¯(*w*)| 

∀*w* ∈ ∂Ω. 

(5)

In Section 8 we explain how to enforce (4a) and (5) in practice.

5 DISCRETIZATION

We discretize Equation (3) to obtain a finite dimensional space of

harmonic maps. The holomorphic functions Φ˜ and Ψ˜ are discretized

by using the Cauchy complex barycentric coordinates [Weber et al.

2009] which are derived by approximating the boundary of the

domain using a polygonal shape. Let 

ˆ

P = {*z*1, *z*2, ..., *z**m* }, 

*z**j* ∈ C

be the vertices of a multiply-connected planar polygon (the cage).

The vertices of the cage are split into sets such that the first set

represents the exterior polygon oriented counterclockwise while

the following sets represent the interior polygons oriented clockwise

The holomorphic functions Φ˜ and Ψ˜ are represented as:

Φ˜ (*z*) =

*m*

Õ

*j*=1

*C*˜ *j*(*z*)*φ**j* , 

Ψ˜ (*z*) =

*m*

Õ

*j*=1

*C*˜ *j*(*z*)*ψ**j* , 

(6)

where *C*˜ *j*(*z*) is the *j* *th* holomorphic Cauchy barycentric coordi

nate associated with vertex *z**j* and *φ**j* ,*ψ**j* are complex coefficients.

*C*˜ *j*(*z*) possess a rather simple closed-form expression (see Appendix

D). Note that while Weber et al. [2009] assumed that Pˆ is simply

connected, their derivation can be extended to the case of multiple

boundary components due to the fact that Cauchy’s integral formula

still holds. This can be done by integrating the Cauchy kernel over

*all* the boundary components. Practically, representing holomorphic

functions on such a domain simply boils down to using additional

basis functions that correspond to vertices that lie on the interior

boundaries. We note, that the complex barycentric map induced by

the Cauchy coordinates on multiply-connected domains has a non

empty null space of (complex) dimension 2*N* which corresponds to

a similarity transformation of the vertices of the interior boundary

polygons. To remove this ambiguity, we fix the first two complex

coefficients of each hole to zero.

We proceed by substituting the holomorphic functions Φ˜ and Ψ˜

in the harmonic decomposition (3) with the expressions from (6).

The additional term Í *i N* =1 *ω**i* ln |*z* − *ρ**i* | in (3) is substituted with the

expression:

*m*Õ+*N*

*j*=*m*+1

(*φ**j* +*ψ**j*) ln  *z* − *ρ**j*−*m*  , 

(7)

where *φ**j* ,*ψ**j* are 2*N* additional complex coefficients. Note that split

ting *ω**i* into two variables creates some unnecessary redundancy,

nevertheless it greatly simplifies the exposition as well as the imple

mentation. Later on, we will remove this redundancy by enforcing

a constraint *φ**j* = *ψ**j* , *j* = *m* + 1, . . . ,*m* + *N* for each hole. Finally,

rearranging terms and denoting *n* = *m* + *N* leads to:

*f* (*z*) =

*n*

Õ

*j*=1

*C**j*(*z*)*φ**j* +

*n*

Õ

*j*=1

*C**j*(*z*)*ψ**j* , 

(8)

*C**j*(*z*) = ( *C* ln ˜ *j* ( *z z*) − *ρ**j*−*m*  *j j* = = *m* 1, . . . , + 1, . . . , *m n*

Equation (8) is our closed-form expression for a finite dimensional

harmonic subspace with 2*n* complex variables {*φ**j* ,*ψ**j* } *n j*=1 . The di

mension of the (complex) null space is 4*N* + *N* + 1, where 4*N* is

due to the 2 complex DOF per hole for each of the two Cauchy

barycentric maps (as explained above), *N* is due to the redundancy

introduced by Equation (7) and the term 1 is due to the constant

DOF of the harmonic decomposition (3).

We proceed by constructing simple formulas for the Wirtinger

derivatives of our harmonic map. Luckily, just like the map itself,

it can be expressed in closed-form. By linearity of the Wirtinger

operators, the fact that the derivative of the Cauchy coordinates

with respect to *z* is 0, and assuming that *φ**j* = *ψ**j* , ∀*j* = *m* + 1, . . . ,*n*

we have:

*f**z* (*z*) =

*n*

Õ

*j*=1

*D**j*(*z*)*φ**j* , 

*f**z*¯(*z*) =

*n*

Õ

*j*=1

*D**j*(*z*)*ψ**j* , 

(9)

*D**j*(*z*) = ( *D*˜ *j*(*z*

) 

*j* 

= 

1, . . . ,

*m*

*z*−*ρ* 1

*j*−

*m*

*j* 

= *m* 

\+ 1, . . . ,

*n*.

The derivatives of the Cauchy barycentric coordinates *D*˜ *j*(*z*) (Ap

pendix D) are holomorphic and so is *z*−*ρ* 1

*j*−*m*

, hence it is clear that

*f**z* and *f**z*¯ are both holomorphic (though not necessarily integrable).

6 ISOMETRIC ENERGIES

The main approach in interactive shape deformation is to design

and minimize a distortion energy that aggregates a differential

quantity that strives to keep the map as-isometric-as-possible. Such

differential quantities are minimized when the map is locally iso

metric. However, since a perfect isometry cannot be obtained in

general in the presence of positional constraints, the particular defi

nition of proximity to isometry greatly affects the end result. It is a

common practice to measure distortion at a point *z* as a function

E(*z*) = E(*σ*1(*z*), *σ*2(*z*)) of the two singular values of the Jacobian ma

trix *J**f* (*z*). Such a function is invariant to rigid motions of both the

source and the target domains [Rabinovich et al. 2017]. E(*z*) should

be minimized (at a single point *z*) if *σ*1(*z*) = *σ*2(*z*) = 1. Energies

that minimize *conformal* distortion are also popular. Our harmonic

subspace contains many pure (with zero distortion) conformal maps,

hence, if desired, we can simply restrict the subspace by eliminating

the *ψ**j* variables and use any of our isometric energies to regularize

the result (Figure 5).

A popular choice in graphics is the as-rigid-as-possible (ARAP)

energy [Igarashi et al. 2005; Liu et al. 2008; Sorkine and Alexa 2007]

which defines local proximity to isometry via ∥*J* −*R*∥ *F* 2 , where ∥ · ∥*F*

denotes the Frobenius norm, and *R* denotes the closest rotation to

*J*. It can be expressed as EARAP = (*σ*1 − 1) 2 + (*σ*2 − 1) 2 . The main

limitation of ARAP is that it favors shrinkage over expansion, and

in particular it stays finite even if the map is degenerated (*σ*2(*z*) = 0).

Hence, ARAP tends to attract the map to a configuration which is

not locally injective. Our solver and derivation are applicable to

EARAP, albeit ARAP is arguably a poor choice of energy if local

injectivity is sought after.

Appropriate choices of isometric energy for designing locally in

jective maps become infinite when the map collapses locally, which

serves as a natural barrier term. Since our optimization depends on

Input 

AMIPS 

Conformal

Fig. 5. Harmonic deformations of a triply-connected domain. The domain

on the left has *N* = 2 holes in it. The result in the middle minimizes the

Advanced MIPS energy, while the one on the right is a pure conformal map

with least isometric distortion.

high order derivatives, we focus on energies which are smooth in

our variables *φ**j* ,*ψ**j* . To this end, we express the distortion measure

at *z* as a smooth function of |*f**z* | 2 and |*f**z*¯| 2 . Since |*f**z* | 2 and |*f**z*¯| 2

are quadratic functions in *φ**j* ,*ψ**j* , the composition is also smooth.

The symmetric Dirichlet isometric energy Eiso = 1 2 |*J*| *F* 2 + 1 2 |*J* −1 | *F* 2

has been successfully used in [Kovalsky et al. 2016; Rabinovich et al.

2017; Schreiner et al. 2004; Smith and Schaefer 2015] for mesh pa

rameterization. It can be expressed in terms of the singular values:

Eiso(*σ*1, *σ*2) =

2 1 *σ*1 2 + *σ*1 −2 + *σ*2 2 + *σ*2 −2

(10a)

=

*σ*

2

1

\+ *σ*

2

2

2

  1 + *σ*1 2 1 *σ*2 2 ! . 

(10b)

Recall that for an orientation preserving locally injective planar

map *f* , we have *σ*1 = |*f**z* | + |*f**z*¯| and *σ*2 = |*f**z* | − |*f**z*¯|. We get:

*σ*

2

1

\+ *σ*

2

2

2

= |*f**z* | 2 + |*f**z*¯| 2 , 

*σ*1*σ*2 = |*f**z* | 2 − |*f**z*¯| 2 , 

(11)

where the left term is the Dirichlet energy and the right term is

det(*J*). Substituting into Equation (10b) gives:

Eiso(|*f**z* | 2 , |*f**z*¯| 2 ) = |*f**z* | 2 + |*f**z*¯| 2 © ­ ­

«

1 +

1

|*f**z* | 2 − 

|*f**z*¯| 2 2 ª ® ®

¬

,

which is clearly smooth in |*f**z* | 2 and |*f**z*¯| 2 since |*f**z* | 2 , |*f**z*¯| 2 .

In Table 1, we list several possible choices for such smooth iso

metric energies. These include the exponential symmetric Dirichlet

isometric energy: Eexp = exp(*s* · Eiso) [Rabinovich et al. 2017]. The

motivation to use Eexp is to penalize more drastically high values of

the distortion measure. As demonstrated in Figure 6, this allows the

user to trade-off low average versus low maximal distortion. Finally,

we include the Advanced MIPS energy [Fu et al. 2015] which pro

vides user-controlled balance between area preservation and angle

preservation.

We define the isometric distortion of a planar harmonic map *f*

as a boundary integral over the pointwise distortion quantity E(*w*):

E *f* = ∮ ∂Ω E(*w*)*ds*

We use the superscript *f* throughout the paper to denote the bound

ary integrated distortion and omit it to denote the pointwise quantity.

We also experimented with an area integral instead of the boundary

one, but did not notice any benefit. Theorem 4.2 ensures that for any

bound on E(*w*) along the boundary, a global upper bound on *σ*1(*z*),

and a global lower bound on *σ*2(*z*) exist. Hence, a global bound on

E(*z*) is naturally formed.

The gradient and the Hessian of the overall isometric energy are:

∇E *f* = ∮ ∂Ω ∇E(*w*)*ds* 

(13)

∇ 2E *f* = ∮ ∂Ω ∇ 2E(*w*)*ds*. 

(14)

The gradient and the Hessian of our energy measures have relatively

simple closed-form expressions. A complete derivation is given in

Appendix E. Let *D* = (*D*1,*D*2, . . . ,*D**n*) ∈ C 1×*n* be a complex row

vector, where *D**j* is defined as in (9). We use bold symbols to denote

*real* vectors and matrices. Define the real matrix **D** (note the bold

symbol) as:

**D** = Im Re ( ( *D D* ) ) − Re Im (*D* (*D* ) ) ∈ R 2×2*n* . 

(15)

We express the complex Wirtinger derivatives as 2×1 real vectors:

**f****z** = Im Re ( ( *f f* *z z* ) ) , **f****z****¯** =     



Im Re  *f f* *z z* ¯ ¯        ∈ R 2×1 . (16)

The gradient of E with respect to the 4*n* real variables is:

∇E(*z*) = 2 *α α* 1 2 **D D** T T **f f** **z z** **¯** ∈ R 4*n*×1 , 

(17)

where *α*1, *α*2 are real parameters which depend on the particular

choice of energy. Table 1 provides the parameters needed to instanti

ate some particular energies (out of many possible). The expression

for the 4*n*×4*n* Hessian of E(*z*) at a single point is:

∇ 2E(*z*) = **D** 0 T **D** 0 T

|  {z  }

4*n*×4

|{z} **K**

4×4

**D** 0 **D** 0

|  {z  }

4×4*n*

∈ R 4*n*×4*n* , 

(18)

where **K** is the a 4×4 real matrix:

**K** = " 2*α*1*I* 4*β* + 3 4 **f****z** *β* **¯** 1 **f****z** **f** T **z** **f****z** T 2*α*2*I* 4 + *β*3 4 **f** *β* **z** 2 **f f** **z****¯** **z****¯** T **f****z****¯** T # ∈ R 4×4 . (19)

The parameters *β*1, *β*2, *β*3 are also energy dependent (see Table 1).

6.1 Positional Constraints

The point-to-point (P2P) metaphor is an intuitive drag-and-drop

user-interface that best fits interactive deformation tasks. The user

of our system can add or remove (by clicking) positional constraints

at any time during interaction. Dragging the P2P handles signals the

application to invoke the optimization and to render the updated

result. We incorporate the P2P constraints as soft constraints as was

advocated by [Chen and Weber 2015; Poranne and Lipman 2014;

Rabinovich et al. 2017]. We define the P2P energy:

E

*f*

p2p 

=

1

2

|P |

Õ

*i*=1

|*f* (*p**i*) − *q**i* | 2 ,

where *p**i* ∈ P ⊂ Ω is the position of the *i* *th* handle in the source

domain, and *q**i* ∈ C is its target desired position. The gradient and

the Hessian of E

*f*

p2p 

are derived in Appendix F. The full energy of

our unconstrained minimization problem is:

E

*f*

Def 

= E *f* + *λ*E

*f*

p2p

, 

(20)

where *λ* is a user-defined weight that balances the two terms.

7 POSITIVE DEFINITE HESSIAN

The Hessian of E

*f*

p2p 

is positive semi-definite (PSD). However, the

Hessian of E *f* is, in general, not PSD, and neither is the Hessian of

E

*f*

Def 

(Equation (20)). Our key observation here is that the closest

(in Frobenius norm) PSD matrix to the Hessian ∇ 2E(*z*) ∈ R 4*n*×4*n* at

a *single* point *z*, can be expressed in closed-form. With that at hand

we substitute Equation (14) with:

∇ 2E *f* + = ∮ ∂Ω ∇ 2E + (*w*)*ds*, 

(21)

where ∇ 2E +(*w*) is the closest PSD matrix to ∇ 2E(*w*). Since, the in

tegral (or sum) of PSD matrices is PSD (due to the convex cone

structure of the PSD set), it is clear that the modified Hessian of

the isometric energy (21) is guaranteed to be PSD. In Appendix I,

we further show that the dimension of the null space of (21) in

the case of Eiso and Eexp is 2 or 3. Therefore with 2 or more posi

tional constraints, ∇ 2E *f* + is nonsingular. We refer to the variant of

Newton’s method that computes the closest PSD matrix to ∇ 2E *f*

as Newton-Eigen and stress that our modified Newton iterations

are dramatically faster to compute. Moreover, throughout extensive

experiments, we observe that our local modification leads to itera

tions which are more *effective*, where less iterations are required for

convergence (Figures 1, 10, 11).

7.1 Hessian Modification

Our goal is to compute the eigen-factorization of the local Hessian

matrix ∇ 2E. On the one hand, doing it numerically is impractical,

whereas on the other hand, analytic eigen-factorization of a 4*n*×4*n*

matrix is challenging to derive. Our first observation is that each

of the nontrivial eigenvectors (with nonzero eigenvalue) of ∇ 2E

can be expressed as a product of **B** = **D** 0 **D** 0 and a corresponding

eigenvector of **K** (Equation (19)). This is due to the fact that **B** has 4

rows that are orthogonal to each other (easy to verify by comput

ing the inner product of each pair) and all the rows have the same

norm. Furthermore, the eigenvalues of **K** and ∇ 2E are the same up

to a positive scale. Hence, we have reduced our problem to that of

analytically computing the eigenvalues of a 4×4 matrix. This is still

challenging as these are the roots of a 4 *th* order polynomial. De

note the (unsorted) eigenvalues of **K** as (*λ*1, *λ*2, *λ*3, *λ*4). Our second

observation is that *λ*1 = 2*α*1 and *λ*2 = 2*α*2. To see why 2*α*1 is an

eigenvalue, subtract 2*α*1 from the diagonal of **K**. The first two rows

of **K** − 2*α*1*I* are:

**f****z**

|{z}

2×1

h 4*β*1 **f****z** T 4*β*3 **f****z****¯** T i

|  {z  }

1×4

, 

(22)

where we can see that the 1×4 row vector on the right hand side of

(22) is multiplied by two scalars (the elements of **f****z** ), hence, these

two rows are linearly dependent, meaning that the matrix**K**−2*α*1*I* is

singular and 2*α*1 is a root of the characteristic polynomial. Showing

that 2*α*2 is an eigenvalue can be done similarly. Knowing that 2*α*1

and 2*α*2 are two eigenvalues of **K**, we can compute the other two

eigenvalues by directly solving the quartic characteristic equation.

The derivation is long but straightforward, hence omitted. We get

these expressions:

*λ*3,4 = *s*1 ± q *s* 2 2 + 16*β* 3 2 |*f**z* | 2 |*f**z*¯| 2 , 

(23)

where *s*1,2 = *α*1 + 2*β*1 |*f**z* | 2 ± *α*2 + 2*β*2 |*f**z*¯| 2 .

The corresponding four eigenvectors are:

0 Im , (*f**z* ), −Re 0 ( , *f**z* ), Im( 0 *f* , *z*¯), −Re(*f**z*¯ 0 )

Re Re ( ( *f f* *z z* ) ) , , Im Im ( ( *f f* *z z* ) ) , , *t t* 1 2 Re Re ( ( *f f* *z z* ¯ ¯ ) ) , , *t t* 1 2 Im Im ( ( *f f* *z z* ¯ ¯ ) )

(24)

where:

*t*1,2 =

*λ*3,4 − 2*α*1 − 4*β*1 |*f**z* | 2

4*β*3 |*f**z*¯| 2

.

The signs of these eigenvalues depend on the particular choice of

isometric energy, therefore in the most general case, the 4 eigenval

ues are evaluated and negative ones are substituted with 0 to obtain

the modified Hessian. For particular energy choices, it is possible

to simplify matter even more. For the first two energies listed in

Table 1, we have that only *λ*1 = 2*α*1 can be (at times) negative. This

allows us to directly express the modified matrix. For example, for

Eiso, it turns out that *λ*3, *λ*4 have quite simple expressions:

*λ*3 = 4(1 + 3(|*f**z* | + |*f**z*¯|) −4 ), 

*λ*4 = 4(1 + 3(|*f**z* | − |*f**z*¯|) −4 ).

The spectrum is then sorted as follows: 2*α*1 ≤ *λ*3 ≤ 2*α*2 ≤ *λ*4. With

this information at hand, the modification is done by checking for

the sign of *α*1, and if it is negative, we substitute **K** in (18) with:

**K** + =

 

 

 

( | 2 *f**z* *α*1 | 2 + 4*β*1)

**f****z** **f****z** T

4

*β*3 

**f**

**z** 

**f**

**z****¯**

T

4*β*3 **f****z****¯** **f**

T

**z**

2*α*2*I* 

\+ 

4

*β*

2 

**f**

**z****¯** 

**f****z****¯**

T    

 

. 

(25)

8 LOCALLY INJECTIVE CERTIFICATION

To ensure that the map is locally injective at each iteration, we

need to verify that Conditions (4a) and (5) hold (Section 4.1), and

backtrack during line search otherwise. As (5) involves infinite

number of inequalities: |*f**z* (*w*)| > |*f**z*¯(*w*)| 

∀*w* ∈ ∂Ω, we use a

simpler sufficient condition based on a finite number of conditions

following the approach of [Chen and Weber 2015] which utilizes

the fact that the Wirtinger derivatives are Lipschitz continuous.

Condition (5) can be enforced on the entire boundary by enforcing it

(individually) on many small boundary segments. For each segment

[*v**i* ,*v**i*+1] (see Figure 4 for notations), we compute lower and upper

bounds for |*f**z* | and |*f**z*¯| respectively as follows:

|*f**z* |min B

|*f**z* (*v**i*)| + |*f**z* (*v**i*+1)|

2

−

*L**f**z* *l*

2

≤ 

min

*w* ∈[*v**i* ,*v**i*+1]

|*f**z* (*w*)|,

|*f**z*¯|max B

|*f**z*¯(*v**i*)| + |*f**z*¯(*v**i*+1)|

2

+

*L**f**z*¯ *l*

2

≥ 

max

*w* ∈[*v**i* ,*v**i*+1]

|*f**z*¯(*w*)|.

*L**f**z* and *L**f**z*¯ are the corresponding Lipschitz constants on the seg

ment, and *l* = |*v**i* −*v**i*+1 |. Condition (5) is then substituted with:

|*f**z* (*v**i*)| − |*f**z*¯(*v**i*)| + |*f**z* (*v**i*+1)| − |*f**z*¯(*v**i*+1)| ≥ (*L**f**z*¯ + *L**f**z* )*l*, (26)

or more concisely:

*σ*2(*v**i*) + *σ*2(*v**i*+1) ≥ (*L**f**z*¯ + *L**f**z* )*l*. 

(27)

It is crucial that the sufficient condition above is as tight as possible,

as otherwise the Newton step size may become too small and will

stop the Newton iterations prematurely. Note that the condition

becomes tighter as the Lipschitz constants and/or the length of the

segment *l* decrease. Since denser sampling requires more computa

tions, it is advised to obtain as small as possible Lipschitz constants.

In Appendix H, we derive the following Lipschitz constants that

can be used on multiply-connected domains. More importantly,

our newly-derived constants are significantly smaller than those of

BDHM.

*L**f**z* =

|*f**z* ′ (*v**i*)| + |*f**z* ′ (*v**i*+1)|

2

+

*l*

2

© ­

«

Õ *m*

*j*=1

*L**j* |*s**j* − *s**j*+1 | + Õ *n*

*j*=*m*+1

*L* *h j* |*φ**j* | ª®

¬

*L**f**z*¯ =

|*f* *z*¯ ′ (*v**i*)| + |*f* *z*¯ ′ (*v**i*+1)|

2

+

*l*

2

© ­

«

Õ *m*

*j*=1

*L**j* |*t**j* − *t**j*+1 | + Õ *n*

*j*=*m*+1

*L* *h j* |*ψ**j* | ª®

¬

where *L**j* = 2*πd* 1

2

(*z**j*) , *L* *h j* = *d* 3 (*ρ* 2

*j*−*m*

) , *d*(*z*) is the distance from a

point *z* to the segment, *s**j* = *φ*

*j*

−

*φ*

*j*

−

1

*z*

*j*

−

*z**j*

−

1

, and *t**j* = *ψ*

*j*

−

*ψ*

*j*

−

1

*z*

*j*

−

*z**j*

−

1

. In Figure

7 we compare the Lipschitz constants obtained with our formulas

against that of BDHM and show that they are significantly

We now turn to Condition (4a) requiring that the boundary in

tegral (or equivalently the number of zeros of *f**z* ) is 0. Theorem

11 in [Chen and Weber 2015] provides a sufficient (but not neces

sary) condition that implies (4a), albeit their proof assumes that the

domain is simply-connected. We show a much stronger result by

deriving a new condition which is applicable to multiply-connected

domains, and is both necessary and sufficient as long as (27) holds.

The following theorem is proved in Appendix C.

Theorem 8.1. *Let* *д*(*z*) *be an* *L**-Lipschitz continuous holomorphic*

*function in a neighborhood of a simple open curve with length* *l* *and*

*two endpoints* *v**i* ,*v**i*+1 ∈ C *such that:*

|*д*(*v**i*)| + |*д*(*v**i*+1)| > *Ll*, 

(28)

*then:* ∫ *v**i* *v**i*+1 *д д* ′ ( ( *z z* ) ) *dz* = ln   *д д* (*v* (*v* *i*+ *i*) 1)   + i Arg *д д* (*v* (*v* *i*+ *i*) 1) , (29)

*where* Arg *is the principle branch of the complex argument function.*

Theorem 8.1 is applicable to our *f**z* along any line segment

[*v**i* ,*v**i*+1] since our algorithm always verifies that (27) holds (which

implies (28)). Consequently we have the following corollary.

Corollary 8.2. *Under the assumption that* (27) *holds,* *f**z* *does not*

*vanish inside the multiply-connected polygon* P *if and only if:*

*N*

Õ

*j*=0

Õ 

*i*

Arg *f**z* 

(*v*

*j*

*i*

+

1

)

*f**z* 

(*v*

*j*

*i*

)

= 0, 

(30)

*where the first summation is over the polygonal loops, and the second*

*one is over the segments in each loop.*

Proof. It follows immediately from Cauchy’s argument principle

and (29) that:

2*π*iN = ∮ ∂Ω *f f* *z z* ′ ( ( *w w* ) ) *dw* = Õ *j N* =0 Õ *i*  ln    *f**z* *f**z* (*v* (*v* *i j* + *i j* 1 ) )   + iArg *f**z* *f**z* (*v* (*v* *i j* + *i j* 1 ) ) ! ,

where N is the number of zeros of *f**z* . The ln | · | terms cancel since

ln *x*/*y* = ln *x* − ln*y* and all the boundary polygons are closed. 



To conclude, we first verify that (27) holds on all the boundary

segments and if so, we simply compute the sum in (30). If it is zero,

the map is *guaranteed* to be locally injective everywhere.