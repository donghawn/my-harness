# DESIGN.md — SEED Design System

> Source: SEED Design **Rootage v2.9.0** token/component spec (seed-docs MCP), extracted 2026-09-30.
> Token names use Rootage notation (`$color.bg.brand-solid`). In CSS they map to `var(--seed-color-bg-brand-solid)`.
>
> **HOWPET override:** the brand color is swapped from Seed carrot to **HOWPET green `#10AB7D` (Seed green-600)**. Every `brand` token now points to the green scale. So it can be told apart from the brand color, `positive` moves to the **blue** scale and `informative` moves to the **purple** scale. Everything else stays as Seed defines it.

---

## 1. Visual Theme & Atmosphere

- **Fresh and friendly.** HOWPET green `#10AB7D` is the only brand accent. Everything else is built from a neutral gray scale.
- **Lots of whitespace, few decorations.** Hierarchy comes from surface layers (basement → default → floating) and font weight, not from lines or shadows.
- **Mobile-first.** 16px global gutter, 44px (iOS) / 56px (Android) top navigation, 52px CTA buttons.
- **Tactile feedback.** Pressed elements scale down slightly (scale), and color transitions are 150ms with standard easing.
- **Light and dark themes both come built in.** Every semantic color has its own light/dark value.

---

## 2. Color

### 2.1 Brand & Palette (Light / Dark)

| Scale | 100 | 200 | 300 | 400 | 500 | **600** | 700 | 800 | 900 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| **green = brand** (L) | #edfaf6 | #d9f6e9 | #b9e9d2 | #7ddcb3 | #42c593 | **#10ab7d** | #079171 | #00745f | #075445 | #0a2b24 |
| **green = brand** (D) | #202926 | #20362e | #20493b | #19604c | #117956 | #1b946d | #22b27f | #35ce9a | #93e5c0 | #d4f6ef |
| gray (L) | #f7f8f9 | #f3f4f5 | #eeeff1 | #dcdee3 | #d1d3d8 | #b0b3ba | #868b94 | #555d6d | #2a3038 | #1a1c20 |
| gray (D) | #16171b | #1d2025 | #2b2e35 | #393d46 | #5b606a | #868b94 | #b0b3ba | #dcdee3 | #e9eaec | #f3f4f5 |
| blue (L) | #eff6ff | #e2edfc | #cbdffa | #aacefd | #85b8fd | #5e98fe | #217cf9 | #135fcd | #0b4596 | #032451 |
| red (L) | #fdf0f0 | #fde7e7 | #fed4d2 | #feb7b3 | #fe928d | #fc6a66 | #fa342c | #ca1d13 | #921708 | #4a1209 |
| yellow (L) | #fff7de | #fdefb9 | #fbdc65 | #e9c647 | #d4ab28 | #c49725 | #9b7821 | #755b22 | #4f3e1f | #2c2512 |
| purple (L) | #f5f3fe | #efeafe | #e1d8ff | #d0c0ff | #b8a1ff | #9f84fb | #8969ea | #6d50cb | #50379b | #29175d |

The Seed `carrot` scale isn't used in HOWPET. `gray-00` = #ffffff (Light) / #000000 (Dark). `static-white` and `static-black` stay the same in both themes.

> **Rule:** don't use palette tokens directly in UI code. Always go through the semantic tokens below.

### 2.2 Semantic — Foreground (`$color.fg.*`)

| Token | Light | Dark | Use |
|---|---|---|---|
| `fg.neutral` | #1a1c20 | #f3f4f5 | Default text |
| `fg.neutral-muted` | #555d6d | #dcdee3 | Secondary text, descriptions |
| `fg.neutral-subtle` | #868b94 | #b0b3ba | Tertiary text, meta info, unselected tabs |
| `fg.neutral-inverted` | #ffffff | #16171b | Text on inverted backgrounds |
| `fg.placeholder` | #b0b3ba | #868b94 | Input placeholder |
| `fg.disabled` | #d1d3d8 | #5b606a | Disabled |
| `fg.brand` | #10ab7d | #22b27f | Brand emphasis (green-600) |
| `fg.brand-contrast` | #079171 | #22b27f | Brand text on weak backgrounds (green-700) |
| `fg.critical` / `-contrast` | #fa342c / #921708 | #ff6e60 / #f8c5c3 | Errors, danger |
| `fg.informative` / `-contrast` | #8969ea / #50379b | #a78df0 / #d9cefa | Information (HOWPET: purple) |
| `fg.positive` / `-contrast` | #217cf9 / #0b4596 | #41a2f9 / #b9d7fb | Success, done (HOWPET: blue) |
| `fg.warning` / `-contrast` | #9b7821 / #4f3e1f | #ca901c / #e5d49b | Caution |

