---
version: alpha
name: Nasdaq100-Watchlist-Design
description: >
  A data-analytics design language built for the Nasdaq-100 편입·편출 관찰 후보 PoC & Prototype.
  Inspired by Bloomberg Terminal aesthetics and modern fintech dashboards: near-black canvas,
  electric-blue primary accent, and a strict tabular-figure type system for financial numerics.
  Status indicators use a traffic-light palette (emerald / amber / rose) so PASS / CONDITIONAL_PASS / FAIL
  states read at a glance. Cards float on dark-charcoal surfaces with subtle hairline borders.
  Navigation tabs are underline-style; data tables use monospaced numerics and alternating row tones.
  The Prototype intentionally avoids investment-recommendation language — the design enforces this
  by never using call-to-action button styles that imply trading actions.

colors:
  # ── Brand / Primary ──────────────────────────────────────────────────────────
  primary:          "#3B82F6"   # electric blue (Tailwind blue-500)
  primary-deep:     "#2563EB"   # blue-600 — pressed / active
  primary-soft:     "#93C5FD"   # blue-300 — subtle highlight
  primary-muted:    "#1E3A5F"   # blue on dark — ghost button bg

  # ── Canvas / Surface ─────────────────────────────────────────────────────────
  canvas:           "#0F172A"   # slate-900 — page background
  surface:          "#1E293B"   # slate-800 — card / sidebar
  surface-raised:   "#334155"   # slate-700 — hover / table row alternate
  surface-overlay:  "#0A1628"   # deeper than canvas — modal backdrop

  # ── Ink / Text ───────────────────────────────────────────────────────────────
  ink:              "#F1F5F9"   # slate-100 — primary text
  ink-secondary:    "#94A3B8"   # slate-400 — secondary text, labels
  ink-muted:        "#64748B"   # slate-500 — captions, footnotes
  ink-disabled:     "#475569"   # slate-600 — disabled / placeholder

  # ── Status (Traffic-Light) ────────────────────────────────────────────────────
  status-pass:      "#10B981"   # emerald-500 — PASS
  status-pass-bg:   "#064E3B"   # emerald-900 — badge background
  status-warn:      "#F59E0B"   # amber-500 — CONDITIONAL_PASS
  status-warn-bg:   "#451A03"   # amber-950 — badge background
  status-fail:      "#EF4444"   # red-500 — FAIL
  status-fail-bg:   "#450A0A"   # red-950 — badge background
  status-info:      "#38BDF8"   # sky-400 — informational
  status-info-bg:   "#0C2647"   # sky-950 — badge background

  # ── Data / Chart ─────────────────────────────────────────────────────────────
  data-inclusion:   "#10B981"   # inclusion candidates — green
  data-exclusion:   "#F59E0B"   # exclusion candidates — amber
  data-neutral:     "#6366F1"   # general metric — indigo

  # ── Hairlines / Borders ───────────────────────────────────────────────────────
  hairline:         "#1E293B"   # card border (same as surface)
  hairline-strong:  "#334155"   # table column divider
  hairline-focus:   "#3B82F6"   # input focus ring

typography:
  # Display — Page and section headings
  display-lg:
    fontFamily: "'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif"
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.5px

  display-md:
    fontFamily: "'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif"
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: -0.3px

  display-sm:
    fontFamily: "'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif"
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: -0.2px

  # Heading — Card titles, tab labels
  heading-md:
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    fontSize: 16px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: 0

  heading-sm:
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: 0.1px

  # Body — General prose, descriptions
  body-lg:
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0

  body-md:
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0

  # Tabular — Financial numerics (market cap, ratios, ranks)
  data-tabular:
    fontFamily: "'JetBrains Mono', 'Roboto Mono', 'Fira Code', monospace"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0
    fontFeature: tnum   # tabular numbers — critical for aligned columns

  data-tabular-lg:
    fontFamily: "'JetBrains Mono', 'Roboto Mono', monospace"
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.2px
    fontFeature: tnum

  # Caption — Source attribution, timestamps, disclaimers
  caption:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: 0.1px

  micro:
    fontFamily: "'Inter', system-ui, sans-serif"
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: 0.5px
    textTransform: uppercase   # used for badge labels (PASS, FAIL, ticker symbols)

rounded:
  none:  0px
  xs:    3px
  sm:    6px
  md:    8px
  lg:    12px
  xl:    16px
  pill:  9999px

spacing:
  xxs:  2px
  xs:   4px
  sm:   8px
  md:   12px
  lg:   16px
  xl:   24px
  xxl:  32px
  huge: 64px

shadows:
  card:    "0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)"
  raised:  "0 4px 12px rgba(0,0,0,0.5)"
  focus:   "0 0 0 3px rgba(59,130,246,0.35)"

