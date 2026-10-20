"""Explicit coverage census for every project family and enhancement in the session."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

GROUPS={
'01':('Historical audit',['Computational arithmetic geometry','Arithmetic-spectral effective dimension','Sufficient representation','Restrict transport reduce evolve count','Chronology February2025-October2026','User goals: complete populations and useful decisions']),
'02':('Arithmetic',['Morphonic arithmetic kernel','PerfectPower perfect-power density','Polynomial identities','Sparse growth classes','Mordell curves','Thue equations','Cubic fields and orders','Quartic coverings','Runge methods','Bilu-Tichy','OEIS sequence discovery','Abelian heat and Dirichlet transforms','Heights and Baker-Matveev bounds','Signed rank-two sieve','Arithmetic oscillator program']),
'03':('Pell and transport',['Pell unit orbits','Generalized Pell seed inventory','Quadratic norm matrices','Sqrt2 atlas','Pell7 family','Finite-state congruence filtering','Affine polynomial pullbacks','Solution-carrying descent','Thue23 leaves','D72 residual equation','Integral-image reconstruction','Question-dependent height','Adaptive local sieve']),
'04':('Descent and lattices',['Cubic etale Kummer bridge','Norm-square versus Selmer','S-units','Class-group correction','Complete local Kummer images','Global Selmer intersection','Cassels-Tate and Sha frontier','Rational rank bounds','Global saturation','Prime-specific bounded division','Torsion-aware relation lattices','Hermite and Smith forms','Isogeny point transport','Rational versus integral kernel','Anonymous -107 field descent','457-curve census']),
'05':('Populations',['Petersen50 population','Residual-polynomial decomposition','Meet-in-the-middle','Weighted symmetry compression','Generating polynomial resource use','Conditional completion counts','Original-order ranking','Inverse ranking','Uniform sampling','Maximizer tie count','Factor elimination','Auxiliary witness uniqueness','Distinct-output populations','CRT interval populations','Restricted-digit sums','Monomial degree counts','Integer calibration','Optimization over infinite families']),
'06':('Series',['Weighted automaton series','Positive-cost transfer resolvent','Fibonacci population','Zero-series initialization','Linear response Markov parameters','Word-indexed Hankel rank','Signed versus probabilistic realization','Weighted quotient aggregation','Coefficientwise cost preservation','Multi-output predictive state']),
'07':('Semantics and observations',['SOE legal implementation fibres','Delayed implementation selection','Partial-state definedness','All-future equivalence','Shortest distinguishing words','SOE Lean quotient theorem (upstream)','324 two-state examples (upstream)','Fin2 generator limitation','Adaptive2 versus fixed3 diagnosis','Observable row-space closure','Hidden target witness','Quadratic fibre curvature','Target sensor repair','Delay-coordinate memory','Question-family refinement','Joint representations','Preservation profile']),
'08':('Dynamics',['Polynomial feature closure','Exact coefficient replay','Nonlinear closure defect','Residual-state augmentation','Missing monomial/lag/action features','Initial evolution input error separation','Continuous Lyapunov','Discrete Lyapunov','Schur-Cohn and Routh-Hurwitz frontier','General metric search','Correlated domains and zonotopes','All-time bounds','Roundoff versus model error','Compositional error','Decision margin certificate','Parameter sensitivity state','Descriptor mass matrices','Direct feedthrough','Continuous sampling limits','Switching model limitations','DynaComp native workload economics']),
'09':('Energy and reduction',['HLR carrier and mass inner product','Corrected HLR sign and factor','Zero decay dial','CRO decay estimate','Crystalline rank-one determinant','Compact manifest/receipt idea','IMP Inertial Manifold Projector','SVD invariant-space correction','Fixed-mode decomposition','General retained dynamics','Nonnormal transient behavior','Catmull-Clark local block','Subdivision operator identity','Loop Doo-Sabin Kobbelt Butterfly extensions','Transformer effective rank','CountSketch telemetry','Diffusion mode claims','MEF computational-field design','Arithmetic Shadow speculation','Global refinement period claims']),
'10':('PSG',['PSG defining nonlinear map','Scalar balance flip reduction','Correct multiplier normalization','Numerical flip root','Coefficient curve in v=2L','Exponential extraction','Exceptional denominator factors','Darboux polynomial test','Full prolonged numerator missing','All-degree classification gap','26-term source/100-term elimination missing','B=0 exceptional reconstruction','A amplitude contradiction','Cofactor D versus D/v']),
'11':('Jets',['Root-centered versus origin germ','Finite jet nonidentifiability','Riccati mimicry','Riccati residual rejection','Schroeder flip resonance','Involution criterion','Second-iterate cubic obstruction','Recentered two-cycle sign','Puiseux expansion','B5/B7 triangular selection reports','MTB/GTT proposed taxonomy','Feigenbaum depth profile','Pade and Borel-Stokes archive','Fourteen-step preimage chain','PSG transcendence frontier']),
'12':('Collision arithmetic',['Valuation collision form','Divisor fibre multiplicity','Collision zeta Euler product','Positive-temperature divergence','Coprime endpoint6/pi2','Thermal H_t table','Cyclotomic finite numerator','Complete and partial Gauss blocks','Affine-periodic coefficient state','Stride-L second difference','10^100 index query','Arithmetic penalty not PSD','Positive valuation Gaussian','Prime-zeta branch decomposition','Regularized finite-part product','Tail error bound','Failed finite-part D2 weld']),
'13':('Conductors',['PhaseNet deformation-conductor networks','Finite Heisenberg clock/shift convention','Irrational noncommutative torus','Continued-fraction approximation tower','Quadratic modules S and T','Gauss factor','Weil commutant','Dyadic operator-model distinction','CRT factorization','Fourier degeneracy maps (archive)','Old/new sectors (archive)','Quantum dimension volume','Root/coroot normalization','Fusion wall monic variable','DAT/DAU cost and noise gates','DBD pentagon/spinor obstruction','Native fault graph extraction','Peierls subcritical tail','Colored walk histogram','Weighted pressure covariance','Phase domination','Primitive rays and Farey cells','Orchard visibility is not threshold evidence']),
'14':('Shadow-Core',['5_2 abelian shadow','Discriminant-23 nonabelian core','Explicit cubic field transports','Critical boundary/core factorization','Exact Hessian field element','Exact vertex field element','Polynomial versus field discriminant','Selected Bloch-Wigner regulator','All-conjugate regulator cancellation','Oriented regulator vector','Corner divisibility bounded scan','Theta28-row9-field atlas','Ramified23 local field','Coefficient-ring execution','CoreLift receiving-space architecture']),
'15':('Weyl and invariants',['Monomial Moyal coefficient S_k','Hahn3F2 form','Degree-safe exactness','Cubic quantum obstruction','Polynomial molecular cancellation','Sextic transvectant gates','Universal quartic partner','C3 degree8 partner','Exceptional quintic40/7','Cube-root spine factor','Kernel versus active quotient','Finite partner census3..12','Symbolic rank-minor loci','Squarefree quintic pair','R5 elimination factor','Orbit3->1 correction','Numerical orbit certificate limitation','R7/R9 characteristic-zero gap','N11 census boundary','Incidence variety','No-go theorem scope']),
'16':('Deformation and codes',['Cotangent-complex fibre','Square-zero point lift','Node/cusp tangent obstruction','Tjurina basis','E37 gauge versus moduli','Discriminant changes under gauge','Perfect-complex/RHom proposals','Zsqrt-5 Picard/K0 comparison','Weight-one realization limit','Artin-Schreier-Witt','Hermitian AG codes','P5 weight enumerator','Alternate X_q code','MK-VII refutation']),
'17':('Machine arithmetic',['IEEE754 normal encoding','MIE monotone encoding','Shared-prefix depth','Prefix ultrametric','Signed zeros NaNs subnormals','PADD/PSC missing semantics','Restricted transfer heuristics','Binade crossing correction','Prefix-Fermat proposal','Lawvere/Fermat algebraic theories','Kahler differentials','Jet/truncation towers','lim1 obstruction proposal','Exact dyadic power criterion','Prefix ML null experiment','Transformer validation failure']),
'18':('Physics',['SYMMETRON Weyl crossed products','ADE Hochschild claims','Berry curvature zero comparison','Monster Umbral Mathieu moonshine','VOA modular Hamiltonian','L-value constant proposals','Spectral dimension ansatz','Graphene Kagome models','MMHW wavelet','Noncommutative torus Chern indices','Baum-Connes and soliton reports','384-dimensional framework limits','Flux Hodge candidate counting','66degree cosine potential','Golden phase identity','Conditional CKM observable polynomial','Coefficient7/NKtJ definitions missing','CP-even deformation failure','Allowed invariant contractions','3.A6 central-cover triplet proposal','Global vacuum selection','Stationary perturbation tangent','Loop counterterm frontier','Gauge Yukawa Higgs running','Threshold higher operators higher loops','Domain-wall signs and Higgs barrier','Goldstone gauge leakage','Wall decay widths','Near-threshold cubic law','Frame window','1080vacua','Thermal wall-only phase','Annihilation gravitational waves','Sommerfeld physical-phase nonprediction']),
'19':('WIND',['Radar272-volume historical corpus','Lower velocity split54/54','Measurement geometry and support','Vorticity signed source ledger','Linear SDE covariance','Information debt D','Spatial innovation I','Constraint injection C','Governing residual R','Structural ambiguity expiry','Exterior-law time windows','Pressure rank/time adequacy','Surface/aloft target difference','Assimilation dynamics commutator','Frozen targets versus hindsight','Sustained gust height duration datum distinction','HOx NOx VOC ozone missing rate tables','Two-moment aerosol missing equations','Reactive4D transport plan','Lorenz energy budget frontier']),
'20':('Empirical programs',['Finsler dead-zone action','Legendre conjugate','Hamilton-Jacobi facets','Fenichel throat escape','FW noise normalization','LC circuit reduction','Reversible kink negative result','Thermal purity identity','Hecke theta Gopel spectra','Q-KMS clipping dependence','Near-zero deformation weak exponent identification','Harsh Audit','Tau-Crystal anti-posthoc fitting','Bayes/MDL null tests','NFL Combine scouting','Ordered movement phases','Pauli commutator features','Commutative ablation','Future-speed MSE versus scouting outcomes','Betting baseline market deficit','Industrial portfolio negative result','Family-held-out benchmark scope','Customer break-even economics']),
'21':('Integrations',['Finite Horn closure','Grounding versus entailment','Closure debt','Obstruction partition','Closure-cost invariant','Cech/naturality defects','Actual double-complex requirement','Null-labor residue cost','Polygon triangulation arithmetic','Mesh coverage/topology frontier','Visibility graph completeness frontier','Compatible chart determinants','Shared-factor intersections','Richelot singular/stable reduction','Genus2 periods and marking','Riemannian metric transport','Smooth-curve bound frontier','STRING symbolic states','Pokepolis exact routes','Battle feedback studies','FF7 opcode architecture and missing archive','Procedural3D art scope','PerfectPower Explorer','DynaComp Explorer','Live research data synchronization requirement','NIH BLAST recurrence/annotation','Whole-database recall','Source adapter certification','Dedicated BLAST branch provenance']),
'22':('Enhancements',['Question-relative minimal state','Joint preservation profile','Hankel predictive discovery','Weighted quotient populations','Closure-defect promotion','Delay before new sensors','Compositional approximation','Decision-first refinement','Question-dependent height','Adaptive modulus selection','Integral lattice repair','Order commutator decomposition','Parameter sensitivity preservation','Physical deformation protection','Failure as repair witness','Active partner spectra','Exact ansatz rank jump','Affine-periodic collision engine','Positive kernel distinction','Finite-part tail enclosure','Explicit field maps','Oriented regulator output','Flip involution repair','Model-specific jet rejection','Target-first sensing','Reusable weighted histogram']),
'23':('Missing and corrections',['Arithmetic GCD kernel original unresolved','Full master.txt unresolved','Original SOE corpus unresolved','Original FF7 corpus unresolved','PSG source coefficients unresolved','PADD hardware semantics unresolved','Chemistry rate table unresolved','BLAST original recurrence unresolved','Concrete Petersen50 DAG unresolved','Full radar bytes unresolved','Full formal proof integration unresolved','No new Lean theorem claim','Exact numerical historical proposal status separation'])
}

GROUPS['26']=('NFL motor transfer', ['Official nine-file Combine adapter','LOS onset-travel confounding',
    'Half-second post-onset functional','Independent-repeat source variance','Uncertainty-integrated scouting correction',
    'Exact rational demand gate repair','Original-player bootstrap grouping','Nested source and outcome reconstruction',
    'Chronological rookie outcomes','Strong fifteen-measurement comparator','Fixed-budget shortlist test',
    'Unexecuted real-data status and full historical preservation'])

GROUPS['27']=('NFL math bridges', ['Operational NFL movement target geometry','Bounded two-pass NFL frame extraction',
    'Finite-horizon supervised Hankel continuation','Physical-coordinate SVD transfer',
    'Same-current different-history predictive witness','Equal-player weighting and preserved bootstrap multiplicity',
    'Train-only NFL-to-Combine continuation alignment','Descriptive support distances',
    'Out-of-player movement stacking','Strong shared-availability scouting baseline',
    'Physical source-to-movement-to-outcome loading','Fitted transfer-error decomposition',
    'Exact joint measurement-package optimum','Zero-standalone-value nuisance cancellation','Non-submodular target information',
    'Correlated within-attempt measurement blocks','Original-attempt deduplication',
    'Rationalized fitted-loading provenance','Uniform coefficient-rounding score bound','Rational-snapshot optimization regret','Robust multi-loading allocation',
    'Contender-difference sensing','Synthetic mechanism evidence versus NFL performance'])

GROUPS['28']=('Real NFL evidence', ['Recovered official source hash equality',
    'Timezone-naive relative tracking clocks','Mixed-clock rejection',
    'Observed-launch support bottleneck','Real temporal physical bridge evaluation',
    'Conventional-only two-stage control','NGS chronology sensitivity',
    'Private player outputs and public aggregate receipts','Full-pipeline refit uncertainty',
    'Official-source identity crosswalk','Public Combine temporal rookie outcomes',
    'Position-interaction conventional controls','Independent real NFL tracking replication',
    'Strong history forecasting controls','No scouting advantage from mechanism fit'])

GROUPS['29']=('Stopped-flow readouts', ['C2 common-origin launch ambiguity witness', 'Observed causal speed landmarks', 'Endpoint availability and suffix invariance', 'Time-position antisymmetric signature', 'Positive acceleration kernel', 'Exact sampled quadratic normalization', 'Nuisance-annihilating position contrasts', 'Minimum-variance rational jet readouts', 'Null-polynomial identifiability witness', 'Conditional noise and Taylor bias tradeoff', 'Recovered rolling source coverage', 'Disjoint-attempt measurement repeatability', 'Strong complete-history controls', 'Matched motor target versus get-off', 'Full original-player procedure refits', 'Correlated repeated-view covariance', 'Generalized empirical signal-noise modes', 'Physical-coordinate posterior transport', 'Strong independent-repeat ridge control', 'Adaptive evidence and prospective boundary'])

GROUPS['30']=('Exact Observatory', ['Finite partial-system compiler','Efficient behavioral quotient and commuting replay','Constraint-aware history populations','Lexicographic rank and inverse rank','Exact uniform history draws','Cost distributions and minima','Typed sensor-trace conditioning','Minimum-cost pair separation','Initial-target-preserving adaptive experiments','Destructive-action prefix conditioning','Complete closed ambiguity witnesses','Global whole-state Krylov identities','Rational generating functions and remote coefficients','Question-dependent observable coordinates','Finite-field arithmetic interferometer','Seeded Pell residue transport','Independent absolute relative and sign populations','Local interactive mathematical workbench','JSON batch and Python interfaces','Representation adapter development plan'])

GROUPS['31']=('Integrated Math Lab', ['Stable ranked equation IDs and installed atlas','Question-oriented exact workbench','Target-to-portfolio bounded workflow','Minimum-cost sensor repair','Exact ties and uncertain contenders','Finite Gaussian-rational Moyal algebra','Affine covariance and nonlinear counterexample','Complete Hahn coefficient gate','Classified rays and higher-order decoys','Cyclic obstruction invariant and extension repair','Sector connectivity and generated algebra','Exact conductor transport and CRT twists','Finite Dynkin theta and boundary reciprocity','Root-of-unity torus skein products','Scoped half-lift parity','Cancellation-conditioned precision bounds','Adaptive precision with external uncertainty','Colored weighted finite path populations','Chronology-sensitive histogram repricing','Finite-graph block contraction tails','Conserved outcome-channel partitions','Retry optimization and silent floor','Isolated circular logarithmic replacement','Character-twisted visible-ray coefficients','Progression residue local factors','Positive Pell unit-class asymptotics','Original-equation action histories','Bounded invariant-law discovery','Recovered active quintic partner','Universal sextic partner adapters','HTTP and DOM contract integration','Installed wheel resource replay'])

GROUPS['32']=('Partner incidence', ['Line probes for hypersurface components','Invariant identification on a line',
    'Dense slice with three simple roots','Saturation away from repeated roots','Covariants over a quotient ring',
    'Minimal polynomials of absolute invariants','Single-orbit certificate from a stable Clebsch point',
    'Quintic partner classification','Octahedral quartic jump','Dihedral cubic jump','Degenerate root patterns',
    'Degree-twelve hypersurface part','Open lower-dimensional components',
    'Prime-field Groebner bases','Sextic and septic partner emptiness modulo primes','Fourfold-root uniform source'])

GROUPS['34']=('Asterion basis calculus', ['Coined certified basis nomenclature','Exact commutator-word basis compiler','Reversible unimodular basis optimization','Root-lattice cocycle E8 reference algebra','Full bracket transport certificates','Order-thirty Coxeter lift and difference kernel','Full adjoint phase multiplicities','Principal divided-power polynomial coordinates','Complete normalized transvectant coupling catalogue','Seventy-six trilinear channel bounds','Minimal eight lowering seeds','Two-component polynomial coordinates modulo five','Explicit two-A4 exterior model','Exact fifth-cyclotomic arithmetic','All homogeneous bracket kernels','Thirty-one equal Cartan blocks','Homogeneous Jacobi identities','Obstruction to label-only symmetry','Internal two-dimensional covariance','Lattice index and rational descent boundary','Independent replay and corrupted-certificate rejection','Infinitesimal gauge versus genuine deformation','Linearized Jacobi cohomology','Exact second-order obstruction witnesses','Small-dimensional rigidity comparisons'])

GROUPS['35']=('Asterion fields, hypergeometry and relations', [
    'Principal Rees family and polynomial Jacobi specialization',
    'Class-four nilradical and leading interaction channels',
    'Diagonal contraction cone and complete bounded cut classifications',
    'Invariant-form obstruction and quadratic completion bounds',
    'Canonical cotangent extension with nondegenerate pairing',
    'Affine current cocycle and mode derivation',
    'All-order level-one state character and PBW retention',
    'Jordan sector Fourier populations and eta-quotient Sturm proof',
    'First nonuniform affine null-ideal trace at degree five',
    'Thirty independent Cartan conformal null relations',
    'Five exact invariant tensors and split-Casimir residues',
    'Spectral projectors and arithmetic prime thirty-one',
    'Logarithmic Frobenius recurrences and resonance compatibility',
    'Controlled complex transport and noncommuting holonomy',
    'Rational Racah recoupling and terminating hypergeometric series',
    'Full intermediate-channel Jacobi constraints',
    'Finite differential current algebra and actual homotopy transfer',
    'Moyal enveloping closure and symmetric-square obstruction',
    'Principal quantum embedding obstruction and dynamical derivatives',
    'Affine PBW straightening and explicit singular-square descendants',
    'Explicit weight-four arc-kernel generator and full null lift',
    'Projected polarization and complete low-weight kernel dimensions',
    'Uniform thirty-one-dimensional kernel in every Jordan sector',
    'Literal reduced Jacobi Jacobian and gauge reconstruction',
    'Smooth local rigidity and the full-support gauge component',
    'Modular hypergeometric periods and character cancellation',
    'Evidence-separated discovery ledger and research acceptance gates',
    'Higher-weight differential syzygies and extended quantum frontiers'])

def build():
    rows=[]
    for prefix,(domain,topics) in GROUPS.items():
        chapter=next((ROOT/'docs/chapters').glob(prefix+'_*'))
        for title in topics:
            rows.append({'id':f'PJ-T{len(rows)+1:03d}','domain':domain,'topic':title,
                         'chapter':str(chapter.relative_to(ROOT)),
                         'coverage':'canonical synthesis; see evidence status and missing-source limits'})
    (ROOT/'data/topics.json').write_text(json.dumps({'schema':'perfectjet/topics/1','topics':rows},indent=2)+'\n')
    text=['# Complete session topic coverage','','Every entry has a canonical chapter. Coverage means preserved discussion, not implemented or proved functionality.','','| ID | Family | Topic | Canonical chapter |','|---|---|---|---|']
    text += [f"| {r['id']} | {r['domain']} | {r['topic']} | [{Path(r['chapter']).stem}]({r['chapter'].removeprefix('docs/')}) |" for r in rows]
    (ROOT/'docs/COVERAGE_MAP.md').write_text('\n'.join(text)+'\n')
    print(len(rows),'topics covered')

if __name__=='__main__':build()
