# PSG scalar balance and coefficient geometry

On0<x<pi/2, $L=-\log\cos x$, $U=x^2+L^2$, $K_\alpha=U^{-\alpha/2}$, $T=\tan x$, $H=x+LT$, $A=xH/(2U)$. Since $U'=2H$, $K_\alpha'=-\alpha HK_\alpha/U$. At a fixed point the multiplier is -2alpha A, so flip parameter is1/(2A). In L coordinates, $x=\arccos(e^{-L})$, $T=\sqrt{e^{2L}-1}$, and the scalar balance is $F=\log U+4A\log x=0$. Root replay gives L=.5319166892432992,x=.9428576799823384,A=.6740320257295228,alpha=.7418045150878947. It checks fixed residual and multiplier, but supplies no interval uniqueness or transcendence proof.

For v=2L, $a(v)=x(x+(v/2)T)/(2(x^2+v^2/4))$, $x=\arccos(e^{-v/2})$, $T=\sqrt{e^v-1}$. The archived differential-algebraic equation is $EF_1+F_0=0$, with E=e^v-1, $F_0=a(2a-1)(v+4-8a)^2$, and $F_1=(av-2a-2pv+1)(2av+4a-4pv-v-2)$, p=a'. This extracts E=-F0/F1 away from the exceptional branch.

The cleared field is $\widetilde X=D\partial_v+Dp\partial_a+N\partial_p$, $D=2av^2(2a-1)(v+4-8a)^2$. Its six listed factors are v,a,2a-1,v+4-8a and the two F1 factors. Darboux means $\widetilde X(H)=KH$. Listing and checking factors does not establish all-degree completeness. The source lacks full N and has a cofactor inconsistency: X(v)=D implies cofactor D/v, not D. Complete classification and algebraic-point exclusion need the missing global arguments.

The original26-term PSG source was reported to eliminate T using $T^2=Y^2-1$ into a100-term polynomial with even exponents U=x^2,Z=Y^2. Reconstruction T=-A/B needs the B=0 branch and integer-image conditions. Those actual26/100 coefficients were not recovered here; they remain explicitly missing rather than fabricated.

The sources mix numerical certification language with exact proofs, and one passage says A<1/2 while reporting A*=.674.... These contradictions are preserved in the archival extract and corrected in the canonical text. Neither a high-precision numerical root nor dense-intersection rhetoric establishes transcendence of alpha*.
