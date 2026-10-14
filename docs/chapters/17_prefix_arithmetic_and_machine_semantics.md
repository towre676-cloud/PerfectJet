# Prefix arithmetic and machine semantics

For normal finite binary64 values, x=(-1)^s(2^52+F)2^{E-1075}. Subnormals, zeros, infinities and NaNs require separate semantics. The frozen MIE mapping flips the sign bit for nonnegative encodings and complements all bits for negative encodings. Prefix lcp(a,b)=clz(MIE(a) xor MIE(b)); k(x)=lcp(x,+0), D=64-k. Signed zeros remain distinct in the historical golden model; NaNs used k0/COLLAPSED. A prefix ultrametric2^-lcp on distinct encodings is not ordinary numerical distance.

Restricted transfer predictions included ADD=min(kA,kB),MUL=max(0,kA+kB-53),DIV=max(0,kA-kB),SQRT=max(0,kA-1),FMA=min(MUL,kC). They are retained explicitly as heuristics/restricted-semantic claims, not universal floating-point guarantees. Binade changes, carry, cancellation, exponent alignment, normalization, jamming, rounding, exception handling and extended precision can alter leading bits independently of mantissa precision.

The candidate prefix-Fermat condition k(f(x+delta),f(x))>=k(delta)-kappa_f connects the bit geometry to divided differences, Lawvere/Fermat theories, jets and Kahler differentials. A concrete operation/domain is needed before it becomes a theorem. The original PADD/PSC definitions, segmented-adder semantics, and complete corner-case model were not recovered sufficiently to implement them. A Chisel ordinary addition expression is not proof of those semantics.

The exact dyadic power test is different and sound: write nonzero finite rational dyadic x=+/-u2^e with u odd. It is a rational dth power iff u is an integer dth power and d divides e, with a negative sign only when d odd. Zero is separate. This is arithmetic of the value, not a heuristic prefix-depth prediction.

The historical corrected experiment found lambda_min16 inactive because mean k~1; collision1/escalation0 null; an LCP margin due to initialization; and H2 due to trivial weight shrinkage. Training had not established induced prefix geometry. The December modular-addition Transformer run had training~.99 but validation~.3333 through epoch1000, with ranks about13,76,78 across encoders. These negative results remain in the corpus.