components:
  # ── Page Container ───────────────────────────────────────────────────────────
  page-root:
    backgroundColor: "{colors.canvas}"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    padding:         "0"

  # ── Sidebar ──────────────────────────────────────────────────────────────────
  sidebar:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.none}"
    padding:         "24px 16px"
    borderRight:     "1px solid {colors.hairline}"

  # ── Navigation Tabs ───────────────────────────────────────────────────────────
  tab-inactive:
    backgroundColor: "transparent"
    textColor:       "{colors.ink-secondary}"
    typography:      "{typography.heading-md}"
    rounded:         "{rounded.none}"
    padding:         "10px 16px"
    borderBottom:    "2px solid transparent"

  tab-active:
    backgroundColor: "transparent"
    textColor:       "{colors.ink}"
    typography:      "{typography.heading-md}"
    rounded:         "{rounded.none}"
    padding:         "10px 16px"
    borderBottom:    "2px solid {colors.primary}"

  # ── Metric Cards (KPI) ────────────────────────────────────────────────────────
  metric-card:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink}"
    typography:      "{typography.data-tabular-lg}"
    rounded:         "{rounded.lg}"
    padding:         "20px"
    border:          "1px solid {colors.hairline}"
    shadow:          "{shadows.card}"

  metric-label:
    backgroundColor: "transparent"
    textColor:       "{colors.ink-secondary}"
    typography:      "{typography.caption}"
    rounded:         "{rounded.none}"
    padding:         "0"

  # ── Data Table ────────────────────────────────────────────────────────────────
  table-header:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink-secondary}"
    typography:      "{typography.micro}"
    rounded:         "{rounded.none}"
    padding:         "10px 12px"
    borderBottom:    "1px solid {colors.hairline-strong}"

  table-row:
    backgroundColor: "transparent"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.none}"
    padding:         "12px"

  table-row-alt:
    backgroundColor: "{colors.surface-raised}"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.none}"
    padding:         "12px"

  table-cell-numeric:
    backgroundColor: "transparent"
    textColor:       "{colors.ink}"
    typography:      "{typography.data-tabular}"
    rounded:         "{rounded.none}"
    padding:         "12px"

  # ── Cards (Detail Panels) ─────────────────────────────────────────────────────
  detail-card:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.lg}"
    padding:         "24px"
    border:          "1px solid {colors.hairline}"
    shadow:          "{shadows.card}"

  # ── Status Badges ─────────────────────────────────────────────────────────────
  badge-pass:
    backgroundColor: "{colors.status-pass-bg}"
    textColor:       "{colors.status-pass}"
    typography:      "{typography.micro}"
    rounded:         "{rounded.pill}"
    padding:         "3px 10px"

  badge-warn:
    backgroundColor: "{colors.status-warn-bg}"
    textColor:       "{colors.status-warn}"
    typography:      "{typography.micro}"
    rounded:         "{rounded.pill}"
    padding:         "3px 10px"

  badge-fail:
    backgroundColor: "{colors.status-fail-bg}"
    textColor:       "{colors.status-fail}"
    typography:      "{typography.micro}"
    rounded:         "{rounded.pill}"
    padding:         "3px 10px"

  badge-info:
    backgroundColor: "{colors.status-info-bg}"
    textColor:       "{colors.status-info}"
    typography:      "{typography.micro}"
    rounded:         "{rounded.pill}"
    padding:         "3px 10px"

  badge-ticker:
    backgroundColor: "{colors.primary-muted}"
    textColor:       "{colors.primary-soft}"
    typography:      "{typography.micro}"
    rounded:         "{rounded.sm}"
    padding:         "2px 8px"

  # ── Buttons ───────────────────────────────────────────────────────────────────
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor:       "#ffffff"
    typography:      "{typography.heading-sm}"
    rounded:         "{rounded.md}"
    padding:         "8px 20px"

  button-ghost:
    backgroundColor: "{colors.primary-muted}"
    textColor:       "{colors.primary-soft}"
    typography:      "{typography.heading-sm}"
    rounded:         "{rounded.md}"
    padding:         "8px 20px"
    border:          "1px solid {colors.primary}"

  button-disabled:
    backgroundColor: "{colors.surface-raised}"
    textColor:       "{colors.ink-disabled}"
    typography:      "{typography.heading-sm}"
    rounded:         "{rounded.md}"
    padding:         "8px 20px"
    cursor:          "not-allowed"

  # ── AI Pending Card ────────────────────────────────────────────────────────────
  ai-pending-card:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink-secondary}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.lg}"
    padding:         "20px 24px"
    border:          "1px dashed {colors.hairline-strong}"

  # ── Disclaimer / Alert Boxes ──────────────────────────────────────────────────
  alert-info:
    backgroundColor: "{colors.status-info-bg}"
    textColor:       "{colors.status-info}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.md}"
    padding:         "12px 16px"
    borderLeft:      "3px solid {colors.status-info}"

  alert-warn:
    backgroundColor: "{colors.status-warn-bg}"
    textColor:       "{colors.status-warn}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.md}"
    padding:         "12px 16px"
    borderLeft:      "3px solid {colors.status-warn}"

  alert-success:
    backgroundColor: "{colors.status-pass-bg}"
    textColor:       "{colors.status-pass}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.md}"
    padding:         "12px 16px"
    borderLeft:      "3px solid {colors.status-pass}"

  # ── Search / Filter Inputs ────────────────────────────────────────────────────
  input-search:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.md}"
    padding:         "8px 12px"
    border:          "1px solid {colors.hairline-strong}"

  input-search-focused:
    backgroundColor: "{colors.surface}"
    textColor:       "{colors.ink}"
    typography:      "{typography.body-md}"
    rounded:         "{rounded.md}"
    padding:         "8px 12px"
    border:          "1px solid {colors.primary}"
    shadow:          "{shadows.focus}"

  # ── Section Divider ───────────────────────────────────────────────────────────
  divider:
    borderTop:       "1px solid {colors.hairline}"
    margin:          "24px 0"
