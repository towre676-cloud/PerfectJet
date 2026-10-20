// Exhaustive top-bit state enumeration for the POSIX 48-bit LCG.
// Input lines: output_bits observation_count observation_0 ...
// Output lines: number_of_survivors survivor_state_0 ...
#include <cstdint>
#include <iostream>
#include <vector>

int main() {
    constexpr std::uint64_t mask = (1ULL << 48) - 1;
    constexpr std::uint64_t a = 0x5deece66dULL, c = 11;
    unsigned bits, n;
    while (std::cin >> bits >> n) {
        if (bits < 28 || bits > 48 || n < 3 || n > 128) return 2;
        std::vector<std::uint64_t> words(n), survivors;
        for (auto &word : words) {
            if (!(std::cin >> word) || word >= (1ULL << bits)) return 2;
        }
        const unsigned hidden = 48 - bits;
        const std::uint64_t base = words[0] << hidden;
        for (std::uint64_t low = 0; low < (1ULL << hidden); ++low) {
            std::uint64_t state = base | low;
            bool good = true;
            for (unsigned j = 1; j < n; ++j) {
                state = (a * state + c) & mask;
                if ((state >> hidden) != words[j]) { good = false; break; }
            }
            if (good) survivors.push_back(base | low);
        }
        std::cout << survivors.size();
        for (auto state : survivors) std::cout << ' ' << state;
        std::cout << '\n';
    }
}
