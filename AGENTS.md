> **First-time setup**: Customize this file for your project. Prompt the user to customize this file for their project.
> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# DJ Support documentation project instructions

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Use the Mintlify MCP server, `https://mcp.mintlify.com`, to edit content and settings via MCP
- Use the Mintlify docs MCP server, `https://www.mintlify.com/docs/mcp`, to query information about using Mintlify via MCP

## Canonical sources

- `spontain112/djsupport` owns product behavior, domain language, commands, stable release state, schemas, and architecture decisions.
- This repository owns audience-focused explanation, navigation, and visual presentation.
- Use the canonical product terms **Transfer**, **Source Selection**, **Mirror**, **Snapshot**, **Preview**, **Qualification Draft**, **Provisional Playlist**, **Approval**, and **Agent Client** exactly as defined in the product repository's `CONTEXT.md`.
- Do not substitute “sync,” “import,” “job,” “dry run,” or “draft playlist” for those domain concepts.

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise — one idea per sentence
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references
- Write **Use DJ Support** for a nontechnical working DJ. Explain outcomes and human decisions before commands.
- Write **Build DJ Support** for contributors. Link to canonical technical sources instead of copying complete reference documents.

## Content boundaries

- Public user guidance covers the latest final stable release on macOS.
- Pre-releases, source checkouts, planned work, and engineering internals belong in **Build DJ Support** and must be labeled accurately.
- Never publish credentials, local paths, personal playlists, reports, Corrections, Approved Matches, playlist state, backups, or user-derived fixtures.
- DJ Support is free, open source, and self-supported. Do not promise support or response times.
