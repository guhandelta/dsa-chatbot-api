---
track: language
difficulty: Easy
language: css
category: Fundamentals
source: authored
io_mode: function
---
# CSS fundamentals — Easy — Fundamentals

- **Role and Cascade:** CSS (Cascading Style Sheets) declares visual presentation and layout rules for HTML documents. Rules cascade based on importance (`!important`), specificity (inline > ID > class/attribute/pseudo-class > element/pseudo-element), and source order.
- **Box Model:** Every rendered element is a rectangular box comprising `content`, `padding`, `border`, and `margin`. Modern CSS sets `box-sizing: border-box` so width and height include padding and border.
- **Layout Modes:**
  - **Flexbox (1D):** `display: flex` organizes items along a single main axis or cross axis (`flex-direction`, `justify-content`, `align-items`, `flex-wrap`, `gap`). Ideal for navbars, card rows, and micro-alignments.
  - **Grid (2D):** `display: grid` defines 2D matrix layouts with rows and columns (`grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))`, `grid-template-rows`, `grid-template-areas`, `gap`).
- **Positioning:** `static` (default normal flow), `relative` (offset relative to normal position, establishes containing block), `absolute` (positioned relative to nearest positioned ancestor), `fixed` (viewport-relative), and `sticky` (toggles between relative and fixed based on scroll offset).
- **Responsive Design:** Fluid units (`%`, `vw`, `vh`, `rem`, `ch`), CSS clamp (`clamp(1rem, 2.5vw, 2rem)`), media queries (`@media (min-width: 768px)`), and container queries (`@container`).
- **Variables & Theming:** Custom properties (`--primary-color: #3b82f6; color: var(--primary-color)`) provide dynamic runtime theming, cascade down the DOM, and can be overridden within specific scopes or media queries (`prefers-color-scheme: dark`).
- **Typography and Spacing:** Use `rem` for font sizes and spacing relative to root font size for user accessibility scaling. Avoid fixing container heights to prevent text overflow.
- **Transitions and Animations:** Smooth micro-interactions via `transition: all 0.2s ease` and keyframe animations (`@keyframes`). Respect user motion preferences with `@media (prefers-reduced-motion: reduce)`.
