**6.3 Computing the Lipschitz Constants**

We now explain how to compute the Lipschitz constants *L**f**z* and

*L**f*¯

*z*

. A property of Lipschitz continuous complex functions is that

if *g* and *q* are *L**g* and *L**q* Lipschitz continuous respectively then

any linear combination *ag* + *bq* with complex coefficients *a* and *b*

is Lipschitz continuous with constant *|**a**|**L**g* + *|**b**|**L**q*.

Therefore, based on Equation (9), valid Lipschitz constants (not

necessarily the smallest) can be computed using

*L**f**z* 

=

*n*

X

*j*=1

*L**C**j* *0*

*|**ϕ**j* *|**,* 

(28)

*L**f**z*¯ = *L**f**z*¯ 

=

*n*

X

*j*=1

*L**C**j* *0*

*|**ψ**j* *|**,* 

(29)

where the only missing piece is *L**C**0*

*j*

, which is the Lipschitz con

stant of the derivative of the *j* *th* Cauchy coordinate (associated with

vertex *z**j* ).

**Proposition 10.** *The function* *C**j* *0* (*z*) *is Lipschitz at any point in*

*the domain excluding the cage vertices and its Lipschitz constant*

*is given by the following formula*

*L**C**0*

*j*

=

*|**z**j*+1 *−* *z**j**−*1*|*

2*π d*(*z**j**−*1)*d*(*z**j* )*d*(*z**j*+1)

*,* 

(30)

*where* *z**j**−*1 *and* *z**j*+1 *are the vertices adjacent to* *z**j* *on the cage*

Pˆ *and* *d*(*z**j* ) *is a function that computes the distance between the*

*segment* (*v*1*, v*2) *and the point* *z**j* *. See Figure 2 for notations.*

We prove this proposition in Appendix C.

During the preprocessing step, we compute a *|B| ×* *n* matrix of

Lipschitz constants, where *|B|* is the (typically large) number of

segments on which we want to compute the bounds and *n* is the

number of vertices in the cage. Then at runtime, as *ϕ* and *ψ* change

constantly, we need to evaluate Equations (28) and (29).

As can be seen from Equation (24), the tightness of the bounds

depends on the magnitude of *L* and *l*. Reducing *l* is achieved by

increasing the number of samples in *|B|* which decreases the length

of each segment. However, it turns out that we can also obtain

smaller *L**f**z*

and *L**f*¯

*z*

than those obtained by Equations (28) and

(29). For simplicity, we only describe the strategy to reduce the

magnitude of *L**f**z* . Reducing *L**f**z*¯ is done similarly. The idea is to

substitute the term *|**ϕ**j* *|* in Equation (28) by the more general term

*|**ϕ**j* + *az**j* + *b**|* *,* 

(31)

where *a* and *b* are complex constants. To see why this substitution

makes sense, let us first express *f**z* in a slightly different way

*f**z*(*z*) =

*n*

X

*j*=1

*C**j* *0* (*z*)(*ϕ**j* + *b*) = *−**a*+

*n*

X

*j*=1

*C**j* *0* (*z*)(*ϕ**j* + *b* + *az**j* )*,*

which is possible since *C**j* (*z*) are (complex) barycentric coordi

nates. The first equality is due to P *C**j* *0* (*z*) = 0 (constant precision)

and the second one is due to P *C**j* *0* (*z*)*z**j* = 1 (linear precision).

Then the Lipschitz constant is given by

*L**f**z* 

=

*n*

X

*j*=1

*L**C**j* *0*

*|**ϕ**j* + *b* + *az**j* *|**,* 

(32)

where the Lipschitz constant of *−**a* is zero hence omitted.

It is important to realize that the constants *a* and *b* can be chosen

differently on each segment. Ideally, for each segment we should

choose *a* and *b* that minimize *L**f**z* in Equation (32). This boils down

to solving a linear program with two complex variables. However,

solving *|B|* linear programs interactively is computationally chal

