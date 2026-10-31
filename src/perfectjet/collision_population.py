"""Positive populations behind cyclotomic collision phases.

Cyclotomic coefficients are weighted sums, not counts.  Here a phase residue
is retained instead: C[L,c](e) counts the ordered exponent splits a+b=e with
ab=c mod L.  Residue blocks make its count affine in e//L.  Independent local
splits are combined by exact cyclic convolution to count divisor pairs of a
supplied, prime-verified factorization.  No integer factorization is attempted.
"""

from bisect import bisect_left
from random import SystemRandom


def _integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _parameters(conductor, residue, max_conductor):
    conductor = _integer(conductor, "conductor", 1)
    residue = _integer(residue, "residue")
    max_conductor = _integer(max_conductor, "max_conductor", 1)
    if conductor > max_conductor:
        raise ValueError("conductor exceeds the declared residue budget")
    return conductor, residue % conductor


class ExponentSplitPopulation:
    """Ordered (a,b), a+b=exponent, ab=residue modulo conductor.

    Order is increasing a.  Setup visits conductor residues, independently of
    exponent magnitude.  Output integers have O(log(exponent+1)) bits.
    """

    def __init__(self, conductor, exponent, residue=0, *, max_conductor=4096):
        self.conductor, self.residue = _parameters(conductor, residue, max_conductor)
        self.exponent = _integer(exponent, "exponent")
        L = self.conductor
        d, r = divmod(self.exponent, L)
        self.roots = tuple(a for a in range(L) if a * (r - a) % L == self.residue)
        self._blocks = d
        self._tail = bisect_left(self.roots, r + 1)
        self._count = d * len(self.roots) + self._tail

    def count(self):
        return self._count

    def contains(self, pair):
        try:
            a, b = tuple(pair)
            _integer(a, "left exponent")
            _integer(b, "right exponent")
        except (TypeError, ValueError):
            return False
        return a + b == self.exponent and a * b % self.conductor == self.residue

    def unrank(self, index):
        index = _integer(index, "rank")
        if index >= self._count:
            raise IndexError("rank outside the exponent-split population")
        block, offset = divmod(index, len(self.roots))
        a = block * self.conductor + self.roots[offset]
        return a, self.exponent - a

    def rank(self, pair):
        pair = tuple(pair)
        if not self.contains(pair):
            raise ValueError("pair is not in the exponent-split population")
        a, _ = pair
        block, residue = divmod(a, self.conductor)
        return block * len(self.roots) + bisect_left(self.roots, residue)

    def sample(self, rng=None):
        if not self._count:
            raise ValueError("cannot sample an empty population")
        return self.unrank((rng or SystemRandom()).randrange(self._count))


def _is_prime(n, budget):
    """Exact trial division with a shared explicit operation budget."""
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if budget[0] == 0:
            raise ValueError("prime verification exceeds the declared trial-division budget")
        budget[0] -= 1
        if n % divisor == 0:
            return False
        divisor += 2
    return True


