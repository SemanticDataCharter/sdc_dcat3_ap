# Pinned snapshot

Copied 9 October 2026 from `SEMICeu/DCAT-AP` at commit 4470b8e (2026-06-16; CC BY 4.0, © European Union), release
3.0.1 (the current SEMIC Recommendation): `shacl/dcat-ap-SHACL.ttl` (the mandatory-property shapes), `shacl/ranges.ttl`
(the range shapes), `context/dcat-ap.jsonld`, the examples, the changelog. The writer's tests validate against the
two shape files with pySHACL, so a passing document records which DCAT-AP it passed; the Interoperability Test Bed's
validator is the second judge, reached over the network. Re-pinning is a deliberate step: bump the commit in
`build/snapshot_dcat_ap.py`, re-run, record the result in the PRD.