### 2.3 Semantic — Background (`$color.bg.*`)

**Layers (surface hierarchy)**

| Token | Light | Dark | Use |
|---|---|---|---|
| `bg.layer-basement` | #f3f4f5 | #000000 | Level 0, the deepest full-screen background |
| `bg.layer-default` | #ffffff | #16171b | Default surface: most content such as lists and text fields |
| `bg.layer-default-pressed` | #f7f8f9 | #2b2e35 | Pressed |
| `bg.layer-floating` | #ffffff | #1d2025 | Modals, bottom sheets, dialogs |
| `bg.overlay` | #00000074 | #00000074 | Modal backdrop |
| `bg.overlay-muted` | #0000002c | #0000002c | Faint dimming |

**Intent (solid / weak + pressed)**

| Intent | solid | solid-pressed | weak | weak-pressed |
|---|---|---|---|---|
| **brand** | #10ab7d | #079171 | #edfaf6 | #d9f6e9 |
| neutral | `neutral-solid` #1a1c20 · `neutral-inverted` #2a3038 | inverted-pressed #555d6d | #f3f4f5 | #eeeff1 |
| critical | #fa342c | #ca1d13 | #fdf0f0 | #fde7e7 |
| informative (purple) | #8969ea | #6d50cb | #f5f3fe | #efeafe |
| positive (blue) | #217cf9 | #135fcd | #eff6ff | #e2edfc |
| warning | #fbdc65 | #e9c647 | #fff7de | #fdefb9 |

