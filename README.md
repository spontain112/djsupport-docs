# DJ Support documentation

Classification: public

This repository owns the audience-focused presentation of DJ Support documentation on Mintlify. The product repository remains canonical for behavior, domain language, commands, stable release state, schemas, and architecture decisions.

## Local preview

```bash
mint dev
```

Open `http://localhost:3000`.

## Verify

```bash
mint validate
mint broken-links
mint a11y
python3 scripts/check_product_contract.py --product-repo ../djsupport
```

## Content boundary

- **Use DJ Support** serves a nontechnical working DJ and is macOS-first.
- **Build DJ Support** routes contributors to canonical technical sources.
- Do not publish credentials, private paths, playlist contents, reports, matching state, backups, or user-derived fixtures.
- Do not redefine terms from the product repository's `CONTEXT.md`.
