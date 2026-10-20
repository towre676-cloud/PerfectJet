"""Exact Chevalley E8 and its signed Coxeter orbit kernel.

The root system is generated from the Cartan matrix, rather than loaded from
an opaque table.  Root signs come from a bimultiplicative lattice cocycle.
All public vectors are sparse dictionaries with :class:`Fraction` entries.
No floating point arithmetic or optional computer algebra system is used.

The Coxeter polynomial encoding is a module encoding: its variable acts by a
Lie automorphism.  It is *not* ordinary polynomial multiplication.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Mapping

Root = tuple[int, ...]
Vector = dict[int, Fraction]
SparseInput = Mapping[int, int | Fraction]


def _clean(vector: SparseInput) -> Vector:
    return {i: Fraction(value) for i, value in vector.items() if value}


def _add_scaled(target: dict, source: Mapping, scale=1) -> None:
    for index, value in source.items():
        result = target.get(index, 0) + scale * value
        if result:
            target[index] = result
        else:
            target.pop(index, None)


def encode_vector(vector: SparseInput) -> list[list[int | str]]:
    """A deterministic JSON-safe sparse vector; rationals stay exact strings."""
    return [[index, str(Fraction(value))] for index, value in sorted(vector.items()) if value]


class E8LieAlgebra:
    """The split rational E8 algebra with ``[e_i, f_i] = h_i``.

    Nodes 0 through 6 form a chain and node 7 attaches to node 2. Cartan
    vectors occupy slots 0..7; root vectors occupy slots 8..247.  Negative
    root vectors are gauged so every opposite-root bracket is ``h_alpha``.
    """

    rank = 8
    dimension = 248
    coxeter_number = 30
    exponents = (1, 7, 11, 13, 17, 19, 23, 29)
    coxeter_word = tuple(range(8))

    def __init__(self) -> None:
        edges = {(i, i + 1) for i in range(6)} | {(2, 7)}
        self.cartan_matrix = tuple(
            tuple(2 if i == j else -1 if (min(i, j), max(i, j)) in edges else 0
                  for j in range(8))
            for i in range(8)
        )
        self.cartan = self.cartan_matrix
        simple = tuple(tuple(int(i == j) for j in range(8)) for i in range(8))
        self.simple_roots = simple
        found = set(simple) | {tuple(-a for a in root) for root in simple}
        frontier = list(found)
        while frontier:
            alpha = frontier.pop()
            for i in range(8):
                pairing = sum(self.cartan_matrix[i][j] * alpha[j] for j in range(8))
                reflected = list(alpha)
                reflected[i] -= pairing
                beta = tuple(reflected)
                if beta not in found:
                    found.add(beta)
                    frontier.append(beta)
        self.roots = tuple(sorted(found, key=lambda root: (sum(root), root)))
        if len(self.roots) != 240:
            raise ArithmeticError("E8 reflection closure must have 240 roots")
        self.root_index = {root: i + 8 for i, root in enumerate(self.roots)}
        self.index_root = {index: root for root, index in self.root_index.items()}
        self.root_heights = {index: sum(root) for root, index in self.root_index.items()}
        self._bracket_cache: dict[tuple[int, int], tuple[tuple[int, int], ...]] = {}
        self._coxeter_images: tuple[Vector, ...] | None = None
        self._root_orbits: tuple[tuple[tuple[int, int], ...], ...] | None = None
        self._orbit_kernel: dict[tuple[int, int, int], Vector] | None = None

    def basis(self, index: int | None = None):
        if index is None:
            return tuple({i: Fraction(1)} for i in range(self.dimension))
        if not 0 <= index < self.dimension:
            raise IndexError(index)
        return {index: Fraction(1)}

    def simple_e(self, i: int) -> Vector:
        return self.basis(self.root_index[self.simple_roots[i]])

    def simple_f(self, i: int) -> Vector:
        return self.basis(self.root_index[tuple(-a for a in self.simple_roots[i])])

    def cartan_vector(self, i: int) -> Vector:
        if not 0 <= i < self.rank:
            raise IndexError(i)
        return self.basis(i)

    def height(self, index: int) -> int:
        return self.root_heights.get(index, 0)

    def label(self, index: int) -> str:
        if not 0 <= index < self.dimension:
            raise IndexError(index)
        return f"h_{index + 1}" if index < 8 else "e_(" + ",".join(map(str, self.index_root[index])) + ")"

    def basis_bracket(self, i: int, j: int) -> Vector:
        """Bracket two named basis slots without constructing input vectors."""
        if not (0 <= i < self.dimension and 0 <= j < self.dimension):
            raise IndexError((i, j))
        return {index: Fraction(value) for index, value in self._basis_bracket(i, j)}

    def inner_product(self, alpha: Root, beta: Root) -> int:
        return sum(alpha[i] * self.cartan_matrix[i][j] * beta[j]
                   for i in range(8) for j in range(8))

    def cocycle_sign(self, alpha: Root, beta: Root) -> int:
        """The bimultiplicative sign epsilon on the even E8 root lattice."""
        parity = sum(alpha[i] * beta[i] for i in range(8))
        parity += sum(alpha[i] * beta[j] * self.cartan_matrix[i][j]
                      for i in range(8) for j in range(i))
        return -1 if parity % 2 else 1

    def _basis_bracket(self, i: int, j: int) -> tuple[tuple[int, int], ...]:
        if i == j:
            return ()
        if i > j:
            return tuple((k, -value) for k, value in self._basis_bracket(j, i))
        cached = self._bracket_cache.get((i, j))
        if cached is not None:
            return cached
        if j < 8:
            result = ()
        elif i < 8:
            alpha = self.index_root[j]
            coefficient = sum(self.cartan_matrix[i][k] * alpha[k] for k in range(8))
            result = ((j, coefficient),) if coefficient else ()
        else:
            alpha, beta = self.index_root[i], self.index_root[j]
            total = tuple(a + b for a, b in zip(alpha, beta))
            if not any(total):
                result = tuple((k, a) for k, a in enumerate(alpha) if a)
            elif total in self.root_index:
                gauge = (-1 if sum(alpha) < 0 else 1)
                gauge *= (-1 if sum(beta) < 0 else 1)
                gauge *= (-1 if sum(total) < 0 else 1)
                coefficient = gauge * self.cocycle_sign(alpha, beta)
                result = ((self.root_index[total], coefficient),)
            else:
                result = ()
        self._bracket_cache[i, j] = result
        return result

    def bracket(self, x: SparseInput, y: SparseInput) -> Vector:
        result: dict[int, Fraction] = {}
        for i, a in x.items():
            if not a:
                continue
            if not 0 <= i < self.dimension:
                raise IndexError(i)
            for j, b in y.items():
                if not b:
                    continue
                if not 0 <= j < self.dimension:
                    raise IndexError(j)
                scale = Fraction(a) * Fraction(b)
                for k, coefficient in self._basis_bracket(i, j):
                    value = result.get(k, Fraction(0)) + scale * coefficient
                    if value:
                        result[k] = value
                    else:
                        result.pop(k, None)
        return result

    def _exp_ad(self, generator: SparseInput, vector: SparseInput, sign=1) -> Vector:
        result = _clean(vector)
        term = _clean(vector)
        # Simple-root adjoint operators have nilpotence index at most three.
        for n in range(1, 4):
            term = {i: Fraction(sign, n) * value
                    for i, value in self.bracket(generator, term).items()}
            if not term:
                return result
            _add_scaled(result, term)
        raise ArithmeticError("simple-root adjoint exponential did not terminate")

    def simple_reflection(self, i: int, vector: SparseInput) -> Vector:
        """Apply exp(ad e_i) exp(-ad f_i) exp(ad e_i)."""
        e, f = self.simple_e(i), self.simple_f(i)
        return self._exp_ad(e, self._exp_ad(f, self._exp_ad(e, vector), -1))

    def _ensure_coxeter(self) -> None:
        if self._coxeter_images is not None:
            return
        images = []
        for vector in self.basis():
            for i in self.coxeter_word:
                vector = self.simple_reflection(i, vector)
            if any(value.denominator != 1 for value in vector.values()):
                raise ArithmeticError("Tits action must preserve the integral form")
            images.append(vector)
        self._coxeter_images = tuple(images)

    def coxeter(self, vector: SparseInput, power: int = 1) -> Vector:
        """Apply the Coxeter lift; the listed simple reflections act in order."""
        self._ensure_coxeter()
        result = _clean(vector)
        for _ in range(power % 30):
            image: Vector = {}
            for i, coefficient in result.items():
                _add_scaled(image, self._coxeter_images[i], coefficient)
            result = image
        return result

    def root_orbits(self) -> tuple[tuple[tuple[int, int], ...], ...]:
        """Return (global root index, accumulated sign) in each 30-cycle."""
        self._ensure_coxeter()
        if self._root_orbits is not None:
            return self._root_orbits
        unseen = set(self.index_root)
        orbits = []
        while unseen:
            start = min(unseen)
            vector = self.basis(start)
            orbit = []
            for _ in range(30):
                if len(vector) != 1:
                    raise ArithmeticError("Coxeter root action is not monomial")
                index, coefficient = next(iter(vector.items()))
                if index not in unseen or abs(coefficient) != 1:
                    raise ArithmeticError("root orbit closes before thirty steps")
                unseen.remove(index)
                orbit.append((index, int(coefficient)))
                vector = self.coxeter(vector)
            if vector != self.basis(start):
                raise ArithmeticError("signed orbit has nontrivial monodromy")
            orbits.append(tuple(orbit))
        if len(orbits) != 8:
            raise ArithmeticError("expected eight Coxeter root orbits")
        self._root_orbits = tuple(orbits)
        return self._root_orbits

    def orbit_kernel(self) -> dict[tuple[int, int, int], Vector]:
        """The 1,920 brackets K(i,j,d)=[u_i,C**d u_j]."""
        if self._orbit_kernel is None:
            orbits = self.root_orbits()
            self._orbit_kernel = {
                (i, j, d): self.bracket(self.basis(left[0][0]), {index: Fraction(sign)})
                for i, left in enumerate(orbits)
                for j, right in enumerate(orbits)
                for d, (index, sign) in enumerate(right)
            }
        return {key: dict(vector) for key, vector in self._orbit_kernel.items()}

    def verify_coxeter_kernel(self) -> dict:
        orbits, kernel = self.root_orbits(), self.orbit_kernel()
        checked = 0
        for i, left in enumerate(orbits):
            for j, right in enumerate(orbits):
                for d in range(30):
                    reconstructed = kernel[i, j, d]
                    for a, (left_index, left_sign) in enumerate(left):
                        right_index, right_sign = right[(a + d) % 30]
                        expected = {index: Fraction(left_sign * right_sign * coefficient)
                                    for index, coefficient in self._basis_bracket(left_index, right_index)}
                        if reconstructed != expected:
                            return {"passed": False, "checked": checked,
                                    "failure": (i, j, d, a)}
                        checked += 1
                        reconstructed = self.coxeter(reconstructed)
        return {"passed": True, "checked": checked, "seed_brackets": len(kernel),
                "table_redundancy_factor": 30}

    def coxeter_receipt(self) -> dict:
        self._ensure_coxeter()
        # Do not use coxeter(v,30), whose modular-power shortcut assumes order30.
        all_order_thirty = True
        for index in range(self.dimension):
            vector = self.basis(index)
            for _ in range(30):
                vector = self.coxeter(vector)
            if vector != self.basis(index):
                all_order_thirty = False
                break
        orbits = self.root_orbits()
        cartan_matrix = [[int(self._coxeter_images[j].get(i, 0)) for j in range(8)]
                         for i in range(8)]
        power = [[int(i == j) for j in range(8)] for i in range(8)]
        traces = []
        for _ in range(8):
            power = [[sum(power[i][k] * cartan_matrix[k][j] for k in range(8))
                      for j in range(8)] for i in range(8)]
            traces.append(sum(power[i][i] for i in range(8)))
        descending = [Fraction(1)]
        for k in range(1, 9):
            descending.append(-sum(descending[k - j] * traces[j - 1]
                                   for j in range(1, k + 1)) / k)
        characteristic = [int(value) for value in reversed(descending)]
        phi30 = [1, 1, 0, -1, -1, -1, 0, 1, 1]
        return {"dimension": self.dimension, "rank": self.rank,
                "root_count": len(self.roots), "coxeter_order": 30 if all_order_thirty else None,
                "order_thirty_on_all_basis_vectors": all_order_thirty,
                "root_orbit_lengths": [len(orbit) for orbit in orbits],
                "signed_monodromy": [1] * len(orbits),
                "cartan_characteristic_polynomial_ascending": characteristic,
                "cartan_characteristic_polynomial_is_phi30": characteristic == phi30,
                "cartan_exponents": list(self.exponents),
                "phase_multiplicities": [9 if k in self.exponents else 8 for k in range(30)],
                "kernel_seed_brackets": 1920,
                "ordinary_polynomial_multiplication": False}

    def verify_coxeter_equivariance(self) -> dict:
        """Check C[x,y]=[Cx,Cy] for every distinct pair of basis vectors."""
        self._ensure_coxeter()
        checked = 0
        for i, j in combinations(range(self.dimension), 2):
            left = self.coxeter(self.basis_bracket(i, j))
            right = self.bracket(self._coxeter_images[i], self._coxeter_images[j])
            checked += 1
            if left != right:
                return {"passed": False, "checked": checked, "failure": (i, j)}
        return {"passed": True, "checked": checked,
                "all_distinct_basis_pairs": True}

    def _jacobi_on_indices(self, i: int, j: int, k: int) -> dict[int, int]:
        result: dict[int, int] = {}
        for a, b, c in ((i, j, k), (j, k, i), (k, i, j)):
            for inner, coefficient in self._basis_bracket(b, c):
                for target, outer in self._basis_bracket(a, inner):
                    value = result.get(target, 0) + coefficient * outer
                    if value:
                        result[target] = value
                    else:
                        result.pop(target, None)
        return result

    def verify_jacobi(self, mode: str = "generators") -> dict:
        """Check all distinct basis triples, or all pairs against 16 generators.

        ``full`` is an exhaustive bilinearity certificate, not random sampling.
        Generator mode is reported as such and does not claim exhaustive triples.
        """
        if mode == "full":
            triples = combinations(range(self.dimension), 3)
        elif mode == "generators":
            generators = sorted({next(iter(self.simple_e(i))) for i in range(8)} |
                                {next(iter(self.simple_f(i))) for i in range(8)})
            triples = ((generator, j, k) for generator in generators
                       for j, k in combinations(range(self.dimension), 2)
                       if generator != j and generator != k)
        else:
            raise ValueError("mode must be 'generators' or 'full'")
        checked = 0
        for i, j, k in triples:
            residual = self._jacobi_on_indices(i, j, k)
            checked += 1
            if residual:
                return {"passed": False, "mode": mode, "checked": checked,
                        "failure": (i, j, k), "residual": residual}
        return {"passed": True, "mode": mode, "checked": checked,
                "exhaustive_distinct_triples": mode == "full"}


def e8_receipt(exhaustive: bool = False) -> dict:
    """Build an independently replayable, JSON-safe exact verification receipt."""
    algebra = E8LieAlgebra()
    receipt = algebra.coxeter_receipt()
    receipt["jacobi"] = algebra.verify_jacobi("full" if exhaustive else "generators")
    receipt["coxeter_equivariance"] = algebra.verify_coxeter_equivariance()
    receipt["orbit_kernel"] = algebra.verify_coxeter_kernel()
    receipt["coefficient_field"] = "Q"
    receipt["root_sign_convention"] = "lattice 2-cocycle with negative-root gauge"
    receipt["passed"] = (receipt["order_thirty_on_all_basis_vectors"]
                         and receipt["cartan_characteristic_polynomial_is_phi30"]
                         and receipt["jacobi"]["passed"]
                         and receipt["coxeter_equivariance"]["passed"]
                         and receipt["orbit_kernel"]["passed"])
    return receipt


__all__ = ["E8LieAlgebra", "Root", "Vector", "encode_vector", "e8_receipt"]