(All values are Light. Dark values for HOWPET-changed intents (solid · solid-pressed · weak · weak-pressed): brand #1b946d · #22b27f · #202926 · #20362e / positive #1e82eb · #41a2f9 · #202742 · #1e3352 / informative #8e6bee · #a78df0 · #28213b · #3b2873. For other Dark values, see the Rootage `color.json`.)

- `bg.neutral-weak-alpha` #0000000c (Dark #ffffff20): keeps components visible when placed on basement
- `bg.transparent-pressed` #00000007 · `transparent-selected` #0000000c
- `bg.disabled` #f3f4f5 (Dark #2b2e35)
- `bg.magic-weak` #f9f2ee: AI feature background

### 2.4 Semantic — Stroke (`$color.stroke.*`)

| Token | Light | Dark | Use |
|---|---|---|---|
| `stroke.neutral-weak` | #dcdee3 | #393d46 | **Outlines that define a shape** (cards, inputs, outline buttons) |
| `stroke.neutral-muted` | #00000010 | #ffffff17 | **Boundaries between sections**, used only once or twice per screen |
| `stroke.neutral-subtle` | #0000000c | #ffffff0d | **Dividers between repeated items** (list rows, settings items) |
| `stroke.neutral-contrast` | #1a1c20 | #f3f4f5 | Focused inputs, selected state |
| `stroke.neutral-solid` | #555d6d | #dcdee3 | Strong outlines |
| `stroke.focus-ring` | #5e98fe | #1e82eb | Keyboard focus |
| `stroke.brand-solid` / `-weak` | #079171 / #b9e9d2 | #22b27f / #20493b | Brand outlines |
| `stroke.critical-solid` / `-weak` | #fa342c / #fed4d2 | #ff6e60 / #742826 | Invalid input |
| `stroke.positive-solid` / `-weak` | #217cf9 / #cbdffa | #41a2f9 / #1a4275 | Success (HOWPET: blue) |
| `stroke.informative-solid` / `-weak` | #8969ea / #e1d8ff | #a78df0 / #443081 | Information (HOWPET: purple) |

### 2.5 Gradient (AI / Magic)

| Token | Value (Light) | Use |
|---|---|---|
| `gradient.highlight-magic` | #10ab7d (20%) → #217cf9 (100%) | Icons and shapes for AI features (HOWPET: green → blue) |
| `gradient.glow-magic` | #f3fbf8 → #edfaf6 (80%) → #f7f8f9 | AI background glow (HOWPET: green tint) |
| `gradient.shimmer-neutral` | white 0 → ab → ab → 0 | Skeleton shimmer |
| `gradient.shimmer-magic` | #f3fbf8 alpha | AI skeleton shimmer |

### 2.6 HOWPET Secondary Colors

| Role | Token (proposed) | Light | Dark | Use |
|---|---|---|---|---|
| Secondary yellow (character) | `palette.yellow-300` | #fbdc65 | #543e15 | Shiba character, badges, reward highlights |
| Secondary yellow weak | `palette.yellow-100` | #fff7de | #302819 | Reward card backgrounds |
| Quiz background (dark navy) | `palette.blue-1000` | #032451 | #032451 | Full-screen quiz background (same in both themes) |
| Text on quiz screen | `palette.static-white` / `static-white-alpha-700` | #ffffff / #ffffffb3 | same | Quiz title / description |

- The yellow is the same value as `bg.warning-solid`. Where yellow is used for the character or rewards, pair it with the character or an icon so it doesn't read as a warning.
- Quiz screens stay dark navy in light mode too. Buttons on them use `brandSolid` (green) or `static-white` backgrounds.
- Emergency mode: routes and buttons switch to `bg.critical-solid` #fa342c (per the PRD's red rule).

### 2.7 Special Purpose
- **Banner** `banner.{blue,cool-gray,green,orange,pink,purple,red,teal,warm-gray,yellow}`: soft pastel backgrounds (e.g. orange #fff2e1, blue #e1f7ff).

---

## 3. Typography

- **Font family:** Rootage doesn't define a font token. Use the platform system font (Apple SD Gothic Neo / Roboto and Noto Sans KR).
- **Weights:** `regular 400` · `medium 500` · `bold 700`. Only these three.
- **Sizes are rem-based**, so they respond to OS font scaling. Use the `-static` (px) variants only when text must not scale.
- `t11` and above are recommended only at the **`sm` breakpoint or wider**.

| Step | Size | Line height | Primary use |
|---|---|---|---|
| t1 | 11px (0.6875rem) | 15px | Medium badge |
| t2 | 12px (0.75rem) | 16px | Large badge, subtitles, captions |
| t3 | 13px (0.8125rem) | 18px | List detail, xsmall button |
| t4 | 14px (0.875rem) | 19px | Small/medium buttons, chips, snackbar, small tab |
| t5 | 16px (1rem) | 22px | **Body / default**: list title, input, medium tab |
| t6 | 18px (1.125rem) | 24px | Large CTA button, top nav title |
| t7 | 20px (1.25rem) | 27px | Dialog title |
| t8 | 22px (1.375rem) | 30px | Bottom sheet title |
| t9 | 24px (1.5rem) | 32px | Section heading |
| t10 | 26px (1.625rem) | 35px | Screen title |
| t11 | 28px (1.75rem) | 38px | sm+ |
| t12 | 32px (2rem) | 42px | sm+ |
| t13 | 40px (2.5rem) | 52px | sm+ |
| t14 | 48px (3rem) | 60px | sm+ |

Each step comes in `tNRegular / tNMedium / tNBold` and `tNStatic*` variants.

**Semantic text styles**

| Style | Spec | Use |
|---|---|---|
| `screenTitle` | t10 · 26/35 · Bold | Large title at the top of a screen |
| `articleBody` | t5 · 16px / 24px (lh t6) · Regular | Body text of posts and content (relaxed line height) |
| `articleNote` | t4 · 14px / 22px (lh t5) · Regular | Notes and supplementary info (not for body text) |

---

## 4. Spacing & Layout

**Base unit 4px.** `$dimension.xN` = N × 4px

| Token | px | | Token | px |
|---|---|---|---|---|
| x0_5 | 2 | | x5 | 20 |
| x1 | 4 | | x6 | 24 |
| x1_5 | 6 | | x7 | 28 |
| x2 | 8 | | x8 | 32 |
| x2_5 | 10 | | x9 | 36 |
| x3 | 12 | | x10 | 40 |
| x3_5 | 14 | | x12 | 48 |
| x4 | 16 | | x13 | 52 |
| x4_5 | 18 | | x14 | 56 |
| | | | x16 | 64 |

**Semantic spacing**

| Token | Value | Use |
|---|---|---|
| `spacing-x.global-gutter` | 16px | Default horizontal padding for the whole screen |
| `spacing-x.between-chips` | 8px | Horizontal gap between chips |
| `spacing-y.component-default` | 12px | Default vertical gap between components |
| `spacing-y.nav-to-title` | 20px | Top Navigation → Page Title |
| `spacing-y.between-text` | 6px | Between text elements |
| `spacing-y.screen-bottom` | 56px | Bottom margin of a screen |

---

## 5. Shape (Radius)

| Token | px | Typical use |
|---|---|---|
| r0_5 | 2 | |
| r1 | 4 | Medium badge |
| r1_5 | 6 | Large badge |
| r2 | 8 | Small/medium buttons, snackbar, medium input |
| r2_5 | 10 | List item pressed background |
| r3 | 12 | Large button (CTA), large input |
| r3_5 | 14 | |
| r4 | 16 | Cards |
| r5 | 20 | Alert dialog |
| r6 | 24 | Top corners of bottom sheets |
| full | 9999 | Chips, xsmall buttons (pills) |

---

## 6. Elevation (Shadow)

Depth mostly comes from **surface layer colors**. Keep shadows to a minimum.

| Token | Light | Dark | Use |
|---|---|---|---|
| `shadow.s1` | 0 1px 4px #00000014 | 0 1px 4px #00000080 | Subtle lift |
| `shadow.s2` | 0 2px 10px #0000001a | 0 2px 10px #000000ad | Floating elements (FAB, etc.) |
| `shadow.s3` | 0 4px 16px #0000001f | 0 4px 16px #000000cc | The layer above everything else |

---

## 7. Motion

**Duration:** d1 50ms · d2 100ms · d3 150ms · d4 200ms · d5 250ms · d6 300ms
- `duration.color-transition` = 150ms, `duration.pressed-scale` = 150ms

**Timing function**

| Token | cubic-bezier | Use |
|---|---|---|
| `easing` | (0.35, 0, 0.35, 1) | Default: color and position changes |
| `enter` | (0, 0, 0.15, 1) | Entering |
| `exit` | (0.35, 0, 1, 1) | Exiting |
| `enter-expressive` | (0.03, 0.4, 0.1, 1) | Bottom sheet and dialog entrances |
| `exit-expressive` | (0.35, 0, 0.95, 0.55) | Expressive exits |
| `pressed-scale` | (0, 0, 0.15, 1) | Pressed scale |
| `linear` | (0, 0, 1, 1) | |

**Patterns**
- Bottom sheet: enter 300ms `enter-expressive` / exit 200ms `exit`, backdrop fade 300ms
- Alert dialog: scale 1.3 → 1 + fade, 200ms `enter-expressive` / exit 100ms
- Snackbar: scale 0.8 → 1 + fade, 150ms enter / 100ms exit
- On press, buttons, chips, and tabs scale themselves (`self`). List items scale their content and shrink the background by 6px on each side while rounding corners to 10px.

---

## 8. Components

### Action Button
| Size | Height | Radius | Padding X | Label | Icon |
|---|---|---|---|---|---|
| xsmall | 32 | full (pill) | 14 | t3 13px Bold | 14 |
| small | 36 | r2 8 | 14 | t4 14px Bold | 14 |
| medium | 40 | r2 8 | 16 | t4 14px Bold | 16 |
| large (CTA) | 52 | r3 12 | 20 | t6 18px Bold | 22 |

| Variant | Background | Label | Guide |
|---|---|---|---|
| `brandSolid` | bg.brand-solid #10ab7d | white | HOWPET core actions (start a walk, etc.). **One per screen** |
| `neutralSolid` | bg.neutral-inverted #2a3038 | fg.neutral-inverted | The default CTA on most screens. **One per screen** |
| `neutralWeak` | bg.neutral-weak #f3f4f5 | fg.neutral | Most actions other than the CTA |
| `criticalSolid` | bg.critical-solid #fa342c | white | Irreversible actions such as delete or reset |
| `neutralOutline` / `brandOutline` | transparent + stroke.neutral-muted 1px | fg.neutral / fg.brand | Don't combine with solid variants; pair outlines with each other |
| `ghost` | transparent | fg.neutral | Text or icon only |

Disabled: bg.disabled + fg.disabled. Loading: pressed color + progress circle.

### Text Input
- **outline / large**: height 52, r3 12, padding X 16, gap 10, t5 16px. stroke.neutral-weak 1px → focus: stroke.neutral-contrast 2px → invalid: stroke.critical-solid 2px
- **outline / medium**: height 40, r2 8, t4 14px. **Only at `lg` (desktop) and wider**
- **underline**: bottom 1px line. Recommended when a screen has only one input. Large is 40 tall with t6 18px text
- Multiline: minimum height 94 (large) / 82 (medium)
- Readonly and disabled use bg.disabled for the background. Placeholder uses fg.placeholder

### Top Navigation
- Height **iOS 44 / Android 56**, padding X 6
- Title: t6 18px Bold (titleOnly), or t5 16px Bold + subtitle t2 12px Regular (withSubtitle). Font scaling is capped at 1.2×
- `tone=layer` (bg.layer-default) or `tone=transparent` (white text + top gradient #00000059 → 0, 20px bleed)

### List Item
- Padding Y 12, X 16 (gutter). Title t5 16px Regular fg.neutral. Detail t3 13px fg.neutral-subtle
- Prefix icon 22 (right spacing 12). Suffix text t5 fg.neutral-subtle. Suffix icon 18
- pressed: bg.transparent-pressed, content scales down. highlighted: bg.brand-weak

### Chip
- Heights small 32 / medium 36 / large 40, **radius full**, label t4 14px **Medium**
- `solid` (bg.neutral-weak-alpha) · `outlineStrong` · `outlineWeak`
- Selected: bg.neutral-inverted + inverted text (outlineWeak uses a stroke.neutral-contrast border instead). Disabled: opacity 0.5

### Badge
- large: height 24, r1_5 6, padding 8×4, t2 12px. medium: height 20, r1 4, t1 11px
- `weak` (Medium) · `solid` (Bold) · `outline` (Bold, 1px)
- Tones: neutral / brand / informative / positive / warning / critical
- Weak badges use `bg.{tone}-weak` + `fg.{tone}-contrast`

### Tab
- medium: height 44, t5 16px Bold. small: height 40, t4 14px Bold
- Unselected fg.neutral-subtle → selected fg.neutral

### Bottom Sheet
- bg.layer-floating, **top radius 24**, max width 480
- Header padding top 24 / bottom 16. Title t8 22px Bold. Description t5 fg.neutral-muted
- Footer padding 12 / 16 / 16 (gutter). Close button sits 24 from the top and 16 from the right
- Backdrop bg.overlay

### Alert Dialog
- bg.layer-floating, **radius 20**, max width 272, screen margin X 32 / Y 64
- Padding 20. Title t7 20px Bold. Description t5 16px. Button gap 8

### Snackbar
- bg.neutral-inverted, r2 8, min height 44, max width 464, padding 10
- Message t4 14px Regular fg.neutral-inverted. Action t4 Bold **fg.brand**
- variant positive / critical changes only the prefix icon color

---

## 9. Do's & Don'ts

**Do**
- Use one CTA per screen, either `brandSolid` or `neutralSolid`
- Keep a 16px horizontal gutter on every screen
- Stack surfaces in order: basement → default → floating
- Use the right divider for the job: repeated items get `stroke.neutral-subtle`, section boundaries get `stroke.neutral-muted`, shape outlines get `stroke.neutral-weak`
- Use rem-based font sizes so text responds to OS font scaling
- Give interactive elements a pressed state (scale plus color change, 150ms)

**Don't**
- Don't use palette hex values or tokens directly. Use semantic tokens so dark mode works
- Don't put brand green on large surfaces. Keep it for key actions and highlights
- Don't use font weights other than 400, 500, and 700
- Don't use green for status (success/info). Green is for the brand only. Success is blue, info is purple
- Don't use t11 or larger on mobile widths below sm
- Don't use the medium input size on mobile
- Don't put outline buttons next to solid buttons
- Don't use icon-only buttons without an accessibility label

---

## 10. Agent Prompt Guide (Quick Reference)

```
Brand: #10AB7D (HOWPET green = Seed green-600, pressed #079171, weak #EDFAF6).
Secondary: character yellow #FBDC65, quiz screen dark navy #032451 (white text). Emergency: red #FA342C.
Status: success = blue #217CF9, info = purple #8969EA, warning = yellow, error = red. Never use green for status.
Text #1A1C20 / muted #555D6D / subtle #868B94.
Surface: basement #F3F4F5 → default #FFFFFF → floating #FFFFFF. Overlay #00000074.
Divider: rgba(0,0,0,.05)–.06, outline #DCDEE3.
Type: system font, 400/500/700. Body 16/22, Title 26/35 Bold, Nav 18/24 Bold.
Spacing: 4px grid, gutter 16, component gap 12, screen bottom 56.
Radius: button 8 (L:12), input 12, chip/pill full, sheet 24, dialog 20.
CTA: 52px tall, r12, 18px Bold. Only one per screen.
Motion: 150ms cubic-bezier(.35,0,.35,1); sheets 300ms cubic-bezier(.03,.4,.1,1).
```
