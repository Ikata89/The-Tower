## Summary
- What changed and why

## Implementation
- Format detection: [ ] JSON  [ ] Gzip JSON  [ ] Binary probe
- Schema sections touched: [ ] currencies [ ] tower [ ] cards [ ] modules [ ] labs [ ] relics [ ] research [ ] workshop

## Testing
- [ ] Parsed `tools/sample_data/playerInfo.dat`
- [ ] Outputs in `/out` (`playerInfo.json`, `playerInfo.csv`)
- [ ] Parser does not crash on unknown formats
- Notes:

## Sources (links)
- …

## Checklist
- [ ] Conventional commit title (e.g., `feat(parser): …`)
- [ ] No direct writes to `main` (use `agent/*` branch)
- [ ] Includes brief parsing report (method, counts, errors)