---

## Overview

The Nasdaq-100 관찰 후보 PoC design language draws from **Bloomberg Terminal aesthetics** fused with modern fintech dashboard conventions. The canvas is near-black (`#0F172A`, Tailwind `slate-900`), creating the focused, distraction-free environment needed for financial data analysis.

### Visual Hierarchy

Three surface layers create depth:
- **Canvas** (`#0F172A`) — page background
- **Surface** (`#1E293B`) — cards, sidebar, table headers
- **Surface-Raised** (`#334155`) — hover states, alternating table rows, interactive feedback

### Color Roles

**Electric blue** (`#3B82F6`) is the single primary accent — used exclusively for links, active tab underlines, and primary buttons. It should never appear on a PASS/FAIL status indicator.

**Traffic-light status palette** is reserved strictly for data-quality and PoC result states:
- 🟢 Emerald (`#10B981`) → `PASS`, eligible, data present
- 🟡 Amber (`#F59E0B`) → `CONDITIONAL_PASS`, warnings, data gaps
- 🔴 Rose (`#EF4444`) → `FAIL`, errors, missing data

**Data role colors** differentiate candidate types at a glance:
- Green → inclusion watch candidates
- Amber → exclusion watch candidates
- Indigo → neutral metrics

### Typography

All financial numerics (market cap, ratios, completeness rates, ranking numbers) must use the `data-tabular` or `data-tabular-lg` type style with `font-feature-settings: "tnum"` to ensure column alignment. Ticker symbols use `micro` uppercase style inside `badge-ticker` components.

Body copy uses **Inter** (system fallback to SF Pro / system-ui). No serif fonts are used — this is a data-forward interface.

### Data Tables

Tables are the primary content surface. Rules:
- Headers: `table-header` style — uppercase micro, `ink-secondary`
- Rows alternate between `transparent` and `surface-raised` for scanability
- Numeric columns: always `data-tabular` fontFamily, right-aligned
- Ticker column: wrapped in `badge-ticker` pill for visual anchoring
- No borders between data cells; only one hairline between header and body

### Status Display Rules

| State | Badge Component | Icon |
|---|---|---|
| `PASS` | `badge-pass` | ✅ |
| `CONDITIONAL_PASS` | `badge-warn` | ⚠️ |
| `FAIL` | `badge-fail` | ❌ |
| `UNKNOWN` | `badge-info` | ℹ️ |

### AI Pending Sections

AI-unconnected features use `ai-pending-card` with a dashed border and `ink-secondary` text. A "🔌 AI 연결 대기 중" micro-label appears in the top-right. The dashed border communicates *placeholder* without implying brokenness.

### Disclaimer Design

Investment-disclaimer text always renders inside `alert-info` or `alert-warn`. It must appear:
1. Immediately below the page/tab title
2. In the sidebar footer
3. Within every detail panel

The disclaimer never uses red (`status-fail`) coloring — red is reserved for data errors, not legal notices.

### Spacing System

The 8px base grid drives all spacing. Most card padding is `xl` (24px) or `xxl` (32px). Metric cards use `20px` for density. Section dividers use `24px` vertical margin.

### What This Design Explicitly Avoids

- No CTA buttons phrased as trading actions (Buy, Sell, Invest)
- No green arrows implying stock-price gains
- No red text for exclusion candidates (would imply danger/loss)
- No "예상 수익률" or "편입 확률" displays (factually undefined)
- No decorative gradients that mimic stock-chart aesthetics

The design reinforces the Prototype's core constraint: **this is an observation report, not a trading tool.**
