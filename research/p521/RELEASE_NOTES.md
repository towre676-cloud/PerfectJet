P-521 Provenance Laboratory 0.1.0 adds exact, independently checkable exclusions to the investigation of P-521's public base-point origin.

The source-faithful FreeLIP result excludes every valid internal state under six 26-bit-limb assembly layouts. It includes the original rejection sampler through 768 exact gap-pattern certificates. Separate proofs exclude all 48-bit lrand48 states for 188 coordinate byte windows and 180 specified full byte assemblies, with 179 proof records. A further bit obstruction excludes 17 unsigned 31-bit words in 32-bit slots, for either coordinate and word order.

The release includes source, pinned historical provenance, successful controls, independent checkers, adversarial tests, complete mathematical receipts, a deterministic source archive and SHA-256 checksum. Python alone can verify the retained proofs offline. Optional discovery dependencies and the native scanner have separate reproducible commands.

These are scoped generator/assembly exclusions. The actual P-521 base-point recipe remains unknown. This release establishes no private-key recovery, discrete-logarithm algorithm, cryptographic break or worldwide priority. Previously published seed and base-point reconstructions retain attribution to Anthropic and their independent verifiers.

From the extracted archive root, run `python research/p521/run_research.py --check`. See the included research README for exact scopes, proofs and regeneration commands.
