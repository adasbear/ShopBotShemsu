---
name: Nautical Sketch
colors:
  surface: '#fff8f7'
  surface-dim: '#f1d3d0'
  surface-bright: '#fff8f7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff0ef'
  surface-container: '#ffe9e7'
  surface-container-high: '#ffe2de'
  surface-container-highest: '#f9dcd9'
  on-surface: '#271816'
  on-surface-variant: '#5b403d'
  inverse-surface: '#3e2c2a'
  inverse-on-surface: '#ffedeb'
  outline: '#8f6f6c'
  outline-variant: '#e4beba'
  surface-tint: '#ba1a20'
  primary: '#af101a'
  on-primary: '#ffffff'
  primary-container: '#d32f2f'
  on-primary-container: '#fff2f0'
  inverse-primary: '#ffb3ac'
  secondary: '#695f00'
  on-secondary: '#ffffff'
  secondary-container: '#f9e534'
  on-secondary-container: '#706500'
  tertiary: '#575946'
  on-tertiary: '#ffffff'
  tertiary-container: '#70715d'
  on-tertiary-container: '#f6f6dd'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad6'
  primary-fixed-dim: '#ffb3ac'
  on-primary-fixed: '#410003'
  on-primary-fixed-variant: '#930010'
  secondary-fixed: '#f9e534'
  secondary-fixed-dim: '#dbc90a'
  on-secondary-fixed: '#201c00'
  on-secondary-fixed-variant: '#4f4800'
  tertiary-fixed: '#e4e4cc'
  tertiary-fixed-dim: '#c8c8b0'
  on-tertiary-fixed: '#1b1d0e'
  on-tertiary-fixed-variant: '#474836'
  background: '#fff8f7'
  on-background: '#271816'
  surface-variant: '#f9dcd9'
  ink-black: '#1A1A1A'
  paper-shadow: '#E6E6CC'
  kelp-green: '#8BC34A'
  ocean-blue: '#03A9F4'
typography:
  headline-xl:
    fontFamily: Bricolage Grotesque
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 52px
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Bricolage Grotesque
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 36px
  headline-lg-mobile:
    fontFamily: Bricolage Grotesque
    fontSize: 28px
    fontWeight: '800'
    lineHeight: 32px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-mono:
    fontFamily: Space Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin-mobile: 20px
  margin-desktop: 40px
  card-gap: 12px
---

## Brand & Style

The design system is a high-energy, nostalgic tribute to 90s cartoon aesthetics, specifically capturing the whimsical and slightly chaotic spirit of the "Krusty Krab." It targets a younger, tech-savvy audience in the food delivery space that appreciates character-driven branding over sterile corporate design.

The chosen style is a mix of **Brutalism** and **Tactile Illustrative**. It utilizes heavy 2px - 4px black outlines, hand-drawn textures, and a "paper-scrap" layout philosophy. The UI should feel like a living comic book—vibrant, expressive, and intentionally unrefined. Every element should look like it was sketched on a greasy napkin or a piece of parchment, evoking a sense of fun and immediate appetite.

## Colors

The palette is anchored by a high-contrast trio: **Barnacle Red** for primary actions, **Treasure Yellow** for highlights and attention-grabbing elements, and **Sandy Beige** as the universal canvas.

- **Primary (#D32F2F):** Used for critical CTAs like "Place Order" and key branding moments.
- **Secondary (#FFEB3B):** Used for status indicators (Pending), price badges, and "Add to Cart" interactions.
- **Tertiary (#F5F5DC):** The primary background color. It should be layered with a subtle paper grain texture.
- **Ink Black (#1A1A1A):** Used for all structural borders, sketchy icons, and primary typography to maintain a comic-book feel.
- **Named Accents:** "Kelp Green" for success states and "Ocean Blue" for links or secondary utility actions.

## Typography

The typographic hierarchy balances expressive character with functional clarity.

- **Headlines:** Uses **Bricolage Grotesque**. It provides the "wonky," hand-drawn feel necessary for the brand while remaining professional. Headlines should often be paired with a thick black text-shadow or a yellow "highlighter" background-box.
- **Body:** Uses **Plus Jakarta Sans**. This ensures that menu item descriptions and nutritional info are legible even against textured backgrounds.
- **Labels/Utility:** Uses **Space Mono** for prices, timestamps, and order references. The monospaced nature mimics a printed cash register receipt, reinforcing the retail/food delivery theme.

## Layout & Spacing

The layout follows a **Fixed Grid** model for desktop (centered content at 1200px) and a fluid, edge-to-edge model for the Telegram Mini App view. 

Spacing should feel "loose" rather than systematic. While we use a 4px base unit, elements should often have slight rotations (1-2 degrees) or offset borders to avoid looking too "perfect." 

- **Grid:** 12-column grid for web; 2-column grid for the Menu item list.
- **Breakpoints:** Mobile (under 600px), Tablet (600px - 1024px), Desktop (1025px+).
- **Margins:** Heavy margins are encouraged to allow the "Sandy Beige" background texture to frame the content cards.

## Elevation & Depth

This system rejects soft, realistic shadows in favor of **Hard-Edge Depth** and **Paper Layering**.

- **Shadows:** Use 100% opacity black offsets. A card shouldn't have a blur; it should have a 4px black "shadow" offset to the bottom right.
- **Tonal Layers:** Depth is created by stacking "scraps." A menu item card is a light beige box on top of a red background strip.
- **Outlines:** Every interactive element must have a 2px - 3px Ink Black border.
- **Interactive States:** When a button is pressed, it should move 2px down and 2px right to "meet" its shadow, simulating a physical press.

## Shapes

Shapes in the design system are primarily rectangular but with "imperfect" corners. While we use a base roundedness of `0.25rem` (Soft), the visual interest comes from **Rough Edges**.

Containers should look like hand-cut paper. Use SVG clip-paths or masking to create slightly jagged edges on large banners and buttons. Status pills and tags should use a slightly higher roundedness to differentiate them from structural cards.

## Components

- **Buttons:** Large, bold boxes with 3px black borders and a 4px offset hard shadow. Primary buttons are Red (#D32F2F) with White text.
- **Menu Cards:** Two-column grid items. Image at the top, followed by a bold price in Yellow (#FFEB3B) with a black outline. The "+" button should be a circle with a thick black outline.
- **Chips (Categories):** Horizontal scrollable list of paper-like tags. The active state is highlighted with a yellow "marker" scribble behind the text.
- **Input Fields:** Styled like a form on a clipboard. Sandy Beige background with a solid bottom-border (2px Ink Black).
- **Status Pills:** 
    - *Pending:* Yellow box, black text, "sketchy" border.
    - *Accepted:* Green box, white text, solid border.
    - *Cancelled:* Red box, white text, jagged border.
- **Navigation Bar:** Fixed at the bottom with a 4px top border. Icons should be hand-drawn/line-art style.
- **Debt Banner:** Uses a "WANTED" poster aesthetic—slightly more distressed textures and centered bold typography.