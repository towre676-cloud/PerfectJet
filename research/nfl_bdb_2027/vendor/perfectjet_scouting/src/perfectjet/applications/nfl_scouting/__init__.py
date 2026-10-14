"""Combine movement readouts and their pre-draft scouting value.

Question: does a repeatable, demand-adjusted recovery readout measured at the
Combine predict NFL get-off beyond position, body measurements, timed tests and
other information available before the draft?

The package separates measurement (events, eta, sensitivity), identifiability
(which readouts a player's attempts determine), outcome construction
(cross-fitted context residuals), validation (player-grouped temporal splits with
full-pipeline refits), and decisions (frozen shortlist rules). A synthetic
generator with a planted or null signal tests the pipeline itself; it is never
evidence about football.
"""
EXTRACTION_VERSION = "nfl-events/1"
