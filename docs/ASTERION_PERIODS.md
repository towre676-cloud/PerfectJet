# Exact modular periods and character cancellation

`asterion_periods.py` supplies a bounded exact formal-series certificate for classical theta, elliptic-period and modular-character identities. It uses **Q=exp(pi*i*tau)** for theta series and **q=exp(2*pi*i*tau)=Q^2** for the level-one E8 character. Interchanging these variables changes the first nonconstant coefficient and invalidates the comparisons. The implementation is new program machinery; the mathematical identities are classical.

Define

\[
\theta_3(Q)=1+2\sum_{n\ge1}Q^{n^2},\qquad
A(Q)=\sum_{n\ge0}Q^{n(n+1)},\qquad
\lambda(Q)=\frac{16QA(Q)^4}{\theta_3(Q)^4}.
\]

The lambda branch begins \(16Q-128Q^2+704Q^3-3072Q^4+\cdots\). Its zero constant term makes formal composition well-defined. The exact Gauss coefficients are

\[
F(\lambda)={}_2F_1(1/2,1/2;1;\lambda)
=\sum_{n\ge0}\frac{\binom{2n}{n}^2}{16^n}\lambda^n.
\]

The engine verifies \(F(\lambda(Q))=\theta_3(Q)^2\), followed by

\[
E_4(Q^2)=(1-\lambda+\lambda^2)F^4,\qquad
\Delta(Q^2)=\frac{\lambda^2(1-\lambda)^2F^{12}}{256}.
\]

The references are the complete elliptic integral and hypergeometric expansion in [DLMF 19.5](https://dlmf.nist.gov/19.5), the theta/elliptic relations in [DLMF 20.9](https://dlmf.nist.gov/20.9), and the modular definitions in [DLMF 23.15](https://dlmf.nist.gov/23.15). Here lambda denotes the modular lambda function \(k^2\); other sections of elliptic-integral tables sometimes reuse the letter for a different auxiliary quantity, so the displayed definition is part of the contract.

The normalized level-one E8 character is \(H(q)=E_4(q)/\phi(q)^8\), obtained from the existing `CurrentPopulations.simple` implementation. The full character is \(\chi(q)=q^{-1/3}H(q)\). The period factors cancel in its cube:

\[
H(Q^2)^3
=\frac{256Q^2(1-\lambda+\lambda^2)^3}{\lambda^2(1-\lambda)^2},
\qquad \chi(q)^3=j(\tau).
\]

This is implemented as exact composition, multiplication and inversion of rational formal series. The denominator has valuation two in Q. To verify through order N, the program computes through N+2 before cancelling Q^2 and inverting the remaining unit series. It rejects direct inversion of lambda, whose constant coefficient is zero. At the default order 16, the theta/period, E4 and Delta comparisons each check 19 coefficients, including the guard orders, while the character-cube comparison checks 17 coefficients. The normalized character cube begins \(1+744Q^2+196884Q^4+21493760Q^6+\cdots\), with no odd powers.

`periods_receipt(order=16)` returns JSON-safe coefficients, all residual arrays, the nome convention, source URLs and an explicit finite scope. Orders from zero through forty are accepted. The maximum order checks 43 coefficients for the period/modular identities and 41 for the normalized character cube. The tests independently catch the Q-versus-q substitution error, check guard-order stability against a larger truncation, reject nonunit inversion and invalid orders, and run the maximum precision. Run `PYTHONPATH=src python -m unittest tests.test_asterion_periods -v` to replay them.

Finite coefficient agreement is recorded as finite evidence for the cited classical identities. This component does not establish new analytic continuation, identify these periods with the program's KZ local system, construct an elliptic quantum group, or prove an arithmetic-31 correspondence. Those comparisons remain distinct research tasks.