lenging. Instead, we suggest a heuristic for approximating the opti

mal solution, that turned out to be fast and effective in practice. For

each segment, we find the largest element *L**C**r* *0*

in *{**L**C**0*

*j*

*}* *n j*=1. We

choose another index *q* to be *r* + 1 if *L**C**0*

*r**−*1

*< L**C**0*

*r*+1

. Otherwise

we set *q* = *r**−*1. Finally *a* and *b* are chosen to satisfy the following

two linear equations

*ϕ**r* + *b* + *az**r* = 0*,*

*ϕ**q* + *b* + *az**q* = 0*,*

(33)

which guarantee that the largest element in *{**L**C**0*

*j*

*}* *n j*=1 and its

largest neighbor are contributing nothing to the sum of Equation

(32). Figure 3 shows a comparison of the obtained Lipschitz con

stants on a typical model with *n* = 78 cage vertices and *|B|* = 340

boundary segments on which we evaluate *L*.

**6.4 Nonvanishing Derivative**

The bounds that were computed in the previous section were ob

tained solely on the boundary of the domain. To certify the har

monic mapping *f* as bounded distortion mapping using Theorem

4, we also need to satisfy condition (5a). As explained in Section

4, the argument principle can be used to show that Equation (5a)

holds iff *f**z* does not vanish at every point inside the domain (note

that *f**z* = 0 on the boundary does not necessarily mean that *f**z* = 0

inside). Using our specific discretization, the integrand that appears

in Equation (5a) has an explicit simple formula. However, we were

unable to obtain a closed-form expression for its antiderivative. One

simple, direct and accurate way to obtain a sharp answer to whether

*f**z* vanishes is to evaluate the integral numerically. However, we

have developed an alternative which is several orders of magnitude

faster to evaluate. For that, we will need to rely on the following

theorem (proved in Appendix D).

**Theorem 11.** *Let* *f* *be a complex-valued harmonic function de-*

*fined on a simply connected domain* Ω*. Let* *θ*(*w*) *be any real-valued*

*continuous function defined on the boundary. We denote by* *γ* *the*

*function*

*γ*(*w*) = Re  *f**z*(*w*)ei*θ*(*w*) *.*

*If* *γ*(*w*) *>* 0 *at every point on the* boundary *then* *f**z* *does not vanish*

inside *the domain.*

In Appendix E we derive the Lipschitz constant *L**γ* and show how

to use it in order to formulate the following sufficient condition for

the positivity of *γ* on a specific segment

(2 +  *θ* 2 *−* *θ* 1 ) *l L**f**z* *<* (2 *−*  *θ* 2 *−* *θ* 1 )  *f**z* 1 +  *f**z* 2  *,* (34)

where *l* is the length of the segment,  *f**z* 1 *,*  *f**z* 2 are the values of

*|**f**z**|* at the endpoints, and *θ* 1 *, θ*2 are the values of *θ* at the endpoints.

Satisfying this condition on all the segments in *B* guarantees that

*f**z* = 0 throughout the entire domain. *θ* is chosen to be piecewise

linear, satisfying *θ*(*w* *i* ) = *−* arg *f**z*(*w*)  

*w**i* 

at the samples *w* *i* *∈ B*

Note that the argument function is multivalued and that off-the

shelf software implementations are designed to return the principal

branch which may lead to discontinuities in *θ*. To alleviate that,

we first compute the change in *θ* between each two consecutive

boundary samples by using

*dθ**i* = *Arg*(*f**z i* */f**z i**−*1 )*.*

*Arg* is the principal branch of arg. This avoids branching problems

since *f**z i* */f**z i**−*1 is typically very close to 1. We then compute the

cumulative sum of all the differences *dθ**i* to obtain *θ*(*w* *i* ).

Figures 1 and 4 show harmonic deformations that were obtained

using our algorithm. The global bounds were obtained by applying

the procedure explained in this section using 15*,* 000 boundary seg

ments. Evaluation of the distortion bounds took approximately 25

milliseconds.