class FactorPairResiduePopulation:
    """Divisor pairs (m,n), mn=N, kappa(m,n)=residue modulo conductor.

    ``factorization`` supplies distinct (prime, positive exponent) pairs.  Exact
    bounded trial division verifies each prime; this class never factors N.
    Every object is represented by the tuple of exponents of m in sorted-prime
    order.  Rank follows that lexicographic order, not numerical divisor order.
    ``pair`` optionally reconstructs the original integers under a bit budget.

    Setup uses O(k L**2) integer operations and O(k L) cells.  Count bit lengths
    and integer-operation costs remain real resources; huge exponents do not
    imply that their corresponding integer N can be materialized cheaply.
    """

    def __init__(self, factorization, conductor=2, residue=0, *,
                 max_conductor=4096, max_factors=64, max_work=2_000_000,
                 max_trial_divisions=100_000, max_input_bits=8192):
        self.conductor, self.residue = _parameters(conductor, residue, max_conductor)
        max_factors = _integer(max_factors, "max_factors")
        max_work = _integer(max_work, "max_work")
        max_input_bits = _integer(max_input_bits, "max_input_bits", 1)
        budget = [_integer(max_trial_divisions, "max_trial_divisions")]
        source = factorization.items() if isinstance(factorization, dict) else factorization
        factors = []
        for item in source:
            try:
                prime, exponent = tuple(item)
            except (TypeError, ValueError):
                raise ValueError("factorization entries must be (prime, exponent) pairs") from None
            prime = _integer(prime, "prime", 2)
            exponent = _integer(exponent, "exponent", 1)
            if prime.bit_length() > max_input_bits or exponent.bit_length() > max_input_bits:
                raise ValueError("factorization entry exceeds the declared input-bit budget")
            factors.append((prime, exponent))
            if len(factors) > max_factors:
                raise ValueError("factorization exceeds the declared factor-count budget")
        factors.sort()
        if any(a[0] == b[0] for a, b in zip(factors, factors[1:])):
            raise ValueError("factorization primes must be distinct")
        L = self.conductor
        if len(factors) * L * L > max_work:
            raise ValueError("cyclic convolution exceeds the declared work budget")
        for prime, _ in factors:
            if not _is_prime(prime, budget):
                raise ValueError("factorization contains a composite base")
        self.factorization = tuple(factors)
        self.trial_divisions = max_trial_divisions - budget[0]
        self._suffix = [[0] * L for _ in range(len(factors) + 1)]
        self._suffix[-1][0] = 1
        for i in range(len(factors) - 1, -1, -1):
            e = factors[i][1]
            d, r = divmod(e, L)
            local = [0] * L
            for a in range(L):
                local[a * (r - a) % L] += d + (a <= r)
            for target in range(L):
                self._suffix[i][target] = sum(
                    mass * self._suffix[i + 1][(target - collision) % L]
                    for collision, mass in enumerate(local) if mass)

    def _prefix(self, prefix):
        prefix = tuple(prefix)
        if len(prefix) > len(self.factorization):
            raise ValueError("prefix is longer than the supplied factorization")
        target = self.residue
        for a, (_, e) in zip(prefix, self.factorization):
            a = _integer(a, "left exponent")
            if a > e:
                raise ValueError("left exponent exceeds its supplied prime exponent")
            target = (target - a * (e - a)) % self.conductor
        return prefix, target

    def count(self, prefix=()):
        prefix, target = self._prefix(prefix)
        return self._suffix[len(prefix)][target]

    def histogram(self):
        """Counts for every residue, totaling the number of divisors of N."""
        return tuple(self._suffix[0])

    def contains(self, exponents):
        try:
            exponents, target = self._prefix(exponents)
        except (TypeError, ValueError):
            return False
        return len(exponents) == len(self.factorization) and target == 0

    def _weights(self, i, target):
        L = self.conductor
        e = self.factorization[i][1] % L
        return tuple(self._suffix[i + 1][(target - a * (e - a)) % L] for a in range(L))

    def unrank(self, index):
        index = _integer(index, "rank")
        if index >= self.count():
            raise IndexError("rank outside the factor-pair population")
        target, answer, L = self.residue, [], self.conductor
        for i, (_, e) in enumerate(self.factorization):
            weights = self._weights(i, target)
            block_mass = sum(weights)
            full_blocks, tail = divmod(e, L)
            if index < full_blocks * block_mass:
                block, index = divmod(index, block_mass)
                limit = L - 1
            else:
                block = full_blocks
                index -= full_blocks * block_mass
                limit = tail
            for a in range(limit + 1):
                if index < weights[a]:
                    chosen = block * L + a
                    answer.append(chosen)
                    target = (target - chosen * (e - chosen)) % L
                    break
                index -= weights[a]
            else:
                raise ArithmeticError("factor-pair completion count failed replay")
        if target or index:
            raise ArithmeticError("factor-pair rank remainder failed replay")
        return tuple(answer)

    def rank(self, exponents):
        exponents = tuple(exponents)
        if not self.contains(exponents):
            raise ValueError("exponents are not in the factor-pair population")
        target, index, L = self.residue, 0, self.conductor
        for i, (a, (_, e)) in enumerate(zip(exponents, self.factorization)):
            weights = self._weights(i, target)
            block, residue = divmod(a, L)
            index += block * sum(weights) + sum(weights[:residue])
            target = (target - a * (e - a)) % L
        return index

    def pair(self, index, *, max_output_bits=100_000):
        """Reconstruct (m,n) after a conservative pre-exponentiation bit guard."""
        max_output_bits = _integer(max_output_bits, "max_output_bits", 1)
        if sum(p.bit_length() * e for p, e in self.factorization) > max_output_bits:
            raise ValueError("original integer product exceeds the declared output-bit budget")
        exponents = self.unrank(index)
        m = n = 1
        for a, (p, e) in zip(exponents, self.factorization):
            m *= p ** a
            n *= p ** (e - a)
        return m, n

    def sample(self, rng=None):
        total = self.count()
        if not total:
            raise ValueError("cannot sample an empty population")
        return self.unrank((rng or SystemRandom()).randrange(total))

    def parity_signed_total(self):
        """Sum (-1)**kappa over all original pairs, at conductor two only.

        Local cancellation leaves one for even prime exponents and e+1 for
        odd exponents.  This signed sum is not a residue population count.
        """
        if self.conductor != 2:
            raise ValueError("parity signed total requires conductor two")
        return self._suffix[0][0] - self._suffix[0][1]


def collision_population_receipt(conductor=2, exponent=10**100, residue=0, rank=0):
    """JSON-ready bounded demonstration; huge local exponents stay compressed."""
    rank = _integer(rank, "rank")
    local = ExponentSplitPopulation(conductor, exponent, residue)
    if not local.count() and rank:
        raise IndexError("empty exponent-split population has no requested rank")
    pair = local.unrank(rank) if local.count() else None
    factors = FactorPairResiduePopulation({2: 4, 3: 3, 5: 2}, conductor, residue)
    witness = factors.unrank(0) if factors.count() else None
    return {
        "schema": "perfectjet.collision-population/1",
        "conductor": local.conductor, "residue": local.residue,
        "local_exponent": str(exponent), "local_count": str(local.count()),
        "local_rank": None if pair is None else str(rank), "local_split": None if pair is None else list(map(str, pair)),
        "local_rank_replayed": None if pair is None else local.rank(pair) == rank,
        "factorization": [[p, e] for p, e in factors.factorization],
        "residue_histogram": list(map(str, factors.histogram())),
        "factor_pair_count": str(factors.count()),
        "left_exponent_witness": None if witness is None else list(witness),
        "original_pair": None if witness is None else list(map(str, factors.pair(0))),
        "factor_rank_replayed": witness is None or factors.rank(witness) == 0,
        "scope": "ordered exponent splits and divisor pairs of the supplied verified factorization; lexicographic prime-exponent order",
        "limits": "conductor and convolution work are bounded; no factorization algorithm or asymptotic count theorem is claimed",
    }
