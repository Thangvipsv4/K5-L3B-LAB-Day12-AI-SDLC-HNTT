# Changelog
## Unreleased

### Phase 3 — individual inventory adapter (in progress)

- Added v1.2 inventory item validation, atomic read/write, integer freshness
  conversion, ID allocation helper, and per-tick decay/spoilage adapter helpers.
- Added v1.2 scenario validation when a freshness tuning block is supplied;
  kept the checked-in v1.1 path active during the agreed integration window.
- Full Phase 3 simulation handoff remains pending the Gather and Quan v1.2
  interfaces. See [verification](docs/verification/phase-3.md).
