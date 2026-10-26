# CSS, Sass and Bootstrap: architecture, reference and practice

A technical curriculum for front-end engineers, instructors and AI mentors

## 1 Scope, learning routes and evidence

CSS describes presentation; HTML describes structure and meaning; JavaScript coordinates behavior. Sass is a build-time language that emits CSS. Bootstrap is a collection of CSS conventions, Sass sources, components and JavaScript plugins. Understanding their separate responsibilities is essential to using them together. A working page is the output of the entire system, including browser algorithms, assets, fonts, input devices and user preferences.

This guide follows the earlier HTML curriculum's format: mental model, precise reference, concrete example, common mistake, practice and evidence. It has four main subject areas: CSS fundamentals and architecture, Sass/SCSS, Bootstrap 5, and their runtime integration with the DOM and Web APIs. The reference appendices supply property metadata and additional inventories so that the narrative remains teachable rather than becoming an unstructured list of names.

**Version boundary.** CSS3 is a historical umbrella name. Modern CSS consists of independently versioned modules. The CSS property appendix covers every non-vendor property record in the retrieved W3C Webref package, including advanced, SVG, print, speech and experimental proposals. Records in the CSS Snapshot 2025 property index are identified; inclusion in either source is not a browser-support guarantee. The Snapshot index itself includes historical names. Draft-only entries are research references, not blanket production recommendations. Vendor compatibility aliases and historical aural properties receive separate treatment. Custom properties are an open-ended family.

The package versions and source hashes are recorded in the verification appendix. Bootstrap examples target 5.3.8. Sass examples use Dart Sass 1.105.2. Living specifications and versioned package sources can differ: a new grammar alternative in a draft may be unsupported by all target browsers. Feature detection proves only the specific condition tested. A valid declaration can still be ineffective in the current layout context.

**Accessibility boundary.** The examples use semantic controls, visible labels, keyboard paths, contrast-conscious colors, responsive reflow and motion preferences. The target is WCAG 2.2 AA, including applicable A criteria. An isolated stylesheet or an automated scan cannot certify an entire experience as WCAG compliant. The verification record states which compilation, browser and automated accessibility checks were actually run; manual screen-reader, zoom, forced-color and cross-engine testing remain explicit acceptance work. Small syntax examples are complete rules or complete functions; the integrated labs supply runnable documents and their actual dependencies.

### Common curriculum, different entry points

- Foundations: learn cascade, computed values, boxes, normal flow and source order before layout abstractions.
- Layout: practice intrinsic sizing, Flexbox and Grid, then responsive constraints and component queries.
- Maintainability: introduce tokens, layers, naming, Sass modules and generated utilities after the plain CSS behavior is understood.
- Framework use: map Bootstrap classes to the CSS they emit, then study component state and plugin ownership.
- Runtime integration: connect DOM state and browser APIs to style changes with cleanup, fallbacks and measured performance.
- Assessment: explain a failure, predict the computed result, inspect evidence, repair the cause and test a counterexample. Do not award mastery for matching a screenshot alone.

### Fourteen teaching lenses

For every lesson ask: what is the mental model; how is the rule created; how is its target selected; what changes its value; how do nodes enter or leave; what is the traversal order; what establishes identity; what orders competing rules; what transforms specified values; what work does the renderer perform; what happens at boundaries; which alternative fits; which reusable pattern emerges; and which observation proves the claim? Apply these to CSS rather than inventing algorithmic complexity claims for a selector or framework class.

## 2 CSS grammar, values and the cascade

### Rules and parsing

A qualified rule combines a selector list with a declaration block. A declaration contains a property, colon, value and optional importance flag. An at-rule has a name, prelude and either a semicolon or a block. Comments are removed during tokenization. Unrecognized declarations are generally discarded individually; an invalid selector can invalidate an ordinary selector list. Forgiving selector lists have specifically defined recovery behavior. Parsing recovery is not a guarantee that an intended design survives.

```css
/* Complete stylesheet fragment. */
.notice {
  color: #172b4d;
  background-color: #fff;
  padding: 1rem;
  border: 0.125rem solid currentColor;
}
@media (width >= 48rem) {
  .notice { padding: 1.5rem; }
}
```

Browser devtools distinguishes a rule that never matched, a matched declaration that lost the cascade, an invalid value and a winning value with no visible effect. Debug in that order. Do not respond to every unexpected result by adding `!important`.

Source: https://drafts.csswg.org/css-syntax-3/

### Grammar notation and acceptable value types

In the property appendix, `|` means choose one alternative; `||` permits one or more alternatives in any order; `&&` requires every component in any order; juxtaposition requires sequence. Square brackets group grammar, not literal brackets. `?` means optional, `*` zero or more, `+` one or more, `#` a comma-separated list, and `{m,n}` a repetition range. Quoted property references such as `<'margin-top'>` mean use that property's value grammar. Angle-bracket names refer to defined types, not literal markup. Ranges such as `<number [0,1]>` constrain the value. Consult the defining module for computed-value restrictions and newer syntax.

An identifier is not automatically a string; an unquoted family name can have different parsing rules from a quoted font name. `<custom-ident>` excludes reserved identifiers in its context. `<dashed-ident>` starts with two hyphens. Strings use quotes and escapes. URLs use URL syntax and must still satisfy application security policy. Images include raster resources, gradients and supported generated images. Colors include named values, hex, rgb/hsl and modern color spaces where supported. `currentColor` connects many paint values to the element's color.

Numbers can be unitless or have dimensions. Lengths include px, em, rem, ch, ex, lh, rlh, viewport units and container query units. A CSS pixel is a reference unit, not necessarily a physical device pixel. `em` in font-size relates to the parent; in many other properties it relates to the element's font size. `rem` uses the root font size. `ch` measures a font's zero advance and is useful for approximate line lengths, not exact character counts. Angles include deg, rad, grad and turn; times include s and ms; resolutions include dppx and dpi. Zero-length unit omission is contextual and must not be transferred to time or arbitrary typed values.

Percentages resolve against a property-specific reference. Width, height, padding, transforms, backgrounds and gaps do not share one universal percentage base. An indefinite containing size can change how a percentage participates in layout. `fr` is a Grid flexible track unit, not a general length. `auto`, `normal`, `none`, `initial` and zero are not interchangeable.

`calc()` combines compatible dimensions. `min()` and `max()` choose bounds; `clamp()` constrains a preferred value. Keep spaces around binary plus/minus in calc expressions. Multiplication/division support depends on the CSS Values level; do not assume Sass arithmetic and browser arithmetic have the same rules. Intrinsic keywords such as min-content, max-content, fit-content and stretch are context-sensitive sizing requests.

```css
.article {
  inline-size: min(100% - 2rem, 70rem);
  margin-inline: auto;
  font-size: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  line-height: 1.6;
}
```

The fluid font retains rem bounds. Test browser text scaling; a viewport-only size can defeat the intended enlargement. Small/large/dynamic viewport units address different mobile viewport states; dynamic units can change while browser chrome moves. Container units require a suitable query container, and fallback behavior must be understood before using them.

Source: https://drafts.csswg.org/css-values-4/

### Cascade precedence, specificity and source order

First determine relevance: selector match, media condition, feature condition, scope and tree. Cascade origin and importance then outrank layer order and specificity. In ascending priority the broad origin order is normal user-agent rules, normal user rules, normal author rules, keyframe animation values, important author rules, important user rules, important user-agent rules and active transition values. Encapsulation contexts and inline declarations add defined tie-breaks. Within the same cascade level, normal unlayered author rules outrank normal layered rules; later normal layers outrank earlier ones. Important layer order reverses, so early important layers outrank later ones, and layered important declarations outrank unlayered important declarations. Use importance sparingly and account for user overrides.

Specificity is a tuple: IDs; classes/attributes/pseudo-classes; types/pseudo-elements. Compare left to right, never by a decimal score. Combinators and the universal selector add no weight. `:where()` has zero specificity including its arguments. `:is()`, `:not()` and `:has()` take the specificity of their most specific argument. `:nth-child(... of S)` adds its pseudo-class weight and the most specific selector in S. Inline styles occupy a separate precedence position, not a magical ID score. After specificity ties, scope proximity can matter before source order under `@scope` rules.

Examples: `.card a` is (0,1,1); `[aria-expanded="true"]` is (0,1,0); `#app .card` is (1,1,0); `:where(#app) .card` is (0,1,0); `:is(.card, #special) button` is (1,0,1). Putting an ID in an unused branch of :is can still raise the rule's specificity.

```css
@layer reset, vendor, tokens, base, components, utilities;
@layer base {
  :where(button, input, select, textarea) { font: inherit; }
}
@layer components {
  .action { border: 0.125rem solid currentColor; }
  .action:focus-visible { outline: 0.1875rem solid #111; outline-offset: 0.2rem; }
}
```

A framework loaded unlayered will outrank these normal layered declarations regardless of their selector weight. Load the framework into the vendor layer deliberately or maintain a separate, documented override strategy. CSS imports must obey placement rules; importing with `layer(vendor)` is different from copying Sass source into a layer block.

Source: https://drafts.csswg.org/css-cascade-6/
Source: https://drafts.csswg.org/selectors-4/

### Inheritance, defaults and value processing

A declaration produces a specified value after cascade and defaulting; computation resolves dependencies; layout determines used values; rendering may approximate actual values. `getComputedStyle()` returns resolved values, which can be used values for some properties. It does not reproduce authored shorthand text or prove that a layout is accessible.

Inherited properties normally take the parent's computed value when no declaration wins. Non-inherited properties normally take their initial value. Initial is the specification default, not the browser's HTML stylesheet choice: display initially is inline even though div commonly displays as block. `inherit` explicitly takes the parent's computed value. `initial` resets to the specification initial. `unset` chooses inherit or initial based on normal inheritance. `revert` rolls back the current origin; `revert-layer` rolls back the current cascade layer according to its rules.

Shorthands set multiple longhands together and can reset omitted components. Background can reset background-color; font resets multiple font settings; border resets border-image. Later longhands can override individual parts. A shorthand containing var() may defer parsing, then become invalid at computed-value time. The browser does not necessarily revive an earlier declaration when that happens.

Custom properties usually inherit and preserve token streams; `var()` substitutes tokens in consuming declarations. A fallback is used when substitution needs it, not whenever the substituted value is invalid for the consuming property. `--size: red; width: var(--size, 10rem)` does not make 10rem win. Registration through `@property` supplies syntax, inheritance and an initial value under its constraints. Application token names remain open-ended.

```css
@property --progress {
  syntax: "<number>";
  inherits: false;
  initial-value: 0;
}
:root { --space-2: 0.5rem; --surface: #fff; --ink: #172b4d; }
.panel { padding: var(--space-2); background: var(--surface); color: var(--ink); }
```

Practice: predict the winning color across two layers, an inline declaration and a user important declaration. Then inspect each contender. Separately test an invalid custom-property substitution; explain why cascade selection and computed-value validation are distinct stages.

## 3 Selectors, DOM relationships and state

Type, class, ID, universal and namespace selectors select by different identifiers. Attribute selectors test presence or exact, whitespace-token, language-prefix, prefix, suffix and substring matches: `[x]`, `[x="y"]`, `[x~="y"]`, `[x|="en"]`, `[x^="y"]`, `[x$="y"]`, `[x*="y"]`. The `i` flag requests ASCII case-insensitive matching; `s` requests case-sensitive matching where supported. HTML attribute-name matching and attribute-value matching are not one rule. Escape dynamic identifiers with CSS.escape when constructing a selector; prefer stable references over constructing selectors from untrusted text.

The descendant combinator follows ancestry; `>` means a direct child; `+` means adjacent following sibling; `~` means later siblings. The column combinator belongs to a specialized selector model and needs implementation verification. Selector lists are unions, not sequential operations. A relational :has selector tests relative selectors against its subject; it does not move the selected node to the descendant.

Structural pseudo-classes include :root, :empty, :first-child, :last-child, :only-child, :nth-child, :nth-last-child and their of-type variants. Counting follows the relevant element sibling list; `:nth-child(2 of .item)` differs from `.item:nth-child(2)`. Whitespace handling for :empty has specification and implementation history; do not use a fragile emptiness selector as the sole source of application truth.

State pseudo-classes include :hover, :active, :focus, :focus-visible, :focus-within, :checked, :indeterminate, :disabled, :enabled, :required, :optional, :valid, :invalid, :user-valid, :user-invalid, :in-range, :out-of-range, :read-only, :read-write, :placeholder-shown and :autofill. Match the correct native state. `[checked]` tests a content attribute; `:checked` tests current checkedness. `[aria-disabled="true"]` does not disable a control. `:visited` has deliberate privacy restrictions. :target reflects URL targeting, not generic component selection.

Language and direction selectors use :lang and :dir rather than assuming a lang/dir attribute exists on every descendant. :is, :where, :not and :has provide logical composition. :defined can distinguish upgraded custom elements; :host and :host-context have shadow-tree-specific rules and support constraints. Emerging states such as :state(), :modal and :popover-open are tied to their defining APIs. Treat the complete selector appendix as a source inventory, not a promise every browser implements every selector.

Pseudo-elements select generated or specialized parts: ::before, ::after, ::first-line, ::first-letter, ::marker, ::selection, ::placeholder, ::file-selector-button, ::backdrop, ::part(), ::slotted() and the view-transition pseudo-element tree. Generated content is not a dependable place for essential instructions or interactive controls. ::slotted selects assigned elements under specific restrictions; it does not become an unrestricted descendant selector into light DOM.

```css
.field:focus-within { border-color: #1b4d8a; }
input:checked + label { font-weight: 700; }
button:disabled { opacity: 0.7; cursor: not-allowed; }
button:focus-visible { outline: 0.1875rem solid #111; outline-offset: 0.2rem; }
@supports selector(:has(*)) {
  .field:has(input:user-invalid) { border-color: #9b1c20; }
}
```

A class alone never supplies a label. For the adjacent-selector example, input and associated label must actually be siblings in that order. Validation messages must exist as text and be connected to the control; a red border is insufficient. Practice: implement a disabled submit button and explain how keyboard activation differs from a styled aria-disabled link.

## 4 Boxes, normal flow and positioning

### The box model and intrinsic sizing

The content box is surrounded by padding, border and margin. With content-box, declared width describes content; with border-box it includes padding and border. Margin remains outside both. Minimum and maximum sizes constrain preferred sizes, and intrinsic contributions constrain layout even when percentages or flexible tracks are used. Set border-box consistently on elements and pseudo-elements rather than assuming it is inherited automatically.

```css
*, *::before, *::after { box-sizing: border-box; }
img, video { max-inline-size: 100%; block-size: auto; }
.prose { max-inline-size: 70ch; overflow-wrap: anywhere; }
```

`width: 100%` plus padding can overflow under content-box. `min-inline-size: 0` can allow a flex or grid child to shrink below its automatic minimum; it should be applied to the actual constrained child, not scattered through the whole application. `overflow-wrap: anywhere` affects intrinsic sizing differently from legacy break-word behavior. A fixed height is rarely a good answer to varying text, translation or zoom.

Margins can be negative and vertical margins can collapse in ordinary block flow under defined conditions. Padding cannot be negative and does not collapse. A new block formatting context, including flow-root, changes float interaction and margin behavior. Inline formatting has line boxes and baselines; vertical margins on non-replaced inline boxes do not create block spacing. Replaced elements have intrinsic dimensions and aspect ratios. Tables and ruby have specialized rules.

Logical properties express block/inline directions from writing-mode and direction. Use margin-inline-start, padding-block, inline-size and inset-inline-end where the intention is logical. Top/right/bottom/left remain physical. If physical and logical declarations map to the same side, cascade and mapping determine the result; writing both is not automatically a useful fallback.

### Display, overflow and hiding

Display has outer and inner behavior: block versus inline participation, and flow/flex/grid/table layout within. `inline-flex` is inline outside and flex inside. Display none removes boxes; visibility hidden generally retains layout space; opacity zero still allows focus and hit testing unless other state changes intervene. `content-visibility` can skip rendering work subject to containment, and requires care around intrinsic sizes and offscreen content. `display: contents` removes the principal box but has accessibility and context-specific consequences; test rather than assuming it preserves all semantics identically.

Overflow visible, hidden, clip, scroll and auto differ in clipping and scroll-container behavior. Hidden can still allow programmatic scrolling; clip does not establish the same scroll container. Changing one overflow axis can change computed behavior of the other. A sticky element can attach to an unexpected scrolling ancestor. Reserve necessary scrollbar space with scrollbar-gutter where supported. Do not hide overflow simply to conceal a layout bug or crop focus indicators.

### Positioning and paint order

Static participates in normal flow. Relative retains its place and offsets its box. Absolute is removed from normal flow and positions against a containing block determined by layout rules. Fixed is often viewport-relative, but transformed or containing ancestors can establish another containing block. Sticky participates in flow until constrained by the relevant scroll container and inset; it needs room to move. Insets, opposing constraints, auto margins and intrinsic sizing interact differently for each positioning mode.

A stacking context isolates descendant z-index ordering. Positioned elements with non-auto z-index, certain flex/grid items, opacity, transforms, isolation and other effects can create contexts. A child with z-index 9999 cannot escape its ancestor's stacking context. The browser top layer used by native dialogs and popovers is a different mechanism. Transform changes visual geometry and can create containing blocks without changing the normal-flow allocation.

```css
.page-header { position: sticky; inset-block-start: 0; z-index: 10; background: #fff; }
.anchor-target { scroll-margin-block-start: 6rem; }
.badge-host { position: relative; }
.badge-host .badge { position: absolute; inset-block-start: 0.5rem; inset-inline-end: 0.5rem; }
```

Use this badge pattern only when the badge does not obscure content at zoom or remove meaningful information from source order. Practice: identify every scroll container and stacking context before changing a sticky header's z-index.

Source: https://drafts.csswg.org/css-box-4/
Source: https://drafts.csswg.org/css-display-4/
Source: https://drafts.csswg.org/css-position-3/

## 5 Flexbox in depth

Flexbox distributes items along one main axis, with an orthogonal cross axis. Direction maps row/column through writing mode; row-reverse changes visual order, not DOM reading order. Flex-wrap creates independent lines. A wrapped flex layout is not a two-dimensional grid with aligned tracks across rows.

The container controls display, flex-direction, flex-wrap, justify-content, align-items, align-content and gap. `flex-flow` combines direction and wrapping. Justify-content distributes main-axis free space after flex sizing and auto margins; align-items supplies cross-axis alignment defaults; align-self overrides an item; align-content distributes multiple lines when there is cross-axis free space. Gap creates gutters between items and lines, not outer container padding.

The item controls order, flex-grow, flex-shrink, flex-basis, align-self and its minimum/maximum sizes. Flex basis supplies the initial main-size input; auto can take the main-size property or content sizing. Grow factors distribute positive free space, not a direct percentage width. Shrink factors are weighted by flex base sizes, so equal shrink factors do not necessarily remove equal pixels. Constraints freeze items during the algorithm; inspect the resulting sizes rather than relying on a one-step ratio.

`flex: 1` commonly expands to grow 1, shrink 1 and a zero-percent basis in browsers; specification expansion details matter when the container's size is indefinite. Use explicit `flex: 1 1 0` when that basis is intended. `flex: auto` means 1 1 auto; `flex: none` means 0 0 auto. Automatic minimum sizes can prevent shrinking long tokens. An auto margin can absorb free space before alignment distribution, making it useful for pushing an action group to the end.

```css
.toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; }
.toolbar__title { margin: 0; flex: 1 1 16rem; min-inline-size: 0; }
.toolbar__actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-inline-start: auto; }
```

Real use cases: toolbars, wrapping action groups, media objects, one-dimensional navigation, and a page shell with flexible main content. Avoid flex order for a logical sequence that differs between keyboard and visual traversal. Align-items stretch does not force identical heights if item constraints prevent it. Percentage flex bases, min-content and aspect ratio can interact in surprising ways.

Practice: build three cards with long URLs and different text lengths. Measure widths before and after min-inline-size:0. Explain why gap is still present when justify-content changes and why align-content may have no visible effect on a single line.

Source: https://drafts.csswg.org/css-flexbox-1/

## 6 CSS Grid in depth

Grid defines two-dimensional tracks, lines, areas and gaps. Explicit tracks come from grid-template-columns/rows; implicit tracks come from auto placement and grid-auto-columns/rows. Grid-template-areas names rectangular areas; each named area must form a rectangle. A period marks an empty cell. Line names can repeat and line numbers can be positive or negative relative to the explicit grid.

A track can use fixed lengths, percentages, intrinsic min-content/max-content, flexible fr units, minmax() and fit-content(). `repeat()` compresses repeated track syntax; auto-fill retains empty repeated tracks while auto-fit collapses appropriate empty tracks after placement. A flexible track's automatic minimum can preserve min-content width. `minmax(0, 1fr)` removes that automatic track minimum, but the item may still need its own min-inline-size correction.

Grid-column and grid-row combine start/end lines. Grid-area can refer to a named area or four line positions. Spans describe track counts or named-line relationships. Grid-auto-flow controls row/column placement and optional dense packing. Dense packing can visually move later items into earlier holes; do not use it where the meaning depends on source order. Overlap is legal and needs deliberate paint order.

The grid shorthand combines explicit/implicit settings and resets properties, so prefer longhands while learning. Gap and alignment are separate: justify-items/align-items position items inside areas, justify-content/align-content position the track collection inside the container. Self properties override item alignment. Auto margins can absorb space before self-alignment. Baseline alignment depends on available baselines.

```css
.workbench { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1.5rem; }
.workbench > * { min-inline-size: 0; }
@media (width >= 60rem) {
  .workbench { grid-template-columns: minmax(15rem, 1fr) minmax(0, 3fr); }
}
.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: 1rem;
}
```

Subgrid allows a nested grid to use its parent's track sizing in an axis; it is not ordinary inheritance of the grid-template declaration. A subgrid needs to span the intended parent tracks and can retain its own gap behavior. Newer masonry-like grid proposals have changed names and algorithms; do not equate a draft keyword in an index with a stable production layout.

Practice: create a two-column workbench whose right panel contains a long code sample. Explain which track and item minimums prevent page-wide overflow. Then compare a nested ordinary grid with subgrid for aligning card titles and actions. Preserve DOM order at every viewport.

Source: https://drafts.csswg.org/css-grid-2/

## 7 Responsive design, typography and visual systems

### Constraints before breakpoints

Start with a usable narrow layout. Use intrinsic sizes, wrapping, max-inline-size, auto-fit, minmax and fluid spacing before adding viewport conditions. Choose breakpoints where content needs a different arrangement, not by a list of device brands. Media queries can test width, height, aspect ratio, orientation, resolution, hover, pointer, color scheme, forced colors, reduced motion and print. Range syntax expresses bounds directly. Screen pixels, layout viewport, visual viewport and device scale are distinct measurements.

Container queries respond to an ancestor query container rather than the whole page. Set container-type:inline-size on a suitable wrapper; query a descendant. The queried element cannot freely query its own size to create a circular sizing dependency. Name containers to avoid accidental ancestor selection. Size containment affects intrinsic sizing, so do not add container-type everywhere.

```css
.module-host { container: learning-module / inline-size; }
.module { display: grid; gap: 1rem; }
@container learning-module (width >= 36rem) {
  .module { grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); }
}
```

A container query must have a useful base layout when unsupported. Style queries and scroll-state queries have their own support and syntax boundaries. The property inventory includes their related names without treating them as a universal baseline.

### Typography and internationalization

Choose a robust font stack with a generic fallback. Font-family, size, weight, style, stretch/width, line-height and variant features describe different dimensions. Variable-font axis settings are low-level; prefer high-level properties when they express the requirement. Optical sizing depends on the font and feature. Font display is an @font-face descriptor, not an element property. Font loading can change metrics and cause layout shifts; reserve space where appropriate and use a deliberate fallback strategy.

Unitless line-height scales with the descendant's own font size when inherited. A computed length may inherit as that length. Letter-spacing and word-spacing affect text fit and can impair scripts if applied indiscriminately. Use real language metadata for hyphenation and language-sensitive line breaking. White-space, white-space-collapse, text-wrap and overflow-wrap solve different problems. Text-overflow:ellipsis needs a constrained box and appropriate overflow/white-space behavior; it does not expose the missing content to every user.

Support text resizing, 320 CSS-pixel reflow where applicable, user text spacing and long translations. Horizontal scrolling can be appropriate for a code region or data table, but should not become page-wide scrolling for ordinary content. Direction and writing-mode change logical axes, not the text's language. Do not use bidi controls or visual order to falsify meaningful reading order.

### Color, surfaces and states

Create semantic tokens for ink, surfaces, borders, focus, success, warning and error. A palette name alone does not establish contrast. WCAG AA normally requires 4.5:1 for ordinary text and 3:1 for qualifying large text; relevant non-text component boundaries and indicators generally need 3:1 under the applicable criterion. Disabled/inactive controls have exceptions, but must still be understandable. Alpha colors must be evaluated after compositing against actual surfaces. Color contrast tools for sRGB are not enough to reason blindly about every wide-gamut composition.

Use color-scheme to communicate supported native-control modes when the page actually supports them. prefers-color-scheme can provide an initial choice; an explicit user choice should persist according to product policy. Test both schemes. In forced-colors mode, system colors and user-agent adjustments may override authored paint; avoid disabling forced-color-adjust without a strong, tested reason.

Backgrounds can be layered; the first image is painted above later images and color is below them. Each layer can have independent origin, clip, size, repeat, position and attachment; the background shorthand's slash separates position and size. Border-radius shapes corners but does not replace clipping rules. Box-shadow and outline are not layout space. Filters, blending and backdrop filters can produce expensive rendering and unexpected contrast; maintain a clear fallback.

### Motion and performance

Transitions interpolate a change between style states; animations follow keyframes. Transition-property, duration, delay, easing and behavior form coordinated lists; keyframe animations additionally have names, iteration counts, direction, fill mode, play state, composition and timelines. Negative delays start partway through an effect; fill mode can retain animated values outside the active interval. A zero duration does not make every animation event/lifecycle assumption disappear.

Prefer animating transform and opacity where suitable, but do not promise compositor-only execution: the actual rendering pipeline, paint effects and layer state determine cost. Avoid transition:all in components where unrelated changes should be immediate. will-change is a temporary resource hint, not a universal optimization. Remove long-lived hints when no longer needed. Respect prefers-reduced-motion and keep essential state changes understandable without animation.

```css
.disclosure-icon { transition: transform 160ms ease-out; }
[aria-expanded="true"] .disclosure-icon { transform: rotate(180deg); }
@media (prefers-reduced-motion: reduce) {
  .disclosure-icon { transition: none; }
}
@media (forced-colors: active) {
  .action { border-color: ButtonText; }
}
```

Scroll-driven animation and view transitions are progressive enhancements. Neither should determine whether content, focus or application state updates correctly. For printing, remove purely interactive chrome, preserve meaningful content, avoid clipping long regions and test pagination. Break-before/after/inside, widows and orphans are requests constrained by the fragmentation algorithm, not absolute promises that every requested break can be honored.

Source: https://drafts.csswg.org/css-conditional-5/
Source: https://drafts.csswg.org/mediaqueries-5/
Source: https://www.w3.org/TR/WCAG22/

## 8 CSS architecture and production debugging

A stylesheet needs ownership rules. Tokens describe shared decisions; base styles cover low-specificity semantic defaults; components own local appearance; utilities express intentional single-purpose overrides; state belongs to actual DOM/API state. BEM is one naming convention, CSS Modules provide build-time naming isolation, and Shadow DOM provides tree-scoped styling. None removes the need for accessible markup or a clear theme contract.

Use cascade layers to make override order explicit. A reset should be small and understood; a universal all:unset reset can remove useful native behavior. Keep selectors shallow and stable. Avoid binding styles to incidental DOM depth or database IDs. Scope tokens: public component custom properties are an API, while internal variables can be private by convention but remain observable CSS. Document default values, valid types, inheritance and fallback behavior.

Adopt a spacing scale and semantic color system, but do not generate every possible class and variant. Keep layout primitives reusable: stack, cluster, switcher and grid are compositions of standard layout rules rather than magic framework features. Separate content-specific exceptions from shared primitives so a one-off page fix does not change every card.

Build pipeline: pin compiler and framework versions; resolve modules; compile Sass; apply the chosen CSS transformations and prefix strategy; minify; generate source maps according to deployment policy; hash assets; and verify the actual shipped CSS. A Sass compiler does not automatically add vendor prefixes. A prefixer does not polyfill Grid, container queries or a JavaScript API. CSS purging must understand dynamically generated class names and state selectors; test the production bundle rather than only development output.

Debug a failure through six observations: authored source, matched rules, winning declarations, computed/resolved values, layout geometry and actual interaction. In performance work, measure style recalculation, layout, paint and compositing. Reading geometry after writing style can force synchronous layout; collect reads, compute once and batch writes. A requestAnimationFrame callback alone does not eliminate forced layout if it alternates reads and writes internally.

Acceptance exercises: diagnose a selector defeated by an unlayered framework; locate an automatic minimum causing overflow; repair focus clipped by overflow; compare live state to a stale attribute; explain a transform-created fixed containing block; and remove a DOM-order mismatch introduced with Grid placement. For each exercise, include a deliberately broken variant and an observable test that fails before the repair.


## 9 Sass and SCSS: build-time programming for styles

### Syntax, compilation and the runtime boundary

Sass names the language and tool ecosystem. SCSS uses braces and semicolons and largely follows CSS syntax; the indented .sass syntax uses indentation and omits many delimiters. Both compile to CSS. Browsers do not execute Sass variables, mixins, loops or module loading. A compiled stylesheet remains subject to ordinary CSS cascade, inheritance, layout and browser support. Sass abstraction can improve maintenance, but it can also multiply selectors and output size.

The examples target Dart Sass. LibSass, Node Sass and Ruby Sass are not appropriate baselines for new module-based application code. Use the modern JavaScript API, compile/compileAsync or compileString/compileStringAsync, rather than render/renderSync. Pin versions and retain a lockfile. Build errors should fail CI; warnings need an owner and migration plan rather than permanent blanket suppression.

A standalone SCSS file is a compilation unit. Partials conventionally start with underscore and are loaded through another entry point. A partial does not imply runtime lazy loading. Sass can emit expanded CSS for review and compressed CSS for deployment. Source maps connect output back to source; expose them publicly only under a deliberate deployment policy.

```scss
// Input: spacing.scss
$space: 0.75rem;
.notice {
  padding: $space;
  margin-block-end: $space * 2;
}
```

```css
/* Expanded compiled output */
.notice {
  padding: 0.75rem;
  margin-block-end: 1.5rem;
}
```

This eliminates duplicated source literals; it does not make the runtime CSS inherently faster. Changing $space requires rebuilding. Changing a CSS custom property can affect the running page through the cascade.

Source: https://sass-lang.com/documentation/
Source: https://sass-lang.com/documentation/js-api/

### Variables, scope and configuration

Sass variables hold typed compile-time values and are imperative: earlier declarations use the value that existed when evaluated. Hyphens and underscores in Sass identifiers are treated equivalently in many names; avoid treating $space-small and $space_small as separate public variables. Names are case-sensitive. Local lexical scope controls availability; flow-control assignment has special scope behavior that should be tested when accumulating results.

`!default` assigns only when a variable is undefined or null, making it useful for library configuration. `!global` assigns a global variable and has restrictions; it should not become the normal mechanism for communicating between modules. A module configured with @use ... with must expose configurable !default variables, and configuration must occur before that module's first load. A module is evaluated once per compilation under the module system.

```scss
// _tokens.scss
$space: 0.75rem !default;
$ink: #172b4d !default;

// app.scss: a separate file compiled with _tokens.scss present
@use "tokens" with ($space: 1rem);
.panel { padding: tokens.$space; color: tokens.$ink; }
```

```css
/* Output of app.scss */
.panel {
  padding: 1rem;
  color: #172b4d;
}
```

Use namespaces rather than `as *` for broad application dependencies. Distinguish a Sass value that generates a custom property from the browser variable that consumes it. Interpolation is needed when inserting many Sass expressions into custom-property values because their content is treated as CSS token text.

```scss
$brand: #174ea6;
:root { --brand: #{$brand}; }
.action { color: var(--brand); }
```

### Types, collections and expressions

Numbers carry units. Sass checks dimensional compatibility for arithmetic; dividing lengths can produce unitless values and multiplying can produce compound units that cannot be emitted as an ordinary CSS length. Use math.div for compile-time division. A slash can be a CSS separator, especially for grid lines and font size/line-height, so legacy `/` division is not a safe new-code convention. Preserve browser calculations when runtime values such as var() or viewport units are required.

Strings may be quoted or unquoted, and interpolation can remove quoting in ways that change emitted CSS meaning. Lists have separators and optional brackets; a one-item list and its item may behave similarly in some contexts, but an empty list and a map have special relationships. Maps associate keys with values and preserve the language's collection rules. Null often omits a declaration or list contribution; false is a real boolean. All values except false and null are truthy in Sass conditions, including zero and an empty string. Do not import JavaScript truthiness assumptions.

Colors have color spaces and channels. Prefer sass:color functions such as color.adjust, color.scale, color.change, color.mix, color.channel and color.to-space with explicit intent. Older global lighten/darken or red/green/blue workflows have deprecation and color-space limitations. A Sass color adjustment does not prove WCAG contrast after CSS compositing. Functions and mixins can be first-class values through sass:meta; selectors can be manipulated through sass:selector. Calculations can remain CSS calculation values rather than being reduced immediately.

```scss
@use "sass:math";
@use "sass:map";
@use "sass:list";
$spaces: (small: 0.5rem, medium: 1rem, large: 1.5rem);
$ratio: math.div(3, 2);
.panel {
  padding: map.get($spaces, medium);
  aspect-ratio: $ratio;
  margin-block: list.nth((0.5rem, 1rem), 2);
}
```

```css
.panel {
  padding: 1rem;
  aspect-ratio: 1.5;
  margin-block: 1rem;
}
```

Equality and ordering must respect types and units. Arithmetic may be evaluated during compilation or preserved in CSS calculations according to the syntax. Interpolation inside calc can prevent useful type checking. Use interpolation for identifiers and deliberate text construction, not as a general escape from errors.

### Nesting, the parent selector and interpolation

Nesting expresses selector relationships; it does not create component isolation. `.card { .title { ... } }` emits a descendant selector. `&` refers to the enclosing selector, enabling state modifiers, BEM suffixes and contextual relationships under Sass's rules. Nested selector lists can expand combinatorially. Limit nesting depth and inspect the output specificity.

```scss
.card {
  padding: 1rem;
  &__title { margin-block: 0 0.5rem; }
  &:focus-within { outline: 0.125rem solid #111; }
  [dir="rtl"] & { text-align: right; }
}
```

```css
.card { padding: 1rem; }
.card__title { margin-block: 0 0.5rem; }
.card:focus-within { outline: 0.125rem solid #111; }
[dir=rtl] .card { text-align: right; }
```

The BEM title selector is a class on its own; it does not require a .card ancestor. The dir example only tests the shown attribute relationship; logical text alignment is usually preferable. Native CSS nesting and Sass nesting differ in parsing and specificity details; do not assume compiled Sass is identical to leaving the same nested source in a browser. Modern Sass follows CSS-compatible ordering behavior for declarations interspersed with nested rules; move declarations intentionally and test emitted output when migrating older Sass code.

Interpolation `#{$value}` can generate selector names, property names and text. Never use untrusted strings to generate arbitrary build-time CSS. Nested properties such as `font: { size: ...; weight: ...; }` expand property names; they do not create a runtime object. @at-root can lift nested output to another rule context, optionally preserving or excluding at-rule categories. It is powerful for library authors but can undermine locality when used casually.

### Mixins and content blocks

A mixin emits declarations or rules and can accept positional, named, default and rest arguments. Use @include to invoke it. A function returns a value and should not emit unrelated rules. Content blocks let the caller provide rules at a controlled insertion point. Arguments passed to @content require a matching using clause. A content block's lexical scope belongs to its declaration site; it does not implicitly inherit every local variable from inside the mixin.

```scss
@mixin focus-ring($color: #111, $offset: 0.2rem) {
  &:focus-visible {
    outline: 0.1875rem solid $color;
    outline-offset: $offset;
  }
}
@mixin at-width($width) {
  @media (min-width: $width) { @content; }
}
.action { @include focus-ring; }
.layout {
  display: grid;
  @include at-width(48rem) { grid-template-columns: 1fr 2fr; }
}
```

```css
.action:focus-visible {
  outline: 0.1875rem solid #111;
  outline-offset: 0.2rem;
}
.layout { display: grid; }
@media (min-width: 48rem) {
  .layout { grid-template-columns: 1fr 2fr; }
}
```

Repeated mixin calls repeat CSS. That may be an acceptable tradeoff for clear source, but measure output growth. A semantic mixin name such as focus-ring conveys intent; a mixin that merely renames one property often adds little value. Validate public parameters with @error so invalid configuration fails early.

### Functions and diagnostics

User functions use @function and @return. Keep them deterministic with clear input types and units. @error aborts compilation; @warn emits a warning without automatically failing; @debug prints diagnostic values. Production builds should not depend on parsing debug text. Use the modern logger API when collecting diagnostics in tooling.

```scss
@use "sass:math";
@function space($step, $unit: 0.25rem) {
  @if not math.is-unitless($step) { @error "space step must be unitless"; }
  @if $step < 0 { @error "space step must be nonnegative"; }
  @return $step * $unit;
}
.panel { padding: space(4); gap: space(3); }
```

```css
.panel {
  padding: 1rem;
  gap: 0.75rem;
}
```

A numerical type check should precede arithmetic when exposing this to arbitrary library consumers; the example's contract is a numeric step. For stronger public APIs use meta.type-of and math.is-unitless together. The complete lab includes that validation. Sass does not perform unit conversion between arbitrary relative units such as em and rem, because their runtime bases can differ.

### @extend and placeholders

@extend unifies selectors so the extending selector matches rules associated with an existing selector. It is not textual copying. Placeholder selectors beginning with `%` emit no selector until extended. Extension has scope rules across modules and at-rules; extending inside a media query cannot freely alter unrelated rules outside it. Selector unification can create unexpected combinations and move the apparent cascade effect to the extended rule's location.

```scss
%surface {
  background: #fff;
  border: 0.0625rem solid #526170;
}
.card { @extend %surface; padding: 1rem; }
.notice { @extend %surface; padding: 0.75rem; }
```

```css
.notice, .card {
  background: #fff;
  border: 0.0625rem solid #526170;
}
.card { padding: 1rem; }
.notice { padding: 0.75rem; }
```

Choose @extend for a real selector-level semantic relationship and inspect the resulting selector list. Choose a mixin for parameterized output, a utility class for an explicit markup composition, and a custom property for runtime theming. `!optional` can suppress an absent-target extension error, but it can also hide a broken dependency; it should not be a blanket setting.

### Control directives and bounded generation

@if/@else conditionally emit based on compile-time values. @for can use through for an inclusive upper bound or to for an exclusive upper bound. @each iterates lists or map key/value pairs and can destructure entries. @while repeats until a condition becomes false and needs an explicit terminating state change. These constructs run during compilation, not when a user clicks.

```scss
$enable-border: true;
@if $enable-border {
  .panel { border: 0.0625rem solid #526170; }
}
@for $i from 1 through 3 {
  .space-#{$i} { padding: $i * 0.25rem; }
}
@each $name, $value in (compact: 0.5rem, roomy: 1rem) {
  .density-#{$name} { gap: $value; }
}
$i: 1;
@while $i <= 2 {
  .width-step-#{$i} { max-inline-size: $i * 10rem; }
  $i: $i + 1;
}
```

```css
.panel { border: 0.0625rem solid #526170; }
.space-1 { padding: 0.25rem; }
.space-2 { padding: 0.5rem; }
.space-3 { padding: 0.75rem; }
.density-compact { gap: 0.5rem; }
.density-roomy { gap: 1rem; }
.width-step-1 { max-inline-size: 10rem; }
.width-step-2 { max-inline-size: 20rem; }
```

Never generate classes for arbitrary unbounded user input. The product of utilities, values, breakpoints, states and color modes can become large. Set an output budget and generate only the useful combinations. @while is rarely preferable to @for or @each when the iteration set is known.

## 10 Sass modules, built-ins and scalable architecture

### @use, @forward and partials

@use loads a stylesheet once and exposes names under a namespace. It must obey ordering rules and precede ordinary style rules, with allowed configuration declarations handled as defined. @forward re-exports a public API and can show/hide members or add a prefix. Forwarding does not itself make members available locally; add @use if the forwarding file also consumes them. Public module paths are part of a library's API. Leading underscore/hyphen members are private under module rules.

```scss
// abstracts/_tokens.scss
$space: 1rem !default;

// abstracts/_index.scss
@forward "tokens";

// components/_card.scss
@use "../abstracts" as design;
.card { padding: design.$space; }

// app.scss
@use "abstracts" with ($space: 1.25rem);
@use "components/card";
```

```css
.card { padding: 1.25rem; }
```

Configure the tokens before any component indirectly loads them. A second @use with a different configuration is not an independent module instance. Avoid CSS output in pure token modules so importing a dependency does not unexpectedly emit base rules. Use package importers and documented load paths rather than fragile chains of parent-directory traversal in published libraries.

### The 7-1 pattern and alternatives

The 7-1 pattern places seven concerns under one entry point: abstracts, vendors, base, layout, components, pages and themes. Abstracts contain non-emitting tokens/functions/mixins. Vendors contain adapters and integration entry points rather than edited upstream source. Base contains resets and semantic defaults. Layout contains shared arrangements. Components contain local UI styling. Pages contain real route-specific exceptions. Themes contain deliberate theme contracts. The final entry point establishes order.

This is a convention, not a Sass feature. A small application can use fewer folders. A large design system may organize by component package instead. Modern @use loading order and CSS cascade layers must be designed together; folder names do not control runtime precedence. Runtime themes often belong in custom properties and data attributes rather than separate compiled copies of every component.

```scss
// main.scss; each referenced partial is an actual project dependency.
@use "abstracts";
@use "vendors";
@use "base";
@use "layout";
@use "components";
@use "pages";
@use "themes";
```

This entry-point contract is illustrated fully in the accompanying module lab. Do not create empty architecture folders solely to satisfy a diagram. A useful review asks which files emit CSS, which expose API and which may depend on which others. Cyclic modules are architectural errors, not something to fix with repeated imports.

### Built-in module map

- `sass:math`: numerical bounds, rounding, trigonometry, logarithms, random values, unit inspection and compatible-unit operations. Random compile-time values produce unstable output unless deliberately controlled outside Sass; avoid them for deterministic design tokens.
- `sass:color`: color-space-aware channel inspection, adjustment, scaling, mixing and conversion. Distinguish an absolute channel change from proportional scaling and verify rendered contrast.
- `sass:string`: quoting/unquoting, insertion, slicing, replacement through composition, indexing and identifiers. Sass indexing conventions differ from JavaScript's zero-based string APIs; inspect the specific function contract.
- `sass:list`: length, nth, set-nth, append, join, zip, index, separator and bracket inspection. A list's comma/space/slash separator affects emitted CSS.
- `sass:map`: get, has-key, keys, values, merge, remove, set and nested map operations, including deep operations where provided. Merging a map does not update derived maps that were already computed elsewhere.
- `sass:selector`: append, nest, extend, replace, unify, parse and superselector checks. Selector values are structured Sass lists; string concatenation is not a substitute for unification.
- `sass:meta`: type inspection, inspect, feature/tool introspection, function/mixin lookup and invocation, module member discovery and load-css. load-css emits CSS; it does not replace a clear @use public API or create access to private members.

The appendix enumerates the public function and mixin names exposed by the installed compiler, grouped by module. Signatures and version behavior belong to the linked official module documentation. This prevents claiming that a remembered function list is complete while omitting newer APIs.

Source: https://sass-lang.com/documentation/modules/

### Migration, compatibility and code quality

Sass @import and global built-in functions were deprecated beginning with Dart Sass 1.80.0. New application modules should use @use/@forward and namespaced built-ins. Bootstrap 5.3 still uses the older import architecture, so its integration is a deliberate compatibility exception. A mechanical replacement of @import with @use can break shared scope, configurable variables and map ordering. Keep that exception at the vendor boundary and plan the migration against the upstream framework version.

Other migration concerns include slash division, color function changes, mixed declarations after nested rules, the legacy JavaScript API, invalid combinators, stricter argument handling and changes to conditional function syntax. Use @if for clear control flow rather than writing new examples around a deprecated legacy if() function. Preserve plain CSS functions when the browser should evaluate them. Run the official Sass migrator on a reviewable branch and inspect compiled diffs; a successful migration command does not prove unchanged design behavior.

Production checks: compile every entry point; test functions against invalid units and types; compare expanded CSS snapshots for deliberate output changes; enforce a selector-depth and output-size budget; verify source-map policy; render component states; and run accessibility checks in the final CSS build. Separate owned-code warnings from upstream dependency warnings. Record which warnings remain and why. Do not silently suppress a warning merely to call a build pristine.

### Side-by-side reasoning and review exercises

Compare each preceding SCSS block with its CSS output as an input/output pair: source abstraction on the left conceptually, emitted selector/declaration behavior on the right. Part 28 provides actual two-column source/output comparisons from the compiler; the larger teaching blocks here remain convenient to read and copy. Ask what disappears at compile time, what duplicates in output, what remains configurable at runtime and which selector specificity the browser actually sees.

Exercises: replace duplicated spacing with a validated function; refactor a deep nested selector into an explicit component class; convert a configuration import into a module facade; choose mixin versus placeholder versus custom property for three variants; demonstrate an @each map that emits only three useful utility values; and explain why changing a Sass map after a framework's derived maps were evaluated may have no intended effect.

### Indented Sass syntax and advanced emitting contracts

The same small rule can be authored in either syntax. The indented form below is a complete .sass entry point, not whitespace-formatted SCSS. Compile it with the same Dart Sass compiler. Its emitted .panel rule is identical in meaning to the SCSS form, and neither syntax exists in the browser at runtime.

```sass
$space: 1rem
.panel
  padding: $space
  &:focus-within
    outline: 2px solid #111
```

```scss
$space: 1rem;
.panel {
  padding: $space;
  &:focus-within { outline: 2px solid #111; }
}
```

Content arguments, keyword rest arguments and @at-root are useful when a library needs controlled output placement. The following complete entry point passes a breakpoint label into a caller-owned content block, lifts a label rule out of the card's selector nesting, and emits two deliberate spacing utilities from keyword arguments. The caller's using clause makes the content parameter explicit. meta.keywords inspects named arguments; it does not invent runtime settings.

```scss
@use "sass:meta";
@mixin at-breakpoint($name, $width) {
  @media (min-width: $width) { @content($name); }
}
@mixin space-variants($options...) {
  @each $name, $value in meta.keywords($options) {
    .space-#{$name} { padding: $value; }
  }
}
.card {
  @include at-breakpoint(wide, 48rem) using ($label) {
    --layout-label: #{$label};
    padding: 2rem;
  }
  @at-root .card-label { font-weight: 700; }
}
@include space-variants($compact: 0.5rem, $roomy: 1rem);
```

Review the actual compiled output in Part 28. @at-root changes output location, not DOM ownership; keyword-generated utility names are a build API that needs bounded values and stable naming. Keep this machinery in a small library layer rather than spreading metaprogramming through every page stylesheet.


## 11 Bootstrap 5 ecosystem and layout

### What the framework provides

Bootstrap 5 combines Reboot defaults, typography/content styles, a responsive Flexbox grid, utilities, helpers, forms, components and optional JavaScript plugins. It is utility-rich and component-oriented; calling it purely utility-first hides the component selectors and runtime plugins that are central to the system. Bootstrap Icons is a separate project. Bootstrap 5 does not require jQuery. The bundled JavaScript includes Popper for components that need positioning; the non-bundle build needs the required dependency supplied separately.

Pin CSS and JavaScript to the same version. The integrated lab uses local files from bootstrap@5.3.8, avoiding a live CDN dependency. If using a CDN in a product, verify the exact URL and integrity hash together, include the appropriate crossorigin setting and define the application's CSP. An integrity hash from a different version breaks loading. A framework stylesheet does not supply HTML labels, meaningful content, server validation or a screen-reader-tested interaction by itself.

Load exactly one owner for each interactive component. Do not load both a bundled UMD file and an independently bundled copy of the same plugins. Framework data APIs and a React/Vue state layer can conflict if both mutate the same classes, attributes or children. Either let Bootstrap own its documented component lifecycle through a wrapper, or use a framework-native implementation with compatible styling and an explicitly different API.

Source: https://getbootstrap.com/docs/5.3/getting-started/introduction/
Source: https://getbootstrap.com/docs/5.3/getting-started/javascript/

### Breakpoints and containers

The default tiers are xs below 576px, sm from 576px, md from 768px, lg from 992px, xl from 1200px and xxl from 1400px. There is no xs infix: `.col-6` starts at the smallest tier. Most min-width responsive classes continue applying at larger widths until overridden. Breakpoints are configuration, not device detection.

`.container` provides width 100% with responsive max-widths: 540, 720, 960, 1140 and 1320px from sm through xxl. `.container-fluid` remains 100% wide. `.container-md`, for example, is fluid below md, then uses responsive max-width behavior from md upward. Container padding and gutters still matter; a max-width is not the final width of all nested content. Custom Sass can change these values, so verify a customized build rather than assuming defaults.

Bootstrap's `.container` class is not a CSS query-container declaration. Its breakpoints are viewport media queries. For a component that appears in a sidebar and a main panel, native container queries may express its layout more accurately than adding more Bootstrap viewport classes.

### The 12-column grid

The grid relationship is container, row, columns, then content. Rows use flex wrapping and gutter compensation; columns provide padding. `.col` shares remaining space; `.col-auto` sizes to content; `.col-1` through `.col-12` allocate fractions of the 12-column width. `.col-12.col-md-6.col-xl-4` means full width, then half width, then one third. `.row-cols-1.row-cols-md-2` sets a default number of columns per row. A nested grid needs its own row inside an existing column.

```html
<section class="container py-4" aria-labelledby="courses-heading">
  <h2 id="courses-heading">Practice courses</h2>
  <div class="row g-3">
    <article class="col-12 col-md-6 col-xl-4">
      <div class="card h-100"><div class="card-body">
        <h3 class="h5 card-title">JavaScript fundamentals</h3>
        <p class="card-text">Practice values, functions and collections.</p>
        <a class="btn btn-primary" href="#javascript">View JavaScript course</a>
      </div></div>
    </article>
    <article class="col-12 col-md-6 col-xl-4">
      <div class="card h-100"><div class="card-body">
        <h3 class="h5 card-title">Java fundamentals</h3>
        <p class="card-text">Practice types, methods and collections.</p>
        <a class="btn btn-primary" href="#java">View Java course</a>
      </div></div>
    </article>
  </div>
  <p id="javascript">JavaScript course information is available in this section.</p>
  <p id="java">Java course information is available in this section.</p>
</section>
```

This is a complete semantic section fragment for a document already loading Bootstrap. The integrated lab includes the document shell. Grid gutters use `.g-*`, `.gx-*` and `.gy-*` and the related `--bs-gutter-x/y` variables. Large gutters combined with poorly placed rows can create overflow. Use `.g-0` intentionally; it removes spacing, not the need for readable separation.

Offsets `.offset-md-2` add tier-specific starting space and may need resetting at later tiers. `.order-*` changes visual order; prefer source order that already matches meaning. `.align-items-*`, `.align-self-*` and `.justify-content-*` are Flexbox utilities, not separate grid algorithms. `.w-100` can force a flex line break in a controlled row but should not replace clear markup and layout.

Bootstrap's optional CSS Grid implementation is a separate, experimental opt-in build path using `.grid`, `.g-col-*` and CSS custom properties. It is not the default `.row` Flexbox grid, and default compiled CSS does not necessarily include it. Native CSS Grid can also be used directly without that optional framework layer.

Source: https://getbootstrap.com/docs/5.3/layout/breakpoints/
Source: https://getbootstrap.com/docs/5.3/layout/containers/
Source: https://getbootstrap.com/docs/5.3/layout/grid/
Source: https://getbootstrap.com/docs/5.3/layout/css-grid/

## 12 Bootstrap utilities, content, helpers and forms

### Utility grammar and coverage

A utility class maps to actual declarations. Many are generated with `!important` by default, so a later ordinary component rule may not override them. Responsive and state variants are generated only for configured families; do not invent a class because a naming pattern seems plausible. The utility appendix extracts every entry of the installed `$utilities` Sass map and lists its CSS properties, class prefix, values, responsive setting, print setting and generated states. That is the exact build-source contract, not a list remembered from another Bootstrap version.

Spacing uses `{property}{sides}-{breakpoint?}-{size}`: m/p for margin/padding; t/b/s/e/x/y or no side; optional sm through xxl; and default scale 0,1,2,3,4,5 with values 0,0.25,0.5,1,1.5,3rem. Auto belongs to margin where generated. s/e are logical start/end conventions processed by the appropriate LTR/RTL build; loading LTR CSS and expecting every direction-sensitive utility to flip automatically is insufficient. Negative margins are opt-in through Sass and should not be assumed present. Gap utilities follow their configured families.

Display includes none, inline, inline-block, block, grid, inline-grid, table forms, flex and inline-flex with responsive/print variants where configured. Flex families cover direction, wrapping, fill, grow/shrink, alignment and order. Sizing provides selected percentage/auto values, viewport-relative helpers and min/max helpers; arbitrary values such as `.w-37` are not generated by default. Position utilities cover static/relative/absolute/fixed/sticky and selected edges/translations; responsive position variants are not universally available.

Other families cover background and text colors, opacity, borders and rounding, shadows, object fit, overflow, float, vertical alignment, interaction, visibility, link opacity/underlines, font sizing/weight/style, line height, text alignment/wrapping/transformation/decoration and small z-index values. `.invisible` retains layout space and differs from `.d-none`. `.text-truncate` needs a suitable constrained formatting context. `.pe-none` disables pointer targeting, not keyboard focus or programmatic activation. `.user-select-none` should not be used to obstruct normal text use.

### Content and helper layer

Reboot normalizes selected element defaults using box-sizing, typography, margins and native-control adjustments. It is global CSS; assess it before importing into an existing site. Heading utility classes such as h1/h5 change appearance but do not change heading semantics. Use the correct HTML heading level. `.lead`, `.small`, `.mark`, list-unstyled and list-inline are presentational conventions, not substitutes for meaning.

Images can use `.img-fluid`, `.img-thumbnail`, rounded utilities and figure classes; they still need appropriate alternatives and actual width/height information. Tables use `.table` with contextual, striped, hover, bordered, borderless, size and responsive wrappers. A `.table-responsive` wrapper enables horizontal overflow and can clip floating content; preserve header associations and consider how keyboard users reach an overflowing region.

Helpers include clearfix, color/background helpers, colored links, focus-ring, icon-link, fixed/sticky positioning, ratio, hstack/vstack, stretched-link, text-truncation, vertical-rule and visually-hidden. `.visually-hidden` keeps content available to assistive technology while hiding it visually; `.visually-hidden-focusable` is useful for a skip link that appears on focus. A stretched link overlays an anchor's click area and can conflict with other controls; keep its containing block and interaction boundaries deliberate. A ratio helper creates geometry, not an accessible media title.

### Forms and validation

`.form-control` styles text-like inputs and textareas; `.form-select` styles selects; `.form-check`, `.form-check-input`, `.form-check-label` and `.form-switch` structure choices; `.form-range` styles range controls. `.input-group` groups controls and visible add-ons, but add-ons do not automatically become labels. Floating labels require the documented order and placeholder relationship; a floating placeholder is not a substitute for the real label element.

Use visible labels, correct input types, name attributes, autocomplete tokens and text instructions. Connect help/error text with aria-describedby where appropriate. Reflect actual error state with aria-invalid and provide an understandable error message after validation. A red border or icon is insufficient. Do not display errors for untouched fields indiscriminately. Disabled controls are normally excluded from submission; readonly controls differ and have narrower applicability.

Bootstrap's custom client-side validation styles and tooltip feedback have documented accessibility limitations. Prefer native browser validation or a carefully implemented accessible error workflow, and always validate on the server. `.was-validated`, `.is-valid` and `.is-invalid` are style triggers, not proof that a server accepted the data. Server errors must be mapped back to the relevant field and, for longer forms, summarized with useful links and deliberate focus handling.

```html
<form action="#saved" method="get" class="p-3 border rounded">
  <div class="mb-3">
    <label for="contact-email" class="form-label">Email</label>
    <input id="contact-email" name="email" type="email" autocomplete="email"
      required class="form-control" aria-describedby="email-help">
    <div id="email-help" class="form-text">Used for your learning account.</div>
  </div>
  <button type="submit" class="btn btn-primary">Check email format</button>
</form>
<p id="saved">This demonstration performs a local navigation, not account registration.</p>
```

Use this as a native validation exercise. Production registration needs an actual endpoint, privacy policy and server rules; the lab deliberately makes no account mutation. Test empty, malformed and valid inputs with keyboard and touch.

Source: https://getbootstrap.com/docs/5.3/utilities/api/
Source: https://getbootstrap.com/docs/5.3/forms/validation/
Source: https://getbootstrap.com/docs/5.3/getting-started/accessibility/

## 13 Bootstrap component mastery and lifecycle

### Static components and semantic contracts

Accordion combines collapse state with heading/button structure. Use real buttons with matching aria-controls and panel IDs; headings must remain meaningful. Alerts communicate messages; dismissible alerts need a labeled close button and a plan for focus when the alert disappears. Badges supplement labels and should not make unexplained numbers the sole accessible name. Breadcrumbs use navigation labeling, a list and aria-current for the current item.

Buttons should be button elements for actions and anchors for navigation. Outline variants still require contrast checks. Button groups need a useful group label and appropriate control semantics. Cards are visual containers; select headings, links, images and landmarks based on their actual content. Close buttons need an accessible label and sufficient target area. List groups can be lists, navigation or actionable controls; mixing these arbitrarily changes keyboard and screen-reader expectations.

Pagination uses navigation, descriptive labels and aria-current; an anchor with a disabled-looking class is still an anchor unless its behavior and focus are handled. Placeholders represent loading presentation and should not create fake operable controls or repeated meaningless announcements. Progress markup in 5.3 puts progressbar semantics and value attributes on the documented outer progress element; include a label and useful min/max/current values. Spinners need a meaningful status strategy and reduced-motion consideration. Repeated decorative spinners should not each announce the same loading state.

### Interactive plugins: API contract

Bootstrap plugins generally expose `getInstance(element)`, `getOrCreateInstance(element, options)` and `dispose()`, with component-specific methods. Configuration comes from defaults, data attributes and explicit options under the documented precedence. `data-bs-config` can hold supported JSON configuration, but security-sensitive options such as sanitization settings are restricted. Data attributes use the bs prefix and kebab-case. Do not assume an option supported by one component exists on another.

Methods that start transitions generally return before the transition finishes. Listen for lifecycle events such as shown.bs.modal or hidden.bs.offcanvas when completion matters. A call during an active transition can be ignored according to the plugin contract. The show/hide events are often cancelable; shown/hidden report completion. Event names and payloads differ by component. The appendix extracts the exact default option names, default values and declared types from all 12 JavaScript plugin constructors in the pinned UMD bundle.

### Component-by-component behavior

- Accordion/collapse: methods show, hide and toggle; events show/shown/hide/hidden.bs.collapse. `parent` enables grouped behavior. `toggle` affects construction. It does not automatically implement every optional ARIA accordion keyboard pattern; decide which keyboard model is required and test it. Keep triggers operable when transitions are disabled.
- Alert: close removes the alert after its transition; close/closed.bs.alert describe the lifecycle. Move focus to a meaningful surviving control if dismissal removes the focused close button. A nonurgent message may fit role=status rather than an interruptive alert.
- Button: toggle manages the plugin's active state; a toggle button needs an accurate pressed state and a label that makes sense in both states. Do not use the plugin's class as a substitute for a real checkbox when a form value is needed.
- Carousel: next, prev, to, pause and cycle coordinate slides; slide/slid.bs.carousel indicate transitions. Autoplay, hover pauses and keyboard settings require deliberate accessibility design. Provide accessible previous/next controls, an actual pause mechanism for moving content where required, meaningful slide content and reduced-motion behavior. Prefer static content if rotation is unnecessary.
- Dropdown: show/hide/toggle/update and dispose coordinate a trigger and menu. Popper manages positioning in appropriate contexts. Bootstrap dropdowns are generic overlays and do not automatically imply ARIA menu/menuitem semantics; choose semantics matching navigation or actions. Test Escape, arrow keys where supported, outside clicks and autoClose options.
- Modal: show/hide/toggle/handleUpdate manage a document-level overlay; show/shown/hide/hidden/hidePrevented.bs.modal describe outcomes. Only one modal is supported at a time. Use a label, deliberate initial focus and a return-focus policy. HTML autofocus is not the Bootstrap modal focus solution; focus the desired element after shown when needed. A static backdrop is not permission to trap a user without an exit.
- Offcanvas: show/hide/toggle manage a side panel; backdrop, keyboard, scroll and responsive classes influence behavior. It shares document focus/scroll concerns with modals. Avoid overlapping modal and offcanvas ownership on the same user task. Test the responsive breakpoint while the panel is open.
- Tab: show activates a trigger; hide/hidden and show/shown.bs.tab coordinate old/new triggers with relatedTarget. Use the required tablist/tab/tabpanel relationships only for a real tab interface. Navigation links to routes should remain navigation links, not be relabeled tabs merely for appearance.
- Toast: show/hide/isShown and dispose control brief messages. delay and autohide must fit reading needs. Establish a live region before inserting/updating the toast. Keep critical errors or required actions persistently available outside an auto-hiding toast.
- Tooltip: show/hide/toggle/update, enable/disable/toggleEnabled and setContent manage an enhancement that needs a positioned trigger. Do not put essential instructions only in hover/focus tooltips. Touch and keyboard behavior differ. Tooltips are opt-in initialization and require Popper.
- Popover: shares tooltip foundations but presents richer content. It is still not a complete focus-managed dialog. Interactive form controls inside a popover need a deliberate keyboard/focus model; a native dialog can be more suitable. Sanitization is not a substitute for a trusted content policy.
- ScrollSpy: refresh/dispose and activate.bs.scrollspy relate scrolling sections to navigation. Initialize against a real scrollable root/target structure and use refresh when the target layout changes. A highlighted navigation class does not move focus or change document headings.

Navbar combines responsive layout with collapse/offcanvas and navigation semantics. It has no independent Navbar plugin constructor. Navs/tabs, accordions and visual helper components should therefore be distinguished from the 12 JavaScript classes rather than counted as separate plugins.

### State ownership and teardown

Choose a component controller that creates the plugin after its DOM exists, subscribes to lifecycle events, and disposes/removes listeners before permanently removing the node. If a component is open, close it and wait for the appropriate completion before disposal when its backdrop/scroll state needs normal cleanup. Blindly removing a visible modal can leave an inert-looking page or stale body state. Repeated mounting must not create multiple instances and duplicate callbacks.

The integrated Bootstrap lab uses the data API for an accordion and an explicit Modal instance for review. It updates an existing live status region and tests the close path. Do not copy that lifecycle into an SPA without adapting mount/unmount and route-change behavior.

Source: https://getbootstrap.com/docs/5.3/components/modal/
Source: https://getbootstrap.com/docs/5.3/components/dropdowns/
Source: https://getbootstrap.com/docs/5.3/components/tooltips/
Source: https://getbootstrap.com/docs/5.3/components/toasts/

## 14 Bootstrap customization: Sass maps and CSS variables

### Compile-time versus runtime customization

Sass variables choose generated values before compilation: grid breakpoints, container max-widths, enabled features, theme maps, spacing scales and utility generation. CSS custom properties expose runtime tokens used by the compiled CSS, including component-level --bs-* values and color modes. Changing --bs-primary does not necessarily regenerate every derived component color, RGB tuple, contrast value or state token. Inspect the actual consuming rule.

For example, a `.btn` family exposes local --bs-btn-* properties. Override the complete set of relevant foreground, background, border and state variables for the intended variant, not just one global hue. Check normal, hover, focus-visible, active, selected and disabled presentations. `data-bs-theme="dark"` changes the scoped color-mode variables where Bootstrap defines them; it is a CSS attribute contract, not a JavaScript theme engine.

### Ordered Sass integration

The tested custom build follows Bootstrap 5.3's documented dependency order: functions; scalar overrides; variables; variables-dark; map overrides; maps; mixins; utilities; root and selected CSS-emitting partials; helpers; utilities/api last. The upstream source still relies on Sass @import. Keep the compatibility file isolated and do not rewrite its imports to @use without verifying its global-scope and configuration assumptions.

```scss
// bootstrap-custom.scss; compile with node_modules on the Sass load path.
@use "sass:map";
@import "bootstrap/scss/functions";
$primary: #174ea6;
$enable-negative-margins: false;
@import "bootstrap/scss/variables";
@import "bootstrap/scss/variables-dark";
$theme-colors: map.merge($theme-colors, ("learning": #174ea6));
@import "bootstrap/scss/maps";
@import "bootstrap/scss/mixins";
@import "bootstrap/scss/utilities";
$utilities: map.merge($utilities, (
  "reading-width": (
    property: max-width,
    class: reading-width,
    values: (prose: 70ch),
    responsive: true
  )
));
@import "bootstrap/scss/root";
@import "bootstrap/scss/reboot";
@import "bootstrap/scss/type";
@import "bootstrap/scss/containers";
@import "bootstrap/scss/grid";
@import "bootstrap/scss/buttons";
@import "bootstrap/scss/helpers";
@import "bootstrap/scss/utilities/api";
```

This selected build intentionally emits only its named components. It is a compilation example, not the stylesheet used by the full-component Bootstrap lab, which loads the complete pinned distribution. The resulting CSS includes reading-width-prose and responsive variants; it does not include every component merely because variables were imported. The generated output is preserved as evidence in the example package. Upstream deprecation warnings are recorded, not misrepresented as owned-code warnings.

Maps have dependencies. Update theme colors before derived maps so background/text RGB maps can include the new key. Removing a key may break functions or components that expect it. Modify breakpoint and container maps coherently, preserving their ascending assumptions. Re-importing maps later can duplicate CSS or produce inconsistent derived state. Use the actual framework source for the selected version as the dependency authority.

### Utility API contract

Each utility entry can define property/properties, class, values, responsive, print, state, local-vars, css-var, css-variable-name and related options supported by the generator. A map merge changes the generator input; utilities/api emits output. Enabling responsive and hover/focus variants multiplies classes. `!important` generation follows the framework configuration. Null-valued entries can disable generation in the documented way. Test both positive presence and deliberate absence in compiled CSS.

### CSS layer and RTL integration

A normal vendor layer can make custom components easier to override; existing important Bootstrap utilities still follow important layer precedence. Do not assume wrapping compiled Bootstrap in a layer removes !important. Layer the actual CSS artifact or use a supported build transformation, then inspect the production result. Avoid two independent copies of Reboot.

For RTL, use the documented RTL build and appropriate direction/language metadata. Logical application properties reduce custom exceptions, but framework-generated directional values may still require its RTL transformation. Test a real translated interface rather than mirroring a screenshot. Fonts, long labels, numeric content and icon direction can require different decisions.

Source: https://getbootstrap.com/docs/5.3/customize/sass/
Source: https://getbootstrap.com/docs/5.3/customize/css-variables/
Source: https://getbootstrap.com/docs/5.3/customize/color-modes/
Source: https://getbootstrap.com/docs/5.3/getting-started/rtl/


## 15 Symbiotic ecosystem: from source files to a running interface

### The lifecycle and ownership model

At build time, application SCSS loads modules, evaluates variables/functions/loops and emits CSS. Bootstrap Sass can participate in that build or arrive as a precompiled dependency. At request time, HTML parsing creates DOM nodes while linked CSS is fetched and parsed into stylesheets. Script execution can affect both trees. Style resolution matches selectors, runs cascade/defaulting and computes values. Layout resolves geometry, paint produces drawing commands and compositing combines relevant layers. Resource and font completion, viewport changes, user input and DOM mutations can invalidate work. A rendering engine can optimize this pipeline, so the phases are a conceptual model rather than a promise every mutation runs every phase.

A component has at least four representations: semantic DOM and native control state, application state, CSS state and geometry, and accessibility exposure. A reliable implementation keeps them aligned. SCSS cannot observe runtime DOM changes. A utility class cannot authorize a server operation. A JavaScript property change does not always rewrite the corresponding HTML attribute. A visual state alone does not establish an accessible name or an evaluation result. Animate theme paint cautiously: changing foreground immediately while a background slowly transitions can create a low-contrast intermediate state. The lab changes foreground and background together.

Consider a practice-card disclosure. HTML supplies a button with aria-expanded and aria-controls and a region with hidden. JavaScript owns opening and closing, updating the two states together. CSS derives its arrow presentation from aria-expanded. A live region can announce a meaningful result if the workflow needs it. Sass can generate the shared styles, and Bootstrap could supply a different collapse controller, but both controllers should not own the same region simultaneously.

### HTML attributes, pseudo-classes and custom properties

Use native attributes such as disabled, required, checked and hidden when their semantics match the intended behavior. Boolean attributes are true by presence: disabled="false" remains disabled. Attribute selectors test serialized content; pseudo-classes can test current native state. A checkbox's checked property can differ from its checked attribute after user interaction. :checked follows current state. A data attribute is an application-defined string, not a browser-enforced permission. CSS custom properties carry style tokens and normally inherit; they are not private storage.

ARIA state may be a useful style hook when application behavior keeps it truthful. `[aria-expanded="true"]` is appropriate for styling an actual expanded control; it does not expand a region itself. aria-hidden does not automatically remove focusability and can create a hidden-but-focusable interface. The hidden attribute and display rules interact; author CSS that overrides `[hidden]` can accidentally reveal content. The integrated labs explicitly keep `[hidden] { display:none !important; }` as a narrowly owned application rule.

ClassList manages tokens without replacing unrelated classes. Toggle with an explicit boolean rather than inverting uncertain state repeatedly. Use style.setProperty for an intentional custom-property update; do not replace the entire style attribute. Keep untrusted strings out of CSS URLs, selectors and declarations. CSS.escape escapes identifiers for selector construction; it is not a universal CSS sanitizer.

### CSSOM, resolved style and geometry

Document.styleSheets and CSSStyleSheet expose stylesheet objects, subject to origin restrictions. Reading cssRules from a cross-origin sheet can fail. element.style sees inline declarations, not all matching styles. getComputedStyle returns resolved values after cascade; it can require pending style/layout work. getBoundingClientRect reports a viewport-relative rectangle including transforms and may be fractional. offsetWidth and clientWidth measure different boxes and round differently. Scroll sizes describe scrollable overflow, not semantic content completeness.

## 16 CSS Typed OM and Houdini boundaries

CSS Typed OM replaces some string-based access with typed CSS values. attributeStyleMap addresses inline declarations; computedStyleMap addresses computed style values where supported. CSSUnitValue holds a value and unit; CSS.px(), CSS.percent() and related factories construct values; CSSKeywordValue represents keywords; CSSMathValue subclasses represent calculations; CSSTransformValue and transform components represent supported transforms. CSSStyleValue.parse can parse supported property values. Custom property values can appear as CSSUnparsedValue rather than a fully typed numeric object.

Typed access can reduce manual parsing, but it does not eliminate cascade, layout invalidation or unsupported-property errors. A resolved `auto` is not a number to divide by two. Converting incompatible units is invalid; converting relative lengths can need context that a detached numerical value does not contain. Typed OM coverage is not universal. Feature detection must check the exact API and use a string-based fallback.

```javascript
// Complete function; call with an existing HTMLElement and a finite pixel value.
function setInlineMeasure(element, pixels) {
  if (!Number.isFinite(pixels) || pixels < 0) {
    throw new TypeError('pixels must be a finite nonnegative number');
  }
  if (element.attributeStyleMap && globalThis.CSS?.px) {
    try {
      element.attributeStyleMap.set('width', CSS.px(pixels));
      return 'typed';
    } catch {
      // A supported interface may still reject this property/value combination.
    }
  }
  element.style.width = `${pixels}px`;
  return 'string';
}
```

This is an API access example, not a recommendation to replace responsive CSS with pixel measurements. Use intrinsic CSS layout first. A registered @property or CSS.registerProperty can define a custom property's syntax, inheritance and initial value; registration can enable typed interpolation under its rules. Registration is distinct from Typed OM access and from a worklet. The CSS Painting API and other Houdini worklets are separate capabilities with their own lifecycle, support and security considerations.

Practice: inspect the return type for width:auto and a numeric width. Compare authored inline values to computedStyleMap and getComputedStyle. Test the fallback without the API, and verify the layout still has its normal CSS constraints.

Source: https://www.w3.org/TR/css-typed-om-1/
Source: https://drafts.css-houdini.org/css-properties-values-api-1/

## 17 ResizeObserver: geometry changes without window polling

ResizeObserver reports observed element box sizes, including changes caused by layout or content rather than a window resize. Choose content-box, border-box or device-pixel-content-box where supported and appropriate. ResizeObserverEntry exposes different measurements; box-size collections can represent fragments. inlineSize and blockSize follow writing mode, whereas contentRect width/height are physical dimensions. Do not quietly treat the first fragment as a total across all fragments without declaring that assumption.

Callbacks run during the rendering lifecycle. Writing a size that changes the observed element can trigger another observation and a loop warning. requestAnimationFrame can move work to a later frame but does not resolve an unstable feedback equation by itself. Prefer observing a container and updating a non-sizing output, or compute an idempotent bounded result. Disconnect when the component is no longer owned; unobserve individual targets when appropriate.

```javascript
// Complete controller; output is a separate non-sizing text node in the page.
function reportWidth(target, output) {
  if (typeof globalThis.ResizeObserver !== 'function') {
    output.textContent = 'Automatic measurement is unavailable.';
    return () => {};
  }
  const observer = new ResizeObserver(entries => {
    const entry = entries.find(item => item.target === target);
    if (!entry) return;
    const text = `${Math.round(entry.contentRect.width)} CSS px wide`;
    if (output.textContent !== text) output.textContent = text;
  });
  observer.observe(target, { box: 'content-box' });
  return () => observer.disconnect();
}
```

Do not add aria-live to rapidly changing dimensions by default; repeated announcements while resizing can overwhelm a user. Provide an explicit measurement request or a quiet visible readout when needed. Native container queries should handle presentational layout changes; an observer is justified when application logic needs actual measurement, canvas backing size or integration with a non-CSS system.

For canvas, set its backing pixel dimensions separately from its CSS size and account for device scale. Changing width/height resets drawing state. Avoid reading pixel data or exporting a tainted cross-origin canvas. A chart also needs accessible text or table content; sharp pixels do not expose data relationships.

Source: https://www.w3.org/TR/resize-observer/

## 18 MutationObserver: structural evidence, not visual truth

MutationObserver observes configured changes to attributes, child lists and character data within a chosen subtree. Attribute filters reduce noise; old-value options preserve selected prior values. It does not directly observe every form property change, computed style change, layout change or stylesheet-driven visual transition. An input.value assignment can occur without a value-attribute mutation. A media query can change appearance with no DOM mutation.

Callbacks are delivered asynchronously through the specified microtask machinery and can contain multiple records. Treat records as evidence of mutations, then read the current relevant state; do not assume every record is a complete historical application state. Avoid observing an attribute and rewriting it unconditionally in the same callback. Disconnect before teardown, and use takeRecords deliberately when queued records matter.

```javascript
// Complete observer utility for third-party markup integration.
function watchExpanded(button, onState) {
  const read = () => onState(button.getAttribute('aria-expanded') === 'true');
  const observer = new MutationObserver(read);
  observer.observe(button, { attributes: true, attributeFilter: ['aria-expanded'] });
  read();
  return () => observer.disconnect();
}
```

When your application already owns the state, update the dependent state directly rather than creating an observer to rediscover your own writes. This utility is useful at a genuine integration boundary. Native input/change events, ResizeObserver, font-loading events and transition/animation events answer different questions. Select the observation based on the fact needed, not based on familiarity with one API.

Practice: change a class that changes width, assign input.value and append a child. Predict which mutation records exist and which visible changes need another source of evidence. Include a test that would fail if the observer were incorrectly treated as a layout observer.

Source: https://dom.spec.whatwg.org/#mutation-observers

## 19 View Transitions API: preserving the update contract

A same-document view transition captures visual states around a DOM update callback, builds a transition pseudo-element tree and animates the change where supported. Cross-document transitions use a different opt-in and navigation lifecycle. A view-transition-name pairs elements and must meet uniqueness rules within the relevant capture. The generated pseudo-elements include root, group, image-pair, old and new layers. Styling them is different from styling the live element itself.

The application update must work when the API is absent, capture is skipped, names conflict or the user prefers reduced motion. Distinguish updateCallbackDone, ready and finished promises; a visual transition can fail while the DOM update succeeds. Do not run a mutating update twice in a catch handler after it already ran. Track whether the update began before deciding on a fallback.

```javascript
// Complete helper for a synchronous, idempotent DOM update.
async function updateView(update) {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!document.startViewTransition || reduced) {
    update();
    return;
  }
  let began = false;
  let transition;
  try {
    transition = document.startViewTransition(() => {
      began = true;
      update();
    });
  } catch (error) {
    if (!began) update();
    else throw error;
    return;
  }
  // Consume capture failures separately from the application's update result.
  transition.ready.catch(() => {});
  const finished = transition.finished.catch(() => {});
  await transition.updateCallbackDone;
  await finished;
}
```

The helper's update must be synchronous and should not perform a network mutation; the lab uses it only to toggle a local presentation theme. If update throws, the caller receives the rejection and must report the actual application failure. An API fallback must not swallow server errors and pretend an action succeeded. Focus and announcements need their own policy; a transition screenshot is not a new accessible document.

```css
::view-transition-old(root), ::view-transition-new(root) {
  animation-duration: 150ms;
}
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(root), ::view-transition-new(root) { animation: none; }
}
```

Practice: test absent API, reduced motion, duplicate element names and a rejected update callback. Assert one application update, correct final state and no unhandled rejection. Then test keyboard focus before and after the transition independently of the animation.

Source: https://www.w3.org/TR/css-view-transitions-1/

## 20 Custom Elements, Shadow DOM and style contracts

Custom elements define a lifecycle for valid hyphenated element names. Construction, connection, disconnection, observed attribute changes, adoption and supported state-preserving moves have distinct roles. A constructor should initialize its own structure without assuming attributes/children are already fully parsed. connectedCallback can run more than once; guard initialization and make resource setup repeatable. disconnectedCallback releases listeners, observers, timers and other resources. A reconnection should restore needed resources without duplicating the shadow tree.

Shadow DOM scopes selectors and retargets events under defined rules. It is not a security boundary for hostile code. A closed shadow root changes access conventions; it does not isolate an attacker's script. A host remains part of the outer tree; inherited values and custom properties can cross into shadow content through inheritance. Global selectors do not simply reach internal buttons. Use :host, ::part and documented custom properties for a deliberate public styling API.

A slot projects light-DOM children without moving their ownership into the shadow tree. ::slotted applies to assigned elements under its limited selector model; it cannot arbitrarily select deeply nested projected descendants. slotchange reports assignment changes, not every mutation inside an already assigned node. Shared constructable stylesheets and adoptedStyleSheets can reduce repeated sheet creation where supported; a shared stylesheet mutation affects every adopter, so ownership and fallback handling matter.

The integrated `learning-panel` element exposes a named title slot and a `panel` part, accepts a tone attribute, and reads --panel-accent as a theme token. Its internal button is a real button with aria-expanded and a controlled hidden region. It uses an AbortController for connection-owned listeners, disconnects its observer on removal and restores resources on reconnection. Unsupported APIs leave a usable basic disclosure or slot content rather than blocking the whole page.

Form-associated custom elements require explicit ElementInternals participation, form value/validity and accessibility design. Merely naming a tag input-like does not make it submit. CustomStateSet/:state can express supported custom states; it is separate from defining an aria attribute. Avoid duplicating native controls unless the design requirement justifies the additional keyboard, form and accessibility work.

Source: https://html.spec.whatwg.org/multipage/custom-elements.html
Source: https://dom.spec.whatwg.org/#shadow-trees
Source: https://drafts.csswg.org/css-scoping-1/

## 21 High-performance interaction and accessible runtime behavior

Batch geometry reads before style writes. Cache results only for a known validity window; font loading, zoom, content changes and container changes can invalidate them. requestAnimationFrame schedules work near rendering, but it does not make an expensive read-write loop free. Avoid observing every element with every API merely because the APIs are available.

Use CSS for declarative layout and known visual states; use JavaScript for state transitions and facts CSS cannot express. Prefer a single state owner. A server result can update a status region, but visual success styling must not precede actual success. Respect pending/error/empty states. Fetch cancellation does not undo a completed server mutation; idempotency and authorization belong to the receiver.

Separate geometry from semantics: a ResizeObserver can choose a canvas resolution but does not decide an accessible name. A MutationObserver can report a changed attribute but does not prove the intended state transition occurred. A CSS transitionend event can be absent when duration is zero, a property does not transition, the node is removed or the transition is canceled. Do not make essential cleanup depend exclusively on an event that may never arrive; use the component's authoritative lifecycle and bounded fallbacks.

IntersectionObserver can defer nonessential work until visibility conditions are met, but it is not proof that a human read content. FontFaceSet readiness can help coordinate measurements, but fonts can be loaded later. matchMedia change listeners can follow user preference changes and need removal during teardown. The Web Animations API exposes animation objects and promises, with cancellation behavior that differs from simply removing a CSS class. CSS.supports is a parsing/capability check, not a browser bug detector or accessibility test.

Performance exercise: append 100 practice rows in a fragment, then apply a class once. Compare with a loop that reads each row's geometry immediately after inserting it. Record actual browser trace durations on representative hardware; do not assert a fixed speedup. Use content-visibility only after verifying search, keyboard navigation, scroll position and placeholder sizing in the target engines.

## 22 Integrated labs, assessments and production acceptance

The complete lab sources follow in the document. They use local Bootstrap assets and compile-time Sass dependencies pinned in the evidence record. Each standalone HTML lab supplies a doctype, language, charset, viewport, title and semantic document structure. API demonstrations use progressive enhancement. Small snippets elsewhere teach one contract at a time; the labs combine those contracts without relying on undeclared variables or imaginary endpoints.

### Lab A: responsive learning workbench

Build a semantic page with a skip link, header, main content, a filter form, a result list and a help disclosure. Use Grid for the page and card list, Flexbox for action clusters, logical properties, intrinsic constraints and rem-based bounds. Keep labels visible and update an existing status node after explicit filtering. Test 320, 768 and 1280 CSS-pixel widths, long labels and zero results. Verify source order and keyboard behavior before visual polish.

### Lab B: Bootstrap review flow

Use the pinned full Bootstrap CSS and bundle, a responsive container/row/column layout, cards, a native validation form, an accordion and a review modal. The modal displays a local summary and performs no payment or account operation. Verify its label, focus entry, close action, Escape and focus return. Keep dark-mode support explicit. Test with transitions reduced and confirm the component's actual shown/hidden events rather than arbitrary sleeps.

### Lab C: custom element and API lifecycle

Mount a learning-panel, toggle its internal disclosure, change its tone, observe size and an aria-expanded attribute, then disconnect and reconnect the host. A theme button uses the guarded view-transition helper. Typed OM is attempted only where available with a string fallback. Verify cleanup by reconnecting and ensuring one listener response per click. Rendering should remain usable without the advanced APIs.

### Lab D: Sass source-to-output workshop

Compile independent examples for variables, nesting, mixins/content, functions, placeholders, loops, interpolation, maps and module configuration. Assert generated selectors and selected declarations, then test deliberate invalid argument cases. Compile a selected Bootstrap customization build and inspect the generated utility family and theme class. Keep dependency deprecations visible in the evidence report.

### Assessment rubric and answer boundaries

Score semantic correctness, state correctness, layout robustness, maintainability, performance evidence and accessibility evidence separately. A learner who chooses Grid rather than Flexbox can be correct if the requirements and observable behavior hold. A screenshot match with incorrect reading order is not a passing solution. A successful compile says nothing about whether the UI is usable with a keyboard.

For RAG teaching, chunk a property record with its family explanation, applicability, shorthand relationships and source; retrieve the relevant layout chapter when answering why a valid declaration has no effect. Separate reference knowledge from private evaluator fixtures. Do not index hidden tests or unrevealed exercise solutions into unrestricted hint retrieval. This document supplies content and examples; it does not claim the current application's ingestion schema or browser runner has been implemented.

### Production acceptance sequence

1. Confirm requirements: content order, devices/input modes, supported engines, languages, themes and WCAG target.
2. Build reproducibly: lock dependencies, compile all entries, review warnings, inspect output size and production asset loading.
3. Validate semantics: headings, regions, labels, unique IDs, real control states, meaningful alternatives and actual form payloads.
4. Verify layout: narrow viewport, zoom/reflow, long text, localization, RTL, missing assets, fonts and overflow boundaries.
5. Verify interactions: keyboard paths, focus visibility, modal cleanup, repeated actions, pending/error states and teardown/reconnection.
6. Verify accessibility: automated rules plus manual screen-reader, contrast, focus, target-size, reduced-motion and forced-color checks appropriate to the product.
7. Measure performance: representative content/hardware, trace style/layout/paint, investigate long tasks and check layout shifts.
8. Record evidence: exact source/package versions, source hashes, test commands, observed results, untested conditions and accepted tradeoffs. Retest after material changes.

Accessibility references include WCAG 2.2 criteria for information/relationships, meaningful sequence, use of color, contrast, resize/reflow, text spacing, non-text contrast, keyboard operation, focus order/visibility/not-obscured, target size, labels/instructions, error identification, name/role/value and status messages. Additional criteria can apply to the actual product; this list is a training map rather than a complete conformance audit.

Source: https://www.w3.org/TR/WCAG22/
Source: https://www.w3.org/WAI/ARIA/apg/


## 23 Complete CSS property dictionary

The following records cover all **752 non-vendor property names** in W3C Webref @webref/css 8.7.7. This is a specification inventory, not 752 recommended browser-baseline features. Each record provides a teaching explanation, exact extracted value grammar, initial value, inheritance, applicability, percentage behavior, computed-value rule, animation type, shorthand members and a primary definition link. Some draft records lack fields in the source; those fields are labeled rather than guessed.

Read every shorthand together with its listed longhands. The five CSS-wide keywords inherit, initial, unset, revert and revert-layer are generally available in addition to property-specific grammars, under the cascade rules. Custom properties are covered in Part 2 and are not a finite named set. The source grammar can include extended draft alternatives; consult the linked modules and test the precise syntax in target engines.

A Snapshot-index flag identifies presence in the retrieved CSS Snapshot 2025 index, which itself contains historical and specialized entries. Supplemental means absent from that index, not automatically experimental. SVG-only, speech, paged-media and draft properties retain their own applicability and do not become general HTML layout properties.

### P001 accent-color

Set the accent used by supporting native controls; verify contrast and forced-color behavior rather than replacing their semantics.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <color>`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: the keyword auto or a computed color. Animation: by computed value type.

Source: https://drafts.csswg.org/css-ui-4/#propdef-accent-color

### P002 align-content

Distribute the line/track collection in available cross/block space; a one-line flex container usually has no line collection to distribute.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <baseline-position> | <content-distribution> | <overflow-position>? <content-position>`

Initial: normal. Inherited: no. Applies to: block containers, multicol containers, flex containers, and grid containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-align-3/#propdef-align-content

### P003 align-items

Set the default self-alignment of flex or grid items in the relevant alignment axis; stretch remains subject to item sizing constraints.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | stretch | <baseline-position> | <overflow-position>? <self-position>`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-align-3/#propdef-align-items

### P004 align-self

Override the container's align-items for this item; auto margins and explicit sizes can affect the visible result.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <overflow-position>? [ normal | <self-position> ]| stretch | <baseline-position> | anchor-center`

Initial: auto. Inherited: no. Applies to: flex items, grid items, and absolutely-positioned boxes.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/#propdef-align-self.

Source: https://drafts.csswg.org/css-align-3/#propdef-align-self

### P005 alignment-baseline

Choose which baseline participates in baseline alignment in the applicable inline or SVG context.

Family/use case: Inline formatting and baselines. Use for typography requiring baseline/line-box control; actual font metrics and writing modes determine the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `baseline | <baseline-metric>`

Initial: baseline. Inherited: no. Applies to: inline-level boxes, flex items, grid items, table cells, and SVG text content elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-alignment-baseline

### P006 all

Reset nearly all properties at once; direction, unicode-bidi and custom properties are excluded. Avoid erasing useful native-control styling indiscriminately.

Family/use case: Cascade and defaulting. Use to define an explicit reset/override boundary while preserving native controls and user preferences.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `initial | inherit | unset | revert | revert-layer | revert-rule`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Source: https://drafts.csswg.org/css-cascade-5/#propdef-all

### P007 anchor-name

Name an element as a potential anchor for supported anchor-positioned UI; a name alone does not position another element.

Family/use case: Specialized or draft module: css-anchor-position-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <anchor-name>#`

Initial: none. Inherited: no. Applies to: all elements that generate a principal box.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-anchor-name

### P008 anchor-scope

Constrain anchor-name lookup to a scope so repeated components can avoid unintended anchor associations.

Family/use case: Specialized or draft module: css-anchor-position-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | all | <anchor-name>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-anchor-scope

### P009 animation

Set an animation list through a shorthand; omitted members reset and newer timeline/range members require careful reset-order review.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<single-animation>#`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: not animatable.

Shorthand members: `animation-name`, `animation-duration`, `animation-timing-function`, `animation-delay`, `animation-iteration-count`, `animation-direction`, `animation-fill-mode`, `animation-play-state`, `animation-timeline`.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation

### P010 animation-composition

Choose how an animation's effect combines with underlying values; replace, add and accumulate have property-specific consequences.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<single-animation-composition>#`

Initial: replace. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a keyword as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-2/#propdef-animation-composition

### P011 animation-delay

Offset when an animation's active interval begins; a negative delay starts partway through its timeline.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <'animation-delay-start'> <'animation-delay-end'>? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `animation-delay-start`, `animation-delay-end`.

Source: https://drafts.csswg.org/css-animations-2/#propdef-animation-delay

### P012 animation-delay-end

The `animation-delay-end` setting belongs to motion and timelines; its grammar and applicability below define the animation delay end contract. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<time [0s,∞]>#`

Initial: 0s. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a duration. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-2/#propdef-animation-delay-end

### P013 animation-delay-start

The `animation-delay-start` setting belongs to motion and timelines; its grammar and applicability below define the animation delay start contract. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<time>#`

Initial: 0s. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a duration. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-2/#propdef-animation-delay-start

### P014 animation-direction

Choose normal/reverse/alternating playback across iterations; alternating motion does not change DOM order.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<single-animation-direction>#`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a keyword as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation-direction

### P015 animation-duration

Set the duration of an iteration under the selected timeline model; auto has timeline-specific behavior in newer modules.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ auto | <time [0s,∞]> ]#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item either a time or the keyword auto. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-2/#propdef-animation-duration

### P016 animation-fill-mode

Choose whether animated values apply before or after the active interval; retained effects can complicate later overrides.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<single-animation-fill-mode>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a keyword as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation-fill-mode

### P017 animation-iteration-count

Set a finite or infinite repeat count; provide a pause/stop strategy where moving-content accessibility requirements apply.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<single-animation-iteration-count>#`

Initial: 1. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item either a number or the keyword infinite. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation-iteration-count

### P018 animation-name

Associate an animation with named keyframes; an unknown name supplies no keyframe effect.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ none | <keyframes-name> ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item either a case-sensitive css identifier or the keyword none. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation-name

### P019 animation-play-state

Pause or resume the applicable CSS animation; pausing does not reset it to the beginning.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<single-animation-play-state>#`

Initial: running. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a keyword as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation-play-state

### P020 animation-range

Define the attachment range on a supported timeline; its start/end components constrain where the effect runs.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'animation-range-start'> <'animation-range-end'>? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `animation-range-start`, `animation-range-end`.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-animation-range

### P021 animation-range-center

The `animation-range-center` setting belongs to motion and timelines; its grammar and applicability below define the animation range center contract. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ normal | [ <length-percentage> | <timeline-range-center-subject> <length-percentage>? ] ]#`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: relative to the corresponding dimension of the specified timeline range center subject, else relative to the start of the animation attachment range. Computed value: list, each item either the keyword normal or a timeline range center subject and a length-percentage value. Animation: not animatable.

Source: https://drafts.csswg.org/pointer-animations-1/#propdef-animation-range-center

### P022 animation-range-end

The `animation-range-end` setting belongs to motion and timelines; its grammar and applicability below define the animation range end contract. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ normal | <length-percentage> | <timeline-range-name> <length-percentage>? ]#`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: relative to the specified named timeline range if one was specified, else to the entire timeline. Computed value: list, each item either the keyword normal or a timeline range and progress percentage. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-animation-range-end

### P023 animation-range-start

The `animation-range-start` setting belongs to motion and timelines; its grammar and applicability below define the animation range start contract. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ normal | <length-percentage> | <timeline-range-name> <length-percentage>? ]#`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: relative to the specified named timeline range if one was specified, else to the entire timeline. Computed value: list, each item either the keyword normal or a timeline range and progress percentage. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-animation-range-start

### P024 animation-timeline

Select a time-based or supported scroll/view timeline; keep content usable when scroll-driven animation is unavailable.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<single-animation-timeline>#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item either the keyword none, the keyword auto, a case-sensitive css identifier, a computed scroll() function, or a computed view() function. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-2/#propdef-animation-timeline

### P025 animation-timing-function

Control progress interpolation between relevant keyframes; easing is not a guarantee of a compositor-only animation.

Family/use case: Motion and timelines. Use for a bounded visual explanation or state transition, with reduced-motion behavior and a usable static state.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<easing-function>#`

Initial: ease. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a computed <easing-function>. Animation: not animatable.

Source: https://drafts.csswg.org/css-animations-1/#propdef-animation-timing-function

### P026 animation-trigger

The `animation-trigger` setting belongs to draft animation triggers; its grammar and applicability below define the animation trigger contract. Research reference for trigger-based motion; preserve a complete nonanimated application state.

Family/use case: Draft animation triggers. Research reference for trigger-based motion; preserve a complete nonanimated application state.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | [ <dashed-ident> <animation-action>+ ]+ ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-animation-trigger

### P027 appearance

Control native widget appearance; removing it transfers responsibility for a recognizable, operable and contrast-safe presentation to the author.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | auto | base | base-select | <compat-auto> | <compat-special>`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-appearance

### P028 aspect-ratio

Supply a preferred width-to-height ratio for auto sizing; min/max constraints and intrinsic replaced-element ratios can still change the used box.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto || <ratio>`

Initial: auto. Inherited: no. Applies to: all elements except inline boxes and internal ruby or table boxes.

Percentages: n/a. Computed value: specified keyword or a pair of numbers. Animation: by computed value.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-aspect-ratio

### P029 backdrop-filter

Filter pixels behind an element in the applicable backdrop; keep a readable opaque fallback and measure rendering cost.

Family/use case: Specialized or draft module: filter-effects-2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <filter-value-list>`

Initial: none. Inherited: no. Applies to: All elements. In SVG, it applies to container elements without the defs element and all graphics elements.

Percentages: n/a. Computed value: as specified. Animation: see prose in Filter Effects 1 § 14. Animation of Filters..

Source: https://drafts.csswg.org/filter-effects-2/#propdef-backdrop-filter

### P030 backface-visibility

Control whether the reverse face of a transformed element is visible; it does not disable interaction or change semantic visibility by itself.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `visible | hidden`

Initial: visible. Inherited: no. Applies to: transformable elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-backface-visibility

### P031 background

Set coordinated background layers and color; the slash separates position/size, and omitted longhands reset.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<bg-layer>#? , <final-bg-layer>`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `background-image`, `background-position`, `background-size`, `background-repeat`, `background-attachment`, `background-origin`, `background-clip`, `background-color`.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background

### P032 background-attachment

Choose whether each background layer scrolls with the element, its local scroll content or the viewport under the relevant rules.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<attachment>#`

Initial: scroll. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item the keyword as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-attachment

### P033 background-blend-mode

Choose how background layers blend with one another and the background color; blending can change effective text contrast.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'mix-blend-mode'>#`

Initial: normal. Inherited: no. Applies to: All HTML elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/compositing-2/#propdef-background-blend-mode

### P034 background-clip

Choose the box to which background painting is clipped; border-box, padding-box and content-box differ from the positioning origin.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<bg-clip>#`

Initial: border-box. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-clip

### P035 background-color

Paint the background color beneath background images; evaluate text contrast on the actual composited surface.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color>`

Initial: transparent. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: computed color. Animation: by computed value.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-color

### P036 background-image

Provide one or more image layers, including gradients; background imagery is not an accessible substitute for meaningful HTML images.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<bg-image>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item either an <image> or the keyword none. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-image

### P037 background-origin

Choose the reference box for positioning each background image; it does not itself determine clipping.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<visual-box>#`

Initial: padding-box. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a keyword as specified. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-origin

### P038 background-position

Place each image within its positioning area; percentages relate the image size and positioning area rather than simply measuring from the left edge.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<bg-position>#`

Initial: 0% 0%. Inherited: no. Applies to: all elements.

Percentages: refer to size of background positioning area minus size of background image; see text. Computed value: a list, each item a pair of offsets (horizontal and vertical) from the top left origin, each offset given as a computed <length-percentage> value. Animation: repeatable list.

Shorthand members: `background-position-x`, `background-position-y`.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-position

### P039 background-position-block

The `background-position-block` setting belongs to background painting; its grammar and applicability below define the background position block contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ center | [ [ start | end ]? <length-percentage>? ]! ]#`

Initial: 0%. Inherited: no. Applies to: all elements.

Percentages: refer to size of background positioning area minus size of background image. Computed value: A list, each item consisting of: an offset given as a computed <length-percentage> value, plus an origin keyword. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-position-block

### P040 background-position-inline

The `background-position-inline` setting belongs to background painting; its grammar and applicability below define the background position inline contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ center | [ [ start | end ]? <length-percentage>? ]! ]#`

Initial: 0%. Inherited: no. Applies to: all elements.

Percentages: refer to inline-size of background positioning area minus inline-size of background image. Computed value: A list, each item consisting of: an offset given as a computed <length-percentage> value, plus an origin keyword. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-position-inline

### P041 background-position-x

The `background-position-x` setting belongs to background painting; its grammar and applicability below define the background position x contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ center | [ [ left | right | x-start | x-end ]? <length-percentage>? ]! ]#`

Initial: 0%. Inherited: no. Applies to: all elements.

Percentages: refer to width of background positioning area minus width of background image. Computed value: A list, each item consisting of: an offset given as a computed <length-percentage> value, plus an origin keyword. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-position-x

### P042 background-position-y

The `background-position-y` setting belongs to background painting; its grammar and applicability below define the background position y contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ center | [ [ top | bottom | y-start | y-end ]? <length-percentage>? ]! ]#`

Initial: 0%. Inherited: no. Applies to: all elements.

Percentages: refer to height of background positioning area minus height of background image. Computed value: A list, each item consisting of: an offset given as a computed <length-percentage> value, plus an origin keyword. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-position-y

### P043 background-repeat

Control repetition of each layer, including space/round behavior; a gradient can repeat as a tile unless configured appropriately.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<repeat-style>#`

Initial: repeat. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a pair of keywords, one per dimension. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-repeat

### P044 background-repeat-block

The `background-repeat-block` setting belongs to background painting; its grammar and applicability below define the background repeat block contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<repetition>#`

Initial: repeat. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-repeat-block

### P045 background-repeat-inline

The `background-repeat-inline` setting belongs to background painting; its grammar and applicability below define the background repeat inline contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<repetition>#`

Initial: repeat. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-repeat-inline

### P046 background-repeat-x

The `background-repeat-x` setting belongs to background painting; its grammar and applicability below define the background repeat x contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<repetition>#`

Initial: repeat. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-repeat-x

### P047 background-repeat-y

The `background-repeat-y` setting belongs to background painting; its grammar and applicability below define the background repeat y contract. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<repetition>#`

Initial: repeat. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-repeat-y

### P048 background-size

Size each image layer using dimensions or cover/contain; cover can crop and contain can leave unused space.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<bg-size>#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: see text. Computed value: list, each item a pair of sizes (one per axis) each represented as either a keyword or a computed <length-percentage> value. Animation: repeatable list.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-size

### P049 background-tbd

A draft placeholder name in the source inventory, not a production authoring recommendation. Use the established background longhands and follow the defining draft before interpreting this provisional record.

Family/use case: Background painting. Use for surface decoration behind semantic content; keep text contrast and missing-resource fallbacks explicit.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<bg-layer>#`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Source: https://drafts.csswg.org/css-backgrounds-4/#propdef-background-tbd

### P050 baseline-shift

Offset the applicable baseline; check the inline/SVG module context rather than treating this as general block positioning.

Family/use case: Inline formatting and baselines. Use for typography requiring baseline/line-box control; actual font metrics and writing modes determine the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage> | sub | super | top | center | bottom`

Initial: 0. Inherited: no. Applies to: inline-level boxes and SVG text content elements.

Percentages: refer to the used value of line-height. Computed value: the specified keyword or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-inline-3/#propdef-baseline-shift

### P051 baseline-source

Choose the baseline source for baseline-aligned boxes where the inline layout model supports it.

Family/use case: Inline formatting and baselines. Use for typography requiring baseline/line-box control; actual font metrics and writing modes determine the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | first | last`

Initial: auto. Inherited: no. Applies to: inline-level boxes that establish an independent formatting context.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-baseline-source

### P052 block-ellipsis

The `block-ellipsis` setting belongs to block layout extensions; its grammar and applicability below define the block ellipsis contract. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `no-ellipsis | ellipsis | <string>`

Initial: no-ellipsis. Inherited: yes. Applies to: block containers.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-block-ellipsis

### P053 block-size

Set the preferred size in the block axis determined by writing-mode; it corresponds to height in ordinary horizontal writing.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements except non-replaced inlines.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value type, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-block-size

### P054 block-step

The `block-step` setting belongs to block layout extensions; its grammar and applicability below define the block step contract. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'block-step-size'> || <'block-step-insert'> || <'block-step-align'> || <'block-step-round'>`

Initial: see individual properties. Inherited: no. Applies to: block-level boxes.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `block-step-size`, `block-step-insert`, `block-step-align`, `block-step-round`.

Source: https://drafts.csswg.org/css-rhythm-1/#propdef-block-step

### P055 block-step-align

The `block-step-align` setting belongs to block layout extensions; its grammar and applicability below define the block step align contract. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | center | start | end`

Initial: auto. Inherited: no. Applies to: block-level boxes.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-rhythm-1/#propdef-block-step-align

### P056 block-step-insert

The `block-step-insert` setting belongs to block layout extensions; its grammar and applicability below define the block step insert contract. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `margin-box | padding-box | content-box`

Initial: margin-box. Inherited: no. Applies to: block-level boxes.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-rhythm-1/#propdef-block-step-insert

### P057 block-step-round

The `block-step-round` setting belongs to block layout extensions; its grammar and applicability below define the block step round contract. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `up | down | nearest`

Initial: up. Inherited: no. Applies to: block-level boxes.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-rhythm-1/#propdef-block-step-round

### P058 block-step-size

The `block-step-size` setting belongs to block layout extensions; its grammar and applicability below define the block step size contract. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Family/use case: Block layout extensions. Use the defining sizing/fragmentation module and verify implementation; the name alone does not imply a general height control.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <length [0,∞]>`

Initial: none. Inherited: no. Applies to: block-level boxes.

Percentages: N/A. Computed value: specified keyword or absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-rhythm-1/#propdef-block-step-size

### P059 bookmark-label

The `bookmark-label` setting belongs to paged-media navigation; its grammar and applicability below define the bookmark label contract. Use only with a verified paged-media processor that supports the generated-document bookmark model.

Family/use case: Paged-media navigation. Use only with a verified paged-media processor that supports the generated-document bookmark model.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<content-list>`

Initial: content(text). Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-content-3/#propdef-bookmark-label

### P060 bookmark-level

The `bookmark-level` setting belongs to paged-media navigation; its grammar and applicability below define the bookmark level contract. Use only with a verified paged-media processor that supports the generated-document bookmark model.

Family/use case: Paged-media navigation. Use only with a verified paged-media processor that supports the generated-document bookmark model.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <integer [1,∞]>`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: the keyword none or the specified integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-content-3/#propdef-bookmark-level

### P061 bookmark-state

The `bookmark-state` setting belongs to paged-media navigation; its grammar and applicability below define the bookmark state contract. Use only with a verified paged-media processor that supports the generated-document bookmark model.

Family/use case: Paged-media navigation. Use only with a verified paged-media processor that supports the generated-document bookmark model.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `open | closed`

Initial: open. Inherited: no. Applies to: block-level elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-content-3/#propdef-bookmark-state

### P062 border

The `border` setting belongs to borders and corners; its grammar and applicability below define the border contract. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-width`, `border-style`, `border-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border

### P063 border-block

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-block-start'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start`, `border-block-end`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block

### P064 border-block-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-clip'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start-clip`, `border-block-end-clip`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-clip

### P065 border-block-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-color'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start-color`, `border-block-end-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-color

### P066 border-block-end

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-end-width`, `border-block-end-style`, `border-block-end-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-end

### P067 border-block-end-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-end-clip

### P068 border-block-end-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-end-color

### P069 border-block-end-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-end-start-radius`, `border-end-end-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-end-radius

### P070 border-block-end-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-end-style

### P071 border-block-end-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-end-width

### P072 border-block-start

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start-width`, `border-block-start-style`, `border-block-start-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-start

### P073 border-block-start-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-start-clip

### P074 border-block-start-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-start-color

### P075 border-block-start-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-start-start-radius`, `border-start-end-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-start-radius

### P076 border-block-start-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-start-style

### P077 border-block-start-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-start-width

### P078 border-block-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-style'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start-style`, `border-block-end-style`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-style

### P079 border-block-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-width'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start-width`, `border-block-end-width`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-block-width

### P080 border-bottom

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-bottom-width`, `border-bottom-style`, `border-bottom-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom

### P081 border-bottom-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-clip

### P082 border-bottom-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-color

### P083 border-bottom-left-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-left-radius

### P084 border-bottom-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-bottom-left-radius`, `border-bottom-right-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-radius

### P085 border-bottom-right-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-right-radius

### P086 border-bottom-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-style

### P087 border-bottom-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-width

### P088 border-boundary

The `border-boundary` setting belongs to borders and corners; its grammar and applicability below define the border boundary contract. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | parent | display`

Initial: none. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-round-display-1/#propdef-border-boundary

### P089 border-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-clip'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-clip`, `border-right-clip`, `border-bottom-clip`, `border-left-clip`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-clip

### P090 border-collapse

Choose separate or collapsed table border models; collapsed borders use a conflict-resolution algorithm and change which other border properties apply.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `separate | collapse`

Initial: separate. Inherited: yes. Applies to: table grid boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-tables-3/#propdef-border-collapse

### P091 border-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <color> | <image-1D> ]{1,4}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-color`, `border-right-color`, `border-bottom-color`, `border-left-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-color

### P092 border-end-end-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-end-end-radius

### P093 border-end-start-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-end-start-radius

### P094 border-image

Use an image to paint border regions; the shorthand controls source, slicing, sizing, outset and repetition and resets omitted parts.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-image-source'> || <'border-image-slice'> [ / <'border-image-width'> | / <'border-image-width'>? / <'border-image-outset'> ]? || <'border-image-repeat'>`

Initial: See individual properties. Inherited: no. Applies to: See individual properties.

Percentages: N/A. Computed value: See individual properties. Animation: See individual properties.

Shorthand members: `border-image-source`, `border-image-slice`, `border-image-width`, `border-image-outset`, `border-image-repeat`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-image

### P095 border-image-outset

Extend the border image beyond its border box; extra paint does not reserve matching layout space.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <length [0,∞]> | <number [0,∞]> ]{1,4}`

Initial: 0. Inherited: no. Applies to: All elements, except internal table elements when border-collapse is collapse.

Percentages: N/A. Computed value: four values, each a number or absolute length. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-image-outset

### P096 border-image-repeat

Choose stretch, repeat, round or space for edge regions according to support and image-border rules.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ stretch | repeat | round | space ]{1,2}`

Initial: stretch. Inherited: no. Applies to: All elements, except internal table elements when border-collapse is collapse.

Percentages: N/A. Computed value: two keywords, one per axis. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-image-repeat

### P097 border-image-slice

Slice the source into border/corner regions; unitless source coordinates and percentages follow image-slicing rules rather than ordinary CSS lengths.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[<number [0,∞]> | <percentage [0,∞]>]{1,4} && fill?`

Initial: 100%. Inherited: no. Applies to: All elements, except internal table elements when border-collapse is collapse.

Percentages: refer to size of the border image. Computed value: four values, each either a number or percentage; plus a fill keyword if specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-image-slice

### P098 border-image-source

Select the border image resource or gradient; an unavailable source needs a suitable ordinary border fallback.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <image>`

Initial: none. Inherited: no. Applies to: All elements, except internal table elements when border-collapse is collapse.

Percentages: N/A. Computed value: the keyword none or the computed <image>. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-image-source

### P099 border-image-width

Set the painted border-image region widths; numeric multipliers relate to border widths rather than being bare CSS pixel lengths.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <length-percentage [0,∞]> | <number [0,∞]> | auto ]{1,4}`

Initial: 1. Inherited: no. Applies to: All elements, except internal table elements when border-collapse is collapse.

Percentages: Relative to width/height of the border image area. Computed value: four values, each either a number, the keyword auto, or a computed <length-percentage> value. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-image-width

### P100 border-inline

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-block-start'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start`, `border-inline-end`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline

### P101 border-inline-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-clip'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start-clip`, `border-inline-end-clip`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-clip

### P102 border-inline-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-color'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start-color`, `border-inline-end-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-color

### P103 border-inline-end

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-end-width`, `border-inline-end-style`, `border-inline-end-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end

### P104 border-inline-end-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end-clip

### P105 border-inline-end-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end-color

### P106 border-inline-end-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-start-end-radius`, `border-end-end-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end-radius

### P107 border-inline-end-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end-style

### P108 border-inline-end-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end-width

### P109 border-inline-start

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start-width`, `border-inline-start-style`, `border-inline-start-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start

### P110 border-inline-start-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start-clip

### P111 border-inline-start-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start-color

### P112 border-inline-start-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-start-start-radius`, `border-end-start-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start-radius

### P113 border-inline-start-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start-style

### P114 border-inline-start-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start-width

### P115 border-inline-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-style'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start-style`, `border-inline-end-style`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-style

### P116 border-inline-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-width'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start-width`, `border-inline-end-width`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-inline-width

### P117 border-left

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-left-width`, `border-left-style`, `border-left-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-left

### P118 border-left-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-left-clip

### P119 border-left-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-left-color

### P120 border-left-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-left-radius`, `border-bottom-left-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-left-radius

### P121 border-left-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-left-style

### P122 border-left-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-left-width

### P123 border-limit

The `border-limit` setting belongs to borders and corners; its grammar and applicability below define the border limit contract. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `all | [ sides | corners ] <length-percentage [0,∞]>? | [ top | right | bottom | left ] <length-percentage [0,∞]>`

Initial: all. Inherited: no. Applies to: all elements, except table element when border-collapse is collapse.

Percentages: relative to border-box. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-limit

### P124 border-radius

Shape elliptical or circular box corners; slash-separated horizontal/vertical radii differ from a four-side margin shorthand.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage [0,∞]>{1,4} [ / <length-percentage [0,∞]>{1,4} ]?`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-left-radius`, `border-top-right-radius`, `border-bottom-right-radius`, `border-bottom-left-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-radius

### P125 border-right

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-right-width`, `border-right-style`, `border-right-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-right

### P126 border-right-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-right-clip

### P127 border-right-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-right-color

### P128 border-right-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-right-radius`, `border-bottom-right-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-right-radius

### P129 border-right-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-right-style

### P130 border-right-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-right-width

### P131 border-shape

The `border-shape` setting belongs to borders and corners; its grammar and applicability below define the border shape contract. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <basic-shape> <geometry-box>?]{1,2}`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: see prose. Computed value: list, each item a computed color. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-shape

### P132 border-spacing

Set horizontal and vertical distances between cells in the separate-border table model; it does not create ordinary margins on cells.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length [0,∞]>{1,2}`

Initial: 0px 0px. Inherited: yes. Applies to: table grid boxes when border-collapse is separate.

Percentages: n/a. Computed value: two absolute lengths. Animation: by computed value.

Source: https://drafts.csswg.org/css-tables-3/#propdef-border-spacing

### P133 border-start-end-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-start-end-radius

### P134 border-start-start-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-start-start-radius

### P135 border-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-top-style'>{1,4}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-style`, `border-right-style`, `border-bottom-style`, `border-left-style`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-style

### P136 border-top

Set combined border settings for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width> || <line-style> || <color>`

Initial: See individual properties. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-width`, `border-top-style`, `border-top-color`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top

### P137 border-top-clip

Set draft border clipping geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <length-percentage [0,∞]> | <flex> ]+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: refer to length of border-edge side. Computed value: none, or a list consisting of absolute lengths, or percentages as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-clip

### P138 border-top-color

Set paint color for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color> | <image-1D>`

Initial: currentcolor. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: the computed color and/or a one-dimensional image function. Animation: see prose.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-color

### P139 border-top-left-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-left-radius

### P140 border-top-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>{1,2} [ / <length-percentage [0,∞]>{1,2} ]?`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-left-radius`, `border-top-right-radius`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-radius

### P141 border-top-right-radius

Set corner radius geometry for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<border-radius>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: pair of computed <length-percentage> values. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-right-radius

### P142 border-top-style

Set stroke style for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-style>`

Initial: none. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-style

### P143 border-top-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements except ruby base containers and ruby annotation containers.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-top-width

### P144 border-width

Set border thickness for the named physical side/corner or logical block/inline edge. Logical mapping follows writing-mode and direction; omitted shorthand members reset. Read the exact grammar and longhand expansion below.

Family/use case: Borders and corners. Use for component boundaries or table geometry; distinguish layout border space from image/shape painting.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-top-width'>{1,4}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-width`, `border-right-width`, `border-bottom-width`, `border-left-width`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-border-width

### P145 bottom

Set the physical bottom inset for a positioned element; it has no positioning effect on a static box.

Family/use case: Positioning. Use for a sticky header or deliberate overlay after identifying the containing block and scroll/stacking contexts.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage> | <anchor()> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-position-3/#propdef-bottom

### P146 box-decoration-break

Choose how decorations are sliced or cloned across fragmented boxes such as line-wrapped inline content.

Family/use case: Fragmentation. Use to improve print or multicol page breaks; impossible keep/break constraints remain subject to the formatter.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `slice | clone`

Initial: slice. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-break-4/#propdef-box-decoration-break

### P147 box-shadow

Paint one or more exterior/inset shadows; offsets, blur and spread are paint effects and do not reserve layout space.

Family/use case: Shadow painting. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<spread-shadow>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `box-shadow-color`, `box-shadow-offset`, `box-shadow-blur`, `box-shadow-spread`, `box-shadow-position`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-box-shadow

### P148 box-shadow-blur

The `box-shadow-blur` setting belongs to shadow painting; its grammar and applicability below define the box shadow blur contract. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Family/use case: Shadow painting. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length [0,∞]>#`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a <length>. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-box-shadow-blur

### P149 box-shadow-color

The `box-shadow-color` setting belongs to shadow painting; its grammar and applicability below define the box shadow color contract. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Family/use case: Shadow painting. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color>#`

Initial: currentcolor. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a computed color. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-box-shadow-color

### P150 box-shadow-offset

The `box-shadow-offset` setting belongs to shadow painting; its grammar and applicability below define the box shadow offset contract. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Family/use case: Shadow painting. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | <length>{1,2} ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item either none or a pair of offsets (horizontal and vertical) from the element's box. Animation: by computed value, treating none as 0 0 when interpolated with non-none values..

Source: https://drafts.csswg.org/css-borders-4/#propdef-box-shadow-offset

### P151 box-shadow-position

The `box-shadow-position` setting belongs to shadow painting; its grammar and applicability below define the box shadow position contract. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Family/use case: Shadow painting. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ outset | inset ]#`

Initial: outset. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item one of the keywords. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-box-shadow-position

### P152 box-shadow-spread

The `box-shadow-spread` setting belongs to shadow painting; its grammar and applicability below define the box shadow spread contract. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Family/use case: Shadow painting. Use to express elevation where useful; the shadow reserves no layout space and must not be the only boundary in forced colors.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length>#`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a <length>. Animation: by computed value.

Source: https://drafts.csswg.org/css-borders-4/#propdef-box-shadow-spread

### P153 box-sizing

Choose whether the preferred width/height includes padding and border; margins remain outside either sizing box.

Family/use case: Sizing constraints. Use preferred/intrinsic sizes with min/max bounds; verify long content, zoom and indefinite percentage bases.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `content-box | border-box`

Initial: content-box. Inherited: no. Applies to: all elements that accept width or height.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-box-sizing

### P154 box-snap

The `box-snap` setting belongs to specialized or draft module: css-line-grid-1; its grammar and applicability below define the box snap contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-line-grid-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | block-start | block-end | center | baseline | last-baseline`

Initial: none. Inherited: yes. Applies to: block-level boxes and internal table elements except table cells.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-line-grid-1/#propdef-box-snap

### P155 break-after

Request a fragmentation break after a box in the applicable page/column context; available break opportunities and competing constraints still matter.

Family/use case: Fragmentation. Use to improve print or multicol page breaks; impossible keep/break constraints remain subject to the formatter.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | avoid | always | all | avoid-page | page | left | right | recto | verso | avoid-column | column | avoid-region | region`

Initial: auto. Inherited: no. Applies to: block-level boxes, grid items, flex items, table row groups, table rows (but see prose).

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-break-4/#propdef-break-after

### P156 break-before

Request a fragmentation break before a box; page/column keywords are not interchangeable in every formatting context.

Family/use case: Fragmentation. Use to improve print or multicol page breaks; impossible keep/break constraints remain subject to the formatter.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | avoid | always | all | avoid-page | page | left | right | recto | verso | avoid-column | column | avoid-region | region`

Initial: auto. Inherited: no. Applies to: block-level boxes, grid items, flex items, table row groups, table rows (but see prose).

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-break-4/#propdef-break-before

### P157 break-inside

Control permitted fragmentation within a box; avoid is a constraint subject to content and available space, not an absolute no-split guarantee.

Family/use case: Fragmentation. Use to improve print or multicol page breaks; impossible keep/break constraints remain subject to the formatter.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | avoid | avoid-page | avoid-column | avoid-region`

Initial: auto. Inherited: no. Applies to: all elements except inline-level boxes, internal ruby boxes, table column boxes, table column group boxes, absolutely-positioned boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-break-4/#propdef-break-inside

### P158 caption-side

Choose where a table caption is placed in the table formatting model; retain an actual caption element.

Family/use case: Table formatting. Use for genuine tabular data with header associations and a plan for narrow viewports.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `top | bottom`

Initial: top. Inherited: yes. Applies to: table-caption boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-tables-3/#propdef-caption-side

### P159 caret

The `caret` setting belongs to editable caret presentation; its grammar and applicability below define the caret contract. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Family/use case: Editable caret presentation. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'caret-color'> || <'caret-animation'> || <'caret-shape'>`

Initial: auto. Inherited: yes. Applies to: text or elements that accept text input.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `caret-color`, `caret-animation`, `caret-shape`.

Source: https://drafts.csswg.org/css-ui-4/#propdef-caret

### P160 caret-animation

The `caret-animation` setting belongs to editable caret presentation; its grammar and applicability below define the caret animation contract. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Family/use case: Editable caret presentation. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | manual`

Initial: auto. Inherited: yes. Applies to: text or elements that accept text input.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-caret-animation

### P161 caret-color

Set the editable text insertion caret color; it should remain distinguishable from the input surface.

Family/use case: Editable caret presentation. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <color> [auto | <color>]?`

Initial: auto. Inherited: yes. Applies to: text or elements that accept text input.

Percentages: N/A. Computed value: The computed value for auto is auto. For <color> values, see CSS Color 4 § 15. Resolving <color> Values.. Animation: by computed value.

Source: https://drafts.csswg.org/css-ui-4/#propdef-caret-color

### P162 caret-shape

The `caret-shape` setting belongs to editable caret presentation; its grammar and applicability below define the caret shape contract. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Family/use case: Editable caret presentation. Use for editable controls with a visible insertion point; preserve native editing and sufficient contrast.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | bar | block | underscore`

Initial: auto. Inherited: yes. Applies to: text or elements that accept text input.

Percentages: N/A. Computed value: specified keyword. Animation: by computed value.

Source: https://drafts.csswg.org/css-ui-4/#propdef-caret-shape

### P163 clear

Move a box below relevant earlier floats under the float rules; it is not a Flexbox alignment property.

Family/use case: Specialized or draft module: css-page-floats-3. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `inline-start | inline-end | block-start | block-end | left | right | top | bottom | both-inline | both-block | both | none`

Initial: none. Inherited: no. Applies to: block-level elements, floats, regions, pages.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-page-floats-3/#propdef-clear

### P164 clip

Legacy rectangle clipping for applicable absolutely positioned elements; prefer clip-path for new geometry and evaluate interaction separately.

Family/use case: Specialized or draft module: css-masking-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<rect()> | auto`

Initial: auto. Inherited: no. Applies to: Absolutely positioned elements. In SVG, it applies to elements which establish a new viewport, pattern elements and mask elements..

Percentages: n/a. Computed value: as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-masking-1/#propdef-clip

### P165 clip-path

Clip painting to a geometric shape or referenced resource; clipping can affect hit testing but does not create semantic hiding or reserve space.

Family/use case: Specialized or draft module: css-masking-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<clip-source> | [ <basic-shape> || <geometry-box> ] | none`

Initial: none. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: as specified, but with <url> values made absolute. Animation: by computed value.

Source: https://drafts.csswg.org/css-masking-1/#propdef-clip-path

### P166 clip-rule

Choose the rule for determining inside/outside regions in applicable SVG clip geometry; it is distinct from fill-rule.

Family/use case: Specialized or draft module: css-masking-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `nonzero | evenodd`

Initial: nonzero. Inherited: yes. Applies to: Applies to SVG graphics elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-clip-rule

### P167 color

Set the foreground color and the currentColor reference for dependent paint; it normally inherits.

Family/use case: Color and compositing inputs. Use semantic foreground/surface tokens and verify actual composited contrast across themes and user color settings.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color>`

Initial: CanvasText. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: computed color, see resolving color values. Animation: by computed value type.

Source: https://drafts.csswg.org/css-color-4/#propdef-color

### P168 color-adjust

The `color-adjust` setting belongs to user-agent color adaptation; its grammar and applicability below define the color adjust contract. Use to cooperate with native color schemes, forced colors and printing rather than overriding user preferences blindly.

Family/use case: User-agent color adaptation. Use to cooperate with native color schemes, forced colors and printing rather than overriding user preferences blindly.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'print-color-adjust'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `print-color-adjust`.

Source: https://drafts.csswg.org/css-color-adjust-1/#propdef-color-adjust

### P169 color-interpolation

The `color-interpolation` setting belongs to svg geometry and rendering; its grammar and applicability below define the color interpolation contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | sRGB | linearRGB`

Initial: sRGB. Inherited: yes. Applies to: container elements, graphics elements, gradient elements, 'use' and 'animate'.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#ColorInterpolationProperty

### P170 color-interpolation-filters

The `color-interpolation-filters` setting belongs to svg geometry and rendering; its grammar and applicability below define the color interpolation filters contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | sRGB | linearRGB`

Initial: linearRGB. Inherited: yes. Applies to: All filter primitives.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/filter-effects-1/#propdef-color-interpolation-filters

### P171 color-scheme

Declare supported color schemes for native controls and related browser rendering; it does not author a complete dark theme.

Family/use case: User-agent color adaptation. Use to cooperate with native color schemes, forced colors and printing rather than overriding user preferences blindly.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | [ light | dark | <custom-ident> ]+ && only?`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: the keyword normal, or a color scheme support. Animation: discrete.

Source: https://drafts.csswg.org/css-color-adjust-1/#propdef-color-scheme

### P172 column-count

Choose an ideal number of columns in multicol layout; actual track sizing also depends on column-width and available space.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <integer [1,∞]>`

Initial: auto. Inherited: no. Applies to: block containers except table wrapper boxes.

Percentages: N/A. Computed value: specified value. Animation: by computed value.

Source: https://drafts.csswg.org/css-multicol-2/#propdef-column-count

### P173 column-fill

Choose balancing or sequential filling in the applicable multicol fragmentation context; constrained block size changes the visible result.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | balance | balance-all`

Initial: balance. Inherited: no. Applies to: multicol containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-multicol-2/#propdef-column-fill

### P174 column-gap

Set a column gutter in Grid, Flexbox or multicol as applicable; normal can resolve differently between layout modes.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <length-percentage [0,∞]> | <line-width>`

Initial: normal. Inherited: no. Applies to: multi-column containers, flex containers, grid containers, and grid lanes containers.

Percentages: see § 2.3 Percentages In gap Properties. Computed value: specified keyword, else a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-gap

### P175 column-height

The `column-height` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column height contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <length [0,∞]>`

Initial: auto. Inherited: no. Applies to: block containers except table wrapper boxes.

Percentages: N/A. Computed value: the keyword auto or an absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-multicol-2/#propdef-column-height

### P176 column-rule

Paint a rule between multicol columns through width/style/color; it does not create a separate gutter width.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<gap-rule-list> | <gap-auto-rule-list>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-width`, `column-rule-style`, `column-rule-color`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule

### P177 column-rule-break

The `column-rule-break` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule break contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | normal | intersection`

Initial: normal. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-break

### P178 column-rule-color

The `column-rule-color` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule color contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-color-list> | <auto-line-color-list>`

Initial: currentcolor. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: repeatable list, see § 4.7 Interpolation of list values..

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-color

### P179 column-rule-inset

The `column-rule-inset` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset-cap'> [ / <'column-rule-inset-junction'> ]?`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap, column-rule-inset-junction, row-rule-inset-cap, and row-rule-inset-junction.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-cap-start`, `column-rule-inset-cap-end`, `column-rule-inset-junction-start`, `column-rule-inset-junction-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset

### P180 column-rule-inset-cap

The `column-rule-inset-cap` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset cap contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value> <inset-value>?`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-cap-end, column-rule-inset-junction-start, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-cap-end, row-rule-inset-junction-start, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-cap-start`, `column-rule-inset-cap-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-cap

### P181 column-rule-inset-cap-end

The `column-rule-inset-cap-end` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset cap end contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-cap-end

### P182 column-rule-inset-cap-start

The `column-rule-inset-cap-start` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset cap start contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-cap-start

### P183 column-rule-inset-end

The `column-rule-inset-end` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset end contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-junction-start, column-rule-inset-cap-end, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-junction-start, row-rule-inset-cap-end, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-cap-end`, `column-rule-inset-junction-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-end

### P184 column-rule-inset-junction

The `column-rule-inset-junction` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset junction contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value> <inset-value>?`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-cap-end, column-rule-inset-junction-start, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-cap-end, row-rule-inset-junction-start, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-junction-start`, `column-rule-inset-junction-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-junction

### P185 column-rule-inset-junction-end

The `column-rule-inset-junction-end` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset junction end contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-junction-end

### P186 column-rule-inset-junction-start

The `column-rule-inset-junction-start` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset junction start contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-junction-start

### P187 column-rule-inset-start

The `column-rule-inset-start` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule inset start contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-junction-start, column-rule-inset-cap-end, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-junction-start, row-rule-inset-cap-end, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-cap-start`, `column-rule-inset-junction-start`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-inset-start

### P188 column-rule-style

The `column-rule-style` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule style contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-style-list> | <auto-line-style-list>`

Initial: none. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-style

### P189 column-rule-visibility-items

The `column-rule-visibility-items` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule visibility items contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `all | around | between | normal`

Initial: normal. Inherited: no. Applies to: grid containers and multicol containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-visibility-items

### P190 column-rule-width

The `column-rule-width` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column rule width contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width-list> | <auto-line-width-list>`

Initial: medium. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: list of absolute lengths, snapped as a border width. Animation: repeatable list, see § 4.7 Interpolation of list values..

Source: https://drafts.csswg.org/css-gaps-1/#propdef-column-rule-width

### P191 column-span

Allow applicable content to span the multicol column set; spanning can split balancing contexts.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <integer [1,∞]> | all | auto`

Initial: none. Inherited: no. Applies to: in-flow block-level elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-multicol-2/#propdef-column-span

### P192 column-width

Set an ideal column width for multicol layout; it is not a rigid width assigned independently to every column. The base multicol grammar is auto or a nonnegative length. The consolidated sizing draft adds box-size alternatives; that extension is marked at risk and likely to be dropped. Do not treat the broader draft grammar as an interoperable baseline.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <box-size> | auto | <box-size>`

Initial: auto. Inherited: no. Applies to: block containers except table wrapper boxes.

Percentages: N/A in the base multicol grammar; draft box-size extensions require the sizing-module rules. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-sizing-4/.

Source: https://drafts.csswg.org/css-sizing-3/#column-sizing

Metadata supplement: https://drafts.csswg.org/css-multicol-2/#propdef-column-width

### P193 column-wrap

The `column-wrap` setting belongs to multicolumn and gap decoration; its grammar and applicability below define the column wrap contract. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Family/use case: Multicolumn and gap decoration. Use for newspaper-like text fragmentation or supported gap rules; ordinary responsive application columns are usually Grid/Flexbox.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | nowrap | wrap`

Initial: auto. Inherited: no. Applies to: multicol containers.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-multicol-2/#propdef-column-wrap

### P194 columns

Combine ideal column width and column count; omitted components reset to their initial values.

Family/use case: Specialized or draft module: css-multicol-2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <'column-width'> || <'column-count'> ] [ / <'column-height'> ]?`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-width`, `column-count`, `column-height`.

Source: https://drafts.csswg.org/css-multicol-2/#propdef-columns

### P195 contain

Limit selected layout/style/paint/size effects to enable isolation and optimization; each containment type has concrete sizing/painting consequences.

Family/use case: Containment. Use only after measuring the rendering cost and verifying the sizing/paint isolation consequences.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | strict | content | [ [size | inline-size] || layout || style || paint ]`

Initial: none. Inherited: no. Applies to: See below.

Percentages: n/a. Computed value: the keyword none or one or more of size, layout, style, paint. Animation: not animatable.

Source: https://drafts.csswg.org/css-contain-2/#propdef-contain

### P196 contain-intrinsic-block-size

The `contain-intrinsic-block-size` setting belongs to containment and placeholder sizing; its grammar and applicability below define the contain intrinsic block size contract. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Family/use case: Containment and placeholder sizing. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto? [ none | <length [0,∞]> ]`

Initial: none. Inherited: no. Applies to: elements with size containment.

Percentages: n/a. Computed value: as specified, with <length> values computed. Animation: by computed value type.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-contain-intrinsic-block-size

### P197 contain-intrinsic-height

The `contain-intrinsic-height` setting belongs to containment and placeholder sizing; its grammar and applicability below define the contain intrinsic height contract. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Family/use case: Containment and placeholder sizing. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto? [ none | <length [0,∞]> ]`

Initial: none. Inherited: no. Applies to: elements with size containment.

Percentages: n/a. Computed value: as specified, with <length> values computed. Animation: by computed value type.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-contain-intrinsic-height

### P198 contain-intrinsic-inline-size

The `contain-intrinsic-inline-size` setting belongs to containment and placeholder sizing; its grammar and applicability below define the contain intrinsic inline size contract. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Family/use case: Containment and placeholder sizing. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto? [ none | <length [0,∞]> ]`

Initial: none. Inherited: no. Applies to: elements with size containment.

Percentages: n/a. Computed value: as specified, with <length> values computed. Animation: by computed value type.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-contain-intrinsic-inline-size

### P199 contain-intrinsic-size

Supply placeholder intrinsic dimensions under size containment or skipped rendering; choose estimates that limit scroll jumps.

Family/use case: Containment and placeholder sizing. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ auto? [ none | <length [0,∞]> ] ]{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `contain-intrinsic-width`, `contain-intrinsic-height`.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-contain-intrinsic-size

### P200 contain-intrinsic-width

The `contain-intrinsic-width` setting belongs to containment and placeholder sizing; its grammar and applicability below define the contain intrinsic width contract. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Family/use case: Containment and placeholder sizing. Use a defensible placeholder size for content whose rendering is skipped; test scroll stability and navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto? [ none | <length [0,∞]> ]`

Initial: none. Inherited: no. Applies to: elements with size containment.

Percentages: n/a. Computed value: as specified, with <length> values computed. Animation: by computed value type.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-contain-intrinsic-width

### P201 container

Combine query-container naming and type; the query relationship still targets a suitable ancestor, not an unrestricted self-size feedback loop.

Family/use case: Specialized or draft module: css-conditional-5. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'container-name'> [ / <'container-type'> ]?`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `container-name`, `container-type`.

Source: https://drafts.csswg.org/css-conditional-5/#propdef-container

### P202 container-name

Name query containers so nested component queries select the intended ancestor.

Family/use case: Specialized or draft module: css-conditional-5. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <custom-ident>+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none, or an ordered list of identifiers. Animation: not animatable.

Source: https://drafts.csswg.org/css-conditional-5/#propdef-container-name

### P203 container-type

Establish supported size/style/scroll-state query capabilities and their associated containment effects; do not add it globally without sizing analysis.

Family/use case: Specialized or draft module: css-conditional-5. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | [ [ size | inline-size ] || scroll-state ]`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: not animatable.

Source: https://drafts.csswg.org/css-conditional-5/#propdef-container-type

### P204 content

Generate pseudo-element content or participate in other specialized generated-content contexts; essential instructions belong in semantic DOM text.

Family/use case: Specialized or draft module: css-content-3. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | none | [ <content-replacement> | <content-list> ] [/ <alt-text> ]? | <element()>`

Initial: normal. Inherited: no. Applies to: all elements, tree-abiding pseudo-elements, and page margin boxes.

Percentages: n/a. Computed value: See prose below. Animation: discrete.

Grammar extensions: https://drafts.csswg.org/css-gcpm-3/.

Source: https://drafts.csswg.org/css-content-3/#propdef-content

### P205 content-visibility

Permit rendering work to be skipped for offscreen/hidden content under containment rules; verify navigation, search and intrinsic placeholders.

Family/use case: Containment. Use only after measuring the rendering cost and verifying the sizing/paint isolation consequences.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `visible | auto | hidden`

Initial: visible. Inherited: no. Applies to: elements for which size containment can apply.

Percentages: n/a. Computed value: as specified. Animation: see § 4.1 Animating and Interpolating content-visibility.

Source: https://drafts.csswg.org/css-contain-2/#propdef-content-visibility

### P206 continue

The `continue` setting belongs to overflow and scrolling; its grammar and applicability below define the continue contract. Use for a deliberate scroll region or truncation boundary; keep focused content and essential text reachable.

Family/use case: Overflow and scrolling. Use for a deliberate scroll region or truncation boundary; keep focused content and essential text reachable.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | discard | collapse | -webkit-legacy | overflow | paginate | fragments`

Initial: normal. Inherited: no. Applies to: block containers and multicol containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Grammar extensions: https://drafts.csswg.org/css-overflow-5/.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-continue

### P207 copy-into

The `copy-into` setting belongs to specialized or draft module: css-gcpm-4; its grammar and applicability below define the copy into contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-gcpm-4. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ [ <custom-ident> <content-level>] [, <custom-ident> <content-level>]* ]?`

Initial: none. Inherited: no. Applies to: all elements and pseudo-elements, but not ::first-line or ::first-letter..

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gcpm-4/#propdef-copy-into

### P208 corner

The `corner` setting belongs to draft corner geometry; its grammar and applicability below define the corner contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-radius'> || <'corner-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-radius`, `corner-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner

### P209 corner-block-end

The `corner-block-end` setting belongs to draft corner geometry; its grammar and applicability below define the corner block end contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-end-radius`, `corner-block-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-block-end

### P210 corner-block-end-shape

The `corner-block-end-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner block end shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-end-start-shape`, `corner-end-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-block-end-shape

### P211 corner-block-start

The `corner-block-start` setting belongs to draft corner geometry; its grammar and applicability below define the corner block start contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-block-start-radius`, `corner-block-start-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-block-start

### P212 corner-block-start-shape

The `corner-block-start-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner block start shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-start-start-shape`, `corner-start-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-block-start-shape

### P213 corner-bottom

The `corner-bottom` setting belongs to draft corner geometry; its grammar and applicability below define the corner bottom contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-bottom-radius`, `corner-bottom-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-bottom

### P214 corner-bottom-left

The `corner-bottom-left` setting belongs to draft corner geometry; its grammar and applicability below define the corner bottom left contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-bottom-left-radius`, `corner-bottom-left-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-bottom-left

### P215 corner-bottom-left-shape

The `corner-bottom-left-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner bottom left shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-bottom-left-shape

### P216 corner-bottom-right

The `corner-bottom-right` setting belongs to draft corner geometry; its grammar and applicability below define the corner bottom right contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-bottom-right-radius`, `corner-bottom-right-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-bottom-right

### P217 corner-bottom-right-shape

The `corner-bottom-right-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner bottom right shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-bottom-right-shape

### P218 corner-bottom-shape

The `corner-bottom-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner bottom shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-bottom-left-shape`, `corner-bottom-right-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-bottom-shape

### P219 corner-end-end

The `corner-end-end` setting belongs to draft corner geometry; its grammar and applicability below define the corner end end contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-end-end-radius`, `corner-end-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-end-end

### P220 corner-end-end-shape

The `corner-end-end-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner end end shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-end-end-shape

### P221 corner-end-start

The `corner-end-start` setting belongs to draft corner geometry; its grammar and applicability below define the corner end start contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-end-start-radius`, `corner-end-start-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-end-start

### P222 corner-end-start-shape

The `corner-end-start-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner end start shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-end-start-shape

### P223 corner-inline-end

The `corner-inline-end` setting belongs to draft corner geometry; its grammar and applicability below define the corner inline end contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-end-radius`, `corner-inline-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-inline-end

### P224 corner-inline-end-shape

The `corner-inline-end-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner inline end shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-start-end-shape`, `corner-end-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-inline-end-shape

### P225 corner-inline-start

The `corner-inline-start` setting belongs to draft corner geometry; its grammar and applicability below define the corner inline start contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-inline-start-radius`, `corner-inline-start-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-inline-start

### P226 corner-inline-start-shape

The `corner-inline-start-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner inline start shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-start-start-shape`, `corner-end-start-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-inline-start-shape

### P227 corner-left

The `corner-left` setting belongs to draft corner geometry; its grammar and applicability below define the corner left contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-left-radius`, `corner-left-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-left

### P228 corner-left-shape

The `corner-left-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner left shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-top-left-shape`, `corner-bottom-left-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-left-shape

### P229 corner-right

The `corner-right` setting belongs to draft corner geometry; its grammar and applicability below define the corner right contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-right-radius`, `corner-right-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-right

### P230 corner-right-shape

The `corner-right-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner right shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-top-right-shape`, `corner-bottom-right-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-right-shape

### P231 corner-shape

The `corner-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,4}`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-top-left-shape`, `corner-top-right-shape`, `corner-bottom-right-shape`, `corner-bottom-left-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-shape

### P232 corner-start-end

The `corner-start-end` setting belongs to draft corner geometry; its grammar and applicability below define the corner start end contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-start-end-radius`, `corner-start-end-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-start-end

### P233 corner-start-end-shape

The `corner-start-end-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner start end shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-start-end-shape

### P234 corner-start-start

The `corner-start-start` setting belongs to draft corner geometry; its grammar and applicability below define the corner start start contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-start-start-radius`, `corner-start-start-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-start-start

### P235 corner-start-start-shape

The `corner-start-start-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner start start shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-start-start-shape

### P236 corner-top

The `corner-top` setting belongs to draft corner geometry; its grammar and applicability below define the corner top contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-radius'> || <'corner-top-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-radius`, `corner-top-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-top

### P237 corner-top-left

The `corner-top-left` setting belongs to draft corner geometry; its grammar and applicability below define the corner top left contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-left-radius`, `corner-top-left-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-top-left

### P238 corner-top-left-shape

The `corner-top-left-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner top left shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-top-left-shape

### P239 corner-top-right

The `corner-top-right` setting belongs to draft corner geometry; its grammar and applicability below define the corner top right contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'border-top-left-radius'> || <'corner-top-left-shape'>`

Initial: 0. Inherited: no. Applies to: all elements (but see prose).

Percentages: Refer to corresponding dimension of the border box.. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `border-top-right-radius`, `corner-top-right-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-top-right

### P240 corner-top-right-shape

The `corner-top-right-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner top right shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<corner-shape-value>`

Initial: round. Inherited: no. Applies to: all elements where border-radius can apply.

Percentages: n/a. Computed value: the corresponding superellipse() value. Animation: see superellipse interpolation.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-top-right-shape

### P241 corner-top-shape

The `corner-top-shape` setting belongs to draft corner geometry; its grammar and applicability below define the corner top shape contract. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Family/use case: Draft corner geometry. Research reference for newer corner-shape proposals; use an ordinary border-radius fallback until the required implementation is verified.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'corner-top-left-shape'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `corner-top-left-shape`, `corner-top-right-shape`.

Source: https://drafts.csswg.org/css-borders-4/#propdef-corner-top-shape

### P242 counter-increment

Increment named counters in the applicable generated-content scope; this is presentation state, not a persistent application record.

Family/use case: Counters and lists. Use to present an actual ordered/unordered structure without replacing semantic list markup.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <counter-name> <integer>? ]+ | none`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none or a list, each item an identifier paired with an integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-lists-3/#propdef-counter-increment

### P243 counter-reset

Instantiate/reset counters under CSS counter scoping rules; it is not equivalent to assigning a JavaScript variable.

Family/use case: Counters and lists. Use to present an actual ordered/unordered structure without replacing semantic list markup.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <counter-name> <integer>? | <reversed-counter-name> <integer>? ]+ | none`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none or a list, each item an identifier or a reversed() function paired with an integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-lists-3/#propdef-counter-reset

### P244 counter-set

Set the value of an existing applicable counter or create one under its rules; distinguish it from reset's scope behavior.

Family/use case: Counters and lists. Use to present an actual ordered/unordered structure without replacing semantic list markup.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <counter-name> <integer>? ]+ | none`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none or a list, each item an identifier paired with an integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-lists-3/#propdef-counter-set

### P245 cue

The `cue` setting belongs to speech cues; its grammar and applicability below define the cue contract. Specialized aural cue reference for a supporting speech renderer; do not assume ordinary browsers or assistive technologies honor it.

Family/use case: Speech cues. Specialized aural cue reference for a supporting speech renderer; do not assume ordinary browsers or assistive technologies honor it.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'cue-before'> <'cue-after'>?`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `cue-before`, `cue-after`.

Source: https://drafts.csswg.org/css-speech-1/#propdef-cue

### P246 cue-after

The `cue-after` setting belongs to speech cues; its grammar and applicability below define the cue after contract. Specialized aural cue reference for a supporting speech renderer; do not assume ordinary browsers or assistive technologies honor it.

Family/use case: Speech cues. Specialized aural cue reference for a supporting speech renderer; do not assume ordinary browsers or assistive technologies honor it.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<url> <decibel>? | none`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-cue-after

### P247 cue-before

The `cue-before` setting belongs to speech cues; its grammar and applicability below define the cue before contract. Specialized aural cue reference for a supporting speech renderer; do not assume ordinary browsers or assistive technologies honor it.

Family/use case: Speech cues. Specialized aural cue reference for a supporting speech renderer; do not assume ordinary browsers or assistive technologies honor it.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<url> <decibel>? | none`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-cue-before

### P248 cursor

Select a pointer cursor or image fallback; a pointer shape does not supply button semantics or keyboard behavior.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[<cursor-image>,]* <cursor-predefined>`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: as specified, except with any relative URLs converted to absolute. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-cursor

### P249 cx

The `cx` setting belongs to svg geometry and rendering; its grammar and applicability below define the cx contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: 'circle' and 'ellipse' elements.

Percentages: refer to the width of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#CxProperty

### P250 cy

The `cy` setting belongs to svg geometry and rendering; its grammar and applicability below define the cy contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: 'circle' and 'ellipse' elements.

Percentages: refer to the height of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#CyProperty

### P251 d

The `d` setting belongs to svg geometry and rendering; its grammar and applicability below define the d contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <string>`

Initial: none. Inherited: no. Applies to: 'path'.

Percentages: N/A. Computed value: as specified. Animation: See prose.

Source: https://w3c.github.io/svgwg/svg2-draft/paths.html#DProperty

### P252 direction

Set base inline direction for formatting; prefer HTML dir for semantic document direction and use unicode-bidi only with a defined need.

Family/use case: Writing modes and direction. Use for actual vertical or bidirectional content with appropriate HTML language/direction and logical geometry.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `ltr | rtl`

Initial: ltr. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: specified value. Animation: not animatable.

Source: https://drafts.csswg.org/css-writing-modes-4/#propdef-direction

### P253 display

Choose outer participation and inner layout, or suppress boxes; the initial inline value differs from browser HTML defaults for many tags.

Family/use case: Formatting contexts. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <display-outside> || <display-inside> ] | <display-listitem> | <display-internal> | <display-box> | <display-legacy> | grid-lanes | inline-grid-lanes | <display-outside> || [ <display-inside> | math ]`

Initial: inline. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: a pair of keywords representing the inner and outer display types plus optional list-item flag, or a <display-internal> or <display-box> keyword; see prose in a variety of specs for computation rules. Animation: see § 2.9 Animating and Interpolating display.

Grammar extensions: https://drafts.csswg.org/css-grid-3/, https://w3c.github.io/mathml-core/.

Source: https://drafts.csswg.org/css-display-4/#propdef-display

### P254 dominant-baseline

The `dominant-baseline` setting belongs to svg geometry and rendering; its grammar and applicability below define the dominant baseline contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <baseline-metric>`

Initial: auto. Inherited: yes. Applies to: block containers, inline boxes, table rows, grid containers, flex containers, and SVG text content elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-dominant-baseline

### P255 dynamic-range-limit

The `dynamic-range-limit` setting belongs to specialized or draft module: css-color-hdr-1; its grammar and applicability below define the dynamic range limit contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-color-hdr-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `standard | no-limit | constrained | <dynamic-range-limit-mix()>`

Initial: no-limit. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: see Computed Value for dynamic-range-limit. Animation: by dynamic-range-limit-mix().

Source: https://drafts.csswg.org/css-color-hdr-1/#propdef-dynamic-range-limit

### P256 empty-cells

Control painting of empty table cells in the separate-border model; it does not remove the cell's semantic data position.

Family/use case: Table formatting. Use for genuine tabular data with header associations and a plan for narrow viewports.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `show | hide`

Initial: show. Inherited: yes. Applies to: table-cell boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-tables-3/#propdef-empty-cells

### P257 event-trigger

The `event-trigger` setting belongs to draft event-triggered animation; its grammar and applicability below define the event trigger contract. Research reference; verify the exact event/timeline model and avoid coupling essential state to a draft animation mechanism.

Family/use case: Draft event-triggered animation. Research reference; verify the exact event/timeline model and avoid coupling essential state to a draft animation mechanism.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <'event-trigger-name'> <'event-trigger-source'> ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-event-trigger

### P258 event-trigger-name

The `event-trigger-name` setting belongs to draft event-triggered animation; its grammar and applicability below define the event trigger name contract. Research reference; verify the exact event/timeline model and avoid coupling essential state to a draft animation mechanism.

Family/use case: Draft event-triggered animation. Research reference; verify the exact event/timeline model and avoid coupling essential state to a draft animation mechanism.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <dashed-ident>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-event-trigger-name

### P259 event-trigger-source

The `event-trigger-source` setting belongs to draft event-triggered animation; its grammar and applicability below define the event trigger source contract. Research reference; verify the exact event/timeline model and avoid coupling essential state to a draft animation mechanism.

Family/use case: Draft event-triggered animation. Research reference; verify the exact event/timeline model and avoid coupling essential state to a draft animation mechanism.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | <event-function>+ [ / <event-function>+ ]? ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-event-trigger-source

### P260 field-sizing

The `field-sizing` setting belongs to sizing; its grammar and applicability below define the field sizing contract. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `fixed | content`

Initial: fixed. Inherited: no. Applies to: elements with default preferred size.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-forms-1/#propdef-field-sizing

### P261 fill

The `fill` setting belongs to svg paint; its grammar and applicability below define the fill contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<paint>`

Initial: black. Inherited: yes. Applies to: shapes and text content elements.

Percentages: N/A. Computed value: as specified, but with <color> values computed and <url> values made absolute. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#FillProperty

### P262 fill-break

The `fill-break` setting belongs to svg paint; its grammar and applicability below define the fill break contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `bounding-box | slice | clone`

Initial: bounding-box. Inherited: yes?. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-break

### P263 fill-color

The `fill-color` setting belongs to svg paint; its grammar and applicability below define the fill color contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color>`

Initial: currentcolor. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: the computed color. Animation: by computed value.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-color

### P264 fill-image

The `fill-image` setting belongs to svg paint; its grammar and applicability below define the fill image contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<paint>#`

Initial: none. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: as specified, with any <image> computed. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-image

### P265 fill-opacity

The `fill-opacity` setting belongs to svg paint; its grammar and applicability below define the fill opacity contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'opacity'>`

Initial: 1. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: the specified value converted to a <number>, clamped to the range [0,1]. Animation: by computed value.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-opacity

### P266 fill-origin

The `fill-origin` setting belongs to svg paint; its grammar and applicability below define the fill origin contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `match-parent | fill-box | stroke-box | content-box | padding-box | border-box`

Initial: match-parent. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-origin

### P267 fill-position

The `fill-position` setting belongs to svg paint; its grammar and applicability below define the fill position contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<position>#`

Initial: 0% 0%. Inherited: yes. Applies to: text and SVG shapes.

Percentages: n/a. Computed value: A list, each item consisting of: a pair of offsets (horizontal and vertical) from the top left origin each given as a combination of an absolute length and a percentage. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-position

### P268 fill-repeat

The `fill-repeat` setting belongs to svg paint; its grammar and applicability below define the fill repeat contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<repeat-style>#`

Initial: repeat. Inherited: yes. Applies to: text and SVG shapes.

Percentages: n/a. Computed value: A list, each item consisting of: two keywords, one per dimension. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-repeat

### P269 fill-rule

The `fill-rule` setting belongs to svg paint; its grammar and applicability below define the fill rule contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `nonzero | evenodd`

Initial: nonzero. Inherited: yes. Applies to: SVG shapes.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-rule

### P270 fill-size

The `fill-size` setting belongs to svg paint; its grammar and applicability below define the fill size contract. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Family/use case: SVG paint. Use on an applicable SVG shape/text paint target; the meaning is not an HTML box background.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<bg-size>#`

Initial: auto. Inherited: yes. Applies to: text and SVG shapes.

Percentages: n/a. Computed value: as specified, but with lengths made absolute and omitted auto keywords filled in. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-fill-size

### P271 filter

Apply a filter list to the element's rendering; blur/drop-shadow/color effects can create stacking and performance consequences.

Family/use case: Specialized or draft module: filter-effects-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <filter-value-list>`

Initial: none. Inherited: no. Applies to: All elements. In SVG, it applies to container elements without the defs element, all graphics elements and the use element..

Percentages: n/a. Computed value: as specified. Animation: See prose in Animation of Filters..

Source: https://drafts.csswg.org/filter-effects-1/#propdef-filter

### P272 fit-tolerance

The `fit-tolerance` setting belongs to specialized or draft module: css-grid-3; its grammar and applicability below define the fit tolerance contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-grid-3. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <length-percentage [0,∞]> | infinite`

Initial: normal. Inherited: no. Applies to: grid lanes containers.

Percentages: relative to the grid-axis content box size of the grid lanes container. Computed value: a computed <length-percentage> value. Animation: as length.

Source: https://drafts.csswg.org/css-grid-3/#propdef-fit-tolerance

### P273 flex

Combine grow, shrink and basis inputs for flex sizing; its values are not direct percentages of the container width.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ <'flex-grow'> <'flex-shrink'>? || <'flex-basis'> ]`

Initial: 0 1 auto. Inherited: no. Applies to: flex items.

Percentages: see individual properties. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `flex-grow`, `flex-shrink`, `flex-basis`.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex

### P274 flex-basis

Set the flex base size input before free-space distribution; auto and content-dependent sizing differ from an explicit zero basis.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `content | <'width'>`

Initial: auto. Inherited: no. Applies to: flex items.

Percentages: relative to the flex container's inner main size. Computed value: specified keyword or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-basis

### P275 flex-direction

Choose the main axis and direction; reverse values change visual arrangement without repairing DOM reading order.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `row | row-reverse | column | column-reverse`

Initial: row. Inherited: no. Applies to: flex containers.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-direction

### P276 flex-flow

Combine direction and wrapping; it does not configure alignment or item growth.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'flex-direction'> || <'flex-wrap'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `flex-direction`, `flex-wrap`.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-flow

### P277 flex-grow

Set the factor for distributing positive free space among eligible flex items after constraints are considered.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<number [0,∞]>`

Initial: 0. Inherited: no. Applies to: flex items.

Percentages: n/a. Computed value: specified number. Animation: by computed value type.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-grow

### P278 flex-line-count

The `flex-line-count` setting belongs to flex layout; its grammar and applicability below define the flex line count contract. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<integer [1,∞]>`

Initial: 1. Inherited: no. Applies to: multi-line flex containers.

Percentages: n/a. Computed value: the specified integer, computed. Animation: as integer.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-line-count

### P279 flex-shrink

Set the shrink factor weighted by the flex base size; equal factors do not guarantee equal pixel reductions.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<number [0,∞]>`

Initial: 1. Inherited: no. Applies to: flex items.

Percentages: n/a. Computed value: specified value. Animation: number.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-shrink

### P280 flex-wrap

Allow flex items to form multiple lines or reverse cross-axis stacking; each line distributes its own main-axis free space.

Family/use case: Flex layout. Use for a one-dimensional action group or row/column; inspect main-axis sizing and cross-axis alignment separately.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `nowrap | [ wrap | wrap-reverse ] || balance`

Initial: nowrap. Inherited: no. Applies to: flex containers.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-flexbox-2/#propdef-flex-wrap

### P281 float

Place a box to a side for surrounding inline flow, such as text around an image; it is not the primary tool for application page layout.

Family/use case: Floats and page floats. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `block-start | block-end | inline-start | inline-end | snap-block | <snap-block()> | snap-inline | <snap-inline()> | left | right | top | bottom | none | footnote`

Initial: none. Inherited: no. Applies to: all elements..

Percentages: N/A. Computed value: as specified. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-gcpm-3/.

Source: https://drafts.csswg.org/css-page-floats-3/#propdef-float

### P282 float-defer

The `float-defer` setting belongs to floats and page floats; its grammar and applicability below define the float defer contract. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Family/use case: Floats and page floats. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<integer> | last | none`

Initial: none. Inherited: no. Applies to: floats.

Percentages: N/A. Computed value: specified keyword or integer. Animation: discrete.

Source: https://drafts.csswg.org/css-page-floats-3/#propdef-float-defer

### P283 float-offset

The `float-offset` setting belongs to floats and page floats; its grammar and applicability below define the float offset contract. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Family/use case: Floats and page floats. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: floats.

Percentages: see prose. Computed value: computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-page-floats-3/#propdef-float-offset

### P284 float-reference

The `float-reference` setting belongs to floats and page floats; its grammar and applicability below define the float reference contract. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Family/use case: Floats and page floats. Use for text exclusion or specialized paged-media floats; newer page-float controls are not ordinary browser application layout defaults.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `inline | column | region | page`

Initial: inline. Inherited: no. Applies to: all elements..

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-page-floats-3/#propdef-float-reference

### P285 flood-color

The `flood-color` setting belongs to svg geometry and rendering; its grammar and applicability below define the flood color contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color>`

Initial: black. Inherited: no. Applies to: feFlood and feDropShadow elements.

Percentages: n/a. Computed value: as specified. Animation: by computed value.

Source: https://drafts.csswg.org/filter-effects-1/#propdef-flood-color

### P286 flood-opacity

The `flood-opacity` setting belongs to svg geometry and rendering; its grammar and applicability below define the flood opacity contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'opacity'>`

Initial: 1. Inherited: no. Applies to: feFlood and feDropShadow elements.

Percentages: n/a. Computed value: the specified value converted to a number, clamped to the range [0,1]. Animation: by computed value.

Source: https://drafts.csswg.org/filter-effects-1/#propdef-flood-opacity

### P287 flow-from

The `flow-from` setting belongs to named flows/regions; its grammar and applicability below define the flow from contract. Research or specialized formatter reference; maintain normal-flow content for environments without the region model.

Family/use case: Named flows/regions. Research or specialized formatter reference; maintain normal-flow content for environments without the region model.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<custom-ident> | none`

Initial: none. Inherited: no. Applies to: Non-replaced block containers. This might be expanded in future versions of the specification to allow other types of containers to receive flow content..

Percentages: n/a. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-regions-1/#propdef-flow-from

### P288 flow-into

The `flow-into` setting belongs to named flows/regions; its grammar and applicability below define the flow into contract. Research or specialized formatter reference; maintain normal-flow content for environments without the region model.

Family/use case: Named flows/regions. Research or specialized formatter reference; maintain normal-flow content for environments without the region model.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <custom-ident> [element | content]?`

Initial: none. Inherited: no. Applies to: All elements, but not pseudo-elements such as ::first-line, ::first-letter, ::before or ::after..

Percentages: n/a. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-regions-1/#propdef-flow-into

### P289 font

Set coordinated font settings and line-height through a shorthand; omitted/reset-only settings can lose earlier typography choices.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ [ <'font-style'> || <font-variant-css2> || <'font-weight'> || <font-width-css3> ]? <'font-size'> [ / <'line-height'> ]? <'font-family'># ] | <system-font-family-name>`

Initial: see individual properties. Inherited: yes. Applies to: all elements and text.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `font-style`, `font-variant`, `font-weight`, `font-stretch`, `font-size`, `line-height`, `font-family`.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font

### P290 font-family

Choose an ordered font fallback list ending with an appropriate generic family; loading and glyph coverage affect the actual font used.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <font-family-name> | <generic-font-family> ]#`

Initial: depends on user agent. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: list, each item a string and/or <generic-font-family> keywords. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-family

### P291 font-feature-settings

Enable low-level OpenType feature tags; prefer semantic font-variant properties when they express the requirement.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <feature-tag-value>#`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-feature-settings

### P292 font-kerning

Control font kerning behavior where the font and renderer support it.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | normal | none`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-kerning

### P293 font-language-override

Request language-system behavior in a font independently of the document language; do not use it to replace correct lang metadata.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <string>`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: specified string or the keyword none. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-language-override

### P294 font-optical-sizing

Allow an appropriate variable font to adjust optical design for the rendered size.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | none`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-optical-sizing

### P295 font-palette

Select a palette for supporting color fonts; it is not a general page color palette.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | light | dark | <palette-identifier> | <palette-mix()>`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: N/a. Computed value: specified keyword, identifier or <palette-mix()> function. <palette-mix()> must be simplified to a single keyword or identifier if resulting palette is equivalent.. Animation: by computed value.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-palette

### P296 font-size

Set the font's requested size with inherited and relative-unit effects; keep user text scaling and reflow usable.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<absolute-size> | <relative-size> | <length-percentage [0,∞]> | math`

Initial: medium. Inherited: yes. Applies to: all elements and text.

Percentages: refer to parent element's font size. Computed value: an absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-size

### P297 font-size-adjust

Adjust fallback font sizing using supported metric ratios to reduce perceived size changes across fonts.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ ex-height | cap-height | ch-width | ic-width | ic-height ]? [ from-font | <number [0,∞]> ]`

Initial: none. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: the keyword none, or a pair of a metric keyword and a <number>. Animation: discrete if the keywords differ, otherwise by computed value type.

Source: https://drafts.csswg.org/css-fonts-5/#propdef-font-size-adjust

### P298 font-stretch

Legacy naming/alias relationship for font width selection in newer font specifications; do not confuse it with a geometric transform.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <percentage [0,∞]> | ultra-condensed | extra-condensed | condensed | semi-condensed | semi-expanded | expanded | extra-expanded | ultra-expanded`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: Not resolved. Computed value: a percentage, see below. Animation: by computed value type.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-stretch

Metadata supplement: https://drafts.csswg.org/css-fonts-4/#propdef-font-width

### P299 font-style

Choose normal, italic or oblique font styling with supported angle ranges; synthesized slant differs from a true italic design.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | italic | left | right | oblique <angle [-90deg,90deg]>?`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: the keyword specified, plus angle in degrees if specified. Animation: by computed value type; normal animates as oblique 0deg.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-style

### P300 font-synthesis

Control permitted synthesis of unavailable font styles; disable only when fallback behavior remains readable and appropriate.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ weight || style || small-caps || position]`

Initial: weight style small-caps position. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Shorthand members: `font-synthesis-weight`, `font-synthesis-style`, `font-synthesis-small-caps`.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-synthesis

### P301 font-synthesis-position

Control synthesis of the named missing font feature. Prefer an available real font face and test fallback readability rather than assuming synthesized glyphs match the design.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | none`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-synthesis-position

### P302 font-synthesis-small-caps

Control synthesis of the named missing font feature. Prefer an available real font face and test fallback readability rather than assuming synthesized glyphs match the design.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | none`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-synthesis-small-caps

### P303 font-synthesis-style

Control synthesis of the named missing font feature. Prefer an available real font face and test fallback readability rather than assuming synthesized glyphs match the design.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | none | oblique-only`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-synthesis-style

### P304 font-synthesis-weight

Control synthesis of the named missing font feature. Prefer an available real font face and test fallback readability rather than assuming synthesized glyphs match the design.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | none`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-synthesis-weight

### P305 font-variant

Combine high-level typographic variant requests; omitted members reset, and font support determines visible glyph changes.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | none | [ [ <common-lig-values> || <discretionary-lig-values> || <historical-lig-values> || <contextual-alt-values> ] || [ small-caps | all-small-caps | petite-caps | all-petite-caps | unicase | titling-caps ] || [ stylistic(<font-feature-value-name>) || historical-forms || styleset(<font-feature-value-name>#) || character-variant(<font-feature-value-name>#) || swash(<font-feature-value-name>) || ornaments(<font-feature-value-name>) || annotation(<font-feature-value-name>) ] || [ <numeric-figure-values> || <numeric-spacing-values> || <numeric-fraction-values> || ordinal || slashed-zero ] || [ <east-asian-variant-values> || <east-asian-width-values> || ruby ] || [ sub | super ] || [ text | emoji | unicode ] ]`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Shorthand members: `font-variant-ligatures`, `font-variant-caps`, `font-variant-alternates`, `font-variant-numeric`, `font-variant-east-asian`, `font-variant-position`, `font-variant-emoji`.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant

### P306 font-variant-alternates

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | [ stylistic(<font-feature-value-name>) || historical-forms || styleset(<font-feature-value-name>#) || character-variant(<font-feature-value-name>#) || swash(<font-feature-value-name>) || ornaments(<font-feature-value-name>) || annotation(<font-feature-value-name>) ]`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-alternates

### P307 font-variant-caps

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | small-caps | all-small-caps | petite-caps | all-petite-caps | unicase | titling-caps`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-caps

### P308 font-variant-east-asian

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | [ <east-asian-variant-values> || <east-asian-width-values> || ruby ]`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-east-asian

### P309 font-variant-emoji

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | text | emoji | unicode`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: N/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-emoji

### P310 font-variant-ligatures

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | none | [ <common-lig-values> || <discretionary-lig-values> || <historical-lig-values> || <contextual-alt-values> ]`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-ligatures

### P311 font-variant-numeric

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | [ <numeric-figure-values> || <numeric-spacing-values> || <numeric-fraction-values> || ordinal || slashed-zero ]`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-numeric

### P312 font-variant-position

Select the named high-level typographic variant category. The available font and shaping engine determine glyph behavior; use this semantic category before low-level OpenType tags when possible.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | sub | super`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variant-position

### P313 font-variation-settings

Set low-level variable-font axis values; prefer high-level weight/width/style properties for their supported axes.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | [ <opentype-tag> <number> ]#`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: the keyword normal or a list, each item a string paired with a number. Animation: see prose.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-variation-settings

### P314 font-weight

Choose weight, including variable ranges in supporting fonts; relative bolder/lighter uses font-weight mapping rules.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<font-weight-absolute> | bolder | lighter`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: a number, see below. Animation: by computed value type.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-weight

### P315 font-width

Select a font's width axis through modern font properties; the available font determines whether a matching design exists.

Family/use case: Typography and font selection. Use with an actual font supporting the requested feature, preserve readable fallback metrics and test text resizing.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <percentage [0,∞]> | ultra-condensed | extra-condensed | condensed | semi-condensed | semi-expanded | expanded | extra-expanded | ultra-expanded`

Initial: normal. Inherited: yes. Applies to: all elements and text.

Percentages: Not resolved. Computed value: a percentage, see below. Animation: by computed value type.

Source: https://drafts.csswg.org/css-fonts-4/#propdef-font-width

### P316 footnote-display

The `footnote-display` setting belongs to paged-media footnotes; its grammar and applicability below define the footnote display contract. Specialized print/pagination reference; supply a usable ordinary reading path when the formatting engine lacks support.

Family/use case: Paged-media footnotes. Specialized print/pagination reference; supply a usable ordinary reading path when the formatting engine lacks support.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `block | inline | compact`

Initial: block. Inherited: no. Applies to: elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-gcpm-3/#propdef-footnote-display

### P317 footnote-policy

The `footnote-policy` setting belongs to paged-media footnotes; its grammar and applicability below define the footnote policy contract. Specialized print/pagination reference; supply a usable ordinary reading path when the formatting engine lacks support.

Family/use case: Paged-media footnotes. Specialized print/pagination reference; supply a usable ordinary reading path when the formatting engine lacks support.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | line | block`

Initial: auto. Inherited: no. Applies to: elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-gcpm-3/#propdef-footnote-policy

### P318 forced-color-adjust

The `forced-color-adjust` setting belongs to user-agent color adaptation; its grammar and applicability below define the forced color adjust contract. Use to cooperate with native color schemes, forced colors and printing rather than overriding user preferences blindly.

Family/use case: User-agent color adaptation. Use to cooperate with native color schemes, forced colors and printing rather than overriding user preferences blindly.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none | preserve-parent-color`

Initial: auto. Inherited: yes. Applies to: all elements and text.

Percentages: n/a. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-color-adjust-1/#propdef-forced-color-adjust

### P319 frame-sizing

The `frame-sizing` setting belongs to sizing; its grammar and applicability below define the frame sizing contract. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | content-width | content-height | content-block-size | content-inline-size`

Initial: auto. Inherited: no. Applies to: replaced elements (but see below for details).

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-frame-sizing

### P320 gap

Combine row and column gaps in applicable layout modes; it supplies internal gutters and not outer container padding.

Family/use case: Layout gutters. Use internal spacing between relevant tracks/items; gaps are not outer margins or arbitrary semantic separators.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'row-gap'> <'column-gap'>?`

Initial: see individual properties. Inherited: no. Applies to: multi-column containers, flex containers, grid containers, and grid lanes containers.

Percentages: refer to corresponding dimension of the content area. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `row-gap`, `column-gap`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-gap

### P321 glyph-orientation-vertical

The `glyph-orientation-vertical` setting belongs to writing modes and direction; its grammar and applicability below define the glyph orientation vertical contract. Use for actual vertical or bidirectional content with appropriate HTML language/direction and logical geometry.

Family/use case: Writing modes and direction. Use for actual vertical or bidirectional content with appropriate HTML language/direction and logical geometry.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | 0deg | 90deg | 0 | 90`

Initial: n/a. Inherited: n/a. Applies to: n/a.

Percentages: n/a. Computed value: n/a. Animation: n/a.

Source: https://drafts.csswg.org/css-writing-modes-4/#propdef-glyph-orientation-vertical

### P322 grid

Set grid template or auto-flow-related settings through a resetting shorthand; prefer explicit longhands during diagnosis.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'grid-template'> | <'grid-template-rows'> / [ auto-flow && dense? ] <'grid-auto-columns'>? | [ auto-flow && dense? ] <'grid-auto-rows'>? / <'grid-template-columns'>`

Initial: none. Inherited: see individual properties. Applies to: grid containers.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `grid-template-rows`, `grid-template-columns`, `grid-template-areas`, `grid-auto-rows`, `grid-auto-columns`, `grid-auto-flow`.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid

### P323 grid-area

Assign a named area or start/end line positions in both axes; it can change visual order without changing reading order.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line> [ / <grid-line> ]{0,3}`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: N/A. Computed value: see individual properties. Animation: discrete.

Shorthand members: `grid-row-start`, `grid-column-start`, `grid-row-end`, `grid-column-end`.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-area

### P324 grid-auto-columns

Size implicit columns created outside the explicit template; it does not replace grid-template-columns.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<track-size>+`

Initial: auto. Inherited: no. Applies to: grid containers.

Percentages: see Track Sizing. Computed value: see Track Sizing. Animation: if the list lengths match, by computed value type per item; discrete otherwise.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-auto-columns

### P325 grid-auto-flow

Choose row/column auto placement and optional dense filling; dense placement can produce a visual/DOM-order mismatch.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ row | column ] || dense`

Initial: row. Inherited: no. Applies to: grid containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-auto-flow

### P326 grid-auto-rows

Size implicit rows; a fixed row size can clip varying or translated content.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<track-size>+`

Initial: auto. Inherited: no. Applies to: grid containers.

Percentages: see Track Sizing. Computed value: see Track Sizing. Animation: if the list lengths match, by computed value type per item; discrete otherwise.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-auto-rows

### P327 grid-column

Combine column start/end placement, including line names/numbers and spans.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line> [ / <grid-line> ]?`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: N/A. Computed value: see individual properties. Animation: discrete.

Shorthand members: `grid-column-start`, `grid-column-end`.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-column

### P328 grid-column-end

Set the end line or span constraint for an item's grid column placement.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line>`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: n/a. Computed value: specified keyword, identifier, and/or integer. Animation: discrete.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-column-end

### P329 grid-column-gap

A legacy grid-prefixed alias for gap, row-gap or column-gap respectively. Use the unprefixed canonical property in new code; the canonical definition supplies shared metadata below.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <length-percentage [0,∞]> | <line-width>`

Initial: normal. Inherited: no. Applies to: multi-column containers, flex containers, grid containers, and grid lanes containers.

Percentages: see § 2.3 Percentages In gap Properties. Computed value: specified keyword, else a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-grid-column-gap

Metadata supplement: https://drafts.csswg.org/css-gaps-1/#propdef-column-gap

### P330 grid-column-start

Set the start line or span constraint for an item's grid column placement.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line>`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: n/a. Computed value: specified keyword, identifier, and/or integer. Animation: discrete.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-column-start

### P331 grid-gap

A legacy grid-prefixed alias for gap, row-gap or column-gap respectively. Use the unprefixed canonical property in new code; the canonical definition supplies shared metadata below.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'row-gap'> <'column-gap'>?`

Initial: see individual properties. Inherited: no. Applies to: multi-column containers, flex containers, grid containers, and grid lanes containers.

Percentages: refer to corresponding dimension of the content area. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `row-gap`, `column-gap`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-grid-gap

Metadata supplement: https://drafts.csswg.org/css-gaps-1/#propdef-gap

### P332 grid-row

Combine row start/end placement within explicit or implicit grid tracks.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line> [ / <grid-line> ]?`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: N/A. Computed value: see individual properties. Animation: discrete.

Shorthand members: `grid-row-start`, `grid-row-end`.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-row

### P333 grid-row-end

Set the end line or span constraint for an item's row placement.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line>`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: n/a. Computed value: specified keyword, identifier, and/or integer. Animation: discrete.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-row-end

### P334 grid-row-gap

A legacy grid-prefixed alias for gap, row-gap or column-gap respectively. Use the unprefixed canonical property in new code; the canonical definition supplies shared metadata below.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <length-percentage [0,∞]> | <line-width>`

Initial: normal. Inherited: no. Applies to: multi-column containers, flex containers, grid containers, and grid lanes containers.

Percentages: see § 2.3 Percentages In gap Properties. Computed value: specified keyword, else a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-grid-row-gap

Metadata supplement: https://drafts.csswg.org/css-gaps-1/#propdef-row-gap

### P335 grid-row-start

Set the start line or span constraint for an item's row placement.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<grid-line>`

Initial: auto. Inherited: no. Applies to: grid items and absolutely-positioned boxes whose containing block is a grid container.

Percentages: n/a. Computed value: specified keyword, identifier, and/or integer. Animation: discrete.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-row-start

### P336 grid-template

Combine explicit rows, columns and named areas without configuring every implicit grid property.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ <'grid-template-rows'> / <'grid-template-columns'> ] | [ <line-names>? <string> <track-size>? <line-names>? ]+ [ / <explicit-track-list> ]?`

Initial: none. Inherited: see individual properties. Applies to: grid containers.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `grid-template-rows`, `grid-template-columns`, `grid-template-areas`.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-template

### P337 grid-template-areas

Describe named rectangular regions using row strings; every repeated area name must form a rectangle.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <string>+`

Initial: none. Inherited: no. Applies to: grid containers.

Percentages: n/a. Computed value: the keyword none or a list of string values. Animation: discrete.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-template-areas

### P338 grid-template-columns

Define explicit column tracks using fixed, intrinsic or flexible sizes; minmax(0,1fr) differs from 1fr's automatic minimum.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <track-list> | <auto-track-list> | subgrid <line-name-list>?`

Initial: none. Inherited: no. Applies to: grid containers.

Percentages: refer to corresponding dimension of the content area. Computed value: the keyword none or a computed track list. Animation: if the list lengths match, by computed value type per item in the computed track list (see § 7.2.5 Computed Value of a Track Listing and § 7.2.3.3 Interpolation/Combination of repeat()); discrete otherwise.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-template-columns

### P339 grid-template-rows

Define explicit row tracks; track sizing, intrinsic content and available block size interact.

Family/use case: Grid track layout. Use for two-dimensional relationships; inspect explicit/implicit tracks and preserve a meaningful source sequence.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <track-list> | <auto-track-list> | subgrid <line-name-list>?`

Initial: none. Inherited: no. Applies to: grid containers.

Percentages: refer to corresponding dimension of the content area. Computed value: the keyword none or a computed track list. Animation: if the list lengths match, by computed value type per item in the computed track list (see § 7.2.5 Computed Value of a Track Listing and § 7.2.3.3 Interpolation/Combination of repeat()); discrete otherwise.

Source: https://drafts.csswg.org/css-grid-2/#propdef-grid-template-rows

### P340 hanging-punctuation

Allow selected punctuation to hang outside line edges under the text layout rules; test the language and renderer.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ first || [ force-end | allow-end ] || last ]`

Initial: none. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-hanging-punctuation

### P341 height

Set a physical preferred height; percentage resolution and intrinsic sizing depend on the containing context.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements except non-replaced inlines.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value type, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-height

### P342 hyphenate-character

The `hyphenate-character` setting belongs to hyphenation controls; its grammar and applicability below define the hyphenate character contract. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Family/use case: Hyphenation controls. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <string>`

Initial: auto. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-hyphenate-character

### P343 hyphenate-limit-chars

The `hyphenate-limit-chars` setting belongs to hyphenation controls; its grammar and applicability below define the hyphenate limit chars contract. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Family/use case: Hyphenation controls. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ auto | <integer [0,∞]> ]{1,3}`

Initial: auto. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: three values, each either the auto keyword or an integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-hyphenate-limit-chars

### P344 hyphenate-limit-last

The `hyphenate-limit-last` setting belongs to hyphenation controls; its grammar and applicability below define the hyphenate limit last contract. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Family/use case: Hyphenation controls. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | always | column | page | spread`

Initial: none. Inherited: yes. Applies to: block containers.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-hyphenate-limit-last

### P345 hyphenate-limit-lines

The `hyphenate-limit-lines` setting belongs to hyphenation controls; its grammar and applicability below define the hyphenate limit lines contract. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Family/use case: Hyphenation controls. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `no-limit | <integer [0,∞]>`

Initial: no-limit. Inherited: yes. Applies to: block containers.

Percentages: n/a. Computed value: specified keyword or integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-hyphenate-limit-lines

### P346 hyphenate-limit-zone

The `hyphenate-limit-zone` setting belongs to hyphenation controls; its grammar and applicability below define the hyphenate limit zone contract. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Family/use case: Hyphenation controls. Use with correct lang metadata and a supporting dictionary; line-break quality depends on language and implementation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: yes. Applies to: block containers.

Percentages: refers to length of the line box. Computed value: computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-hyphenate-limit-zone

### P347 hyphens

Control word hyphenation; correct language metadata and available dictionaries determine useful automatic behavior.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | manual | auto`

Initial: manual. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-hyphens

### P348 image-animation

The `image-animation` setting belongs to specialized or draft module: css-image-animation-1; its grammar and applicability below define the image animation contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-image-animation-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | paused | stopped | running`

Initial: normal. Inherited: yes. Applies to: declarative images.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-image-animation-1/#propdef-image-animation

### P349 image-orientation

Control applicable image orientation handling, including orientation metadata; confirm actual source geometry before measuring.

Family/use case: Replaced content and image rendering. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `from-image | none | [ <angle> || flip ]`

Initial: from-image. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: the specified keyword, or an <angle>, rounded and normalized (see text), plus optionally a flip keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-images-3/#propdef-image-orientation

### P350 image-rendering

Choose an image resampling preference; pixelated imagery is a deliberate content choice, not a universal quality improvement.

Family/use case: Replaced content and image rendering. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | smooth | high-quality | pixelated | crisp-edges`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-images-3/#propdef-image-rendering

### P351 image-resolution

The `image-resolution` setting belongs to replaced content and image rendering; its grammar and applicability below define the image resolution contract. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Family/use case: Replaced content and image rendering. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ from-image || <resolution> ] && snap?`

Initial: 1dppx. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword(s) and/or <resolution> (possibly adjusted for snap, see below). Animation: discrete.

Source: https://drafts.csswg.org/css-images-4/#propdef-image-resolution

### P352 initial-letter

The `initial-letter` setting belongs to initial-letter typography; its grammar and applicability below define the initial letter contract. Use for supported drop-cap/initial-letter layout with readable plain text fallback and language-aware testing.

Family/use case: Initial-letter typography. Use for supported drop-cap/initial-letter layout with readable plain text fallback and language-aware testing.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <number [1,∞]> <integer [1,∞]> | <number [1,∞]> && [ drop | raise ]?`

Initial: normal. Inherited: no. Applies to: certain inline-level boxes and ::first-letter and inside ::marker boxes (see prose).

Percentages: N/A. Computed value: the keyword normal or a number paired with an integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-inline-3/#propdef-initial-letter

### P353 initial-letter-align

The `initial-letter-align` setting belongs to initial-letter typography; its grammar and applicability below define the initial letter align contract. Use for supported drop-cap/initial-letter layout with readable plain text fallback and language-aware testing.

Family/use case: Initial-letter typography. Use for supported drop-cap/initial-letter layout with readable plain text fallback and language-aware testing.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ border-box? [ alphabetic | ideographic | hanging | leading ]? ]!`

Initial: alphabetic. Inherited: yes. Applies to: certain inline-level boxes and ::first-letter and inside ::marker boxes (see prose).

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-initial-letter-align

### P354 initial-letter-wrap

The `initial-letter-wrap` setting belongs to initial-letter typography; its grammar and applicability below define the initial letter wrap contract. Use for supported drop-cap/initial-letter layout with readable plain text fallback and language-aware testing.

Family/use case: Initial-letter typography. Use for supported drop-cap/initial-letter layout with readable plain text fallback and language-aware testing.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | first | all | grid | <length-percentage>`

Initial: none. Inherited: yes. Applies to: certain inline-level boxes and ::first-letter and inside ::marker boxes (see prose).

Percentages: relative to logical width of (last fragment of) initial letter. Computed value: specified keyword or computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-inline-3/#propdef-initial-letter-wrap

### P355 inline-size

Set preferred size in the inline axis; it maps to width in common horizontal writing modes.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements except non-replaced inlines.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value type, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-inline-size

### P356 inline-sizing

The `inline-sizing` setting belongs to sizing; its grammar and applicability below define the inline sizing contract. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | stretch`

Initial: normal. Inherited: yes. Applies to: inline boxes, but not ruby container boxes nor internal ruby boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-inline-sizing

### P357 input-security

The `input-security` setting belongs to specialized or draft module: css-forms-1; its grammar and applicability below define the input security contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-forms-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none`

Initial: auto. Inherited: no. Applies to: sensitive text inputs.

Percentages: N/A. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-forms-1/#propdef-input-security

### P358 inset

Combine physical top/right/bottom/left offsets for positioned boxes; it does not apply ordinary layout spacing.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'top'>{1,4}`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `top`, `right`, `bottom`, `left`.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset

### P359 inset-block

The `inset-block` setting belongs to positioning offsets; its grammar and applicability below define the inset block contract. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'top'>{1,2}`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `inset-block-start`, `inset-block-end`.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset-block

### P360 inset-block-end

The `inset-block-end` setting belongs to positioning offsets; its grammar and applicability below define the inset block end contract. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <length-percentage>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset-block-end

### P361 inset-block-start

The `inset-block-start` setting belongs to positioning offsets; its grammar and applicability below define the inset block start contract. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <length-percentage>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset-block-start

### P362 inset-inline

The `inset-inline` setting belongs to positioning offsets; its grammar and applicability below define the inset inline contract. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'top'>{1,2}`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `inset-inline-start`, `inset-inline-end`.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset-inline

### P363 inset-inline-end

The `inset-inline-end` setting belongs to positioning offsets; its grammar and applicability below define the inset inline end contract. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <length-percentage>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset-inline-end

### P364 inset-inline-start

The `inset-inline-start` setting belongs to positioning offsets; its grammar and applicability below define the inset inline start contract. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Family/use case: Positioning offsets. Use on an applicable positioned box, identify its containing block and prefer logical axes when that matches the requirement.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <length-percentage>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-position-3/#propdef-inset-inline-start

### P365 interactivity

The `interactivity` setting belongs to native controls and user interaction; its grammar and applicability below define the interactivity contract. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | inert`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-interactivity

### P366 interest-delay

The `interest-delay` setting belongs to native controls and user interaction; its grammar and applicability below define the interest delay contract. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'interest-delay-start'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `interest-delay-start`, `interest-delay-end`.

Source: https://drafts.csswg.org/css-ui-4/#propdef-interest-delay

### P367 interest-delay-end

The `interest-delay-end` setting belongs to native controls and user interaction; its grammar and applicability below define the interest delay end contract. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <time>`

Initial: normal. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: the keyword normal or a computed time. Animation: by computed value type.

Source: https://drafts.csswg.org/css-ui-4/#propdef-interest-delay-end

### P368 interest-delay-start

The `interest-delay-start` setting belongs to native controls and user interaction; its grammar and applicability below define the interest delay start contract. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <time>`

Initial: normal. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: the keyword normal or a computed time. Animation: by computed value type.

Source: https://drafts.csswg.org/css-ui-4/#propdef-interest-delay-start

### P369 interpolate-size

The `interpolate-size` setting belongs to sizing; its grammar and applicability below define the interpolate size contract. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `numeric-only | allow-keywords`

Initial: numeric-only. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-values-5/#propdef-interpolate-size

### P370 isolation

Create an isolated blending group and stacking context where specified; it does not isolate script or accessibility semantics.

Family/use case: Specialized or draft module: compositing-2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<isolation-mode>`

Initial: auto. Inherited: no. Applies to: All elements. In SVG, it applies to container elements, graphics elements and graphics referencing elements. [SVG11].

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/compositing-2/#propdef-isolation

### P371 justify-content

Distribute remaining space along the relevant main/inline axis after sizing and auto margins; the layout mode determines the axis.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <content-distribution> | <overflow-position>? [ <content-position> | left | right ]`

Initial: normal. Inherited: no. Applies to: multicol containers, flex containers, and grid containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-align-3/#propdef-justify-content

### P372 justify-items

Supply inline-axis self-alignment defaults for applicable items; it does not align flex items along their main axis.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | stretch | <baseline-position> | <overflow-position>? [ <self-position> | left | right ] | legacy | legacy && [ left | right | center ]`

Initial: legacy. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword(s), except for legacy (see prose). Animation: discrete.

Source: https://drafts.csswg.org/css-align-3/#propdef-justify-items

### P373 justify-self

Override inline-axis self-alignment for an applicable item; it has no equivalent ordinary main-axis Flexbox effect.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <overflow-position>? [ normal | <self-position> | left | right ] | stretch | <baseline-position> | anchor-center`

Initial: auto. Inherited: no. Applies to: block-level boxes, absolutely-positioned boxes, and grid items.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/#propdef-justify-self.

Source: https://drafts.csswg.org/css-align-3/#propdef-justify-self

### P374 left

Set a physical left positioning inset; use logical inset properties when the intent follows writing direction.

Family/use case: Positioning. Use for a sticky header or deliberate overlay after identifying the containing block and scroll/stacking contexts.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage> | <anchor()> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-position-3/#propdef-left

### P375 letter-spacing

Adjust inter-character spacing under text-shaping rules; verify readability and language behavior rather than applying it globally.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <length-percentage>`

Initial: normal. Inherited: yes. Applies to: inline boxes and text.

Percentages: relative to used font-size. Computed value: an absolute length and/or a percentage. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-letter-spacing

### P376 lighting-color

The `lighting-color` setting belongs to svg geometry and rendering; its grammar and applicability below define the lighting color contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color>`

Initial: white. Inherited: no. Applies to: feDiffuseLighting and feSpecularLighting elements.

Percentages: n/a. Computed value: as specified. Animation: by computed value.

Source: https://drafts.csswg.org/filter-effects-1/#propdef-lighting-color

### P377 line-break

Choose line-breaking strictness for relevant scripts and punctuation; it differs from word-break and overflow-wrap.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | loose | normal | strict | anywhere`

Initial: auto. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-line-break

### P378 line-clamp

The `line-clamp` setting belongs to inline layout and line metrics; its grammar and applicability below define the line clamp contract. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [<'max-lines'> || <'block-ellipsis'>] -webkit-legacy?`

Initial: none. Inherited: see individual properties. Applies to: see individual properties.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `max-lines`, `block-ellipsis`, `continue`.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-line-clamp

### P379 line-fit-edge

The `line-fit-edge` setting belongs to inline layout and line metrics; its grammar and applicability below define the line fit edge contract. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `leading | <text-edge>`

Initial: leading. Inherited: yes. Applies to: inline boxes.

Percentages: N/A. Computed value: the specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-line-fit-edge

### P380 line-grid

The `line-grid` setting belongs to inline layout and line metrics; its grammar and applicability below define the line grid contract. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `match-parent | create`

Initial: match-parent. Inherited: no. Applies to: block, flex and grid containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-line-grid-1/#propdef-line-grid

### P381 line-height

Set line box height behavior; a unitless inherited factor scales with descendant font sizes differently from an inherited length.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <number [0,∞]> | <length-percentage [0,∞]>`

Initial: normal. Inherited: yes. Applies to: non-replaced inline boxes and SVG text content elements.

Percentages: computed relative to 1em. Computed value: the specified keyword, a number, or a computed <length> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-inline-3/#propdef-line-height

### P382 line-height-step

The `line-height-step` setting belongs to inline layout and line metrics; its grammar and applicability below define the line height step contract. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length [0,∞]>`

Initial: 0. Inherited: yes. Applies to: block containers.

Percentages: N/A. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-rhythm-1/#propdef-line-height-step

### P383 line-padding

The `line-padding` setting belongs to inline layout and line metrics; its grammar and applicability below define the line padding contract. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length>`

Initial: 0. Inherited: yes. Applies to: inline boxes.

Percentages: N/A. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-line-padding

### P384 line-snap

The `line-snap` setting belongs to inline layout and line metrics; its grammar and applicability below define the line snap contract. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Family/use case: Inline layout and line metrics. Use only within the defining inline/text/grid context; baseline metrics and font fallback can change results.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | baseline | contain`

Initial: none. Inherited: yes. Applies to: block container elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-line-grid-1/#propdef-line-snap

### P385 link-parameters

The `link-parameters` setting belongs to specialized or draft module: css-link-params-1; its grammar and applicability below define the link parameters contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-link-params-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <param()>#`

Initial: none. Inherited: no. Applies to: all elements and pseudo-elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-link-params-1/#propdef-link-parameters

### P386 list-style

Combine marker type, position and image; preserve actual list semantics and verify the effect of removing markers in target assistive technology.

Family/use case: Lists and markers. Use to style actual list content; decorative markers must not replace semantic sequence or item identification.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'list-style-position'> || <'list-style-image'> || <'list-style-type'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: list items.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `list-style-type`, `list-style-position`, `list-style-image`.

Source: https://drafts.csswg.org/css-lists-3/#propdef-list-style

### P387 list-style-image

Use an image as a list marker with a type fallback; decorative marker imagery must not carry the only essential meaning.

Family/use case: Lists and markers. Use to style actual list content; decorative markers must not replace semantic sequence or item identification.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<image> | none`

Initial: none. Inherited: yes. Applies to: list items.

Percentages: n/a. Computed value: the keyword noneor the computed <image>. Animation: discrete.

Source: https://drafts.csswg.org/css-lists-3/#propdef-list-style-image

### P388 list-style-position

Place the marker inside or outside the principal list item content box under list formatting rules.

Family/use case: Lists and markers. Use to style actual list content; decorative markers must not replace semantic sequence or item identification.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `inside | outside`

Initial: outside. Inherited: yes. Applies to: list items.

Percentages: n/a. Computed value: keyword, but see prose. Animation: discrete.

Source: https://drafts.csswg.org/css-lists-3/#propdef-list-style-position

### P389 list-style-type

Choose a marker/counter style; the result is generated presentation rather than a persistent item identifier.

Family/use case: Lists and markers. Use to style actual list content; decorative markers must not replace semantic sequence or item identification.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<counter-style> | <string> | none`

Initial: disc. Inherited: yes. Applies to: list items.

Percentages: n/a. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-lists-3/#propdef-list-style-type

### P390 margin

Set physical outer spacing in top/right/bottom/left shorthand order; auto, negative values and margin collapse have context-specific effects.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'margin-top'>{1,4}`

Initial: 0. Inherited: no. Applies to: all elements except internal table elements, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `margin-top`, `margin-right`, `margin-bottom`, `margin-left`.

Source: https://drafts.csswg.org/css-box-4/#propdef-margin

### P391 margin-block

Set the block component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'margin-top'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `margin-block-start`, `margin-block-end`.

Source: https://drafts.csswg.org/css-logical-1/#propdef-margin-block

### P392 margin-block-end

Set the block-end component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'margin-top'>`

Initial: 0. Inherited: no. Applies to: Same as margin-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding margin-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-margin-block-end

### P393 margin-block-start

Set the block-start component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'margin-top'>`

Initial: 0. Inherited: no. Applies to: Same as margin-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding margin-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-margin-block-start

### P394 margin-bottom

Set the bottom component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage> | auto | <anchor-size()>`

Initial: 0. Inherited: no. Applies to: all elements except internal table elements, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-box-4/#propdef-margin-bottom

### P395 margin-break

Set the break component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | keep | discard`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-break-4/#propdef-margin-break

### P396 margin-inline

Set the inline component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'margin-top'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `margin-inline-start`, `margin-inline-end`.

Source: https://drafts.csswg.org/css-logical-1/#propdef-margin-inline

### P397 margin-inline-end

Set the inline-end component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'margin-top'>`

Initial: 0. Inherited: no. Applies to: Same as margin-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding margin-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-margin-inline-end

### P398 margin-inline-start

Set the inline-start component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'margin-top'>`

Initial: 0. Inherited: no. Applies to: Same as margin-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding margin-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-margin-inline-start

### P399 margin-left

Set the left component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage> | auto | <anchor-size()>`

Initial: 0. Inherited: no. Applies to: all elements except internal table elements, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-box-4/#propdef-margin-left

### P400 margin-right

Set the right component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage> | auto | <anchor-size()>`

Initial: 0. Inherited: no. Applies to: all elements except internal table elements, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-box-4/#propdef-margin-right

### P401 margin-top

Set the top component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage> | auto | <anchor-size()>`

Initial: 0. Inherited: no. Applies to: all elements except internal table elements, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-box-4/#propdef-margin-top

### P402 margin-trim

Set the trim component of margin. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Margin can be auto/negative or collapse in applicable block flow.

Family/use case: Outer spacing. Use to separate boxes or align an auto-sized region; account for collapse, auto distribution, negative values and writing direction.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | block | [ block-start || block-end ]`

Initial: none. Inherited: no. Applies to: block containers, multi-column containers.

Percentages: N/A. Computed value: a set of zero to two keywords indicating which sides to trim. Animation: discrete.

Source: https://drafts.csswg.org/css-box-4/#propdef-margin-trim

### P403 marker

The `marker` setting belongs to svg markers or list markers; its grammar and applicability below define the marker contract. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Family/use case: SVG markers or list markers. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <marker-ref>`

Initial: not defined for shorthand properties. Inherited: yes. Applies to: shapes.

Percentages: N/A. Computed value: see individual properties. Animation: discrete.

Shorthand members: `marker-start`, `marker-mid`, `marker-end`.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#MarkerProperty

### P404 marker-end

The `marker-end` setting belongs to svg markers or list markers; its grammar and applicability below define the marker end contract. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Family/use case: SVG markers or list markers. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <marker-ref>`

Initial: none. Inherited: yes. Applies to: shapes.

Percentages: N/A. Computed value: as specified, but with <url> values (that are part of a <marker-ref>) made absolute. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#MarkerEndProperty

### P405 marker-mid

The `marker-mid` setting belongs to svg markers or list markers; its grammar and applicability below define the marker mid contract. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Family/use case: SVG markers or list markers. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <marker-ref>`

Initial: none. Inherited: yes. Applies to: shapes.

Percentages: N/A. Computed value: as specified, but with <url> values (that are part of a <marker-ref>) made absolute. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#MarkerMidProperty

### P406 marker-side

The `marker-side` setting belongs to svg markers or list markers; its grammar and applicability below define the marker side contract. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Family/use case: SVG markers or list markers. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `match-self | match-parent`

Initial: match-self. Inherited: yes. Applies to: list items.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-lists-3/#propdef-marker-side

### P407 marker-start

The `marker-start` setting belongs to svg markers or list markers; its grammar and applicability below define the marker start contract. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Family/use case: SVG markers or list markers. Use in the precise defining SVG/list context; a visual marker does not provide an accessible label for the entire diagram.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <marker-ref>`

Initial: none. Inherited: yes. Applies to: shapes.

Percentages: N/A. Computed value: as specified, but with <url> values (that are part of a <marker-ref>) made absolute. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#MarkerStartProperty

### P408 mask

Combine masking layers and resetting mask settings; masking changes painted visibility without providing semantic hiding.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<mask-layer>#`

Initial: see individual properties. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `mask-image`, `mask-position`, `mask-size`, `mask-repeat`, `mask-origin`, `mask-clip`, `mask-composite`, `mask-mode`.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask

### P409 mask-border

Configure a nine-slice mask border; its source/slice/width/outset/repeat/mode are separate from ordinary border paint.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'mask-border-source'> || <'mask-border-slice'> [ / <'mask-border-width'>? [ / <'mask-border-outset'> ]? ]? || <'mask-border-repeat'> || <'mask-border-mode'>`

Initial: See individual properties. Inherited: no. Applies to: See individual properties.

Percentages: n/a. Computed value: See individual properties. Animation: See individual properties.

Shorthand members: `mask-border-source`, `mask-border-slice`, `mask-border-width`, `mask-border-outset`, `mask-border-repeat`, `mask-border-mode`.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border

### P410 mask-border-mode

The `mask-border-mode` setting belongs to masking; its grammar and applicability below define the mask border mode contract. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `luminance | alpha`

Initial: alpha. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border-mode

### P411 mask-border-outset

The `mask-border-outset` setting belongs to masking; its grammar and applicability below define the mask border outset contract. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-image-outset'>`

Initial: 0. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: all <length>s made absolute, otherwise as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border-outset

### P412 mask-border-repeat

The `mask-border-repeat` setting belongs to masking; its grammar and applicability below define the mask border repeat contract. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-image-repeat'>`

Initial: stretch. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border-repeat

### P413 mask-border-slice

The `mask-border-slice` setting belongs to masking; its grammar and applicability below define the mask border slice contract. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-image-slice'>`

Initial: 0. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: refer to size of the mask border image. Computed value: as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border-slice

### P414 mask-border-source

The `mask-border-source` setting belongs to masking; its grammar and applicability below define the mask border source contract. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-image-source'>`

Initial: none. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: they keyword none or the computed <image>. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border-source

### P415 mask-border-width

The `mask-border-width` setting belongs to masking; its grammar and applicability below define the mask border width contract. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'border-image-width'>`

Initial: auto. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: relative to width/height of the mask border image area. Computed value: all <length>s made absolute, otherwise as specified. Animation: by computed value.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-border-width

### P416 mask-clip

Choose each mask layer's painting area; no-clip and geometry-box values have masking-specific behavior.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <coord-box> | no-clip ]#`

Initial: border-box. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: list, each item the keyword as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-clip

### P417 mask-composite

Choose how a mask layer combines with the layers below it; operator order affects the result.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<compositing-operator>#`

Initial: add. Inherited: no. Applies to: All elements. In SVG, it applies to container elements without the defs element and all graphics elements.

Percentages: n/a. Computed value: list, each item the keyword as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-composite

### P418 mask-image

Select mask images or referenced masks; failure behavior must be tested because content can become invisible.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<mask-reference>#`

Initial: none. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: list, each item the keyword none, a computed <image>, or a computed <url>. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-image

### P419 mask-mode

Choose alpha/luminance interpretation or source-defined behavior for each mask layer.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<masking-mode>#`

Initial: match-source. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: list, each item the keyword as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-mode

### P420 mask-origin

Choose a positioning reference box for mask layers; it differs from mask clipping.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<coord-box>#`

Initial: border-box. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: list, each item the keyword as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-origin

### P421 mask-position

Place mask layers within their positioning area; coordinate interpretation follows masking/background-style rules.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<position>#`

Initial: 0% 0%. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: refer to size of mask painting area minus size of mask layer image; see text background-position [CSS3BG]. Computed value: list, each item consists of two keywords representing the origin and two offsets from that origin, each given as an absolute length (if given a <length>), otherwise as a percentage.. Animation: repeatable list.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-position

### P422 mask-repeat

Choose mask layer tiling; a mask is not an HTML image alternative.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<repeat-style>#`

Initial: repeat. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: list, each item a pair of keywords, one per dimension. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-repeat

### P423 mask-size

Size each mask layer with dimensions or cover/contain behavior as supported.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<bg-size>#`

Initial: auto. Inherited: no. Applies to: All elements. In SVG, it applies to container elements excluding the defs element, all graphics elements and the use element.

Percentages: n/a. Computed value: list, each item as specified, but with lengths made absolute. Animation: repeatable list.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-size

### P424 mask-type

Choose luminance or alpha behavior for applicable SVG mask elements; it is not a generic page opacity setting.

Family/use case: Masking. Use for decorative paint reduction with a tested fallback; transparent pixels are not semantic hiding and do not create labels.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `luminance | alpha`

Initial: luminance. Inherited: no. Applies to: mask elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-masking-1/#propdef-mask-type

### P425 math-depth

The `math-depth` setting belongs to mathml presentation; its grammar and applicability below define the math depth contract. Use in the applicable mathematical layout context; mathematical semantics require MathML structure, not only CSS values.

Family/use case: MathML presentation. Use in the applicable mathematical layout context; mathematical semantics require MathML structure, not only CSS values.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto-add | add(<integer>) | <integer>`

Initial: 0. Inherited: yes. Applies to: All elements.

Percentages: n/a. Computed value: an integer, see below. Animation: by computed value type.

Source: https://w3c.github.io/mathml-core/#propdef-math-depth

### P426 math-shift

The `math-shift` setting belongs to mathml presentation; its grammar and applicability below define the math shift contract. Use in the applicable mathematical layout context; mathematical semantics require MathML structure, not only CSS values.

Family/use case: MathML presentation. Use in the applicable mathematical layout context; mathematical semantics require MathML structure, not only CSS values.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | compact`

Initial: normal. Inherited: yes. Applies to: All elements.

Percentages: n/a. Computed value: specified keyword. Animation: by computed value type.

Source: https://w3c.github.io/mathml-core/#propdef-math-shift

### P427 math-style

The `math-style` setting belongs to mathml presentation; its grammar and applicability below define the math style contract. Use in the applicable mathematical layout context; mathematical semantics require MathML structure, not only CSS values.

Family/use case: MathML presentation. Use in the applicable mathematical layout context; mathematical semantics require MathML structure, not only CSS values.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | compact`

Initial: normal. Inherited: yes. Applies to: All elements.

Percentages: n/a. Computed value: specified keyword. Animation: by computed value type.

Source: https://w3c.github.io/mathml-core/#propdef-math-style

### P428 max-block-size

The `max-block-size` setting belongs to size constraints; its grammar and applicability below define the max block size contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <box-size> | <anchor-size()>`

Initial: none. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-max-block-size

### P429 max-height

The `max-height` setting belongs to size constraints; its grammar and applicability below define the max height contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <box-size> | <anchor-size()>`

Initial: none. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-max-height

### P430 max-inline-size

The `max-inline-size` setting belongs to size constraints; its grammar and applicability below define the max inline size contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <box-size> | <anchor-size()>`

Initial: none. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-max-inline-size

### P431 max-lines

The `max-lines` setting belongs to overflow and scrolling; its grammar and applicability below define the max lines contract. Use for a deliberate scroll region or truncation boundary; keep focused content and essential text reachable.

Family/use case: Overflow and scrolling. Use for a deliberate scroll region or truncation boundary; keep focused content and essential text reachable.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto || <integer [1,∞]>`

Initial: auto. Inherited: no. Applies to: block containers which are also either line-clamp containers or fragmentation containers that capture region breaks.

Percentages: N/A. Computed value: the keyword auto, or an integer, or both. Animation: by computed value type.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-max-lines

### P432 max-size

The `max-size` setting belongs to size constraints; its grammar and applicability below define the max size contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'max-width'> <'max-height'>?`

Initial: none. Inherited: see individual properties. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `max-width`, `max-height`.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-max-size

### P433 max-width

The `max-width` setting belongs to size constraints; its grammar and applicability below define the max width contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <box-size> | <anchor-size()>`

Initial: none. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-max-width

### P434 min-block-size

The `min-block-size` setting belongs to size constraints; its grammar and applicability below define the min block size contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-min-block-size

### P435 min-height

The `min-height` setting belongs to size constraints; its grammar and applicability below define the min height contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-min-height

### P436 min-inline-size

The `min-inline-size` setting belongs to size constraints; its grammar and applicability below define the min inline size contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-min-inline-size

### P437 min-intrinsic-sizing

The `min-intrinsic-sizing` setting belongs to size constraints; its grammar and applicability below define the min intrinsic sizing contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `legacy | zero-if-scroll || zero-if-extrinsic`

Initial: legacy. Inherited: no. Applies to: all elements except inline boxes.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-min-intrinsic-sizing

### P438 min-size

The `min-size` setting belongs to size constraints; its grammar and applicability below define the min size contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'min-width'> <'min-height'>?`

Initial: auto. Inherited: see individual properties. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `min-width`, `min-height`.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-min-size

### P439 min-width

The `min-width` setting belongs to size constraints; its grammar and applicability below define the min width contract. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Family/use case: Size constraints. Use to bound preferred/intrinsic sizes; automatic minimums can constrain Flexbox/Grid and percentage resolution needs a definite reference where required.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements that accept width or height.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-min-width

### P440 mix-blend-mode

Blend an element's rendering with its backdrop; an isolated group can bound the blend and contrast must be checked after composition.

Family/use case: Specialized or draft module: compositing-2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<blend-mode> | plus-lighter`

Initial: normal. Inherited: no. Applies to: All elements. In SVG, it applies to container elements, graphics elements and graphics referencing elements. [SVG11].

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/compositing-2/#propdef-mix-blend-mode

### P441 nav-down

The `nav-down` setting belongs to spatial navigation; its grammar and applicability below define the nav down contract. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Family/use case: Spatial navigation. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <id> [ current | root | <target-name> ]?`

Initial: auto. Inherited: no. Applies to: all enabled elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-nav-down

### P442 nav-left

The `nav-left` setting belongs to spatial navigation; its grammar and applicability below define the nav left contract. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Family/use case: Spatial navigation. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <id> [ current | root | <target-name> ]?`

Initial: auto. Inherited: no. Applies to: all enabled elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-nav-left

### P443 nav-right

The `nav-right` setting belongs to spatial navigation; its grammar and applicability below define the nav right contract. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Family/use case: Spatial navigation. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <id> [ current | root | <target-name> ]?`

Initial: auto. Inherited: no. Applies to: all enabled elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-nav-right

### P444 nav-up

The `nav-up` setting belongs to spatial navigation; its grammar and applicability below define the nav up contract. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Family/use case: Spatial navigation. Specialized directional navigation reference; do not change logical keyboard tab order based on unverified engine behavior.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <id> [ current | root | <target-name> ]?`

Initial: auto. Inherited: no. Applies to: all enabled elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-nav-up

### P445 object-fit

Fit a replaced element's content within its content box using fill/contain/cover/none/scale-down; cover can crop meaningful image content.

Family/use case: Replaced content and image rendering. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `fill | none | [contain | cover] || scale-down`

Initial: fill. Inherited: no. Applies to: replaced elements.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-images-4/#propdef-object-fit

### P446 object-position

Position replaced content within its box after fitting; it does not move the element's own layout box.

Family/use case: Replaced content and image rendering. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<position>`

Initial: 50% 50%. Inherited: no. Applies to: replaced elements.

Percentages: refer to width and height of element itself. Computed value: as for background-position. Animation: as for background-position.

Source: https://drafts.csswg.org/css-images-3/#propdef-object-position

### P447 object-view-box

The `object-view-box` setting belongs to replaced content and image rendering; its grammar and applicability below define the object view box contract. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Family/use case: Replaced content and image rendering. Use to fit and render real image content while preserving alternatives and meaningful cropping.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <basic-shape-rect>`

Initial: none. Inherited: no. Applies to: replaced elements.

Percentages: n/a. Computed value: specified keyword, or computed <basic-shape> function. Animation: as <basic-shape> if possible, otherwise discrete.

Source: https://drafts.csswg.org/css-images-5/#propdef-object-view-box

### P448 offset

The `offset` setting belongs to motion path; its grammar and applicability below define the offset contract. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Family/use case: Motion path. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'offset-position'>? [ <'offset-path'> [ <'offset-distance'> || <'offset-rotate'> ]? ]? ]! [ / <'offset-anchor'> ]?`

Initial: see individual properties. Inherited: see individual properties. Applies to: transformable elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `offset-path`, `offset-distance`, `offset-rotate`, `offset-anchor`, `offset-position`.

Source: https://drafts.csswg.org/motion-1/#propdef-offset

### P449 offset-anchor

The `offset-anchor` setting belongs to motion path; its grammar and applicability below define the offset anchor contract. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Family/use case: Motion path. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <position>`

Initial: auto. Inherited: no. Applies to: transformable elements.

Percentages: relative to the width and the height of the element's reference box. Computed value: the auto keyword or a computed <position>. Animation: by computed value.

Source: https://drafts.csswg.org/motion-1/#propdef-offset-anchor

### P450 offset-distance

The `offset-distance` setting belongs to motion path; its grammar and applicability below define the offset distance contract. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Family/use case: Motion path. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: transformable elements.

Percentages: relative to the offset path length. Computed value: a computed <length-percentage> value. Animation: by computed value.

Source: https://drafts.csswg.org/motion-1/#propdef-offset-distance

### P451 offset-path

The `offset-path` setting belongs to motion path; its grammar and applicability below define the offset path contract. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Family/use case: Motion path. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <offset-path> || <coord-box>`

Initial: none. Inherited: no. Applies to: transformable elements.

Percentages: n/a. Computed value: as specified. Animation: by computed value.

Source: https://drafts.csswg.org/motion-1/#propdef-offset-path

### P452 offset-position

The `offset-position` setting belongs to motion path; its grammar and applicability below define the offset position contract. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Family/use case: Motion path. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | auto | <position>`

Initial: normal. Inherited: no. Applies to: transformable elements.

Percentages: Refer to the size of containing block. Computed value: The normal or auto keywords, or a computed <position>. Animation: by computed value.

Source: https://drafts.csswg.org/motion-1/#propdef-offset-position

### P453 offset-rotate

The `offset-rotate` setting belongs to motion path; its grammar and applicability below define the offset rotate contract. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Family/use case: Motion path. Use for a supported motion-path effect; verify the path coordinate system, orientation and reduced-motion alternative.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ auto | reverse ] || <angle>`

Initial: auto. Inherited: no. Applies to: transformable elements.

Percentages: n/a. Computed value: computed <angle> value, optionally preceded by auto. Animation: by computed value.

Source: https://drafts.csswg.org/motion-1/#propdef-offset-rotate

### P454 opacity

Apply group opacity to the rendered element and descendants; zero opacity alone does not remove focus or pointer interaction.

Family/use case: Color and compositing inputs. Use semantic foreground/surface tokens and verify actual composited contrast across themes and user color settings.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<opacity-value>`

Initial: 1. Inherited: no. Applies to: all elements.

Percentages: map to the range [0,1]. Computed value: specified number, clamped to the range [0,1]. Animation: by computed value type.

Source: https://drafts.csswg.org/css-color-4/#propdef-opacity

### P455 order

Change visual flex/grid order; maintain a meaningful source sequence and do not use it to repair semantic markup.

Family/use case: Formatting contexts. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<integer>`

Initial: 0. Inherited: no. Applies to: flex items and grid items.

Percentages: n/a. Computed value: specified integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-display-4/#propdef-order

### P456 orphans

Request a minimum number of lines left before a fragmentation break; impossible constraints can be relaxed by the formatter.

Family/use case: Fragmentation. Use to improve print or multicol page breaks; impossible keep/break constraints remain subject to the formatter.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<integer [1,∞]>`

Initial: 2. Inherited: yes. Applies to: block containers that establish an inline formatting context.

Percentages: n/a. Computed value: specified integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-break-4/#propdef-orphans

### P457 outline

Paint a non-layout outline around a box; do not remove focus indicators without a visible replacement.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'outline-width'> || <'outline-style'> || <'outline-color'>`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `outline-width`, `outline-style`, `outline-color`.

Source: https://drafts.csswg.org/css-ui-4/#propdef-outline

### P458 outline-color

Choose outline paint, including currentColor/system-aware choices; verify contrast on adjacent surfaces.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <'border-top-color'>`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see below. Animation: by computed value.

Source: https://drafts.csswg.org/css-ui-4/#propdef-outline-color

### P459 outline-offset

Offset an outline from the border edge; surrounding clipping can still hide it.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: absolute length. Animation: by computed value.

Source: https://drafts.csswg.org/css-ui-4/#propdef-outline-offset

### P460 outline-style

Choose outline stroke behavior; none removes the indicator and needs an alternate focus treatment where relevant.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <outline-line-style>`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword. Animation: by computed value.

Source: https://drafts.csswg.org/css-ui-4/#propdef-outline-style

### P461 outline-width

Set outline thickness without changing layout size; a visibly adequate focus indicator needs more than a nominal width.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<line-width>`

Initial: medium. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: absolute length, snapped as a border width. Animation: by computed value.

Source: https://drafts.csswg.org/css-ui-4/#propdef-outline-width

### P462 overflow

Combine overflow axes and clipping/scrolling behavior; hidden and clip have different scrolling consequences.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'overflow-block'>{1,2}`

Initial: visible. Inherited: no. Applies to: block containers [CSS2], flex containers [CSS3-FLEXBOX], and grid containers [CSS3-GRID-LAYOUT].

Percentages: N/A. Computed value: see individual properties. Animation: discrete.

Shorthand members: `overflow-x`, `overflow-y`.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-overflow

### P463 overflow-anchor

The `overflow-anchor` setting belongs to overflow and wrapping; its grammar and applicability below define the overflow anchor contract. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-scroll-anchoring-1/#propdef-overflow-anchor

### P464 overflow-block

The `overflow-block` setting belongs to overflow and wrapping; its grammar and applicability below define the overflow block contract. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `visible | hidden | clip | scroll | auto`

Initial: visible. Inherited: no. Applies to: block containers [CSS2], flex containers [CSS-FLEXBOX-1], grid containers [CSS-GRID-1], and table grid boxes [CSS-TABLES-3].

Percentages: N/A. Computed value: usually specified value, but see text. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-overflow-block

### P465 overflow-clip-margin

The `overflow-clip-margin` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `overflow-clip-margin-top`, `overflow-clip-margin-right`, `overflow-clip-margin-bottom`, `overflow-clip-margin-left`.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin

### P466 overflow-clip-margin-block

The `overflow-clip-margin-block` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin block contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `overflow-clip-margin-block-start`, `overflow-clip-margin-block-end`.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-block

### P467 overflow-clip-margin-block-end

The `overflow-clip-margin-block-end` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin block end contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-block-end

### P468 overflow-clip-margin-block-start

The `overflow-clip-margin-block-start` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin block start contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-block-start

### P469 overflow-clip-margin-bottom

The `overflow-clip-margin-bottom` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin bottom contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-bottom

### P470 overflow-clip-margin-inline

The `overflow-clip-margin-inline` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin inline contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `overflow-clip-margin-inline-start`, `overflow-clip-margin-inline-end`.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-inline

### P471 overflow-clip-margin-inline-end

The `overflow-clip-margin-inline-end` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin inline end contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-inline-end

### P472 overflow-clip-margin-inline-start

The `overflow-clip-margin-inline-start` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin inline start contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-inline-start

### P473 overflow-clip-margin-left

The `overflow-clip-margin-left` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin left contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-left

### P474 overflow-clip-margin-right

The `overflow-clip-margin-right` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin right contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-right

### P475 overflow-clip-margin-top

The `overflow-clip-margin-top` setting belongs to overflow clipping bounds; its grammar and applicability below define the overflow clip margin top contract. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Family/use case: Overflow clipping bounds. Use to control supported overflow-clip paint bounds; it is not a substitute for making focused controls visible.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<visual-box> || <length>`

Initial: 0px. Inherited: no. Applies to: boxes to which overflow applies.

Percentages: see individual properties. Computed value: the computed <length> and a <visual-box> keyword. Animation: per computed value if the <visual-box> values match; otherwise discrete.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-overflow-clip-margin-top

### P476 overflow-inline

The `overflow-inline` setting belongs to overflow and wrapping; its grammar and applicability below define the overflow inline contract. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `visible | hidden | clip | scroll | auto`

Initial: visible. Inherited: no. Applies to: block containers [CSS2], flex containers [CSS-FLEXBOX-1], grid containers [CSS-GRID-1], and table grid boxes [CSS-TABLES-3].

Percentages: N/A. Computed value: usually specified value, but see text. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-overflow-inline

### P477 overflow-wrap

Allow otherwise unbreakable inline content to wrap; anywhere participates in intrinsic sizing differently from legacy break-word behavior.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | break-word | anywhere`

Initial: normal. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-overflow-wrap

### P478 overflow-x

Control physical horizontal overflow; its computed interaction with overflow-y can create a scroll container unexpectedly.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `visible | hidden | clip | scroll | auto`

Initial: visible. Inherited: no. Applies to: block containers [CSS2], flex containers [CSS-FLEXBOX-1], grid containers [CSS-GRID-1], and table grid boxes [CSS-TABLES-3].

Percentages: N/A. Computed value: usually specified value, but see text. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-overflow-x

### P479 overflow-y

Control physical vertical overflow and its interaction with the other axis; keep scrollable regions usable by keyboard.

Family/use case: Overflow and wrapping. Use to define a deliberate scroll/clip region; diagnose the sizing cause rather than concealing unintended overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `visible | hidden | clip | scroll | auto`

Initial: visible. Inherited: no. Applies to: block containers [CSS2], flex containers [CSS-FLEXBOX-1], grid containers [CSS-GRID-1], and table grid boxes [CSS-TABLES-3].

Percentages: N/A. Computed value: usually specified value, but see text. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-overflow-y

### P480 overlay

The `overlay` setting belongs to positioning; its grammar and applicability below define the overlay contract. Use for a sticky header or deliberate overlay after identifying the containing block and scroll/stacking contexts.

Family/use case: Positioning. Use for a sticky header or deliberate overlay after identifying the containing block and scroll/stacking contexts.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | auto`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: see prose.

Source: https://drafts.csswg.org/css-position-4/#propdef-overlay

### P481 overscroll-behavior

The `overscroll-behavior` setting belongs to scroll boundary behavior; its grammar and applicability below define the overscroll behavior contract. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Family/use case: Scroll boundary behavior. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ contain | none | auto | chain ]{1,2}`

Initial: auto auto. Inherited: no. Applies to: scroll container elements.

Percentages: n/a. Computed value: see individual properties. Animation: discrete.

Shorthand members: `overscroll-behavior-x`, `overscroll-behavior-y`.

Source: https://drafts.csswg.org/css-overscroll-1/#propdef-overscroll-behavior

### P482 overscroll-behavior-block

The `overscroll-behavior-block` setting belongs to scroll boundary behavior; its grammar and applicability below define the overscroll behavior block contract. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Family/use case: Scroll boundary behavior. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `contain | none | auto | chain`

Initial: auto. Inherited: no. Applies to: scroll container elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-overscroll-1/#propdef-overscroll-behavior-block

### P483 overscroll-behavior-inline

The `overscroll-behavior-inline` setting belongs to scroll boundary behavior; its grammar and applicability below define the overscroll behavior inline contract. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Family/use case: Scroll boundary behavior. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `contain | none | auto | chain`

Initial: auto. Inherited: no. Applies to: scroll container elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-overscroll-1/#propdef-overscroll-behavior-inline

### P484 overscroll-behavior-x

The `overscroll-behavior-x` setting belongs to scroll boundary behavior; its grammar and applicability below define the overscroll behavior x contract. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Family/use case: Scroll boundary behavior. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `contain | none | auto | chain`

Initial: auto. Inherited: no. Applies to: scroll container elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-overscroll-1/#propdef-overscroll-behavior-x

### P485 overscroll-behavior-y

The `overscroll-behavior-y` setting belongs to scroll boundary behavior; its grammar and applicability below define the overscroll behavior y contract. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Family/use case: Scroll boundary behavior. Use to control scroll chaining or boundary actions without disabling essential page navigation or browser gestures.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `contain | none | auto | chain`

Initial: auto. Inherited: no. Applies to: scroll container elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-overscroll-1/#propdef-overscroll-behavior-y

### P486 padding

Set inner spacing on physical sides; it cannot be negative, does not collapse and participates in sizing according to box-sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'padding-top'>{1,4}`

Initial: 0. Inherited: no. Applies to: all elements except: internal table elements other than table cells, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `padding-top`, `padding-right`, `padding-bottom`, `padding-left`.

Source: https://drafts.csswg.org/css-box-4/#propdef-padding

### P487 padding-block

Set the block component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'padding-top'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `padding-block-start`, `padding-block-end`.

Source: https://drafts.csswg.org/css-logical-1/#propdef-padding-block

### P488 padding-block-end

Set the block-end component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'padding-top'>`

Initial: 0. Inherited: no. Applies to: Same as padding-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding padding-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-padding-block-end

### P489 padding-block-start

Set the block-start component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'padding-top'>`

Initial: 0. Inherited: no. Applies to: Same as padding-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding padding-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-padding-block-start

### P490 padding-bottom

Set the bottom component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage [0,∞]>`

Initial: 0. Inherited: no. Applies to: all elements except: internal table elements other than table cells, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-box-4/#propdef-padding-bottom

### P491 padding-inline

Set the inline component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'padding-top'>{1,2}`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `padding-inline-start`, `padding-inline-end`.

Source: https://drafts.csswg.org/css-logical-1/#propdef-padding-inline

### P492 padding-inline-end

Set the inline-end component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'padding-top'>`

Initial: 0. Inherited: no. Applies to: Same as padding-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding padding-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-padding-inline-end

### P493 padding-inline-start

Set the inline-start component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'padding-top'>`

Initial: 0. Inherited: no. Applies to: Same as padding-top.

Percentages: As for the corresponding physical property. Computed value: Same as corresponding padding-* properties. Animation: by computed value type.

Source: https://drafts.csswg.org/css-logical-1/#propdef-padding-inline-start

### P494 padding-left

Set the left component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage [0,∞]>`

Initial: 0. Inherited: no. Applies to: all elements except: internal table elements other than table cells, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-box-4/#propdef-padding-left

### P495 padding-right

Set the right component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage [0,∞]>`

Initial: 0. Inherited: no. Applies to: all elements except: internal table elements other than table cells, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-box-4/#propdef-padding-right

### P496 padding-top

Set the top component of padding. Physical sides stay fixed; block/inline sides map through writing-mode and direction. Padding is nonnegative inner space and participates in box sizing.

Family/use case: Inner spacing. Use to separate content from a component edge; padding affects border-box/content-box sizing and never collapses.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage [0,∞]>`

Initial: 0. Inherited: no. Applies to: all elements except: internal table elements other than table cells, ruby base containers, and ruby annotation containers.

Percentages: refer to logical width of containing block. Computed value: a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-box-4/#propdef-padding-top

### P497 page

The `page` setting belongs to paged-media layout; its grammar and applicability below define the page contract. Use in a verified print/PDF formatting environment; screen-layout behavior and printer output require separate checks.

Family/use case: Paged-media layout. Use in a verified print/PDF formatting environment; screen-layout behavior and printer output require separate checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <custom-ident>`

Initial: auto. Inherited: no (but see prose). Applies to: boxes that create class A break points.

Percentages: n/a. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-page-3/#propdef-page

### P498 page-break-after

Legacy alias for a subset of break-after values; use the modern fragmentation property for new authored rules.

Family/use case: Specialized or draft module: css2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | always | avoid | left | right | inherit`

Initial: auto. Inherited: no. Applies to: block-level elements (but see text).

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css2/#propdef-page-break-after

### P499 page-break-before

Legacy alias for supported page break-before behavior; it does not supply arbitrary column breaks.

Family/use case: Specialized or draft module: css2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | always | avoid | left | right | inherit`

Initial: auto. Inherited: no. Applies to: block-level elements (but see text).

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css2/#propdef-page-break-before

### P500 page-break-inside

Legacy alias for applicable break-inside values; an avoid request remains subject to fragmentation constraints.

Family/use case: Specialized or draft module: css2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `avoid | auto | inherit`

Initial: auto. Inherited: no. Applies to: block-level elements (but see text).

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css2/#propdef-page-break-inside

### P501 paint-order

The `paint-order` setting belongs to svg paint order; its grammar and applicability below define the paint order contract. Use to coordinate fill/stroke/marker rendering for vector content while retaining a semantic description.

Family/use case: SVG paint order. Use to coordinate fill/stroke/marker rendering for vector content while retaining a semantic description.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | [ fill || stroke || markers ]`

Initial: normal. Inherited: yes. Applies to: shapes and text content elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#PaintOrderProperty

### P502 path-length

The `path-length` setting belongs to svg geometry and rendering; its grammar and applicability below define the path length contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <length> [0,∞]`

Initial: none. Inherited: no. Applies to: 'path', 'circle', 'ellipse', 'line', 'polygon', 'polyline', 'rect'.

Percentages: N/A. Computed value: the keyword none, or an absolute length. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/paths.html#PathLengthCSSProperty

### P503 pause

The `pause` setting belongs to speech pauses; its grammar and applicability below define the pause contract. Use only in a verified speech styling environment; semantic punctuation and document structure remain necessary.

Family/use case: Speech pauses. Use only in a verified speech styling environment; semantic punctuation and document structure remain necessary.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'pause-before'> <'pause-after'>?`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `pause-before`, `pause-after`.

Source: https://drafts.csswg.org/css-speech-1/#propdef-pause

### P504 pause-after

The `pause-after` setting belongs to speech pauses; its grammar and applicability below define the pause after contract. Use only in a verified speech styling environment; semantic punctuation and document structure remain necessary.

Family/use case: Speech pauses. Use only in a verified speech styling environment; semantic punctuation and document structure remain necessary.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<time [0s,∞]> | none | x-weak | weak | medium | strong | x-strong`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-pause-after

### P505 pause-before

The `pause-before` setting belongs to speech pauses; its grammar and applicability below define the pause before contract. Use only in a verified speech styling environment; semantic punctuation and document structure remain necessary.

Family/use case: Speech pauses. Use only in a verified speech styling environment; semantic punctuation and document structure remain necessary.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<time [0s,∞]> | none | x-weak | weak | medium | strong | x-strong`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-pause-before

### P506 perspective

Supply perspective for transformed descendants; it differs from applying a perspective() transform to the same element.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <length [0,∞]>`

Initial: none. Inherited: no. Applies to: transformable elements.

Percentages: N/A. Computed value: the keyword none or an absolute length. Animation: by computed value.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-perspective

### P507 perspective-origin

Choose the vanishing-point origin for the element's perspective effect.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<position>`

Initial: 50% 50%. Inherited: no. Applies to: transformable elements.

Percentages: refer to the size of the reference box. Computed value: see background-position. Animation: by computed value.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-perspective-origin

### P508 place-content

Combine align-content and justify-content; axis meanings depend on the layout mode.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'align-content'> <'justify-content'>?`

Initial: normal. Inherited: no. Applies to: see individual properties.

Percentages: n/a. Computed value: see individual properties. Animation: discrete.

Shorthand members: `align-content`, `justify-content`.

Source: https://drafts.csswg.org/css-align-3/#propdef-place-content

### P509 place-items

Combine align-items and justify-items; the justify-items component does not become a Flexbox main-axis alignment control.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'align-items'> <'justify-items'>?`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: see individual properties. Animation: discrete.

Shorthand members: `align-items`, `justify-items`.

Source: https://drafts.csswg.org/css-align-3/#propdef-place-items

### P510 place-self

Combine align-self and justify-self for an applicable item.

Family/use case: Box alignment. Use to align a toolbar, card collection or grid area in the correct layout axis; automatic margins and sizing happen before free-space distribution.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'align-self'> <'justify-self'>?`

Initial: auto. Inherited: no. Applies to: see individual properties.

Percentages: n/a. Computed value: see individual properties. Animation: discrete.

Shorthand members: `align-self`, `justify-self`.

Source: https://drafts.csswg.org/css-align-3/#propdef-place-self

### P511 pointer-events

Control pointer hit testing in the applicable HTML/SVG model; none does not automatically remove keyboard focus or disable a control.

Family/use case: Specialized or draft module: linked specification. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | bounding-box | visiblePainted | visibleFill | visibleStroke | visible | painted | fill | stroke | all | none`

Initial: auto. Inherited: yes. Applies to: container elements, graphics elements and 'use'.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/interact.html#PointerEventsProperty

### P512 pointer-timeline

The `pointer-timeline` setting belongs to draft pointer timelines; its grammar and applicability below define the pointer timeline contract. Research pointer-driven animation with keyboard and reduced-motion alternatives; no implementation baseline is implied.

Family/use case: Draft pointer timelines. Research pointer-driven animation with keyboard and reduced-motion alternatives; no implementation baseline is implied.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'pointer-timeline-name'> <'pointer-timeline-axis'>? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `pointer-timeline-name`, `pointer-timeline-axis`.

Source: https://drafts.csswg.org/pointer-animations-1/#propdef-pointer-timeline

### P513 pointer-timeline-axis

The `pointer-timeline-axis` setting belongs to draft pointer timelines; its grammar and applicability below define the pointer timeline axis contract. Research pointer-driven animation with keyboard and reduced-motion alternatives; no implementation baseline is implied.

Family/use case: Draft pointer timelines. Research pointer-driven animation with keyboard and reduced-motion alternatives; no implementation baseline is implied.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ block | inline | x | y ]#`

Initial: block. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: a list of the keywords specified. Animation: not animatable.

Source: https://drafts.csswg.org/pointer-animations-1/#propdef-pointer-timeline-axis

### P514 pointer-timeline-name

The `pointer-timeline-name` setting belongs to draft pointer timelines; its grammar and applicability below define the pointer timeline name contract. Research pointer-driven animation with keyboard and reduced-motion alternatives; no implementation baseline is implied.

Family/use case: Draft pointer timelines. Research pointer-driven animation with keyboard and reduced-motion alternatives; no implementation baseline is implied.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | <dashed-ident> ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none or a list of CSS identifiers. Animation: not animatable.

Source: https://drafts.csswg.org/pointer-animations-1/#propdef-pointer-timeline-name

### P515 position

Choose static, relative, absolute, fixed or sticky positioning behavior and its relationship to normal flow and containing blocks.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `static | relative | absolute | sticky | fixed | <running()>`

Initial: static. Inherited: no. Applies to: all elements except table-column-group and table-column.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Grammar extensions: https://drafts.csswg.org/css-gcpm-3/.

Source: https://drafts.csswg.org/css-position-3/#propdef-position

### P516 position-anchor

The `position-anchor` setting belongs to positioning and anchors; its grammar and applicability below define the position anchor contract. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | none | auto | <anchor-name> | match-parent`

Initial: normal. Inherited: no. Applies to: absolutely positioned boxes.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-position-anchor

### P517 position-area

The `position-area` setting belongs to positioning and anchors; its grammar and applicability below define the position area contract. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <position-area>`

Initial: none. Inherited: no. Applies to: positioned boxes with a default anchor box.

Percentages: n/a. Computed value: the keyword none or a pair of keywords, see § 3.1.3 Computed Value and Serialization of <position-area>. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-position-area

### P518 position-try

The `position-try` setting belongs to positioning and anchors; its grammar and applicability below define the position try contract. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'position-try-order'>? <'position-try-fallbacks'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `position-try-order`, `position-try-fallbacks`.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-position-try

### P519 position-try-fallbacks

The `position-try-fallbacks` setting belongs to positioning and anchors; its grammar and applicability below define the position try fallbacks contract. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ [<dashed-ident> || <try-tactic>] | <position-area> ]#`

Initial: none. Inherited: no. Applies to: absolutely positioned boxes.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-position-try-fallbacks

### P520 position-try-order

The `position-try-order` setting belongs to positioning and anchors; its grammar and applicability below define the position try order contract. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <try-size>`

Initial: normal. Inherited: no. Applies to: absolutely positioned boxes.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-position-try-order

### P521 position-visibility

The `position-visibility` setting belongs to positioning and anchors; its grammar and applicability below define the position visibility contract. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Family/use case: Positioning and anchors. Use for overlays under the appropriate containing-block/anchor rules, with clipping, scroll and fallback analysis.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `always | [ anchor-valid || anchor-visible || no-overflow ]`

Initial: anchor-visible. Inherited: no. Applies to: absolutely positioned boxes.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-anchor-position-1/#propdef-position-visibility

### P522 print-color-adjust

Express a preference for preserving authored colors in print; user/UA decisions can still override it.

Family/use case: User-agent color adaptation. Use to cooperate with native color schemes, forced colors and printing rather than overriding user preferences blindly.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `economy | exact`

Initial: economy. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-color-adjust-1/#propdef-print-color-adjust

### P523 quotes

Choose quotation pairs used by generated open-quote/close-quote content; HTML q remains the semantic quotation element.

Family/use case: Specialized or draft module: css-content-3. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | none | bikeshed-this | [ <string> <string> ]+`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none, the keyword auto, a content language, or a list, each item a pair of string values. Animation: discrete.

Source: https://drafts.csswg.org/css-content-3/#propdef-quotes

### P524 r

The `r` setting belongs to svg geometry and rendering; its grammar and applicability below define the r contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: 'circle' element.

Percentages: refer to the normalized diagonal of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#RProperty

### P525 reading-flow

The `reading-flow` setting belongs to formatting contexts; its grammar and applicability below define the reading flow contract. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Family/use case: Formatting contexts. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | source-order | flex-visual | flex-flow | grid-rows | grid-columns | grid-order`

Initial: normal. Inherited: no. Applies to: block, flex and grid containers.

Percentages: n/a. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-display-4/#propdef-reading-flow

### P526 reading-order

The `reading-order` setting belongs to formatting contexts; its grammar and applicability below define the reading order contract. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Family/use case: Formatting contexts. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<integer>`

Initial: 0. Inherited: no. Applies to: Direct block-level, grid item, or flex item children of a reading flow container..

Percentages: n/a. Computed value: specified integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-display-4/#propdef-reading-order

### P527 region-fragment

The `region-fragment` setting belongs to specialized or draft module: css-regions-1; its grammar and applicability below define the region fragment contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-regions-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | break`

Initial: auto. Inherited: no. Applies to: CSS Regions.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-regions-1/#propdef-region-fragment

### P528 resize

Allow a user resizing handle in applicable overflow contexts; a handle does not replace a responsive base layout.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | both | horizontal | vertical | block | inline`

Initial: none. Inherited: no. Applies to: elements that are scroll containers and optionally replaced elements such as images, videos, and iframes.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-resize

### P529 rest

The `rest` setting belongs to speech rests; its grammar and applicability below define the rest contract. Specialized timing in speech presentation; distinguish a rendered rest from layout spacing and application timers.

Family/use case: Speech rests. Specialized timing in speech presentation; distinguish a rendered rest from layout spacing and application timers.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'rest-before'> <'rest-after'>?`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `rest-before`, `rest-after`.

Source: https://drafts.csswg.org/css-speech-1/#propdef-rest

### P530 rest-after

The `rest-after` setting belongs to speech rests; its grammar and applicability below define the rest after contract. Specialized timing in speech presentation; distinguish a rendered rest from layout spacing and application timers.

Family/use case: Speech rests. Specialized timing in speech presentation; distinguish a rendered rest from layout spacing and application timers.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<time [0s,∞]> | none | x-weak | weak | medium | strong | x-strong`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-rest-after

### P531 rest-before

The `rest-before` setting belongs to speech rests; its grammar and applicability below define the rest before contract. Specialized timing in speech presentation; distinguish a rendered rest from layout spacing and application timers.

Family/use case: Speech rests. Specialized timing in speech presentation; distinguish a rendered rest from layout spacing and application timers.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<time [0s,∞]> | none | x-weak | weak | medium | strong | x-strong`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-rest-before

### P532 right

Set a physical right positioning inset; opposing inset constraints and auto sizes depend on positioning mode.

Family/use case: Positioning. Use for a sticky header or deliberate overlay after identifying the containing block and scroll/stacking contexts.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage> | <anchor()> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-position-3/#propdef-right

### P533 rotate

Apply an individual rotation transform, composing in the defined order with translate, scale and transform.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <angle> | [ x | y | z | <number>{3} ] && <angle>`

Initial: none. Inherited: no. Applies to: transformable elements.

Percentages: n/a. Computed value: the keyword none, or an <angle> with an axis consisting of a list of three <number>s. Animation: as SLERP, but see below for none.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-rotate

### P534 row-gap

Set the gutter between applicable rows or flex lines; percentage gaps can have cyclic sizing rules.

Family/use case: Layout gutters. Use internal spacing between relevant tracks/items; gaps are not outer margins or arbitrary semantic separators.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <length-percentage [0,∞]> | <line-width>`

Initial: normal. Inherited: no. Applies to: multi-column containers, flex containers, grid containers, and grid lanes containers.

Percentages: see § 2.3 Percentages In gap Properties. Computed value: specified keyword, else a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-gap

### P535 row-rule

The `row-rule` setting belongs to draft gap decoration; its grammar and applicability below define the row rule contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<gap-rule-list> | <gap-auto-rule-list>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `row-rule-width`, `row-rule-style`, `row-rule-color`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule

### P536 row-rule-break

The `row-rule-break` setting belongs to draft gap decoration; its grammar and applicability below define the row rule break contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | normal | intersection`

Initial: normal. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-break

### P537 row-rule-color

The `row-rule-color` setting belongs to draft gap decoration; its grammar and applicability below define the row rule color contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-color-list> | <auto-line-color-list>`

Initial: currentcolor. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: repeatable list, see § 4.7 Interpolation of list values..

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-color

### P538 row-rule-inset

The `row-rule-inset` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset-cap'> [ / <'column-rule-inset-junction'> ]?`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap, column-rule-inset-junction, row-rule-inset-cap, and row-rule-inset-junction.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `row-rule-inset-cap-start`, `row-rule-inset-cap-end`, `row-rule-inset-junction-start`, `row-rule-inset-junction-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset

### P539 row-rule-inset-cap

The `row-rule-inset-cap` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset cap contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value> <inset-value>?`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-cap-end, column-rule-inset-junction-start, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-cap-end, row-rule-inset-junction-start, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `row-rule-inset-cap-start`, `row-rule-inset-cap-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-cap

### P540 row-rule-inset-cap-end

The `row-rule-inset-cap-end` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset cap end contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-cap-end

### P541 row-rule-inset-cap-start

The `row-rule-inset-cap-start` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset cap start contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-cap-start

### P542 row-rule-inset-end

The `row-rule-inset-end` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset end contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-junction-start, column-rule-inset-cap-end, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-junction-start, row-rule-inset-cap-end, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `row-rule-inset-cap-end`, `row-rule-inset-junction-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-end

### P543 row-rule-inset-junction

The `row-rule-inset-junction` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset junction contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value> <inset-value>?`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-cap-end, column-rule-inset-junction-start, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-cap-end, row-rule-inset-junction-start, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `row-rule-inset-junction-start`, `row-rule-inset-junction-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-junction

### P544 row-rule-inset-junction-end

The `row-rule-inset-junction-end` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset junction end contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-junction-end

### P545 row-rule-inset-junction-start

The `row-rule-inset-junction-start` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset junction start contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: 0. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: refer to the crossing gap width. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-junction-start

### P546 row-rule-inset-start

The `row-rule-inset-start` setting belongs to draft gap decoration; its grammar and applicability below define the row rule inset start contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<inset-value>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap-start, column-rule-inset-junction-start, column-rule-inset-cap-end, column-rule-inset-junction-end, row-rule-inset-cap-start, row-rule-inset-junction-start, row-rule-inset-cap-end, and row-rule-inset-junction-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `row-rule-inset-cap-start`, `row-rule-inset-junction-start`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-inset-start

### P547 row-rule-style

The `row-rule-style` setting belongs to draft gap decoration; its grammar and applicability below define the row rule style contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-style-list> | <auto-line-style-list>`

Initial: none. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-style

### P548 row-rule-visibility-items

The `row-rule-visibility-items` setting belongs to draft gap decoration; its grammar and applicability below define the row rule visibility items contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `all | around | between | normal`

Initial: normal. Inherited: no. Applies to: grid containers and multicol containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-visibility-items

### P549 row-rule-width

The `row-rule-width` setting belongs to draft gap decoration; its grammar and applicability below define the row rule width contract. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Family/use case: Draft gap decoration. Use only after confirming the specific gap-decoration module and implementation; a drawn rule is not a layout track.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<line-width-list> | <auto-line-width-list>`

Initial: medium. Inherited: no. Applies to: grid containers, flex containers, multicol containers, and grid lanes containers.

Percentages: n/a. Computed value: list of absolute lengths, snapped as a border width. Animation: repeatable list, see § 4.7 Interpolation of list values..

Source: https://drafts.csswg.org/css-gaps-1/#propdef-row-rule-width

### P550 ruby-align

The `ruby-align` setting belongs to ruby annotation layout; its grammar and applicability below define the ruby align contract. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Family/use case: Ruby annotation layout. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `start | center | space-between | space-around`

Initial: space-around. Inherited: yes. Applies to: ruby bases, ruby annotations, ruby base containers, ruby annotation containers.

Percentages: n/a. Computed value: specified keyword. Animation: by computed value type.

Source: https://drafts.csswg.org/css-ruby-1/#propdef-ruby-align

### P551 ruby-merge

The `ruby-merge` setting belongs to ruby annotation layout; its grammar and applicability below define the ruby merge contract. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Family/use case: Ruby annotation layout. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `separate | merge | auto`

Initial: separate. Inherited: yes. Applies to: interlinear ruby annotation containers.

Percentages: n/a. Computed value: specified keyword. Animation: by computed value type.

Source: https://drafts.csswg.org/css-ruby-1/#propdef-ruby-merge

### P552 ruby-overhang

The `ruby-overhang` setting belongs to ruby annotation layout; its grammar and applicability below define the ruby overhang contract. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Family/use case: Ruby annotation layout. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | spaces`

Initial: auto. Inherited: yes. Applies to: ruby annotation containers.

Percentages: n/a. Computed value: specified keyword. Animation: by computed value type.

Source: https://drafts.csswg.org/css-ruby-1/#propdef-ruby-overhang

### P553 ruby-position

The `ruby-position` setting belongs to ruby annotation layout; its grammar and applicability below define the ruby position contract. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Family/use case: Ruby annotation layout. Use for language annotations in valid ruby markup; do not simulate general tooltips with ruby layout.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ alternate || [ over | under ] ] | inter-character`

Initial: alternate. Inherited: yes. Applies to: ruby annotation containers.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-ruby-1/#propdef-ruby-position

### P554 rule

The `rule` setting belongs to draft gap decoration; its grammar and applicability below define the rule contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule'>`

Initial: see individual properties. Inherited: no. Applies to: Same as column-rule and row-rule.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule`, `row-rule`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule

### P555 rule-break

The `rule-break` setting belongs to draft gap decoration; its grammar and applicability below define the rule break contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-break'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-break and row-rule-break.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-break`, `row-rule-break`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-break

### P556 rule-color

The `rule-color` setting belongs to draft gap decoration; its grammar and applicability below define the rule color contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-color'>`

Initial: see individual properties. Inherited: no. Applies to: Same as column-rule-color and row-rule-color.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-color`, `row-rule-color`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-color

### P557 rule-inset

The `rule-inset` setting belongs to draft gap decoration; its grammar and applicability below define the rule inset contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset and row-rule-inset.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset`, `row-rule-inset`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-inset

### P558 rule-inset-cap

The `rule-inset-cap` setting belongs to draft gap decoration; its grammar and applicability below define the rule inset cap contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset-cap'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-cap and row-rule-inset-cap.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-cap`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-inset-cap

### P559 rule-inset-end

The `rule-inset-end` setting belongs to draft gap decoration; its grammar and applicability below define the rule inset end contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset-end'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-end and row-rule-inset-end.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-end`, `row-rule-inset-end`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-inset-end

### P560 rule-inset-junction

The `rule-inset-junction` setting belongs to draft gap decoration; its grammar and applicability below define the rule inset junction contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset-junction'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-junction and row-rule-inset-junction.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-junction`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-inset-junction

### P561 rule-inset-start

The `rule-inset-start` setting belongs to draft gap decoration; its grammar and applicability below define the rule inset start contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-inset-start'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-inset-start and row-rule-inset-start.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-inset-start`, `row-rule-inset-start`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-inset-start

### P562 rule-overlap

The `rule-overlap` setting belongs to draft gap decoration; its grammar and applicability below define the rule overlap contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `row-over-column | column-over-row`

Initial: row-over-column. Inherited: no. Applies to: grid containers, flex containers, and grid lanes containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-overlap

### P563 rule-style

The `rule-style` setting belongs to draft gap decoration; its grammar and applicability below define the rule style contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-style'>`

Initial: see individual properties. Inherited: no. Applies to: Same as column-rule-style and row-rule-style.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-style`, `row-rule-style`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-style

### P564 rule-visibility-items

The `rule-visibility-items` setting belongs to draft gap decoration; its grammar and applicability below define the rule visibility items contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-visibility-items'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: Same as column-rule-visibility-items and row-rule-visibility-items.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-visibility-items`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-visibility-items

### P565 rule-width

The `rule-width` setting belongs to draft gap decoration; its grammar and applicability below define the rule width contract. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Family/use case: Draft gap decoration. Research the defining gap-decoration grammar; do not confuse rule paint with DOM structure or borders.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'column-rule-width'>`

Initial: see individual properties. Inherited: no. Applies to: Same as column-rule-width and row-rule-width.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `column-rule-width`, `row-rule-width`.

Source: https://drafts.csswg.org/css-gaps-1/#propdef-rule-width

### P566 rx

The `rx` setting belongs to svg geometry and rendering; its grammar and applicability below define the rx contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage> | auto`

Initial: auto. Inherited: no. Applies to: 'ellipse', 'rect' elements.

Percentages: refer to the width of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#RxProperty

### P567 ry

The `ry` setting belongs to svg geometry and rendering; its grammar and applicability below define the ry contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage> | auto`

Initial: auto. Inherited: no. Applies to: 'ellipse', 'rect'.

Percentages: refer to the height of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: Not captured in source record.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#RyProperty

### P568 scale

The `scale` setting belongs to transformed geometry; its grammar and applicability below define the scale contract. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <number> | <percentage> ]{1,3}`

Initial: none. Inherited: no. Applies to: transformable elements.

Percentages: n/a. Computed value: the keyword none, or a list of 3 <number>s. Animation: by computed value, but see below for none.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-scale

### P569 scroll-axis-lock

The `scroll-axis-lock` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll axis lock contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none`

Initial: auto. Inherited: no. Applies to: scroll container elements.

Percentages: n/a. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-5/#propdef-scroll-axis-lock

### P570 scroll-behavior

Choose automatic or smooth scrolling for applicable programmatic/navigation scrolls; respect reduced-motion needs and user control.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | smooth`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: n/a. Computed value: specified value. Animation: not animatable.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-scroll-behavior

### P571 scroll-initial-target

The `scroll-initial-target` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll initial target contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | nearest`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword. Animation: none.

Source: https://drafts.csswg.org/css-scroll-snap-2/#propdef-scroll-initial-target

### P572 scroll-margin

Define target-side scroll snapping/alignment outsets; useful for fragment targets beneath a sticky header without adding visible layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>{1,4}`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: per side, an absolute length. Animation: by computed value type.

Shorthand members: `scroll-margin-top`, `scroll-margin-right`, `scroll-margin-bottom`, `scroll-margin-left`.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin

### P573 scroll-margin-block

The `scroll-margin-block` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin block contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>{1,2}`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `scroll-margin-block-start`, `scroll-margin-block-end`.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-block

### P574 scroll-margin-block-end

The `scroll-margin-block-end` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin block end contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-block-end

### P575 scroll-margin-block-start

The `scroll-margin-block-start` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin block start contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-block-start

### P576 scroll-margin-bottom

The `scroll-margin-bottom` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin bottom contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-bottom

### P577 scroll-margin-inline

The `scroll-margin-inline` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin inline contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>{1,2}`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: see individual properties. Animation: by computed value type.

Shorthand members: `scroll-margin-inline-start`, `scroll-margin-inline-end`.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-inline

### P578 scroll-margin-inline-end

The `scroll-margin-inline-end` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin inline end contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-inline-end

### P579 scroll-margin-inline-start

The `scroll-margin-inline-start` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin inline start contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-inline-start

### P580 scroll-margin-left

The `scroll-margin-left` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin left contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-left

### P581 scroll-margin-right

The `scroll-margin-right` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin right contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-right

### P582 scroll-margin-top

The `scroll-margin-top` setting belongs to scroll target spacing; its grammar and applicability below define the scroll margin top contract. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Family/use case: Scroll target spacing. Use on an anchor/snap target to account for sticky interface chrome without changing its ordinary layout margin.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length>`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-margin-top

### P583 scroll-marker-group

The `scroll-marker-group` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll marker group contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ [ before | after ] || [ links | tabs ] ]`

Initial: none. Inherited: no. Applies to: scroll containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-5/#propdef-scroll-marker-group

### P584 scroll-padding

Define the scroll container's optimal viewing region, such as space reserved for a sticky toolbar.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ auto | <length-percentage [0,∞]> ]{1,4}`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the corresponding dimension of the scroll container's scrollport. Computed value: per side, either the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Shorthand members: `scroll-padding-top`, `scroll-padding-right`, `scroll-padding-bottom`, `scroll-padding-left`.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding

### P585 scroll-padding-block

The `scroll-padding-block` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding block contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ auto | <length-percentage [0,∞]> ]{1,2}`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: see individual properties. Animation: by computed value.

Shorthand members: `scroll-padding-block-start`, `scroll-padding-block-end`.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-block

### P586 scroll-padding-block-end

The `scroll-padding-block-end` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding block end contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-block-end

### P587 scroll-padding-block-start

The `scroll-padding-block-start` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding block start contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-block-start

### P588 scroll-padding-bottom

The `scroll-padding-bottom` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding bottom contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-bottom

### P589 scroll-padding-inline

The `scroll-padding-inline` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding inline contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ auto | <length-percentage [0,∞]> ]{1,2}`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: see individual properties. Animation: by computed value.

Shorthand members: `scroll-padding-inline-start`, `scroll-padding-inline-end`.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-inline

### P590 scroll-padding-inline-end

The `scroll-padding-inline-end` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding inline end contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-inline-end

### P591 scroll-padding-inline-start

The `scroll-padding-inline-start` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding inline start contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-inline-start

### P592 scroll-padding-left

The `scroll-padding-left` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding left contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-left

### P593 scroll-padding-right

The `scroll-padding-right` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding right contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-right

### P594 scroll-padding-top

The `scroll-padding-top` setting belongs to scroll viewport insets; its grammar and applicability below define the scroll padding top contract. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Family/use case: Scroll viewport insets. Use on the scroll container to define its useful viewing region; distinguish it from padding on the content.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage [0,∞]>`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: relative to the scroll container's scrollport. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-padding-top

### P595 scroll-snap-align

Choose snap positions for an element within its scroll container; verify focus and navigation do not become trapped by the snap design.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ none | start | end | center ]{1,2}`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: two keywords. Animation: discrete.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-snap-align

### P596 scroll-snap-stop

Control whether scrolling may pass over a snap position; aggressive stopping can make large content awkward to traverse.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | always`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-snap-stop

### P597 scroll-snap-type

Choose snapping axes and strictness on a scroll container; mandatory snapping needs careful content and keyboard testing.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ x | y | block | inline | both | pair ] [ mandatory | proximity ]?`

Initial: none. Inherited: no. Applies to: scroll containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-scroll-snap-1/#propdef-scroll-snap-type

### P598 scroll-target-group

The `scroll-target-group` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll target group contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | auto`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-5/#propdef-scroll-target-group

### P599 scroll-timeline

The `scroll-timeline` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll timeline contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'scroll-timeline-name'> <'scroll-timeline-axis'>? ]#`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: not animatable.

Shorthand members: `scroll-timeline-name`, `scroll-timeline-axis`.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-scroll-timeline

### P600 scroll-timeline-axis

The `scroll-timeline-axis` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll timeline axis contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ block | inline | x | y ]#`

Initial: block. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: a list of the keywords specified. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-scroll-timeline-axis

### P601 scroll-timeline-name

The `scroll-timeline-name` setting belongs to scrolling and scroll timelines; its grammar and applicability below define the scroll timeline name contract. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Family/use case: Scrolling and scroll timelines. Use for a deliberate scrolling interaction or progressive timeline enhancement; test keyboard traversal and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | <dashed-ident> ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: list, each item either a CSS identifier or the keyword none. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-scroll-timeline-name

### P602 scrollbar-color

Choose supporting scrollbar thumb/track colors; preserve distinguishability and forced-color adaptation.

Family/use case: Specialized or draft module: css-scrollbars-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <color>{2}`

Initial: auto. Inherited: yes. Applies to: scroll containers.

Percentages: n/a. Computed value: specified keyword or two computed colors. Animation: by computed value.

Source: https://drafts.csswg.org/css-scrollbars-1/#propdef-scrollbar-color

### P603 scrollbar-gutter

Reserve room for classic scrollbars where supported to reduce layout shifts; overlay scrollbars have different space behavior.

Family/use case: Overflow and scrolling. Use for a deliberate scroll region or truncation boundary; keep focused content and essential text reachable.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | stable && both-edges?`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-overflow-3/#propdef-scrollbar-gutter

### P604 scrollbar-width

Choose supported scrollbar thickness behavior; hiding scrollbars can obscure discoverability and must not remove usable scrolling.

Family/use case: Specialized or draft module: css-scrollbars-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | thin | none`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-scrollbars-1/#propdef-scrollbar-width

### P605 shape-image-threshold

Set the alpha threshold for an image-derived float exclusion shape.

Family/use case: Float exclusion shapes. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<opacity-value>`

Initial: 0. Inherited: no. Applies to: floats.

Percentages: n/a. Computed value: specified number, clamped to the range [0,1]. Animation: by computed value.

Source: https://drafts.csswg.org/css-shapes-1/#propdef-shape-image-threshold

### P606 shape-inside

The `shape-inside` setting belongs to float exclusion shapes; its grammar and applicability below define the shape inside contract. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Family/use case: Float exclusion shapes. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | outside-shape | [ <basic-shape> || shape-box ] | <image> | display`

Initial: auto. Inherited: no. Applies to: block-level elements.

Percentages: n/a. Computed value: computed lengths for <basic-shape>, the absolute URL for <url>, otherwise as specified. Animation: as defined for <basic-shape>, otherwise discrete.

Source: https://drafts.csswg.org/css-shapes-2/#propdef-shape-inside

### P607 shape-margin

Add space around a float exclusion shape; it does not replace the element's ordinary margins.

Family/use case: Float exclusion shapes. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<length-percentage [0,∞]>`

Initial: 0. Inherited: no. Applies to: floats and initial letter boxes.

Percentages: refer to the inline size of the containing block. Computed value: computed <length-percentage> value. Animation: by computed value.

Source: https://drafts.csswg.org/css-shapes-1/#propdef-shape-margin

### P608 shape-outside

Define an exclusion shape for inline content around an applicable float; it does not clip the float's image.

Family/use case: Float exclusion shapes. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ <basic-shape> || <shape-box> ] | <image>`

Initial: none. Inherited: no. Applies to: floats and initial letter boxes.

Percentages: n/a. Computed value: as defined for <basic-shape> (with <shape-box> following, if supplied); else the computed <image>; else the keyword as specified. Animation: as defined for <basic-shape>, otherwise discrete.

Source: https://drafts.csswg.org/css-shapes-1/#propdef-shape-outside

### P609 shape-padding

The `shape-padding` setting belongs to float exclusion shapes; its grammar and applicability below define the shape padding contract. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Family/use case: Float exclusion shapes. Use to wrap text around applicable floating content; the exclusion shape is distinct from clipping the painted image.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage [0,∞]>`

Initial: 0. Inherited: no. Applies to: block-level elements.

Percentages: refer to the inline size of the containing block. Computed value: computed <length-percentage> value. Animation: by computed value.

Source: https://drafts.csswg.org/css-shapes-2/#propdef-shape-padding

### P610 shape-rendering

The `shape-rendering` setting belongs to svg geometry and rendering; its grammar and applicability below define the shape rendering contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | optimizeSpeed | crispEdges | geometricPrecision`

Initial: auto. Inherited: yes. Applies to: shapes.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#ShapeRenderingProperty

### P611 size

The `size` setting belongs to sizing constraints; its grammar and applicability below define the size contract. Use preferred/intrinsic sizes with min/max bounds; verify long content, zoom and indefinite percentage bases.

Family/use case: Sizing constraints. Use preferred/intrinsic sizes with min/max bounds; verify long content, zoom and indefinite percentage bases.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'width'> <'height'>?`

Initial: auto. Inherited: see individual properties. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `width`, `height`.

Source: https://drafts.csswg.org/css-sizing-4/#propdef-size

### P612 slider-orientation

The `slider-orientation` setting belongs to specialized or draft module: css-forms-1; its grammar and applicability below define the slider orientation contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-forms-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | left-to-right | right-to-left | top-to-bottom | bottom-to-top`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-forms-1/#propdef-slider-orientation

### P613 spatial-navigation-action

The `spatial-navigation-action` setting belongs to spatial navigation; its grammar and applicability below define the spatial navigation action contract. Research directional-navigation behavior in its actual input environment; it is not ordinary Tab navigation.

Family/use case: Spatial navigation. Research directional-navigation behavior in its actual input environment; it is not ordinary Tab navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | focus | scroll`

Initial: auto. Inherited: no. Applies to: scroll containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-spatial-nav-1/#propdef-spatial-navigation-action

### P614 spatial-navigation-contain

The `spatial-navigation-contain` setting belongs to spatial navigation; its grammar and applicability below define the spatial navigation contain contract. Research directional-navigation behavior in its actual input environment; it is not ordinary Tab navigation.

Family/use case: Spatial navigation. Research directional-navigation behavior in its actual input environment; it is not ordinary Tab navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | contain`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-spatial-nav-1/#propdef-spatial-navigation-contain

### P615 spatial-navigation-function

The `spatial-navigation-function` setting belongs to spatial navigation; its grammar and applicability below define the spatial navigation function contract. Research directional-navigation behavior in its actual input environment; it is not ordinary Tab navigation.

Family/use case: Spatial navigation. Research directional-navigation behavior in its actual input environment; it is not ordinary Tab navigation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | grid`

Initial: normal. Inherited: no. Applies to: spatial navigation containers.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-spatial-nav-1/#propdef-spatial-navigation-function

### P616 speak

The `speak` setting belongs to speech presentation; its grammar and applicability below define the speak contract. Specialized speech output preference; never rely on it to hide essential visual content from assistive technology.

Family/use case: Speech presentation. Specialized speech output preference; never rely on it to hide essential visual content from assistive technology.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | never | always`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-speech-1/#propdef-speak

### P617 speak-as

The `speak-as` setting belongs to speech presentation; its grammar and applicability below define the speak as contract. Specialized speech output preference; never rely on it to hide essential visual content from assistive technology.

Family/use case: Speech presentation. Specialized speech output preference; never rely on it to hide essential visual content from assistive technology.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | spell-out || digits || [ literal-punctuation | no-punctuation ]`

Initial: normal. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-speech-1/#propdef-speak-as

### P618 stop-color

The `stop-color` setting belongs to svg geometry and rendering; its grammar and applicability below define the stop color contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'color'>`

Initial: black. Inherited: no. Applies to: SVG stop elements.

Percentages: N/A. Computed value: Not captured in source record. Animation: yes; see defining interpolation rules.

Source: https://w3c.github.io/svgwg/svg2-draft/pservers.html#StopColorProperty

Metadata supplement: https://svgwg.org/svg2-draft/pservers.html#StopColorProperty

### P619 stop-opacity

The `stop-opacity` setting belongs to svg geometry and rendering; its grammar and applicability below define the stop opacity contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'opacity'>`

Initial: 1. Inherited: no. Applies to: SVG stop elements.

Percentages: N/A. Computed value: the specified value converted to a number, clamped to the range [0,1]. Animation: yes; see defining interpolation rules.

Source: https://w3c.github.io/svgwg/svg2-draft/pservers.html#StopOpacityProperty

Metadata supplement: https://svgwg.org/svg2-draft/pservers.html#StopOpacityProperty

### P620 string-set

The `string-set` setting belongs to specialized or draft module: css-content-3; its grammar and applicability below define the string set contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: css-content-3. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <custom-ident> <string>+ ]#`

Initial: none. Inherited: no. Applies to: all elements, but not pseudo-elements.

Percentages: N/A. Computed value: the keyword none or a list, each item an identifier paired with a list of string values. Animation: discrete.

Source: https://drafts.csswg.org/css-content-3/#propdef-string-set

### P621 stroke

The `stroke` setting belongs to svg stroke painting; its grammar and applicability below define the stroke contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<paint>`

Initial: none. Inherited: yes. Applies to: shapes and text content elements.

Percentages: N/A. Computed value: as specified, but with <color> values computed and <url> values made absolute. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#StrokeProperty

### P622 stroke-align

The `stroke-align` setting belongs to svg stroke painting; its grammar and applicability below define the stroke align contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `center | inset | outset`

Initial: center. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-align

### P623 stroke-alignment

The `stroke-alignment` setting belongs to svg stroke painting; its grammar and applicability below define the stroke alignment contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `center | inner | outer`

Initial: center. Inherited: yes. Applies to: shapes and text content elements.

Percentages: N/A. Computed value: as specified. Animation: Not captured in source record.

Source: https://svgwg.org/specs/strokes/#StrokeAlignmentProperty

### P624 stroke-break

The `stroke-break` setting belongs to svg stroke painting; its grammar and applicability below define the stroke break contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `bounding-box | slice | clone`

Initial: bounding-box. Inherited: ?. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-break

### P625 stroke-color

The `stroke-color` setting belongs to svg stroke painting; its grammar and applicability below define the stroke color contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<color>#`

Initial: transparent. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: the computed color. Animation: by computed value.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-color

### P626 stroke-dash-corner

The `stroke-dash-corner` setting belongs to svg stroke painting; its grammar and applicability below define the stroke dash corner contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <length>`

Initial: none. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: specified value, with lengths made absolute. Animation: by computed value if <length>, otherwise discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-dash-corner

### P627 stroke-dash-justify

The `stroke-dash-justify` setting belongs to svg stroke painting; its grammar and applicability below define the stroke dash justify contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ stretch | compress ] || [ dashes || gaps ]`

Initial: none. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: specified value, with lengths made absolute. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-dash-justify

### P628 stroke-dashadjust

The `stroke-dashadjust` setting belongs to svg stroke painting; its grammar and applicability below define the stroke dashadjust contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [stretch | compress] [dashes | gaps]?`

Initial: none. Inherited: yes. Applies to: shapes and text content elements.

Percentages: N/A. Computed value: as specified. Animation: Not captured in source record.

Source: https://svgwg.org/specs/strokes/#StrokeDashadjustProperty

### P629 stroke-dasharray

The `stroke-dasharray` setting belongs to svg stroke painting; its grammar and applicability below define the stroke dasharray contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [<length-percentage> | <number>]+#`

Initial: none. Inherited: yes. Applies to: text and SVG shapes.

Percentages: relative to the scaled viewport size. Computed value: as specified. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-dasharray

### P630 stroke-dashcorner

The `stroke-dashcorner` setting belongs to svg stroke painting; its grammar and applicability below define the stroke dashcorner contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <length>`

Initial: none. Inherited: yes. Applies to: shapes and text content elements.

Percentages: refer to the size of the current viewport (see Units). Computed value: absolute length or keyword specified. Animation: Not captured in source record.

Source: https://svgwg.org/specs/strokes/#StrokeDashcornerProperty

### P631 stroke-dashoffset

The `stroke-dashoffset` setting belongs to svg stroke painting; its grammar and applicability below define the stroke dashoffset contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage> | <number>`

Initial: 0. Inherited: yes. Applies to: text and SVG shapes.

Percentages: relative to the scaled viewport size. Computed value: as specified. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-dashoffset

### P632 stroke-image

The `stroke-image` setting belongs to svg stroke painting; its grammar and applicability below define the stroke image contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<paint>#`

Initial: none. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: as specified, with any <image> computed. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-image

### P633 stroke-linecap

The `stroke-linecap` setting belongs to svg stroke painting; its grammar and applicability below define the stroke linecap contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `butt | round | square`

Initial: butt. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-linecap

### P634 stroke-linejoin

The `stroke-linejoin` setting belongs to svg stroke painting; its grammar and applicability below define the stroke linejoin contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ crop | arcs | miter ] || [ bevel | round | fallback ]`

Initial: miter. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-linejoin

### P635 stroke-miterlimit

The `stroke-miterlimit` setting belongs to svg stroke painting; its grammar and applicability below define the stroke miterlimit contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<number>`

Initial: 4. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: a number. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-miterlimit

### P636 stroke-opacity

The `stroke-opacity` setting belongs to svg stroke painting; its grammar and applicability below define the stroke opacity contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'opacity'>`

Initial: 1. Inherited: yes. Applies to: text and SVG shapes.

Percentages: N/A. Computed value: the specified value converted to a <number>, clamped to the range [0,1]. Animation: by computed value.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-opacity

### P637 stroke-origin

The `stroke-origin` setting belongs to svg stroke painting; its grammar and applicability below define the stroke origin contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `match-parent | fill-box | stroke-box | content-box | padding-box | border-box`

Initial: match-parent. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-origin

### P638 stroke-position

The `stroke-position` setting belongs to svg stroke painting; its grammar and applicability below define the stroke position contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<position>#`

Initial: 0% 0%. Inherited: yes. Applies to: text and SVG shapes.

Percentages: n/a. Computed value: A list, each item consisting of: a pair of offsets (horizontal and vertical) from the top left origin each given as a combination of an absolute length and a percentage. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-position

### P639 stroke-repeat

The `stroke-repeat` setting belongs to svg stroke painting; its grammar and applicability below define the stroke repeat contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<repeat-style>#`

Initial: repeat. Inherited: yes. Applies to: text and SVG shapes.

Percentages: n/a. Computed value: A list, each item consisting of: two keywords, one per dimension. Animation: discrete.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-repeat

### P640 stroke-size

The `stroke-size` setting belongs to svg stroke painting; its grammar and applicability below define the stroke size contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<bg-size>#`

Initial: auto. Inherited: yes. Applies to: text and SVG shapes.

Percentages: n/a. Computed value: as specified, but with lengths made absolute and omitted auto keywords filled in. Animation: repeatable list.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-size

### P641 stroke-width

The `stroke-width` setting belongs to svg stroke painting; its grammar and applicability below define the stroke width contract. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Family/use case: SVG stroke painting. Use on an applicable vector geometry; scale, joins, dash patterns and visible contrast affect the result.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <length-percentage> | <line-width> | <number> ]#`

Initial: 1px. Inherited: yes. Applies to: text and SVG shapes.

Percentages: relative to the scaled viewport size. Computed value: the absolute length, or percentage. Animation: by computed value.

Source: https://drafts.csswg.org/fill-stroke-3/#propdef-stroke-width

### P642 tab-size

Set the advance width of tab characters in preserved whitespace contexts; it does not define keyboard tab order.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<number [0,∞]> | <length [0,∞]>`

Initial: 8. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: the specified number or absolute length. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-tab-size

### P643 table-layout

Choose automatic content-driven or fixed table layout; fixed layout needs appropriate table sizing and can truncate cell content.

Family/use case: Table formatting. Use for genuine tabular data with header associations and a plan for narrow viewports.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | fixed`

Initial: auto. Inherited: no. Applies to: table grid boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-tables-3/#propdef-table-layout

### P644 text-align

Align inline content within line boxes; start/end follow writing direction and differ from item alignment in Flexbox/Grid.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `start | end | left | right | center | <string> | justify | match-parent | justify-all`

Initial: start. Inherited: yes. Applies to: block containers.

Percentages: see individual properties. Computed value: see individual properties. Animation: discrete.

Shorthand members: `text-align-all`, `text-align-last`.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-align

### P645 text-align-all

Control the alignment of lines under the expanded text-align model; distinguish source maturity and interaction with text-align-last.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `start | end | left | right | center | <string> | justify | match-parent`

Initial: start. Inherited: yes. Applies to: block containers.

Percentages: n/a. Computed value: keyword as specified, except for match-parent which computes as defined above. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-align-all

### P646 text-align-last

Align the last line or a line before a forced break under text formatting rules.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | start | end | left | right | center | justify | match-parent`

Initial: auto. Inherited: yes. Applies to: block containers.

Percentages: n/a. Computed value: keyword as specified, except for match-parent which computes as defined above. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-align-last

### P647 text-anchor

The `text-anchor` setting belongs to svg geometry and rendering; its grammar and applicability below define the text anchor contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `start | middle | end`

Initial: start. Inherited: yes. Applies to: text content elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/text.html#TextAnchorProperty

### P648 text-autospace

The `text-autospace` setting belongs to text layout and decoration; its grammar and applicability below define the text autospace contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <autospace> | auto`

Initial: normal. Inherited: yes. Applies to: text.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-autospace

### P649 text-box

The `text-box` setting belongs to text layout and decoration; its grammar and applicability below define the text box contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | <'text-box-trim'> || <'text-box-edge'>`

Initial: normal. Inherited: no. Applies to: block containers, multi-column containers, and inline boxes.

Percentages: N/A. Computed value: the specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-text-box

### P650 text-box-edge

The `text-box-edge` setting belongs to text layout and decoration; its grammar and applicability below define the text box edge contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <text-edge>`

Initial: auto. Inherited: yes. Applies to: block containers and inline boxes.

Percentages: N/A. Computed value: the specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-text-box-edge

### P651 text-box-trim

The `text-box-trim` setting belongs to text layout and decoration; its grammar and applicability below define the text box trim contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | trim-start | trim-end | trim-both`

Initial: none. Inherited: no. Applies to: block containers, multi-column containers, and inline boxes.

Percentages: N/A. Computed value: the specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-inline-3/#propdef-text-box-trim

### P652 text-combine-upright

Combine selected text into an upright unit in vertical writing; suitable use depends on script and typographic context.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | all | [ digits <integer [2,4]>? ]`

Initial: none. Inherited: yes. Applies to: inline boxes and text.

Percentages: n/a. Computed value: specified keyword, plus integer if digits. Animation: not animatable.

Source: https://drafts.csswg.org/css-writing-modes-4/#propdef-text-combine-upright

### P653 text-decoration

Combine line, style, color and thickness where defined; omitted components reset, and underlines should remain distinguishable from text.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'text-decoration-line'> || <'text-decoration-thickness'> || <'text-decoration-style'> || <'text-decoration-color'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `text-decoration-line`, `text-decoration-thickness`, `text-decoration-style`, `text-decoration-color`.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration

### P654 text-decoration-color

Set decoration paint independently of foreground color; ensure the decoration still provides its intended cue.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color>`

Initial: currentcolor. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: computed color. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-color

### P655 text-decoration-inset

The `text-decoration-inset` setting belongs to text layout and decoration; its grammar and applicability below define the text decoration inset contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>{1,2} | auto`

Initial: 0. Inherited: no. Applies to: all elements.

Percentages: Depending on the value of box-decoration-break, either refer to the inline size of the decorating box or of each individual box fragment. Computed value: specified keyword or absolute length. Animation: by computed value.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-inset

### P656 text-decoration-line

Choose underline, overline, line-through and supported contextual alternatives; visual strike-through does not express a semantic deletion by itself.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ underline || overline || line-through || blink ] | spelling-error | grammar-error`

Initial: none. Inherited: no (but see prose, above). Applies to: all elements.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-line

### P657 text-decoration-skip

The `text-decoration-skip` setting belongs to text layout and decoration; its grammar and applicability below define the text decoration skip contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | auto`

Initial: See individual properties. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: See individual properties. Animation: discrete.

Shorthand members: `text-decoration-skip-self`, `text-decoration-skip-box`, `text-decoration-skip-spaces`, `text-decoration-skip-ink`.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-skip

### P658 text-decoration-skip-box

The `text-decoration-skip-box` setting belongs to text layout and decoration; its grammar and applicability below define the text decoration skip box contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | all`

Initial: none. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-skip-box

### P659 text-decoration-skip-ink

The `text-decoration-skip-ink` setting belongs to text layout and decoration; its grammar and applicability below define the text decoration skip ink contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none | all`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-skip-ink

### P660 text-decoration-skip-self

The `text-decoration-skip-self` setting belongs to text layout and decoration; its grammar and applicability below define the text decoration skip self contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | skip-all | [ skip-underline || skip-overline || skip-line-through ] | no-skip`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword(s) except for skip-all, see below. Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-skip-self

### P661 text-decoration-skip-spaces

The `text-decoration-skip-spaces` setting belongs to text layout and decoration; its grammar and applicability below define the text decoration skip spaces contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | all | [ start || end ]`

Initial: start end. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-skip-spaces

### P662 text-decoration-style

Choose solid/double/dotted/dashed/wavy decoration strokes.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `solid | double | dotted | dashed | wavy`

Initial: solid. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-style

### P663 text-decoration-thickness

Set decoration thickness including supported automatic/font-derived behavior; test thin lines at different scales.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | from-font | <length-percentage> | <line-width>`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-decoration-thickness

### P664 text-emphasis

Combine emphasis marks and color for applicable typography; it is distinct from HTML emphasis semantics.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<'text-emphasis-style'> || <'text-emphasis-color'>`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `text-emphasis-style`, `text-emphasis-color`.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-emphasis

### P665 text-emphasis-color

Set the paint for typographic emphasis marks.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<color>`

Initial: currentcolor. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: computed color. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-emphasis-color

### P666 text-emphasis-position

Place typographic emphasis marks relative to the text and writing mode.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ over | under ] && [ right | left ]?`

Initial: over right. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-emphasis-position

### P667 text-emphasis-skip

The `text-emphasis-skip` setting belongs to text layout and decoration; its grammar and applicability below define the text emphasis skip contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `spaces || punctuation || symbols || narrow`

Initial: spaces punctuation. Inherited: yes. Applies to: text.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-emphasis-skip

### P668 text-emphasis-style

Choose a filled/open mark, named shape or string under emphasis syntax.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [ [ filled | open ] || [ dot | circle | double-circle | triangle | sesame ] ] | <string>`

Initial: none. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: the keyword none, a pair of keywords representing the shape and fill, or a string. Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-emphasis-style

### P669 text-fit

The `text-fit` setting belongs to text layout and decoration; its grammar and applicability below define the text fit contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | grow | shrink ] [consistent | per-line | per-line-all]? <percentage>?`

Initial: none. Inherited: yes. Applies to: block containers.

Percentages: N/A. Computed value: specified keywords or computed <percentage> value. Animation: discrete.

Source: https://drafts.csswg.org/css-text-5/#propdef-text-fit

### P670 text-group-align

The `text-group-align` setting belongs to text layout and decoration; its grammar and applicability below define the text group align contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | start | end | left | right | center`

Initial: none. Inherited: no. Applies to: block containers.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-group-align

### P671 text-indent

Indent the first line and supported hanging/each-line behavior; it does not create general block padding.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <length-percentage> ] && hanging? && each-line?`

Initial: 0. Inherited: yes. Applies to: block containers.

Percentages: refers to block container's own inline-axis inner size. Computed value: computed <length-percentage> value, plus any specified keywords. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-indent

### P672 text-justify

Choose the justification method when justification is used; language, script and browser support influence results.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ auto | none | inter-word | inter-character | ruby ] || no-compress`

Initial: auto. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword (except for the distribute legacy value). Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-justify

### P673 text-orientation

Choose glyph orientation in vertical writing; it does not rotate the whole layout box like transform.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `mixed | upright | sideways`

Initial: mixed. Inherited: yes. Applies to: all elements except table row groups, rows, column groups, and columns; and text.

Percentages: n/a. Computed value: specified value. Animation: not animatable.

Source: https://drafts.csswg.org/css-writing-modes-4/#propdef-text-orientation

### P674 text-overflow

Signal clipped inline overflow with an ellipsis/string where supported; constrain the box and keep missing information available.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ clip | ellipsis | <string> | fade | <fade()> ]{1,2}`

Initial: clip. Inherited: no. Applies to: block containers.

Percentages: refer to the width of the line box. Computed value: as specified, with lengths made absolute. Animation: by computed value type.

Source: https://drafts.csswg.org/css-overflow-4/#propdef-text-overflow

### P675 text-rendering

The `text-rendering` setting belongs to svg geometry and rendering; its grammar and applicability below define the text rendering contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | optimizeSpeed | optimizeLegibility | geometricPrecision`

Initial: auto. Inherited: yes. Applies to: 'text'.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/painting.html#TextRenderingProperty

### P676 text-shadow

Paint text shadows without changing layout; shadows do not substitute for adequate foreground/background contrast.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <shadow>#`

Initial: none. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: either the keyword none or a list, each item consisting of four absolute lengths plus a computed color and optionally also an inset keyword. Animation: as shadow list.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-shadow

### P677 text-size-adjust

The `text-size-adjust` setting belongs to text layout and decoration; its grammar and applicability below define the text size adjust contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none | <percentage [0,∞]>`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: see below. Computed value: specified keyword or percentage. Animation: by computed value.

Source: https://drafts.csswg.org/css-size-adjust-1/#propdef-text-size-adjust

### P678 text-spacing

The `text-spacing` setting belongs to text layout and decoration; its grammar and applicability below define the text spacing contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | auto | <spacing-trim> || <autospace>`

Initial: see individual properties. Inherited: yes. Applies to: text.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Shorthand members: `text-spacing-trim`, `text-autospace`.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-spacing

### P679 text-spacing-trim

The `text-spacing-trim` setting belongs to text layout and decoration; its grammar and applicability below define the text spacing trim contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<spacing-trim> | auto`

Initial: normal. Inherited: yes. Applies to: text.

Percentages: N/A. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-spacing-trim

### P680 text-transform

Transform case and supported typographic forms for presentation; language-sensitive behavior does not change the stored string.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | [capitalize | uppercase | lowercase ] || full-width || full-size-kana | math-auto`

Initial: none. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-transform

### P681 text-underline-offset

Offset underlines relative to their default position; coordinate with thickness and descender handling.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | <length-percentage>`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-underline-offset

### P682 text-underline-position

Choose the underline's typographic placement under the applicable writing mode/font rules.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | [ from-font | under ] || [ left | right ]`

Initial: auto. Inherited: yes. Applies to: all elements.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-decor-4/#propdef-text-underline-position

### P683 text-wrap

Combine text wrapping mode/style under newer text modules; balance and pretty need specific support and content checks.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<'text-wrap-mode'> || <'text-wrap-style'>`

Initial: wrap. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `text-wrap-mode`, `text-wrap-style`.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-wrap

### P684 text-wrap-mode

The `text-wrap-mode` setting belongs to text layout and decoration; its grammar and applicability below define the text wrap mode contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `wrap | nowrap`

Initial: wrap. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-wrap-mode

### P685 text-wrap-style

The `text-wrap-style` setting belongs to text layout and decoration; its grammar and applicability below define the text wrap style contract. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Family/use case: Text layout and decoration. Use for language-aware readable text; verify line breaking, text spacing, zoom and the actual supporting font.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | balance | stable | pretty | avoid-short-last-line`

Initial: auto. Inherited: yes. Applies to: block containers hat establish an inline formatting context.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-text-wrap-style

### P686 timeline-scope

The `timeline-scope` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline scope contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | all | <dashed-ident>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: the keyword none, the keyword all, or a list of CSS identifiers. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-timeline-scope

### P687 timeline-trigger

The `timeline-trigger` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ <'timeline-trigger-name'> <'timeline-trigger-source'> [ <'timeline-trigger-range'> ]? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `timeline-trigger-name`, `timeline-trigger-source`, `timeline-trigger-range`.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger

### P688 timeline-trigger-activation-range

The `timeline-trigger-activation-range` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger activation range contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'timeline-trigger-activation-range-start'> <'timeline-trigger-activation-range-end'>? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `timeline-trigger-activation-range-start`, `timeline-trigger-activation-range-end`.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-activation-range

### P689 timeline-trigger-activation-range-end

The `timeline-trigger-activation-range-end` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger activation range end contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ normal | <length-percentage> | <timeline-range-name> <length-percentage>? ]#`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: relative to the specified named timeline range if one was specified, else to the entire timeline. Computed value: list, each item either the keyword normal or a timeline range and progress percentage. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-activation-range-end

### P690 timeline-trigger-activation-range-start

The `timeline-trigger-activation-range-start` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger activation range start contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ normal | <length-percentage> | <timeline-range-name> <length-percentage>? ]#`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: relative to the specified named timeline range if one was specified, else to the entire timeline. Computed value: list, each item either the keyword normal or a timeline range and progress percentage. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-activation-range-start

### P691 timeline-trigger-active-range

The `timeline-trigger-active-range` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger active range contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'timeline-trigger-active-range-start'> <'timeline-trigger-active-range-end'>? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `timeline-trigger-active-range-start`, `timeline-trigger-active-range-end`.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-active-range

### P692 timeline-trigger-active-range-end

The `timeline-trigger-active-range-end` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger active range end contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ auto | normal | <length-percentage> | <timeline-range-name> <length-percentage>? ]#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: relative to the specified named timeline range if one was specified, else to the entire timeline. Computed value: list, each item either the keyword normal or a timeline range and progress percentage. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-active-range-end

### P693 timeline-trigger-active-range-start

The `timeline-trigger-active-range-start` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger active range start contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ auto | normal | <length-percentage> | <timeline-range-name> <length-percentage>? ]#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: relative to the specified named timeline range if one was specified, else to the entire timeline. Computed value: list, each item either the keyword normal or a timeline range and progress percentage. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-active-range-start

### P694 timeline-trigger-name

The `timeline-trigger-name` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger name contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <dashed-ident>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-name

### P695 timeline-trigger-range

The `timeline-trigger-range` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger range contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'timeline-trigger-activation-range'> [ / <'timeline-trigger-active-range'> ]? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: see individual properties.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `timeline-trigger-activation-range`, `timeline-trigger-active-range`.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-range

### P696 timeline-trigger-source

The `timeline-trigger-source` setting belongs to animation timeline coordination; its grammar and applicability below define the timeline trigger source contract. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Family/use case: Animation timeline coordination. Use only with the precise supporting timeline module; timeline names and scope are not DOM IDs.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | auto | [ <dashed-ident> | <scroll()> | <view()> ]+ ]#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-timeline-trigger-source

### P697 top

Set the physical top inset for positioned boxes; sticky requires a relevant inset and sufficient scroll space.

Family/use case: Positioning. Use for a sticky header or deliberate overlay after identifying the containing block and scroll/stacking contexts.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <length-percentage> | <anchor()> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: refer to size of containing block; see prose. Computed value: the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-position-3/#propdef-top

### P698 touch-action

Declare permitted direct-manipulation gestures before an interaction starts; do not disable user zoom without a strong accessible design requirement.

Family/use case: Specialized or draft module: linked specification. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | none | [ [ pan-x | pan-left | pan-right ] || [ pan-y | pan-up | pan-down ] || pinch-zoom ] | manipulation`

Initial: auto. Inherited: no. Applies to: all elements except: non-replaced inline elements, table rows, row groups, table columns, and column groups..

Percentages: N/A. Computed value: Same as specified value. Animation: not animatable.

Source: https://compat.spec.whatwg.org/#propdef-touch-action

### P699 transform

Apply a composed transform list to rendering; functions are order-dependent and can establish containing/stacking contexts.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <transform-list>`

Initial: none. Inherited: no. Applies to: transformable elements.

Percentages: refer to the size of reference box. Computed value: as specified, but with lengths made absolute. Animation: transform list, see interpolation rules.

Source: https://drafts.csswg.org/css-transforms-1/#propdef-transform

### P700 transform-box

Choose the reference box for transforms, especially across HTML and SVG contexts.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `content-box | border-box | fill-box | stroke-box | view-box`

Initial: view-box. Inherited: no. Applies to: transformable elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-transforms-1/#propdef-transform-box

### P701 transform-origin

Choose the origin around which transforms are applied; percentages resolve against the selected reference box.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ left | center | right | top | bottom | <length-percentage> ] | [ left | center | right | <length-percentage> ] [ top | center | bottom | <length-percentage> ] <length>? | [ [ center | left | right ] && [ center | top | bottom ] ] <length>?`

Initial: 50% 50%. Inherited: no. Applies to: transformable elements.

Percentages: refer to the size of reference box. Computed value: see background-position. Animation: by computed value.

Source: https://drafts.csswg.org/css-transforms-1/#propdef-transform-origin

### P702 transform-style

Choose flat or preserve-3d behavior for transformed descendants under grouping-property constraints.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `flat | preserve-3d`

Initial: flat. Inherited: no. Applies to: transformable elements.

Percentages: N/A. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-transform-style

### P703 transition

Combine the property/duration/easing/delay/behavior list; prefer named properties rather than animating every incidental style change.

Family/use case: State transitions. Use for a bounded optional visual change; state correctness must survive cancellation and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<single-transition>#`

Initial: see individual properties. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: see individual properties. Animation: not animatable.

Shorthand members: `transition-property`, `transition-duration`, `transition-timing-function`, `transition-delay`, `transition-behavior`.

Source: https://drafts.csswg.org/css-transitions-1/#propdef-transition

### P704 transition-behavior

Allow supported discrete-property transitions where appropriate; this does not make every discrete change interpolate smoothly.

Family/use case: State transitions. Use for a bounded optional visual change; state correctness must survive cancellation and reduced motion.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<transition-behavior-value>#`

Initial: normal. Inherited: no. Applies to: All elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-transitions-2/#propdef-transition-behavior

### P705 transition-delay

Offset the start of a transition; a negative delay begins partway through its interpolation.

Family/use case: State transitions. Use for a bounded optional visual change; state correctness must survive cancellation and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<time>#`

Initial: 0s. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a duration. Animation: not animatable.

Source: https://drafts.csswg.org/css-transitions-1/#propdef-transition-delay

### P706 transition-duration

Set the transition interval; zero-duration changes need a cleanup policy that does not rely on transitionend.

Family/use case: State transitions. Use for a bounded optional visual change; state correctness must survive cancellation and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<time [0s,∞]>#`

Initial: 0s. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: list, each item a duration. Animation: not animatable.

Source: https://drafts.csswg.org/css-transitions-1/#propdef-transition-duration

### P707 transition-property

Select which changed properties transition; list matching and shorthand expansion follow CSS transition rules.

Family/use case: State transitions. Use for a bounded optional visual change; state correctness must survive cancellation and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `none | <single-transition-property>#`

Initial: all. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: the keyword none else a list of identifiers. Animation: not animatable.

Source: https://drafts.csswg.org/css-transitions-1/#propdef-transition-property

### P708 transition-timing-function

Choose easing for transition progress; it is distinct from duration and delay.

Family/use case: State transitions. Use for a bounded optional visual change; state correctness must survive cancellation and reduced motion.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<easing-function>#`

Initial: ease. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/css-transitions-1/#propdef-transition-timing-function

### P709 translate

Apply an individual translation, composing with individual rotate/scale and transform in the defined order.

Family/use case: Transformed geometry. Use for deliberate visual transformation; preserve layout allocation, focus and stacking/containing-block reasoning.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <length-percentage> [ <length-percentage> <length>? ]?`

Initial: none. Inherited: no. Applies to: transformable elements.

Percentages: relative to the width of the reference box (for the first value) or the height (for the second value). Computed value: the keyword none or a pair of computed <length-percentage> values and an absolute length. Animation: by computed value, but see below for none.

Source: https://drafts.csswg.org/css-transforms-2/#propdef-translate

### P710 trigger-scope

The `trigger-scope` setting belongs to specialized or draft module: animation-triggers-1; its grammar and applicability below define the trigger scope contract. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Family/use case: Specialized or draft module: animation-triggers-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | all | <dashed-ident>#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: not animatable.

Source: https://drafts.csswg.org/animation-triggers-1/#propdef-trigger-scope

### P711 unicode-bidi

Choose bidi embedding/isolation/override behavior; use correct semantic direction and avoid visually falsifying text order.

Family/use case: Writing modes and direction. Use for actual vertical or bidirectional content with appropriate HTML language/direction and logical geometry.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | embed | isolate | bidi-override | isolate-override | plaintext`

Initial: normal. Inherited: no. Applies to: all elements, but see prose.

Percentages: n/a. Computed value: specified value. Animation: not animatable.

Source: https://drafts.csswg.org/css-writing-modes-4/#propdef-unicode-bidi

### P712 user-select

Control selection behavior in applicable content; do not prevent users from copying ordinary educational material without a real need.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | text | none | contain | all`

Initial: auto. Inherited: no. Applies to: all elements, and optionally to the ::before and ::after pseudo-elements.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-user-select

### P713 vector-effect

The `vector-effect` setting belongs to svg geometry and rendering; its grammar and applicability below define the vector effect contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | non-scaling-stroke | non-scaling-size | non-rotation | fixed-position`

Initial: none. Inherited: no. Applies to: graphics elements and 'use'.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://w3c.github.io/svgwg/svg2-draft/coords.html#VectorEffectProperty

### P714 vertical-align

Align inline-level or table-cell boxes according to their formatting context; it does not vertically center arbitrary block containers.

Family/use case: Inline formatting and baselines. Use for typography requiring baseline/line-box control; actual font metrics and writing modes determine the result.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ first | last] || <'alignment-baseline'> || <'baseline-shift'>`

Initial: baseline. Inherited: no. Applies to: see individual properties.

Percentages: N/A. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `alignment-baseline`, `baseline-shift`, `baseline-source`.

Source: https://drafts.csswg.org/css-inline-3/#propdef-vertical-align

### P715 view-timeline

The `view-timeline` setting belongs to view progress timelines; its grammar and applicability below define the view timeline contract. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Family/use case: View progress timelines. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ <'view-timeline-name'> [ <'view-timeline-axis'> || <'view-timeline-inset'> ]? ]#`

Initial: see individual properties. Inherited: see individual properties. Applies to: all elements.

Percentages: see individual properties. Computed value: see individual properties. Animation: see individual properties.

Shorthand members: `view-timeline-name`, `view-timeline-axis`.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-view-timeline

### P716 view-timeline-axis

The `view-timeline-axis` setting belongs to view progress timelines; its grammar and applicability below define the view timeline axis contract. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Family/use case: View progress timelines. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ block | inline | x | y ]#`

Initial: block. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: a list of the keywords specified. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-view-timeline-axis

### P717 view-timeline-inset

The `view-timeline-inset` setting belongs to view progress timelines; its grammar and applicability below define the view timeline inset contract. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Family/use case: View progress timelines. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ [ auto | <length-percentage> ]{1,2} ]#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: relative to the corresponding dimension of the relevant scrollport. Computed value: a list consisting of two-value pairs representing the start and end insets each as either the keyword auto or a computed <length-percentage> value. Animation: by computed value type.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-view-timeline-inset

### P718 view-timeline-name

The `view-timeline-name` setting belongs to view progress timelines; its grammar and applicability below define the view timeline name contract. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Family/use case: View progress timelines. Use for supported visibility-relative animation timelines while keeping content usable without animation.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `[ none | <dashed-ident> ]#`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: list, each item either a CSS identifier or the keyword none. Animation: not animatable.

Source: https://drafts.csswg.org/scroll-animations-1/#propdef-view-timeline-name

### P719 view-transition-class

The `view-transition-class` setting belongs to visual transition capture; its grammar and applicability below define the view transition class contract. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Family/use case: Visual transition capture. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <custom-ident>+`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-view-transitions-2/#propdef-view-transition-class

### P720 view-transition-group

The `view-transition-group` setting belongs to visual transition capture; its grammar and applicability below define the view transition group contract. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Family/use case: Visual transition capture. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `normal | contain | nearest | <custom-ident>`

Initial: normal. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-view-transitions-2/#propdef-view-transition-group

### P721 view-transition-name

Associate an element with a supported view-transition capture name; duplicate active names can prevent the visual capture.

Family/use case: Visual transition capture. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | <custom-ident>`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-view-transitions-2/#propdef-view-transition-name

### P722 view-transition-scope

The `view-transition-scope` setting belongs to visual transition capture; its grammar and applicability below define the view transition scope contract. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Family/use case: Visual transition capture. Use for a supported view-transition enhancement; final DOM state and focus must remain correct if capture is skipped.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | all`

Initial: none. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-view-transitions-2/#propdef-view-transition-scope

### P723 visibility

Control visibility while generally preserving layout; hidden descendants and focus/accessibility behavior need context-specific verification.

Family/use case: Formatting contexts. Use to choose the inner layout and outer participation of a box while preserving semantic document structure.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `visible | hidden | force-hidden | collapse`

Initial: visible. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-display-4/#propdef-visibility

### P724 voice-balance

The `voice-balance` setting belongs to speech presentation; its grammar and applicability below define the voice balance contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<number> | left | center | right | leftwards | rightwards`

Initial: center. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: the specified value resolved to a <number> between -100 and 100 (inclusive). Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-balance

### P725 voice-duration

The `voice-duration` setting belongs to speech presentation; its grammar and applicability below define the voice duration contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <time [0s,∞]>`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-duration

### P726 voice-family

The `voice-family` setting belongs to speech presentation; its grammar and applicability below define the voice family contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ <voice-family-name> | <generic-voice> ]# | preserve`

Initial: implementation-dependent. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-family

### P727 voice-pitch

The `voice-pitch` setting belongs to speech presentation; its grammar and applicability below define the voice pitch contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<frequency [0Hz,∞]> && absolute | [ [ x-low | low | medium | high | x-high ] || [ <frequency [0Hz,∞]> | <semitones> | <percentage> ] ]`

Initial: medium. Inherited: yes. Applies to: all elements.

Percentages: refer to inherited value. Computed value: one of the predefined pitch keywords if only the keyword is specified by itself, otherwise an absolute frequency calculated by converting the keyword value (if any) to a fixed frequency based on the current voice-family and by applying the specified relative offset (if any). Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-pitch

### P728 voice-range

The `voice-range` setting belongs to speech presentation; its grammar and applicability below define the voice range contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<frequency [0Hz,∞]> && absolute | [ [ x-low | low | medium | high | x-high ] || [ <frequency [0Hz,∞]> | <semitones> | <percentage> ] ]`

Initial: medium. Inherited: yes. Applies to: all elements.

Percentages: refer to inherited value. Computed value: one of the predefined pitch keywords if only the keyword is specified by itself, otherwise an absolute frequency calculated by converting the keyword value (if any) to a fixed frequency based on the current voice-family and by applying the specified relative offset (if any). Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-range

### P729 voice-rate

The `voice-rate` setting belongs to speech presentation; its grammar and applicability below define the voice rate contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `[ normal | x-slow | slow | medium | fast | x-fast ] || <percentage [0,∞]>`

Initial: normal. Inherited: yes. Applies to: all elements.

Percentages: refer to default value. Computed value: a keyword value, and optionally also a percentage relative to the keyword (if not 100%). Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-rate

### P730 voice-stress

The `voice-stress` setting belongs to speech presentation; its grammar and applicability below define the voice stress contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | strong | moderate | none | reduced`

Initial: normal. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: specified value. Animation: discrete.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-stress

### P731 voice-volume

The `voice-volume` setting belongs to speech presentation; its grammar and applicability below define the voice volume contract. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Family/use case: Speech presentation. Specialized speech-rendering reference; it is not a dependable way to control screen-reader behavior on a web page.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `silent | [ [ x-soft | soft | medium | loud | x-loud ] || <decibel> ]`

Initial: medium. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: silent, or a keyword value and optionally also a decibel offset (if not zero). Animation: by computed value type.

Source: https://drafts.csswg.org/css-speech-1/#propdef-voice-volume

### P732 white-space

Combine whitespace collapsing and wrapping behavior; preformatted content can need a local scroll region rather than page overflow.

Family/use case: Whitespace processing. Use to choose preservation, collapse and wrapping; local preformatted scrolling should not cause ordinary page overflow.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | pre | pre-wrap | pre-line | <'white-space-collapse'> || <'text-wrap-mode'> || <'white-space-trim'>`

Initial: normal. Inherited: see individual properties. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Shorthand members: `white-space-collapse`, `text-wrap-mode`.

Source: https://drafts.csswg.org/css-text-4/#propdef-white-space

### P733 white-space-collapse

The `white-space-collapse` setting belongs to whitespace processing; its grammar and applicability below define the white space collapse contract. Use to choose preservation, collapse and wrapping; local preformatted scrolling should not cause ordinary page overflow.

Family/use case: Whitespace processing. Use to choose preservation, collapse and wrapping; local preformatted scrolling should not cause ordinary page overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `collapse | discard | preserve | preserve-breaks | preserve-spaces | break-spaces`

Initial: collapse. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-white-space-collapse

### P734 white-space-trim

The `white-space-trim` setting belongs to whitespace processing; its grammar and applicability below define the white space trim contract. Use to choose preservation, collapse and wrapping; local preformatted scrolling should not cause ordinary page overflow.

Family/use case: Whitespace processing. Use to choose preservation, collapse and wrapping; local preformatted scrolling should not cause ordinary page overflow.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | discard-before || discard-after || discard-inner`

Initial: none. Inherited: no. Applies to: inline boxes and block containers.

Percentages: n/a. Computed value: specified keyword(s). Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-white-space-trim

### P735 widows

Request a minimum number of lines after a fragmentation break; constraints can be relaxed when impossible.

Family/use case: Fragmentation. Use to improve print or multicol page breaks; impossible keep/break constraints remain subject to the formatter.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `<integer [1,∞]>`

Initial: 2. Inherited: yes. Applies to: block containers that establish an inline formatting context.

Percentages: n/a. Computed value: specified integer. Animation: by computed value type.

Source: https://drafts.csswg.org/css-break-4/#propdef-widows

### P736 width

Set a physical preferred width; constraints, intrinsic sizing and box-sizing determine the used outer dimensions.

Family/use case: Sizing. Use to express a preferred or intrinsic size while preserving text growth, user resizing and responsive constraints.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <box-size> | <anchor-size()>`

Initial: auto. Inherited: no. Applies to: all elements except non-replaced inlines.

Percentages: relative to width/height of containing block. Computed value: as specified, with <length-percentage> values computed. Animation: by computed value type, recursing into fit-content().

Grammar extensions: https://drafts.csswg.org/css-anchor-position-1/.

Source: https://drafts.csswg.org/css-sizing-3/#propdef-width

### P737 will-change

Hint at a likely future rendering change; reserve it for measured cases and release unnecessary long-lived hints.

Family/use case: Specialized or draft module: css-will-change-1. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <animateable-feature>#`

Initial: auto. Inherited: no. Applies to: all elements.

Percentages: n/a. Computed value: specified value. Animation: not animatable.

Source: https://drafts.csswg.org/css-will-change-1/#propdef-will-change

### P738 window-drag

The `window-drag` setting belongs to native controls and user interaction; its grammar and applicability below define the window drag contract. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Family/use case: Native controls and user interaction. Use for recognizable controls, visible keyboard focus and deliberate interaction affordances; visual styling does not replace semantics.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | move`

Initial: none. Inherited: yes. Applies to: all elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-ui-4/#propdef-window-drag

### P739 word-break

Choose word-breaking behavior; break-all can damage readability and is not equivalent to overflow-wrap:anywhere.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | break-all | keep-all | manual | auto-phrase | break-word`

Initial: normal. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-word-break

### P740 word-space-transform

The `word-space-transform` setting belongs to text shaping and wrapping; its grammar and applicability below define the word space transform contract. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `none | [ space | ideographic-space ] && auto-phrase?`

Initial: none. Inherited: yes. Applies to: text.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-word-space-transform

### P741 word-spacing

Adjust spacing between word separators under text-shaping rules; verify scripts and user text-spacing overrides.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | <length-percentage>`

Initial: normal. Inherited: yes. Applies to: text.

Percentages: relative to used font-size. Computed value: an absolute length and/or a percentage. Animation: by computed value type.

Source: https://drafts.csswg.org/css-text-4/#propdef-word-spacing

### P742 word-wrap

Legacy alias of overflow-wrap; use the modern property name for new rules.

Family/use case: Text shaping and wrapping. Use for readable language-aware text and verify wrapping, intrinsic sizes and user text-spacing overrides.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `normal | break-word | anywhere`

Initial: normal. Inherited: yes. Applies to: text.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-word-wrap

Metadata supplement: https://drafts.csswg.org/css-text-4/#propdef-overflow-wrap

### P743 wrap-after

The `wrap-after` setting belongs to exclusion and wrapping proposals; its grammar and applicability below define the wrap after contract. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Family/use case: Exclusion and wrapping proposals. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | avoid | avoid-line | avoid-flex | line | flex`

Initial: auto. Inherited: no. Applies to: inline-level boxes and flex items.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-wrap-after

### P744 wrap-before

The `wrap-before` setting belongs to exclusion and wrapping proposals; its grammar and applicability below define the wrap before contract. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Family/use case: Exclusion and wrapping proposals. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | avoid | avoid-line | avoid-flex | line | flex`

Initial: auto. Inherited: no. Applies to: inline-level boxes and flex items.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-wrap-before

### P745 wrap-flow

The `wrap-flow` setting belongs to exclusion and wrapping proposals; its grammar and applicability below define the wrap flow contract. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Family/use case: Exclusion and wrapping proposals. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | both | start | end | minimum | maximum | clear`

Initial: auto. Inherited: no. Applies to: block-level elements..

Percentages: N/A. Computed value: as specified except for element's whose float computed value is not none, in which case the computed value is auto.. Animation: discrete.

Source: https://drafts.csswg.org/css-exclusions-1/#propdef-wrap-flow

### P746 wrap-inside

The `wrap-inside` setting belongs to exclusion and wrapping proposals; its grammar and applicability below define the wrap inside contract. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Family/use case: Exclusion and wrapping proposals. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `auto | avoid`

Initial: auto. Inherited: no. Applies to: inline boxes.

Percentages: n/a. Computed value: specified keyword. Animation: discrete.

Source: https://drafts.csswg.org/css-text-4/#propdef-wrap-inside

### P747 wrap-through

The `wrap-through` setting belongs to exclusion and wrapping proposals; its grammar and applicability below define the wrap through contract. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Family/use case: Exclusion and wrapping proposals. Use only when the exact CSS Exclusions/fragmentation feature is implemented; ordinary layout should have a supported fallback.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `wrap | none`

Initial: wrap. Inherited: no. Applies to: block-level elements.

Percentages: N/A. Computed value: as specified. Animation: discrete.

Source: https://drafts.csswg.org/css-exclusions-1/#propdef-wrap-through

### P748 writing-mode

Choose inline/block flow orientation and line progression; combine with direction and language-aware typography.

Family/use case: Writing modes and direction. Use for actual vertical or bidirectional content with appropriate HTML language/direction and logical geometry.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `horizontal-tb | vertical-rl | vertical-lr | sideways-rl | sideways-lr`

Initial: horizontal-tb. Inherited: yes. Applies to: All elements except table row groups, table column groups, table rows, table columns, ruby base containers, ruby annotation containers.

Percentages: n/a. Computed value: specified value. Animation: not animatable.

Source: https://drafts.csswg.org/css-writing-modes-4/#propdef-writing-mode

### P749 x

The `x` setting belongs to svg geometry and rendering; its grammar and applicability below define the x contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: 'svg', 'rect', 'image', 'foreignObject' elements.

Percentages: refer to the width of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#XProperty

### P750 y

The `y` setting belongs to svg geometry and rendering; its grammar and applicability below define the y contract. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Family/use case: SVG geometry and rendering. Use on applicable SVG elements; preserve viewBox/coordinate-system reasoning and accessible diagram alternatives.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<length-percentage>`

Initial: 0. Inherited: no. Applies to: 'svg', 'rect', 'image', 'foreignObject' elements.

Percentages: refer to the height of the current SVG viewport (see Units). Computed value: an absolute length or percentage. Animation: by computed value.

Source: https://w3c.github.io/svgwg/svg2-draft/geometry.html#YProperty

### P751 z-index

Set stack level in applicable stacking contexts; a large descendant value cannot escape an ancestor context.

Family/use case: Specialized or draft module: css2. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Present in Snapshot 2025 index.

Value grammar: `auto | <integer> | inherit`

Initial: auto. Inherited: no. Applies to: positioned elements.

Percentages: N/A. Computed value: as specified. Animation: by computed value type.

Source: https://drafts.csswg.org/css2/#propdef-z-index

### P752 zoom

Scale layout through the supported CSS zoom model; it differs from transform scale and must not interfere with browser user zoom.

Family/use case: Specialized or draft module: css-viewport. Use only in the applicability context and value grammar below; specialized print, vector and research features require their own implementation checks.

Inventory status: Supplemental module record; assess maturity/support separately.

Value grammar: `<number [0,∞]> | <percentage [0,∞]>`

Initial: 1. Inherited: no. Applies to: all <length> property values of all elements.

Percentages: Converted to <number>. Computed value: as specified, but with <percentage> converted to the equivalent <number>. Animation: by computed value type.

Source: https://drafts.csswg.org/css-viewport/#propdef-zoom

### Historical Snapshot names outside the current property records

The following names occur in the Snapshot index but have no current non-vendor property record in this retrieved Webref dataset. They are retained for audit and migration, not assigned invented current grammar or browser support. Historical CSS2 aural names are particularly unsuitable as a way to control a modern screen reader.

- `azimuth`: Historical aural source direction; specialized speech output has a different modern voice model. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-azimuth

- `elevation`: Historical aural source elevation; not a visual transform or current universal speech setting. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-elevation

- `pitch`: Historical aural pitch; compare voice-pitch in the modern speech module. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-pitch

- `pitch-range`: Historical aural pitch variation; compare voice-range where a speech renderer implements it. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-pitch-range

- `play-during`: Historical aural background sound; use explicit user-controlled media rather than assuming this is a browser audio API. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-play-during

- `property-name`: An index placeholder rather than a concrete authoring property; do not write property-name as a universal configurable setting. Source: https://drafts.csswg.org/css2/#propdef-property-name

- `richness`: Historical aural voice richness; no ordinary screen-reader styling guarantee. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-richness

- `speak-header`: Historical aural table-header repetition; actual table semantics and assistive technology behavior remain essential. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-speak-header

- `speak-numeral`: Historical aural number pronunciation; do not depend on it for accessible mathematical content. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-speak-numeral

- `speak-punctuation`: Historical aural punctuation pronunciation; document semantics and AT preferences control real reading behavior. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-speak-punctuation

- `speech-rate`: Historical aural rate; compare voice-rate only in a verified speech-CSS environment. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-speech-rate

- `stress`: Historical aural stress setting; not a text-decoration control. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-stress

- `volume`: Historical aural volume; actual HTMLMediaElement volume and user controls are separate. Source: https://www.w3.org/TR/CSS2/aural.html#propdef-volume


## 24 At-rules, descriptors and selectors: supplementary inventories

These inventories reproduce factual names and grammars from the same Webref source. They include research proposals and specialized contexts; presence here is not an implementation claim. Descriptors belong to their at-rule and are not ordinary element properties. For example font-display is an @font-face descriptor, while font-size is an element property. The CSS parser has special handling for an initial @charset encoding declaration; it is not an ordinary parsed at-rule API.

### @annotation

Grammar: `@annotation { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-annotation

### @apply

Grammar: `@apply [ <dashed-ident> | <dashed-function> ] [ { <declaration-list> } ]?;`. Context: See defining module.

Source: https://drafts.csswg.org/css-mixins-1/#at-ruledef-apply

### @bottom-center

Grammar: `@bottom-center { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-bottom-center

### @bottom-left

Grammar: `@bottom-left { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-bottom-left

### @bottom-left-corner

Grammar: `@bottom-left-corner { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-bottom-left-corner

### @bottom-right

Grammar: `@bottom-right { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-bottom-right

### @bottom-right-corner

Grammar: `@bottom-right-corner { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-bottom-right-corner

### @character-variant

Grammar: `@character-variant { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-character-variant

### @charset

Grammar: `Defined in source prose`. Context: See defining module.

Source: https://drafts.csswg.org/css-syntax-3/#at-ruledef-charset

### @color-profile

Grammar: `@color-profile [<dashed-ident> | device-cmyk] { <declaration-list> }`. Context: See defining module.

- `components`: `<ident>#`; initial n/a.

- `rendering-intent`: `relative-colorimetric | absolute-colorimetric | perceptual | saturation`; initial relative-colorimetric.

- `src`: `<url>`; initial n/a.

Source: https://drafts.csswg.org/css-color-5/#at-ruledef-profile

### @container

Grammar: `@container <container-condition># { <rule-list> }`. Context: See defining module.

- `aspect-ratio`: `<ratio>`; initial not captured.

- `block-size`: `<length>`; initial not captured.

- `fallback`: `none | [ [<dashed-ident> || <try-tactic>] | <position-area-query> ]`; initial not captured.

- `height`: `<length>`; initial not captured.

- `inline-size`: `<length>`; initial not captured.

- `orientation`: `portrait | landscape`; initial not captured.

- `scrollable`: `none | top | right | bottom | left | block-start | inline-start | block-end | inline-end | x | y | block | inline`; initial not captured.

- `scrolled`: `none | top | right | bottom | left | block-start | inline-start | block-end | inline-end | x | y | block | inline`; initial not captured.

- `snapped`: `none | x | y | block | inline | both`; initial not captured.

- `stuck`: `none | top | right | bottom | left | block-start | inline-start | block-end | inline-end`; initial not captured.

- `width`: `<length>`; initial not captured.

Source: https://drafts.csswg.org/css-conditional-5/#at-ruledef-container

### @contents

Grammar: `@contents [ { <declaration-list> } ]?`. Context: See defining module.

Source: https://drafts.csswg.org/css-mixins-1/#at-ruledef-contents

### @counter-style

Grammar: `@counter-style <counter-style-name> { <declaration-list> }`. Context: See defining module.

- `additive-symbols`: `[ <integer [0,∞]> && <symbol> ]#`; initial n/a.

- `fallback`: `<counter-style-name>`; initial decimal.

- `negative`: `<symbol> <symbol>?`; initial "-".

- `pad`: `<integer [0,∞]> && <symbol>`; initial 0 "".

- `prefix`: `<symbol>`; initial "".

- `range`: `[ [ <integer> | infinite ]{2} ]# | auto`; initial auto.

- `speak-as`: `auto | bullets | numbers | words | spell-out | <counter-style-name>`; initial auto.

- `suffix`: `<symbol>`; initial ". ".

- `symbols`: `<symbol>+`; initial n/a.

- `system`: `cyclic | numeric | alphabetic | symbolic | additive | [fixed <integer>?] | [ extends <counter-style-name> ]`; initial symbolic.

Source: https://drafts.csswg.org/css-counter-styles-3/#at-ruledef-counter-style

### @custom-media

Grammar: `@custom-media <extension-name> [ <media-query-list> | true | false ] ;`. Context: See defining module.

Source: https://drafts.csswg.org/mediaqueries-5/#at-ruledef-custom-media

### @custom-selector

Grammar: `@custom-selector <custom-selector> <selector-list> ;`. Context: See defining module.

Source: https://drafts.csswg.org/css-extensions-1/#at-ruledef-custom-selector

### @else

Grammar: `@else <boolean-condition>? { <rule-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-conditional-5/#at-ruledef-else

### @font-face

Grammar: `@font-face { <declaration-list> }`. Context: See defining module.

- `ascent-override`: `[ normal | <percentage [0,∞]> ]{1,2}`; initial normal.

- `descent-override`: `[ normal | <percentage [0,∞]> ]{1,2}`; initial normal.

- `font-display`: `auto | block | swap | fallback | optional`; initial auto.

- `font-family`: `<font-family-name>`; initial N/A.

- `font-feature-settings`: `normal | <feature-tag-value>#`; initial normal.

- `font-language-override`: `normal | <string>`; initial normal.

- `font-named-instance`: `auto | <string>`; initial auto.

- `font-size`: `auto | [<number>]{1,2}`; initial auto.

- `font-style`: `auto | normal | italic | left | right | oblique [ <angle [-90deg,90deg]>{1,2} ]?`; initial auto.

- `font-variation-settings`: `normal | [ <string> <number>]#`; initial normal.

- `font-weight`: `auto | <font-weight-absolute>{1,2}`; initial auto.

- `font-width`: `auto | <'font-width'>{1,2}`; initial auto.

- `line-gap-override`: `[ normal | <percentage [0,∞]> ]{1,2}`; initial normal.

- `size-adjust`: `<percentage [0,∞]>`; initial 100%.

- `src`: `<font-src-list>`; initial N/A.

- `subscript-position-override`: `[ normal | from-font | <percentage> ]{1,2}`; initial normal.

- `subscript-size-override`: `[ normal | from-font | <percentage [0,∞]> ]{1,2}`; initial normal.

- `superscript-position-override`: `[ normal | from-font | <percentage> ]{1,2}`; initial normal.

- `superscript-size-override`: `[ normal | from-font | <percentage [0,∞]> ]{1,2}`; initial normal.

- `unicode-range`: `<unicode-range-token>#`; initial U+0-10FFFF.

Source: https://drafts.csswg.org/css-fonts-4/#at-font-face-rule

### @font-feature-values

Grammar: `@font-feature-values <font-family-name># { <declaration-rule-list> }`. Context: See defining module.

- `font-display`: `auto | block | swap | fallback | optional`; initial auto.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values

### @font-palette-values

Grammar: `@font-palette-values <dashed-ident> { <declaration-list> }`. Context: See defining module.

- `base-palette`: `light | dark | <integer [0,∞]>`; initial N/A.

- `font-family`: `<font-family-name>#`; initial N/A.

- `override-colors`: `[ <integer [0,∞]> <color> ]#`; initial N/A.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-palette-values

### @function

Grammar: `@function <function-token> <function-parameter>#? ) [ returns <css-type> ]? { <declaration-rule-list> }`. Context: See defining module.

- `result`: `<declaration-value>?`; initial n/a (see prose).

Source: https://drafts.csswg.org/css-mixins-1/#at-ruledef-function

### @historical-forms

Grammar: `@historical-forms { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-historical-forms

### @import

Grammar: `@import [ <url> | <string> ] [[ layer | layer( <layer-name> ) ] || [ scope | scope( <scope-start> | <scope-boundaries> ) ] || <supports-import-condition>]? <media-import-condition> ;`. Context: See defining module.

Source: https://drafts.csswg.org/css-cascade-6/#at-ruledef-import

### @keyframes

Grammar: `@keyframes <keyframes-name> { <qualified-rule-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes

### @layer

Grammar: `@layer <layer-name>? { <rule-list> } | @layer <layer-name>#;`. Context: See defining module.

Source: https://drafts.csswg.org/css-cascade-5/#at-ruledef-layer

### @left-bottom

Grammar: `@left-bottom { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-left-bottom

### @left-middle

Grammar: `@left-middle { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-left-middle

### @left-top

Grammar: `@left-top { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-left-top

### @location

Grammar: `<location-rule>`. Context: See defining module.

Source: https://drafts.csswg.org/css-navigation-1/#at-ruledef-location

### @media

Grammar: `@media <media-query-list> { <rule-list> }`. Context: See defining module.

- `-webkit-device-pixel-ratio`: `<number>`; initial not captured.

- `-webkit-transform-3d`: `<mq-boolean>`; initial not captured.

- `any-hover`: `none | hover`; initial not captured.

- `any-pointer`: `none | coarse | fine`; initial not captured.

- `aspect-ratio`: `<ratio>`; initial not captured.

- `color`: `<integer>`; initial not captured.

- `color-gamut`: `srgb | p3 | rec2020`; initial not captured.

- `color-index`: `<integer>`; initial not captured.

- `device-aspect-ratio`: `<ratio>`; initial not captured.

- `device-height`: `<length>`; initial not captured.

- `device-width`: `<length>`; initial not captured.

- `display-mode`: `fullscreen | standalone | minimal-ui | browser | picture-in-picture`; initial not captured.

- `display-state`: `normal | minimized | maximized | fullscreen`; initial not captured.

- `dynamic-range`: `standard | high`; initial not captured.

- `environment-blending`: `opaque | additive | subtractive`; initial not captured.

- `forced-colors`: `none | active`; initial not captured.

- `grid`: `<mq-boolean>`; initial not captured.

- `height`: `<length>`; initial not captured.

- `horizontal-viewport-segments`: `<integer>`; initial not captured.

- `hover`: `none | hover`; initial not captured.

- `inverted-colors`: `none | inverted`; initial not captured.

- `monochrome`: `<integer>`; initial not captured.

- `nav-controls`: `none | back`; initial not captured.

- `orientation`: `portrait | landscape`; initial not captured.

- `overflow-block`: `none | scroll | paged`; initial not captured.

- `overflow-inline`: `none | scroll`; initial not captured.

- `pointer`: `none | coarse | fine`; initial not captured.

- `prefers-color-scheme`: `light | dark`; initial not captured.

- `prefers-contrast`: `no-preference | less | more | custom`; initial not captured.

- `prefers-reduced-data`: `no-preference | reduce`; initial not captured.

- `prefers-reduced-motion`: `no-preference | reduce`; initial not captured.

- `prefers-reduced-transparency`: `no-preference | reduce`; initial not captured.

- `resizable`: `true | false`; initial not captured.

- `resolution`: `<resolution> | infinite`; initial not captured.

- `scan`: `interlace | progressive`; initial not captured.

- `scripting`: `none | initial-only | enabled`; initial not captured.

- `shape`: `rect | round`; initial not captured.

- `ua-color-scheme`: `light | dark`; initial not captured.

- `update`: `none | slow | fast`; initial not captured.

- `vertical-viewport-segments`: `<integer>`; initial not captured.

- `video-color-gamut`: `srgb | p3 | rec2020`; initial not captured.

- `video-dynamic-range`: `standard | high`; initial not captured.

- `width`: `<length>`; initial not captured.

Source: https://drafts.csswg.org/css-conditional-3/#at-ruledef-media

### @mixin

Grammar: `@mixin [<function-token> <function-parameter>#? ) | <ident-token> ] { <block-contents> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-mixins-1/#at-ruledef-mixin

### @namespace

Grammar: `@namespace <namespace-prefix>? [ <string> | <url> ] ;`. Context: See defining module.

Source: https://drafts.csswg.org/css-namespaces-3/#at-ruledef-namespace

### @navigation

Grammar: `@navigation <navigation-condition> { <rule-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-navigation-1/#at-ruledef-navigation

### @ornaments

Grammar: `@ornaments { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-ornaments

### @page

Grammar: `@page <page-selector-list>? { <declaration-rule-list> }`. Context: See defining module.

- `bleed`: `auto | <length>`; initial auto.

- `marks`: `none | [ crop || cross ]`; initial none.

- `page-margin-safety`: `none | clamp | add`; initial auto.

- `page-orientation`: `upright | rotate-left | rotate-right`; initial upright.

- `size`: `<length [0,∞]>{1,2} | auto | [ <page-size> || [ portrait | landscape ] ]`; initial auto.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-page

### @position-try

Grammar: `@position-try <dashed-ident> { <declaration-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-anchor-position-1/#at-ruledef-position-try

### @private

Grammar: `@private { <declaration-rule-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-mixins-1/#private

### @property

Grammar: `@property <custom-property-name># { <declaration-list> }`. Context: See defining module.

- `inherits`: `true | false`; initial true.

- `initial-value`: `<declaration-value>?`; initial the guaranteed-invalid value.

- `syntax`: `<string>`; initial "*".

Source: https://drafts.css-houdini.org/css-properties-values-api-1/#at-ruledef-property

### @right-bottom

Grammar: `@right-bottom { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-right-bottom

### @right-middle

Grammar: `@right-middle { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-right-middle

### @right-top

Grammar: `@right-top { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-right-top

### @scope

Grammar: `@scope <scope-boundaries>? { <block-contents> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-cascade-6/#at-ruledef-scope

### @starting-style

Grammar: `Defined in source prose`. Context: See defining module.

Source: https://drafts.csswg.org/css-transitions-2/#at-ruledef-starting-style

### @styleset

Grammar: `@styleset { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-styleset

### @stylistic

Grammar: `@stylistic { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-stylistic

### @supports

Grammar: `@supports <supports-condition> { <rule-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-conditional-3/#at-ruledef-supports

### @supports-condition

Grammar: `@supports-condition <supports-condition-name> { <block-contents> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-conditional-5/#at-ruledef-supports-condition

### @swash

Grammar: `@swash { <declaration-list> }`. Context: @font-feature-values.

Source: https://drafts.csswg.org/css-fonts-4/#at-ruledef-font-feature-values-swash

### @top-center

Grammar: `@top-center { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-top-center

### @top-left

Grammar: `@top-left { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-top-left

### @top-left-corner

Grammar: `@top-left-corner { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-top-left-corner

### @top-right

Grammar: `@top-right { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-top-right

### @top-right-corner

Grammar: `@top-right-corner { <declaration-list> };`. Context: See defining module.

Source: https://drafts.csswg.org/css-page-3/#at-ruledef-top-right-corner

### @view-transition

Grammar: `@view-transition { <declaration-list> }`. Context: See defining module.

- `navigation`: `auto | none`; initial none.

- `types`: `none | <view-transition-type>+`; initial none.

Source: https://drafts.csswg.org/css-view-transitions-2/#at-view-transition-rule

### @when

Grammar: `@when <boolean-condition> { <rule-list> }`. Context: See defining module.

Source: https://drafts.csswg.org/css-conditional-5/#at-ruledef-when

### Complete non-vendor selector inventory

Read this with Part 3 for specificity, tree relationships and state. Some selectors apply only in shadow, SVG, media, paged or other specialized contexts. A pseudo-element is not interchangeable with a pseudo-class.

- `::backdrop` - ::backdrop. Source: https://drafts.csswg.org/css-position-4/#selectordef-backdrop

- `::checkmark` - ::checkmark. Source: https://drafts.csswg.org/css-forms-1/#selectordef-checkmark

- `::clear-icon` - ::clear-icon. Source: https://drafts.csswg.org/css-forms-1/#selectordef-clear-icon

- `::color-swatch` - ::color-swatch. Source: https://drafts.csswg.org/css-forms-1/#selectordef-color-swatch

- `::column` - ::column. Source: https://drafts.csswg.org/css-multicol-2/#selectordef-column

- `::cue` - ::cue. Source: https://w3c.github.io/webvtt/#selectordef-cue

- `::cue-region` - ::cue-region. Source: https://w3c.github.io/webvtt/#selectordef-cue-region

- `::cue-region()` - ::cue-region(selector). Source: https://w3c.github.io/webvtt/#selectordef-cue-region-selector

- `::cue()` - ::cue(selector). Source: https://w3c.github.io/webvtt/#selectordef-cue-selector

- `::details-content` - ::details-content. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-details-content

- `::field-component` - ::field-component. Source: https://drafts.csswg.org/css-forms-1/#selectordef-field-component

- `::field-content` - ::field-content. Source: https://drafts.csswg.org/css-forms-1/#selectordef-field-content

- `::field-separator` - ::field-separator. Source: https://drafts.csswg.org/css-forms-1/#selectordef-field-separator

- `::file-selector-button` - ::file-selector-button. Source: https://drafts.csswg.org/css-forms-1/#selectordef-file-selector-button

- `::first-letter` - ::first-letter. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-first-letter

- `::first-line` - ::first-line. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-first-line

- `::grammar-error` - ::grammar-error. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-grammar-error

- `::highlight()` - ::highlight(<highlight-name-selector>). Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-highlight-highlight-name-selector

- `::interest-button` - ::interest-button. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-interest-button

- `::marker` - ::marker. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-marker

- `::nth-fragment()` - grammar in source. Source: https://drafts.csswg.org/css-overflow-5/#selectordef-nth-fragment

- `::part()` - ::part( <ident>+ ). Source: https://drafts.csswg.org/css-shadow-1/#selectordef-part

- `::picker-icon` - ::picker-icon. Source: https://drafts.csswg.org/css-forms-1/#selectordef-picker-icon

- `::picker()` - ::picker( <form-control-identifier>+ ). Source: https://drafts.csswg.org/css-forms-1/#selectordef-picker

- `::placeholder` - ::placeholder. Source: https://drafts.csswg.org/css-forms-1/#selectordef-placeholder

- `::reveal-icon` - ::reveal-icon. Source: https://drafts.csswg.org/css-forms-1/#selectordef-reveal-icon

- `::scroll-button()` - ::scroll-button( '*' | <scroll-button-direction> ). Source: https://drafts.csswg.org/css-overflow-5/#selectordef-scroll-button---scroll-button-direction

- `::scroll-marker` - ::scroll-marker. Source: https://drafts.csswg.org/css-overflow-5/#selectordef-scroll-marker

- `::scroll-marker-group` - ::scroll-marker-group. Source: https://drafts.csswg.org/css-overflow-5/#selectordef-scroll-marker-group

- `::search-text` - ::search-text. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-search-text

- `::selection` - ::selection. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-selection

- `::slider-fill` - ::slider-fill. Source: https://drafts.csswg.org/css-forms-1/#selectordef-slider-fill

- `::slider-thumb` - ::slider-thumb. Source: https://drafts.csswg.org/css-forms-1/#selectordef-slider-thumb

- `::slider-track` - ::slider-track. Source: https://drafts.csswg.org/css-forms-1/#selectordef-slider-track

- `::slotted()` - grammar in source. Source: https://drafts.csswg.org/css-shadow-1/#selectordef-slotted

- `::spelling-error` - ::spelling-error. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-spelling-error

- `::step-control` - ::step-control. Source: https://drafts.csswg.org/css-forms-1/#selectordef-step-control

- `::step-down` - ::step-down. Source: https://drafts.csswg.org/css-forms-1/#selectordef-step-down

- `::step-up` - ::step-up. Source: https://drafts.csswg.org/css-forms-1/#selectordef-step-up

- `::target-text` - ::target-text. Source: https://drafts.csswg.org/css-pseudo-4/#selectordef-target-text

- `::view-transition` - ::view-transition. Source: https://drafts.csswg.org/css-view-transitions-2/#selectordef-view-transition

- `::view-transition-group-children()` - grammar in source. Source: https://drafts.csswg.org/css-view-transitions-2/#selectordef-view-transition-group-children

- `::view-transition-group()` - grammar in source. Source: https://drafts.csswg.org/css-view-transitions-2/#selectordef-view-transition-group

- `::view-transition-image-pair()` - grammar in source. Source: https://drafts.csswg.org/css-view-transitions-2/#selectordef-view-transition-image-pair

- `::view-transition-new()` - grammar in source. Source: https://drafts.csswg.org/css-view-transitions-2/#selectordef-view-transition-new

- `::view-transition-old()` - grammar in source. Source: https://drafts.csswg.org/css-view-transitions-2/#selectordef-view-transition-old

- `:active` - :active. Source: https://drafts.csswg.org/selectors-4/#active-pseudo

- `:active-view-transition` - :active-view-transition. Source: https://drafts.csswg.org/css-view-transitions-2/#active-view-transition-pseudo

- `:active-view-transition-type()` - grammar in source. Source: https://drafts.csswg.org/css-view-transitions-2/#active-view-transition-type-pseudo

- `:after` - :after. Source: https://drafts.csswg.org/css2/#selectordef-after

- `:animated-image` - :animated-image. Source: https://drafts.csswg.org/css-image-animation-1/#selectordef-animated-image

- `:any-link` - :any-link. Source: https://drafts.csswg.org/selectors-4/#any-link-pseudo

- `:autofill` - :autofill. Source: https://drafts.csswg.org/selectors-4/#selectordef-autofill

- `:before` - :before. Source: https://drafts.csswg.org/css2/#selectordef-before

- `:blank` - :blank. Source: https://drafts.csswg.org/selectors-5/#blank-pseudo

- `:buffering` - :buffering. Source: https://drafts.csswg.org/selectors-4/#selectordef-buffering

- `:checked` - :checked. Source: https://drafts.csswg.org/selectors-4/#checked-pseudo

- `:current` - :current. Source: https://drafts.csswg.org/selectors-5/#current-pseudo

- `:current()` - grammar in source. Source: https://drafts.csswg.org/selectors-5/#selectordef-current

- `:default` - :default. Source: https://drafts.csswg.org/selectors-4/#default-pseudo

- `:defined` - :defined. Source: https://drafts.csswg.org/selectors-4/#defined-pseudo

- `:dir()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#dir-pseudo

- `:disabled` - :disabled. Source: https://drafts.csswg.org/selectors-4/#disabled-pseudo

- `:empty` - :empty. Source: https://drafts.csswg.org/selectors-4/#empty-pseudo

- `:enabled` - :enabled. Source: https://drafts.csswg.org/selectors-4/#enabled-pseudo

- `:first` - :first. Source: https://drafts.csswg.org/css2/#selectordef-first

- `:first-child` - :first-child. Source: https://drafts.csswg.org/selectors-4/#first-child-pseudo

- `:first-letter` - :first-letter. Source: https://drafts.csswg.org/css2/#selectordef-first-letter

- `:first-line` - :first-line. Source: https://drafts.csswg.org/css2/#selectordef-first-line

- `:first-of-page` - :first-of-page. Source: https://drafts.csswg.org/css-gcpm-4/#selectordef-first-of-page

- `:first-of-type` - :first-of-type. Source: https://drafts.csswg.org/selectors-4/#first-of-type-pseudo

- `:focus` - :focus. Source: https://drafts.csswg.org/selectors-4/#focus-pseudo

- `:focus-visible` - :focus-visible. Source: https://drafts.csswg.org/selectors-4/#focus-visible-pseudo

- `:focus-within` - :focus-within. Source: https://drafts.csswg.org/selectors-4/#focus-within-pseudo

- `:fullscreen` - :fullscreen. Source: https://drafts.csswg.org/selectors-4/#selectordef-fullscreen

- `:future` - :future. Source: https://drafts.csswg.org/selectors-5/#future-pseudo

- `:has-slotted` - :has-slotted. Source: https://drafts.csswg.org/css-shadow-1/#selectordef-has-slotted

- `:has()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#has-pseudo

- `:heading` - :heading. Source: https://drafts.csswg.org/selectors-5/#heading-pseudo

- `:heading()` - :heading( <level># ). Source: https://drafts.csswg.org/selectors-5/#heading-functional-pseudo

- `:high-value` - :high-value. Source: https://drafts.csswg.org/css-forms-1/#selectordef-high-value

- `:host` - :host. Source: https://drafts.csswg.org/css-shadow-1/#selectordef-host

- `:host-context()` - grammar in source. Source: https://drafts.csswg.org/css-shadow-1/#selectordef-host-context

- `:host()` - grammar in source. Source: https://drafts.csswg.org/css-shadow-1/#selectordef-host-function

- `:hover` - :hover. Source: https://drafts.csswg.org/selectors-4/#hover-pseudo

- `:in-range` - :in-range. Source: https://drafts.csswg.org/selectors-4/#in-range-pseudo

- `:indeterminate` - :indeterminate. Source: https://drafts.csswg.org/selectors-4/#indeterminate-pseudo

- `:interest-source` - :interest-source. Source: https://drafts.csswg.org/selectors-5/#selectordef-interest-source

- `:interest-target` - :interest-target. Source: https://drafts.csswg.org/selectors-5/#selectordef-interest-target

- `:invalid` - :invalid. Source: https://drafts.csswg.org/selectors-4/#invalid-pseudo

- `:is()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#matches-pseudo

- `:lang()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#lang-pseudo

- `:last-child` - :last-child. Source: https://drafts.csswg.org/selectors-4/#last-child-pseudo

- `:last-of-page` - :last-of-page. Source: https://drafts.csswg.org/css-gcpm-4/#selectordef-last-of-page

- `:last-of-type` - :last-of-type. Source: https://drafts.csswg.org/selectors-4/#last-of-type-pseudo

- `:left` - :left. Source: https://drafts.csswg.org/css2/#selectordef-left

- `:link` - :link. Source: https://drafts.csswg.org/selectors-4/#link-pseudo

- `:link-to()` - grammar in source. Source: https://drafts.csswg.org/css-navigation-1/#link-to-pseudo

- `:local-link` - :local-link. Source: https://drafts.csswg.org/selectors-5/#local-link-pseudo

- `:low-value` - :low-value. Source: https://drafts.csswg.org/css-forms-1/#selectordef-low-value

- `:matches()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#selectordef-matches

- `:modal` - :modal. Source: https://drafts.csswg.org/selectors-4/#selectordef-modal

- `:muted` - :muted. Source: https://drafts.csswg.org/selectors-4/#selectordef-muted

- `:navigation-source` - :navigation-source. Source: https://drafts.csswg.org/css-navigation-1/#navigation-source-pseudo

- `:not()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#negation-pseudo

- `:nth-child()` - :nth-child(An+B [of S]? ). Source: https://drafts.csswg.org/selectors-4/#nth-child-pseudo

- `:nth-col()` - :nth-col(An+B). Source: https://drafts.csswg.org/selectors-5/#nth-col-pseudo

- `:nth-last-child()` - :nth-last-child(An+B [of S]? ). Source: https://drafts.csswg.org/selectors-4/#nth-last-child-pseudo

- `:nth-last-col()` - :nth-last-col(An+B). Source: https://drafts.csswg.org/selectors-5/#nth-last-col-pseudo

- `:nth-last-of-type()` - :nth-last-of-type(An+B). Source: https://drafts.csswg.org/selectors-4/#nth-last-of-type-pseudo

- `:nth-of-page()` - :nth-of-page(n). Source: https://drafts.csswg.org/css-gcpm-4/#selectordef-nth-of-page-n

- `:nth-of-type()` - :nth-of-type(An+B). Source: https://drafts.csswg.org/selectors-4/#nth-of-type-pseudo

- `:nth()` - :nth( <a-n-plus-b> [of <custom-ident>]? ). Source: https://drafts.csswg.org/css-gcpm-3/#selectordef-nth

- `:only-child` - :only-child. Source: https://drafts.csswg.org/selectors-4/#only-child-pseudo

- `:only-of-type` - :only-of-type. Source: https://drafts.csswg.org/selectors-4/#only-of-type-pseudo

- `:open` - :open. Source: https://drafts.csswg.org/selectors-4/#selectordef-open

- `:optimal-value` - :optimal-value. Source: https://drafts.csswg.org/css-forms-1/#selectordef-optimal-value

- `:optional` - :optional. Source: https://drafts.csswg.org/selectors-4/#optional-pseudo

- `:out-of-range` - :out-of-range. Source: https://drafts.csswg.org/selectors-4/#out-of-range-pseudo

- `:past` - :past. Source: https://drafts.csswg.org/selectors-5/#past-pseudo

- `:paused` - :paused. Source: https://drafts.csswg.org/selectors-4/#selectordef-paused

- `:picture-in-picture` - :picture-in-picture. Source: https://drafts.csswg.org/selectors-4/#selectordef-picture-in-picture

- `:placeholder-shown` - :placeholder-shown. Source: https://drafts.csswg.org/selectors-4/#placeholder-shown-pseudo

- `:playing` - :playing. Source: https://drafts.csswg.org/selectors-4/#selectordef-playing

- `:popover-open` - :popover-open. Source: https://drafts.csswg.org/selectors-4/#selectordef-popover-open

- `:read-only` - :read-only. Source: https://drafts.csswg.org/selectors-4/#read-only-pseudo

- `:read-write` - :read-write. Source: https://drafts.csswg.org/selectors-4/#read-write-pseudo

- `:required` - :required. Source: https://drafts.csswg.org/selectors-4/#required-pseudo

- `:right` - :right. Source: https://drafts.csswg.org/css2/#selectordef-right

- `:root` - :root. Source: https://drafts.csswg.org/selectors-4/#root-pseudo

- `:scope` - :scope. Source: https://drafts.csswg.org/selectors-4/#scope-pseudo

- `:seeking` - :seeking. Source: https://drafts.csswg.org/selectors-4/#selectordef-seeking

- `:snapped` - :snapped. Source: https://drafts.csswg.org/css-scroll-snap-2/#selectordef-snapped

- `:snapped-block` - :snapped-block. Source: https://drafts.csswg.org/css-scroll-snap-2/#selectordef-snapped-block

- `:snapped-inline` - :snapped-inline. Source: https://drafts.csswg.org/css-scroll-snap-2/#selectordef-snapped-inline

- `:snapped-x` - :snapped-x. Source: https://drafts.csswg.org/css-scroll-snap-2/#selectordef-snapped-x

- `:snapped-y` - :snapped-y. Source: https://drafts.csswg.org/css-scroll-snap-2/#selectordef-snapped-y

- `:stalled` - :stalled. Source: https://drafts.csswg.org/selectors-4/#selectordef-stalled

- `:start-of-page` - :start-of-page. Source: https://drafts.csswg.org/css-gcpm-4/#selectordef-start-of-page

- `:state()` - :state( <ident> ). Source: https://drafts.csswg.org/selectors-5/#state-pseudo

- `:target` - :target. Source: https://drafts.csswg.org/selectors-4/#target-pseudo

- `:target-after` - :target-after. Source: https://drafts.csswg.org/css-overflow-5/#selectordef-target-after

- `:target-before` - :target-before. Source: https://drafts.csswg.org/css-overflow-5/#selectordef-target-before

- `:target-current` - :target-current. Source: https://drafts.csswg.org/css-overflow-5/#selectordef-target-current

- `:unchecked` - :unchecked. Source: https://drafts.csswg.org/selectors-4/#unchecked-pseudo

- `:user-invalid` - :user-invalid. Source: https://drafts.csswg.org/selectors-4/#user-invalid-pseudo

- `:user-valid` - :user-valid. Source: https://drafts.csswg.org/selectors-4/#user-valid-pseudo

- `:valid` - :valid. Source: https://drafts.csswg.org/selectors-4/#valid-pseudo

- `:visited` - :visited. Source: https://drafts.csswg.org/selectors-4/#visited-pseudo

- `:volume-locked` - :volume-locked. Source: https://drafts.csswg.org/selectors-4/#selectordef-volume-locked

- `:where()` - grammar in source. Source: https://drafts.csswg.org/selectors-4/#where-pseudo

- `:xr-overlay` - :xr-overlay. Source: https://immersive-web.github.io/dom-overlays/#selectordef-xr-overlay

- `&` - '&'. Source: https://drafts.csswg.org/css-nesting-1/#selectordef-

- `+` - '+'. Source: https://drafts.csswg.org/selectors-4/#selectordef-adjacent

- `>` - '>'. Source: https://drafts.csswg.org/selectors-4/#selectordef-child

- `||` - '|' '|'. Source: https://drafts.csswg.org/selectors-5/#selectordef-column

- `~` - '~'. Source: https://drafts.csswg.org/selectors-4/#selectordef-sibling

### CSS value and function lookup

The property grammar references reusable value types. Core types and grammar operators are explained in Part 2. This function inventory supplies all non-vendor function records from the source, including specialized and draft functions; it is a lookup aid, not a claim that every function can be used in every property. A CSS function name is not a Sass function call and may require a supporting property/context.

- `abs()`: `abs( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-abs

- `acos()`: `acos( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-acos

- `alpha()`: `alpha([from <color>] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-alpha

- `anchor-size()`: `anchor-size( [ <anchor-name> || <anchor-size> ]? , <length-percentage>? )`. Source: https://drafts.csswg.org/css-anchor-position-1/#funcdef-anchor-size

- `anchor()`: `anchor( <anchor-name>? && <anchor-side>, <length-percentage>? )`. Source: https://drafts.csswg.org/css-anchor-position-1/#funcdef-anchor

- `asin()`: `asin( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-asin

- `atan()`: `atan( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-atan

- `atan2()`: `atan2( <calc-sum>, <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-atan2

- `attr()`: `attr( <attr-name> <attr-type>? , <declaration-value>?)`. Source: https://drafts.csswg.org/css-values-5/#funcdef-attr

- `blur()`: `blur( <length>? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-blur

- `brightness()`: `brightness( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-brightness

- `calc-interpolate()`: `calc-interpolate( [ <progress-source> && [ by <easing-function> ]? && <easing-function>? ] , <input-position>{1,2} : <calc-sum> , [ <easing-function>? , <input-position>{1,2} : <calc-sum> ]#? )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-calc-interpolate

- `calc-mix()`: `calc-mix( [ <calc-sum> <percentage [0,100]>? ]# )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-calc-mix

- `calc-size()`: `calc-size( <calc-size-basis>, <calc-sum> )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-calc-size

- `calc()`: `calc( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-calc

- `change()`: `change()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-change

- `circle()`: `circle( <radial-size>? [ at <position> ]? )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-circle

- `clamp()`: `clamp( [ <calc-sum> | none ], <calc-sum>, [ <calc-sum> | none ] )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-clamp

- `click()`: `click()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-click

- `color-interpolate()`: `color-interpolate( [ <progress-source> && [ by <easing-function> ]? && <easing-function>? && <color-interpolation-method>? ] , <input-position>{1,2} : <color>, [ [ <easing-function> || <color-interpolation-method> ]?, <input-position>{1,2} : <color> ]#? )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-color-interpolate

- `color-layers()`: `color-layers([ <blend-mode>, ]? <color># )`. Source: https://drafts.csswg.org/css-color-6/#funcdef-color-layers

- `color-mix()`: `color-mix( <color-interpolation-method>? , [ <color> && <percentage [0,100]>? ]#)`. Source: https://drafts.csswg.org/css-color-5/#funcdef-color-mix

- `color()`: `color( [from <color>]? <colorspace-params> [ / [ <alpha-value> | none ] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-color

- `conic-gradient()`: `conic-gradient( [ <conic-gradient-syntax> ] )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-conic-gradient

- `content()`: `content( [ text | before | after | first-letter | marker ]? )`. Source: https://drafts.csswg.org/css-content-3/#funcdef-content

- `contrast-color()`: `contrast-color( [ [ <color> && [ tbd-fg | tbd-bg ] && <target-contrast>? ] | [ <color> && [ tbd-fg | tbd-bg ] && <target-contrast>, <color># ] ] )`. Source: https://drafts.csswg.org/css-color-6/#funcdef-contrast-color

- `contrast()`: `contrast( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-contrast

- `control-value()`: `control-value( <type>? )`. Source: https://drafts.csswg.org/css-forms-1/#funcdef-control-value

- `cos()`: `cos( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-cos

- `counter()`: `counter( <counter-name>, <counter-style>? )`. Source: https://drafts.csswg.org/css-lists-3/#funcdef-counter

- `counters()`: `counters( <counter-name>, <string>, <counter-style>? )`. Source: https://drafts.csswg.org/css-lists-3/#funcdef-counters

- `cross-fade()`: `cross-fade( <cf-image># )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-cross-fade

- `cross-origin()`: `See defining grammar`. Source: https://drafts.csswg.org/css-values-5/#funcdef-request-url-modifier-cross-origin

- `cubic-bezier()`: `cubic-bezier( [ <number [0,1]>, <number> ]#{2} )`. Source: https://drafts.csswg.org/css-easing-2/#funcdef-cubic-bezier

- `cycle()`: `cycle( <whole-value># )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-cycle

- `dblclick()`: `dblclick()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-dblclick

- `device-cmyk()`: `<legacy-device-cmyk-syntax> | <modern-device-cmyk-syntax>`. Source: https://drafts.csswg.org/css-color-5/#funcdef-device-cmyk

- `drop-shadow()`: `drop-shadow( [ <color>? && <length>{2,3} ] )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-drop-shadow

- `dynamic-range-limit-mix()`: `dynamic-range-limit-mix( [ <'dynamic-range-limit'> && <percentage [0,100]> ]# )`. Source: https://drafts.csswg.org/css-color-hdr-1/#funcdef-dynamic-range-limit-mix

- `element()`: `element( <id-selector> )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-element

- `ellipse()`: `ellipse( <radial-size>? [ at <position> ]? )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-ellipse

- `env()`: `env( <custom-ident> <integer [0,∞]>*, <declaration-value>? )`. Source: https://drafts.csswg.org/css-env-1/#funcdef-env

- `exp()`: `exp( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-exp

- `fade()`: `fade( [ <length-percentage> ] )`. Source: https://drafts.csswg.org/css-overflow-4/#funcdef-text-overflow-fade

- `filter()`: `filter( [ <image> | <string> ], <filter-value-list> )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter

- `first-valid()`: `first-valid( <declaration-value># )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-first-valid

- `fit-content()`: `fit-content( <length-percentage> )`. Source: https://drafts.csswg.org/css-grid-2/#funcdef-grid-template-columns-fit-content

- `focusin()`: `focusin()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-focusin

- `focusout()`: `focusout()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-focusout

- `grayscale()`: `grayscale( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-grayscale

- `hdr-color()`: `color-hdr([ <color> && <number [0,∞]>? ]#{2})`. Source: https://drafts.csswg.org/css-color-hdr-1/#funcdef-hdr-color

- `hsl()`: `[ <legacy-hsl-syntax> | <modern-hsl-syntax> ]`. Source: https://drafts.csswg.org/css-color-4/#funcdef-hsl

- `hsla()`: `[ <legacy-hsla-syntax> | <modern-hsla-syntax> ]`. Source: https://drafts.csswg.org/css-color-4/#funcdef-hsla

- `hue-rotate()`: `hue-rotate( [ <angle> | <zero> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-hue-rotate

- `hwb()`: `hwb([from <color>]? [<hue> | none] [<percentage> | <number> | none] [<percentage> | <number> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-hwb

- `hypot()`: `hypot( <calc-sum># )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-hypot

- `ictcp()`: `ictcp([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<percentage> | <number> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-hdr-1/#funcdef-ictcp

- `ident()`: `ident( <ident-arg>+ )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-ident

- `if()`: `if( [ <if-branch> ; ]* <if-branch> ;? )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-if

- `image-set()`: `image-set( <image-set-option># )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-image-set

- `image()`: `image( <image-tags>? [ <image-src>? , <color>? ]! )`. Source: https://drafts.csswg.org/css-images-5/#funcdef-image

- `inherit()`: `inherit( <custom-property-name>, <declaration-value>? )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-inherit

- `input()`: `input()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-input

- `inset()`: `inset( <length-percentage>{1,4} [ round <'border-radius'> ]? )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-inset

- `integrity()`: `See defining grammar`. Source: https://drafts.csswg.org/css-values-5/#funcdef-request-url-modifier-integrity

- `interpolate()`: `interpolate( [ <progress-source> && [ by <easing-function> ]? && <easing-function>? ] , <input-position>{1,2} : <whole-value>, [ <easing-function>?, <input-position>{1,2} : <whole-value> ]#? ) | interpolate( <progress-source> && [ by <easing-function> ]? && <easing-function>? of <keyframes-name> )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-interpolate

- `invert()`: `invert( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-invert

- `jzazbz()`: `jzazbz([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<percentage> | <number> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-hdr-1/#funcdef-jzazbz

- `jzczhz()`: `jzczhz([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<hue> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-hdr-1/#funcdef-jzczhz

- `lab()`: `lab([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<percentage> | <number> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-lab

- `lch()`: `lch([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<hue> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-lch

- `leader()`: `leader( <leader-type> )`. Source: https://drafts.csswg.org/css-content-3/#funcdef-leader

- `light-dark()`: `<light-dark-color> | <light-dark-image>`. Source: https://drafts.csswg.org/css-color-5/#funcdef-light-dark

- `linear-gradient()`: `linear-gradient( [ <linear-gradient-syntax> ] )`. Source: https://drafts.csswg.org/css-images-3/#funcdef-linear-gradient

- `linear()`: `linear( [ <number> && <percentage>{0,2} ]# )`. Source: https://drafts.csswg.org/css-easing-2/#funcdef-linear

- `log()`: `log( <calc-sum>, <calc-sum>? )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-log

- `matrix()`: `matrix( <number>#{6} )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-matrix

- `matrix3d()`: `matrix3d( <number>#{16} )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-matrix3d

- `max()`: `max( <calc-sum># )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-max

- `media()`: `media( [ <mf-plain> | <mf-boolean> | <mf-range> ] )`. Source: https://drafts.csswg.org/css-conditional-5/#funcdef-media

- `min()`: `min( <calc-sum># )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-min

- `minmax()`: `minmax(min, max)`. Source: https://drafts.csswg.org/css-grid-2/#funcdef-grid-template-columns-minmax

- `mod()`: `mod( <calc-sum>, <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-mod

- `oklab()`: `oklab([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<percentage> | <number> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-oklab

- `oklch()`: `oklch([from <color>]? [<percentage> | <number> | none] [<percentage> | <number> | none] [<hue> | none] [ / [<alpha-value> | none] ]? )`. Source: https://drafts.csswg.org/css-color-5/#funcdef-oklch

- `opacity()`: `opacity( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-opacity

- `paint()`: `paint( <ident>, <declaration-value>? )`. Source: https://drafts.css-houdini.org/css-paint-api-1/#funcdef-paint

- `palette-mix()`: `palette-mix( <color-interpolation-method>? , [ <'font-palette'> && <percentage [0,100]>? ]# )`. Source: https://drafts.csswg.org/css-fonts-4/#funcdef-palette-mix

- `param()`: `param( <param-spec> , <declaration-value>? )`. Source: https://drafts.csswg.org/css-link-params-1/#funcdef-param

- `path()`: `path( <'fill-rule'>? , <string> )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-path

- `perspective()`: `perspective( [ <length [0,∞]> | none ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-perspective

- `pointer()`: `pointer( [ <pointer-source> || <pointer-axis> ]? )`. Source: https://drafts.csswg.org/pointer-animations-1/#funcdef-pointer

- `pointerdown()`: `pointerdown()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-pointerdown

- `pointerenter()`: `pointerenter()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-pointerenter

- `pointerleave()`: `pointerleave()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-pointerleave

- `pointerup()`: `pointerup()`. Source: https://drafts.csswg.org/animation-triggers-1/#funcdef-pointerup

- `polygon()`: `polygon( <'fill-rule'>? [ round <length> ]? , [<length-percentage> <length-percentage>]# )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-polygon

- `pow()`: `pow( <calc-sum>, <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-pow

- `progress()`: `progress(no-clamp? <calc-sum>, <calc-sum>, <calc-sum>)`. Source: https://drafts.csswg.org/css-values-5/#funcdef-progress

- `radial-gradient()`: `radial-gradient( [ <radial-gradient-syntax> ] )`. Source: https://drafts.csswg.org/css-images-3/#funcdef-radial-gradient

- `random-item()`: `random-item( <random-key> , [ <declaration-value>? ]# )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-random-item

- `random()`: `random( <random-key>? , <calc-sum>, <calc-sum>, <calc-sum>? )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-random

- `ray()`: `ray( <angle> && <ray-size>? && contain? && [at <position>]? )`. Source: https://drafts.csswg.org/motion-1/#funcdef-ray

- `rect()`: `rect( [ <length-percentage> | auto ]{4} [ round <'border-radius'> ]? )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-rect

- `rect()`: `rect( <top>, <right>, <bottom>, <left> )`. Source: https://drafts.csswg.org/css-masking-1/#funcdef-clip-rect

- `referrer-policy()`: `See defining grammar`. Source: https://drafts.csswg.org/css-values-5/#funcdef-request-url-modifier-referrer-policy

- `rem()`: `rem( <calc-sum>, <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-rem

- `repeat()`: `See defining grammar`. Source: https://drafts.csswg.org/css-gaps-1/#funcdef-repeat-line-color-repeat

- `repeat()`: `See defining grammar`. Source: https://drafts.csswg.org/css-grid-2/#funcdef-track-repeat-repeat

- `repeating-conic-gradient()`: `repeating-conic-gradient( [ <conic-gradient-syntax> ] )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-repeating-conic-gradient

- `repeating-linear-gradient()`: `repeating-linear-gradient( [ <linear-gradient-syntax> ] )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-repeating-linear-gradient

- `repeating-radial-gradient()`: `repeating-radial-gradient( [ <radial-gradient-syntax> ] )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-repeating-radial-gradient

- `rgb()`: `[ <legacy-rgb-syntax> | <modern-rgb-syntax> ]`. Source: https://drafts.csswg.org/css-color-4/#funcdef-rgb

- `rgba()`: `[ <legacy-rgba-syntax> | <modern-rgba-syntax> ]`. Source: https://drafts.csswg.org/css-color-4/#funcdef-rgba

- `rotate()`: `rotate( [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-rotate

- `rotate3d()`: `rotate3d( <number> , <number> , <number> , [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-rotate3d

- `rotateX()`: `rotateX( [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-rotatex

- `rotateY()`: `rotateY( [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-rotatey

- `rotateZ()`: `rotateZ( [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-rotatez

- `round()`: `round( <rounding-strategy>?, <calc-sum>, <calc-sum>? )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-round

- `running()`: `running( <custom-ident> )`. Source: https://drafts.csswg.org/css-gcpm-3/#funcdef-running

- `saturate()`: `saturate( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-saturate

- `scale()`: `scale( [ <number> | <percentage> ]#{1,2} )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-scale

- `scale()`: `scale( <number> , <number>? )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-scale

- `scale3d()`: `scale3d( [ <number> | <percentage> ]#{3} )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-scale3d

- `scaleX()`: `scaleX( [ <number> | <percentage> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-scalex

- `scaleX()`: `scaleX( <number> )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-scalex

- `scaleY()`: `scaleY( [ <number> | <percentage> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-scaley

- `scaleY()`: `scaleY( <number> )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-scaley

- `scaleZ()`: `scaleZ( [ <number> | <percentage> ] )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-scalez

- `scroll()`: `scroll( [ <scroller> || <axis> ]? )`. Source: https://drafts.csswg.org/scroll-animations-1/#funcdef-scroll

- `sepia()`: `sepia( [ <number> | <percentage> ]? )`. Source: https://drafts.csswg.org/filter-effects-1/#funcdef-filter-sepia

- `shape()`: `shape( <'fill-rule'>? from <position> , <shape-command># )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-shape

- `sibling-count()`: `sibling-count()`. Source: https://drafts.csswg.org/css-values-5/#funcdef-sibling-count

- `sibling-index()`: `sibling-index()`. Source: https://drafts.csswg.org/css-values-5/#funcdef-sibling-index

- `sign()`: `sign( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-sign

- `sin()`: `sin( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-sin

- `skew()`: `skew( [ <angle> | <zero> ] , [ <angle> | <zero> ]? )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-skew

- `skewX()`: `skewX( [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-skewx

- `skewY()`: `skewY( [ <angle> | <zero> ] )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-skewy

- `snap-block()`: `snap-block( <length> , [ start | end | near ]? )`. Source: https://drafts.csswg.org/css-page-floats-3/#funcdef-float-snap-block

- `snap-inline()`: `snap-inline( <length> , [ left | right | near ]? )`. Source: https://drafts.csswg.org/css-page-floats-3/#funcdef-float-snap-inline

- `sqrt()`: `sqrt( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-sqrt

- `src()`: `src( <string> <url-modifier>* )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-src

- `steps()`: `steps( <integer>, <step-position>?)`. Source: https://drafts.csswg.org/css-easing-2/#funcdef-steps

- `string()`: `string( <custom-ident> , [ first | start | last | first-except ]? )`. Source: https://drafts.csswg.org/css-content-3/#funcdef-string

- `stripes()`: `stripes( <color-stripe># )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-stripes

- `superellipse()`: `superellipse(<number> | infinity | -infinity)`. Source: https://drafts.csswg.org/css-borders-4/#funcdef-superellipse

- `supports()`: `supports( <declaration> )`. Source: https://drafts.csswg.org/css-conditional-5/#funcdef-supports

- `symbols()`: `symbols( <symbols-type>? [ <string> | <image> ]+ )`. Source: https://drafts.csswg.org/css-counter-styles-3/#funcdef-symbols

- `tan()`: `tan( <calc-sum> )`. Source: https://drafts.csswg.org/css-values-4/#funcdef-tan

- `target-counter()`: `target-counter( [ <string> | <url> ] , <custom-ident> , <counter-style>? )`. Source: https://drafts.csswg.org/css-content-3/#funcdef-target-counter

- `target-counters()`: `target-counters( [ <string> | <url> ] , <custom-ident> , <string> , <counter-style>? )`. Source: https://drafts.csswg.org/css-content-3/#funcdef-target-counters

- `target-text()`: `target-text( [ <string> | <url> ] , [ content | before | after | first-letter ]? )`. Source: https://drafts.csswg.org/css-content-3/#target-text-function

- `transform-interpolate()`: `transform-interpolate( [ <progress-source> && [ by <easing-function> ]? && <easing-function>? ], <input-position>{1,2} : <transform-list>, [ <easing-function>?, <input-position>{1,2} : <transform-list> ]#? )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-transform-interpolate

- `transform-mix()`: `transform-mix( [ <transform-list> && <percentage [0,100]> ]# )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-transform-mix

- `translate()`: `translate( <length-percentage> , <length-percentage>? )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-translate

- `translate3d()`: `translate3d( <length-percentage> , <length-percentage> , <length> )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-translate3d

- `translateX()`: `translateX( <length-percentage> )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-translatex

- `translateY()`: `translateY( <length-percentage> )`. Source: https://drafts.csswg.org/css-transforms-1/#funcdef-transform-translatey

- `translateZ()`: `translateZ( <length> )`. Source: https://drafts.csswg.org/css-transforms-2/#funcdef-translatez

- `type()`: `type( <syntax> )`. Source: https://drafts.csswg.org/css-mixins-1/#funcdef-function-type

- `type()`: `type( <syntax> )`. Source: https://drafts.csswg.org/css-values-5/#funcdef-attr-type

- `type()`: `type( <string> )`. Source: https://drafts.csswg.org/css-images-4/#funcdef-image-set-type

- `url-pattern()`: `url-pattern( <string> )`. Source: https://drafts.csswg.org/css-navigation-1/#funcdef-url-pattern

- `url()`: `url( <string> <url-modifier>* ) | <url-token>`. Source: https://drafts.csswg.org/css-values-4/#funcdef-url

- `var()`: `var( <custom-property-name> , <declaration-value>? )`. Source: https://drafts.csswg.org/css-variables-2/#funcdef-var

- `view()`: `view( [ <axis> || <'view-timeline-inset'> ]? )`. Source: https://drafts.csswg.org/scroll-animations-1/#funcdef-view

- `wcag2()`: `See defining grammar`. Source: https://drafts.csswg.org/css-color-6/#funcdef-contrast-color-wcag2

- `xywh()`: `xywh( <length-percentage>{2} <length-percentage [0,∞]>{2} [ round <'border-radius'> ]? )`. Source: https://drafts.csswg.org/css-shapes-1/#funcdef-basic-shape-xywh


## 25 Sass built-in API inventory

This inventory was queried from the installed Dart Sass compiler using meta.module-functions and meta.module-mixins. It includes compatibility/deprecated functions that remain exposed; exposure is not a recommendation to use them. Prefer modern color-space-aware replacements described in Part 9, namespaced module access, and the exact signatures in the official module reference. Function names are namespaced at use sites, for example math.div rather than a global div call.

### sass:math

Functions (24): `math.abs()`, `math.acos()`, `math.asin()`, `math.atan()`, `math.atan2()`, `math.ceil()`, `math.clamp()`, `math.cos()`, `math.compatible()`, `math.floor()`, `math.hypot()`, `math.is-unitless()`, `math.log()`, `math.max()`, `math.min()`, `math.percentage()`, `math.pow()`, `math.random()`, `math.round()`, `math.sin()`, `math.sqrt()`, `math.tan()`, `math.unit()`, `math.div()`.

Mixins: none exposed.

Source: https://sass-lang.com/documentation/modules/math/

### sass:color

Functions (37): `color.red()`, `color.green()`, `color.blue()`, `color.mix()`, `color.invert()`, `color.hue()`, `color.saturation()`, `color.lightness()`, `color.adjust-hue()`, `color.lighten()`, `color.darken()`, `color.saturate()`, `color.desaturate()`, `color.grayscale()`, `color.hwb()`, `color.whiteness()`, `color.blackness()`, `color.opacify()`, `color.fade-in()`, `color.transparentize()`, `color.fade-out()`, `color.alpha()`, `color.opacity()`, `color.space()`, `color.to-space()`, `color.is-legacy()`, `color.is-missing()`, `color.is-in-gamut()`, `color.to-gamut()`, `color.channel()`, `color.same()`, `color.is-powerless()`, `color.complement()`, `color.adjust()`, `color.scale()`, `color.change()`, `color.ie-hex-str()`.

Mixins: none exposed.

Source: https://sass-lang.com/documentation/modules/color/

### sass:string

Functions (10): `string.unquote()`, `string.quote()`, `string.to-upper-case()`, `string.to-lower-case()`, `string.length()`, `string.insert()`, `string.index()`, `string.slice()`, `string.unique-id()`, `string.split()`.

Mixins: none exposed.

Source: https://sass-lang.com/documentation/modules/string/

### sass:list

Functions (10): `list.length()`, `list.nth()`, `list.set-nth()`, `list.join()`, `list.append()`, `list.zip()`, `list.index()`, `list.is-bracketed()`, `list.separator()`, `list.slash()`.

Mixins: none exposed.

Source: https://sass-lang.com/documentation/modules/list/

### sass:map

Functions (9): `map.get()`, `map.set()`, `map.merge()`, `map.remove()`, `map.keys()`, `map.values()`, `map.has-key()`, `map.deep-merge()`, `map.deep-remove()`.

Mixins: none exposed.

Source: https://sass-lang.com/documentation/modules/map/

### sass:selector

Functions (8): `selector.is-superselector()`, `selector.simple-selectors()`, `selector.parse()`, `selector.nest()`, `selector.append()`, `selector.extend()`, `selector.replace()`, `selector.unify()`.

Mixins: none exposed.

Source: https://sass-lang.com/documentation/modules/selector/

### sass:meta

Functions (20): `meta.feature-exists()`, `meta.inspect()`, `meta.type-of()`, `meta.keywords()`, `meta.calc-name()`, `meta.calc-args()`, `meta.accepts-content()`, `meta.global-variable-exists()`, `meta.variable-exists()`, `meta.function-exists()`, `meta.mixin-exists()`, `meta.content-exists()`, `meta.module-variables()`, `meta.module-functions()`, `meta.module-mixins()`, `meta.get-function()`, `meta.get-mixin()`, `meta.get-module()`, `meta.load()`, `meta.call()`.

Mixins: `meta.css`, `meta.load-css`, `meta.apply`.

Source: https://sass-lang.com/documentation/modules/meta/

### Complete Sass statement map

@use loads a module; @forward re-exports an API; @mixin/@include declare and invoke emitting abstractions; @function/@return compute values; @extend unifies selector relationships; @if/@else choose branches; @each/@for/@while generate bounded output; @at-root controls nesting context; @debug/@warn/@error report diagnostics. @content inserts a caller block and can pass arguments to using. Sass @import is a deprecated dependency mechanism with legacy scope behavior; a preserved CSS @import has different browser/network behavior. CSS at-rules such as @media, @supports, @layer, @container, @keyframes and @font-face are emitted according to Sass nesting/interpolation and CSS parsing rules. Silent // comments disappear; block comments can survive according to output mode and preservation rules.

Private module members, configuration, rest/keyword arguments, list/map destructuring, parent-selector values, placeholder selectors, interpolation, calculations, built-in modules and the modern importer/function/logger APIs complete the major language/tooling surface taught here. A public library should document argument names because callers can use keyword arguments. Passing an argument list can preserve keywords; meta.keywords can inspect them. @content using makes argument transfer explicit.

## 26 Bootstrap utility map: exact default generator inputs

All 97 utility entries below come from Bootstrap 5.3.8 _utilities.scss after its documented prerequisite imports. Keys called null in value maps mean the generator emits the unsuffixed class variant; they are not the literal class suffix null. Sass lists preserve their values, and maps pair suffixes with emitted CSS. Omitted booleans below default to false at this inventory layer. Some source entries are gated by framework options; an input record is not a claim that every variant is enabled in every custom build.

The full distribution and custom build differ. Utilities are generally important according to the generator configuration. Responsive values generate only at configured breakpoints; print/state variants exist only where requested. CSS custom-property references are intentionally preserved because the browser resolves them at runtime.

### Utility align

Property: `vertical-align`. Class prefix: `align`. Responsive: false. Print: false. States: none.

Values: baseline, top, middle, bottom, text-bottom, text-top.

### Utility float

Property: `float`. Class prefix: `float`. Responsive: true. Print: false. States: none.

Values: start: left; end: right; none: none.

### Utility object-fit

Property: `object-fit`. Class prefix: `object-fit`. Responsive: true. Print: false. States: none.

Values: contain: contain; cover: cover; fill: fill; scale: scale-down; none: none.

### Utility opacity

Property: `opacity`. Class prefix: `opacity`. Responsive: false. Print: false. States: none.

Values: 0: 0; 25: 0.25; 50: 0.5; 75: 0.75; 100: 1.

### Utility overflow

Property: `overflow`. Class prefix: `overflow`. Responsive: false. Print: false. States: none.

Values: auto, hidden, visible, scroll.

### Utility overflow-x

Property: `overflow-x`. Class prefix: `overflow-x`. Responsive: false. Print: false. States: none.

Values: auto, hidden, visible, scroll.

### Utility overflow-y

Property: `overflow-y`. Class prefix: `overflow-y`. Responsive: false. Print: false. States: none.

Values: auto, hidden, visible, scroll.

### Utility display

Property: `display`. Class prefix: `d`. Responsive: true. Print: true. States: none.

Values: inline, inline-block, block, grid, inline-grid, table, table-row, table-cell, flex, inline-flex, none.

### Utility shadow

Property: `box-shadow`. Class prefix: `shadow`. Responsive: false. Print: false. States: none.

Values: null: var(--bs-box-shadow); sm: var(--bs-box-shadow-sm); lg: var(--bs-box-shadow-lg); none: none.

### Utility focus-ring

Property: `CSS variable output`. Class prefix: `focus-ring`. Responsive: false. Print: false. States: none.

Values: primary: rgba(var(--bs-primary-rgb), var(--bs-focus-ring-opacity)); secondary: rgba(var(--bs-secondary-rgb), var(--bs-focus-ring-opacity)); success: rgba(var(--bs-success-rgb), var(--bs-focus-ring-opacity)); info: rgba(var(--bs-info-rgb), var(--bs-focus-ring-opacity)); warning: rgba(var(--bs-warning-rgb), var(--bs-focus-ring-opacity)); danger: rgba(var(--bs-danger-rgb), var(--bs-focus-ring-opacity)); light: rgba(var(--bs-light-rgb), var(--bs-focus-ring-opacity)); dark: rgba(var(--bs-dark-rgb), var(--bs-focus-ring-opacity)).

Other generator settings: css-var: true; css-variable-name: focus-ring-color.

### Utility position

Property: `position`. Class prefix: `position`. Responsive: false. Print: false. States: none.

Values: static, relative, absolute, fixed, sticky.

### Utility top

Property: `top`. Class prefix: `top`. Responsive: false. Print: false. States: none.

Values: 0: 0; 50: 50%; 100: 100%.

### Utility bottom

Property: `bottom`. Class prefix: `bottom`. Responsive: false. Print: false. States: none.

Values: 0: 0; 50: 50%; 100: 100%.

### Utility start

Property: `left`. Class prefix: `start`. Responsive: false. Print: false. States: none.

Values: 0: 0; 50: 50%; 100: 100%.

### Utility end

Property: `right`. Class prefix: `end`. Responsive: false. Print: false. States: none.

Values: 0: 0; 50: 50%; 100: 100%.

### Utility translate-middle

Property: `transform`. Class prefix: `translate-middle`. Responsive: false. Print: false. States: none.

Values: null: translate(-50%, -50%); x: translateX(-50%); y: translateY(-50%).

### Utility border

Property: `border`. Class prefix: `border`. Responsive: false. Print: false. States: none.

Values: 0: 0; null: var(--bs-border-width), var(--bs-border-style), var(--bs-border-color).

### Utility border-top

Property: `border-top`. Class prefix: `border-top`. Responsive: false. Print: false. States: none.

Values: 0: 0; null: var(--bs-border-width), var(--bs-border-style), var(--bs-border-color).

### Utility border-end

Property: `border-right`. Class prefix: `border-end`. Responsive: false. Print: false. States: none.

Values: 0: 0; null: var(--bs-border-width), var(--bs-border-style), var(--bs-border-color).

### Utility border-bottom

Property: `border-bottom`. Class prefix: `border-bottom`. Responsive: false. Print: false. States: none.

Values: 0: 0; null: var(--bs-border-width), var(--bs-border-style), var(--bs-border-color).

### Utility border-start

Property: `border-left`. Class prefix: `border-start`. Responsive: false. Print: false. States: none.

Values: 0: 0; null: var(--bs-border-width), var(--bs-border-style), var(--bs-border-color).

### Utility border-color

Property: `border-color`. Class prefix: `border`. Responsive: false. Print: false. States: none.

Values: primary: rgba(var(--bs-primary-rgb), var(--bs-border-opacity)); secondary: rgba(var(--bs-secondary-rgb), var(--bs-border-opacity)); success: rgba(var(--bs-success-rgb), var(--bs-border-opacity)); info: rgba(var(--bs-info-rgb), var(--bs-border-opacity)); warning: rgba(var(--bs-warning-rgb), var(--bs-border-opacity)); danger: rgba(var(--bs-danger-rgb), var(--bs-border-opacity)); light: rgba(var(--bs-light-rgb), var(--bs-border-opacity)); dark: rgba(var(--bs-dark-rgb), var(--bs-border-opacity)); black: rgba(var(--bs-black-rgb), var(--bs-border-opacity)); white: rgba(var(--bs-white-rgb), var(--bs-border-opacity)).

Other generator settings: local-vars: border-opacity: 1.

### Utility subtle-border-color

Property: `border-color`. Class prefix: `border`. Responsive: false. Print: false. States: none.

Values: primary-subtle: var(--bs-primary-border-subtle); secondary-subtle: var(--bs-secondary-border-subtle); success-subtle: var(--bs-success-border-subtle); info-subtle: var(--bs-info-border-subtle); warning-subtle: var(--bs-warning-border-subtle); danger-subtle: var(--bs-danger-border-subtle); light-subtle: var(--bs-light-border-subtle); dark-subtle: var(--bs-dark-border-subtle).

### Utility border-width

Property: `border-width`. Class prefix: `border`. Responsive: false. Print: false. States: none.

Values: 1: 1px; 2: 2px; 3: 3px; 4: 4px; 5: 5px.

### Utility border-opacity

Property: `CSS variable output`. Class prefix: `border-opacity`. Responsive: false. Print: false. States: none.

Values: 10: 0.1; 25: 0.25; 50: 0.5; 75: 0.75; 100: 1.

Other generator settings: css-var: true.

### Utility width

Property: `width`. Class prefix: `w`. Responsive: false. Print: false. States: none.

Values: 25: 25%; 50: 50%; 75: 75%; 100: 100%; auto: auto.

### Utility max-width

Property: `max-width`. Class prefix: `mw`. Responsive: false. Print: false. States: none.

Values: 100: 100%.

### Utility viewport-width

Property: `width`. Class prefix: `vw`. Responsive: false. Print: false. States: none.

Values: 100: 100vw.

### Utility min-viewport-width

Property: `min-width`. Class prefix: `min-vw`. Responsive: false. Print: false. States: none.

Values: 100: 100vw.

### Utility height

Property: `height`. Class prefix: `h`. Responsive: false. Print: false. States: none.

Values: 25: 25%; 50: 50%; 75: 75%; 100: 100%; auto: auto.

### Utility max-height

Property: `max-height`. Class prefix: `mh`. Responsive: false. Print: false. States: none.

Values: 100: 100%.

### Utility viewport-height

Property: `height`. Class prefix: `vh`. Responsive: false. Print: false. States: none.

Values: 100: 100vh.

### Utility min-viewport-height

Property: `min-height`. Class prefix: `min-vh`. Responsive: false. Print: false. States: none.

Values: 100: 100vh.

### Utility flex

Property: `flex`. Class prefix: `flex`. Responsive: true. Print: false. States: none.

Values: fill: 1, 1, auto.

### Utility flex-direction

Property: `flex-direction`. Class prefix: `flex`. Responsive: true. Print: false. States: none.

Values: row, column, row-reverse, column-reverse.

### Utility flex-grow

Property: `flex-grow`. Class prefix: `flex`. Responsive: true. Print: false. States: none.

Values: grow-0: 0; grow-1: 1.

### Utility flex-shrink

Property: `flex-shrink`. Class prefix: `flex`. Responsive: true. Print: false. States: none.

Values: shrink-0: 0; shrink-1: 1.

### Utility flex-wrap

Property: `flex-wrap`. Class prefix: `flex`. Responsive: true. Print: false. States: none.

Values: wrap, nowrap, wrap-reverse.

### Utility justify-content

Property: `justify-content`. Class prefix: `justify-content`. Responsive: true. Print: false. States: none.

Values: start: flex-start; end: flex-end; center: center; between: space-between; around: space-around; evenly: space-evenly.

### Utility align-items

Property: `align-items`. Class prefix: `align-items`. Responsive: true. Print: false. States: none.

Values: start: flex-start; end: flex-end; center: center; baseline: baseline; stretch: stretch.

### Utility align-content

Property: `align-content`. Class prefix: `align-content`. Responsive: true. Print: false. States: none.

Values: start: flex-start; end: flex-end; center: center; between: space-between; around: space-around; stretch: stretch.

### Utility align-self

Property: `align-self`. Class prefix: `align-self`. Responsive: true. Print: false. States: none.

Values: auto: auto; start: flex-start; end: flex-end; center: center; baseline: baseline; stretch: stretch.

### Utility order

Property: `order`. Class prefix: `order`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 1; 2: 2; 3: 3; 4: 4; 5: 5; first: -1; last: 6.

### Utility margin

Property: `margin`. Class prefix: `m`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility margin-x

Property: `margin-right, margin-left`. Class prefix: `mx`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility margin-y

Property: `margin-top, margin-bottom`. Class prefix: `my`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility margin-top

Property: `margin-top`. Class prefix: `mt`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility margin-end

Property: `margin-right`. Class prefix: `me`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility margin-bottom

Property: `margin-bottom`. Class prefix: `mb`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility margin-start

Property: `margin-left`. Class prefix: `ms`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem; auto: auto.

### Utility negative-margin

Property: `margin`. Class prefix: `m`. Responsive: true. Print: false. States: none.

Values: null.

### Utility negative-margin-x

Property: `margin-right, margin-left`. Class prefix: `mx`. Responsive: true. Print: false. States: none.

Values: null.

### Utility negative-margin-y

Property: `margin-top, margin-bottom`. Class prefix: `my`. Responsive: true. Print: false. States: none.

Values: null.

### Utility negative-margin-top

Property: `margin-top`. Class prefix: `mt`. Responsive: true. Print: false. States: none.

Values: null.

### Utility negative-margin-end

Property: `margin-right`. Class prefix: `me`. Responsive: true. Print: false. States: none.

Values: null.

### Utility negative-margin-bottom

Property: `margin-bottom`. Class prefix: `mb`. Responsive: true. Print: false. States: none.

Values: null.

### Utility negative-margin-start

Property: `margin-left`. Class prefix: `ms`. Responsive: true. Print: false. States: none.

Values: null.

### Utility padding

Property: `padding`. Class prefix: `p`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility padding-x

Property: `padding-right, padding-left`. Class prefix: `px`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility padding-y

Property: `padding-top, padding-bottom`. Class prefix: `py`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility padding-top

Property: `padding-top`. Class prefix: `pt`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility padding-end

Property: `padding-right`. Class prefix: `pe`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility padding-bottom

Property: `padding-bottom`. Class prefix: `pb`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility padding-start

Property: `padding-left`. Class prefix: `ps`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility gap

Property: `gap`. Class prefix: `gap`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility row-gap

Property: `row-gap`. Class prefix: `row-gap`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility column-gap

Property: `column-gap`. Class prefix: `column-gap`. Responsive: true. Print: false. States: none.

Values: 0: 0; 1: 0.25rem; 2: 0.5rem; 3: 1rem; 4: 1.5rem; 5: 3rem.

### Utility font-family

Property: `font-family`. Class prefix: `font`. Responsive: false. Print: false. States: none.

Values: monospace: var(--bs-font-monospace).

### Utility font-size

Property: `font-size`. Class prefix: `fs`. Responsive: false. Print: false. States: none.

Values: 1: 2.5rem; 2: 2rem; 3: 1.75rem; 4: 1.5rem; 5: 1.25rem; 6: 1rem.

Other generator settings: rfs: true.

### Utility font-style

Property: `font-style`. Class prefix: `fst`. Responsive: false. Print: false. States: none.

Values: italic, normal.

### Utility font-weight

Property: `font-weight`. Class prefix: `fw`. Responsive: false. Print: false. States: none.

Values: lighter: lighter; light: 300; normal: 400; medium: 500; semibold: 600; bold: 700; bolder: bolder.

### Utility line-height

Property: `line-height`. Class prefix: `lh`. Responsive: false. Print: false. States: none.

Values: 1: 1; sm: 1.25; base: 1.5; lg: 2.

### Utility text-align

Property: `text-align`. Class prefix: `text`. Responsive: true. Print: false. States: none.

Values: start: left; end: right; center: center.

### Utility text-decoration

Property: `text-decoration`. Class prefix: `text-decoration`. Responsive: false. Print: false. States: none.

Values: none, underline, line-through.

### Utility text-transform

Property: `text-transform`. Class prefix: `text`. Responsive: false. Print: false. States: none.

Values: lowercase, uppercase, capitalize.

### Utility white-space

Property: `white-space`. Class prefix: `text`. Responsive: false. Print: false. States: none.

Values: wrap: normal; nowrap: nowrap.

### Utility word-wrap

Property: `word-wrap, word-break`. Class prefix: `text`. Responsive: false. Print: false. States: none.

Values: break: break-word.

Other generator settings: rtl: false.

### Utility color

Property: `color`. Class prefix: `text`. Responsive: false. Print: false. States: none.

Values: primary: rgba(var(--bs-primary-rgb), var(--bs-text-opacity)); secondary: rgba(var(--bs-secondary-rgb), var(--bs-text-opacity)); success: rgba(var(--bs-success-rgb), var(--bs-text-opacity)); info: rgba(var(--bs-info-rgb), var(--bs-text-opacity)); warning: rgba(var(--bs-warning-rgb), var(--bs-text-opacity)); danger: rgba(var(--bs-danger-rgb), var(--bs-text-opacity)); light: rgba(var(--bs-light-rgb), var(--bs-text-opacity)); dark: rgba(var(--bs-dark-rgb), var(--bs-text-opacity)); black: rgba(var(--bs-black-rgb), var(--bs-text-opacity)); white: rgba(var(--bs-white-rgb), var(--bs-text-opacity)); body: rgba(var(--bs-body-color-rgb), var(--bs-text-opacity)); muted: var(--bs-secondary-color); black-50: rgba(0, 0, 0, 0.5); white-50: rgba(255, 255, 255, 0.5); body-secondary: var(--bs-secondary-color); body-tertiary: var(--bs-tertiary-color); body-emphasis: var(--bs-emphasis-color); reset: inherit.

Other generator settings: local-vars: text-opacity: 1.

### Utility text-opacity

Property: `CSS variable output`. Class prefix: `text-opacity`. Responsive: false. Print: false. States: none.

Values: 25: 0.25; 50: 0.5; 75: 0.75; 100: 1.

Other generator settings: css-var: true.

### Utility text-color

Property: `color`. Class prefix: `text`. Responsive: false. Print: false. States: none.

Values: primary-emphasis: var(--bs-primary-text-emphasis); secondary-emphasis: var(--bs-secondary-text-emphasis); success-emphasis: var(--bs-success-text-emphasis); info-emphasis: var(--bs-info-text-emphasis); warning-emphasis: var(--bs-warning-text-emphasis); danger-emphasis: var(--bs-danger-text-emphasis); light-emphasis: var(--bs-light-text-emphasis); dark-emphasis: var(--bs-dark-text-emphasis).

### Utility link-opacity

Property: `CSS variable output`. Class prefix: `link-opacity`. Responsive: false. Print: false. States: hover.

Values: 10: 0.1; 25: 0.25; 50: 0.5; 75: 0.75; 100: 1.

Other generator settings: css-var: true.

### Utility link-offset

Property: `text-underline-offset`. Class prefix: `link-offset`. Responsive: false. Print: false. States: hover.

Values: 1: 0.125em; 2: 0.25em; 3: 0.375em.

### Utility link-underline

Property: `text-decoration-color`. Class prefix: `link-underline`. Responsive: false. Print: false. States: none.

Values: primary: rgba(var(--bs-primary-rgb), var(--bs-link-underline-opacity)); secondary: rgba(var(--bs-secondary-rgb), var(--bs-link-underline-opacity)); success: rgba(var(--bs-success-rgb), var(--bs-link-underline-opacity)); info: rgba(var(--bs-info-rgb), var(--bs-link-underline-opacity)); warning: rgba(var(--bs-warning-rgb), var(--bs-link-underline-opacity)); danger: rgba(var(--bs-danger-rgb), var(--bs-link-underline-opacity)); light: rgba(var(--bs-light-rgb), var(--bs-link-underline-opacity)); dark: rgba(var(--bs-dark-rgb), var(--bs-link-underline-opacity)); null: rgba(var(--bs-link-color-rgb), var(--bs-link-underline-opacity, 1)).

Other generator settings: local-vars: link-underline-opacity: 1.

### Utility link-underline-opacity

Property: `CSS variable output`. Class prefix: `link-underline-opacity`. Responsive: false. Print: false. States: hover.

Values: 0: 0; 10: 0.1; 25: 0.25; 50: 0.5; 75: 0.75; 100: 1.

Other generator settings: css-var: true.

### Utility background-color

Property: `background-color`. Class prefix: `bg`. Responsive: false. Print: false. States: none.

Values: primary: rgba(var(--bs-primary-rgb), var(--bs-bg-opacity)); secondary: rgba(var(--bs-secondary-rgb), var(--bs-bg-opacity)); success: rgba(var(--bs-success-rgb), var(--bs-bg-opacity)); info: rgba(var(--bs-info-rgb), var(--bs-bg-opacity)); warning: rgba(var(--bs-warning-rgb), var(--bs-bg-opacity)); danger: rgba(var(--bs-danger-rgb), var(--bs-bg-opacity)); light: rgba(var(--bs-light-rgb), var(--bs-bg-opacity)); dark: rgba(var(--bs-dark-rgb), var(--bs-bg-opacity)); black: rgba(var(--bs-black-rgb), var(--bs-bg-opacity)); white: rgba(var(--bs-white-rgb), var(--bs-bg-opacity)); body: rgba(var(--bs-body-bg-rgb), var(--bs-bg-opacity)); transparent: transparent; body-secondary: rgba(var(--bs-secondary-bg-rgb), var(--bs-bg-opacity)); body-tertiary: rgba(var(--bs-tertiary-bg-rgb), var(--bs-bg-opacity)).

Other generator settings: local-vars: bg-opacity: 1.

### Utility bg-opacity

Property: `CSS variable output`. Class prefix: `bg-opacity`. Responsive: false. Print: false. States: none.

Values: 10: 0.1; 25: 0.25; 50: 0.5; 75: 0.75; 100: 1.

Other generator settings: css-var: true.

### Utility subtle-background-color

Property: `background-color`. Class prefix: `bg`. Responsive: false. Print: false. States: none.

Values: primary-subtle: var(--bs-primary-bg-subtle); secondary-subtle: var(--bs-secondary-bg-subtle); success-subtle: var(--bs-success-bg-subtle); info-subtle: var(--bs-info-bg-subtle); warning-subtle: var(--bs-warning-bg-subtle); danger-subtle: var(--bs-danger-bg-subtle); light-subtle: var(--bs-light-bg-subtle); dark-subtle: var(--bs-dark-bg-subtle).

### Utility gradient

Property: `background-image`. Class prefix: `bg`. Responsive: false. Print: false. States: none.

Values: gradient: var(--bs-gradient).

### Utility user-select

Property: `user-select`. Class prefix: `user-select`. Responsive: false. Print: false. States: none.

Values: all, auto, none.

### Utility pointer-events

Property: `pointer-events`. Class prefix: `pe`. Responsive: false. Print: false. States: none.

Values: none, auto.

### Utility rounded

Property: `border-radius`. Class prefix: `rounded`. Responsive: false. Print: false. States: none.

Values: 0: 0; 1: var(--bs-border-radius-sm); 2: var(--bs-border-radius); 3: var(--bs-border-radius-lg); 4: var(--bs-border-radius-xl); 5: var(--bs-border-radius-xxl); null: var(--bs-border-radius); circle: 50%; pill: var(--bs-border-radius-pill).

### Utility rounded-top

Property: `border-top-left-radius, border-top-right-radius`. Class prefix: `rounded-top`. Responsive: false. Print: false. States: none.

Values: 0: 0; 1: var(--bs-border-radius-sm); 2: var(--bs-border-radius); 3: var(--bs-border-radius-lg); 4: var(--bs-border-radius-xl); 5: var(--bs-border-radius-xxl); null: var(--bs-border-radius); circle: 50%; pill: var(--bs-border-radius-pill).

### Utility rounded-end

Property: `border-top-right-radius, border-bottom-right-radius`. Class prefix: `rounded-end`. Responsive: false. Print: false. States: none.

Values: 0: 0; 1: var(--bs-border-radius-sm); 2: var(--bs-border-radius); 3: var(--bs-border-radius-lg); 4: var(--bs-border-radius-xl); 5: var(--bs-border-radius-xxl); null: var(--bs-border-radius); circle: 50%; pill: var(--bs-border-radius-pill).

### Utility rounded-bottom

Property: `border-bottom-right-radius, border-bottom-left-radius`. Class prefix: `rounded-bottom`. Responsive: false. Print: false. States: none.

Values: 0: 0; 1: var(--bs-border-radius-sm); 2: var(--bs-border-radius); 3: var(--bs-border-radius-lg); 4: var(--bs-border-radius-xl); 5: var(--bs-border-radius-xxl); null: var(--bs-border-radius); circle: 50%; pill: var(--bs-border-radius-pill).

### Utility rounded-start

Property: `border-bottom-left-radius, border-top-left-radius`. Class prefix: `rounded-start`. Responsive: false. Print: false. States: none.

Values: 0: 0; 1: var(--bs-border-radius-sm); 2: var(--bs-border-radius); 3: var(--bs-border-radius-lg); 4: var(--bs-border-radius-xl); 5: var(--bs-border-radius-xxl); null: var(--bs-border-radius); circle: 50%; pill: var(--bs-border-radius-pill).

### Utility visibility

Property: `visibility`. Class prefix: `null`. Responsive: false. Print: false. States: none.

Values: visible: visible; invisible: hidden.

### Utility z-index

Property: `z-index`. Class prefix: `z`. Responsive: false. Print: false. States: none.

Values: 0: 0; 1: 1; 2: 2; 3: 3; n1: -1.

Source: https://github.com/twbs/bootstrap/blob/v5.3.8/scss/_utilities.scss

## 27 Bootstrap JavaScript plugin options and methods

This inventory was read from all 12 constructors exported by the pinned Bootstrap 5.3.8 browser bundle. Default options and declared validation types are exact runtime data. Methods include public methods across the component prototype chain, including Tooltip methods inherited by Popover and the shared BaseComponent dispose contract; underscore-prefixed internals are excluded. The shared static getInstance/getOrCreateInstance methods are described in Part 13. Do not call internal methods merely because minification leaves them discoverable. Function-valued defaults are represented as [function] rather than omitted.

### Plugin Alert

Instance methods: `close()`, `dispose()`.

Configurable default options: none on this constructor.

Source: https://getbootstrap.com/docs/5.3/components/alert/

### Plugin Button

Instance methods: `dispose()`, `toggle()`.

Configurable default options: none on this constructor.

Source: https://getbootstrap.com/docs/5.3/components/button/

### Plugin Carousel

Instance methods: `cycle()`, `dispose()`, `next()`, `nextWhenVisible()`, `pause()`, `prev()`, `to()`.

- `interval`: default `5000`; accepted type `(number|boolean)`.

- `keyboard`: default `true`; accepted type `boolean`.

- `pause`: default `hover`; accepted type `(string|boolean)`.

- `ride`: default `false`; accepted type `(boolean|string)`.

- `touch`: default `true`; accepted type `boolean`.

- `wrap`: default `true`; accepted type `boolean`.

Source: https://getbootstrap.com/docs/5.3/components/carousel/

### Plugin Collapse

Instance methods: `dispose()`, `hide()`, `show()`, `toggle()`.

- `parent`: default `null`; accepted type `(null|element)`.

- `toggle`: default `true`; accepted type `boolean`.

Source: https://getbootstrap.com/docs/5.3/components/collapse/

### Plugin Dropdown

Instance methods: `dispose()`, `hide()`, `show()`, `toggle()`, `update()`.

- `autoClose`: default `true`; accepted type `(boolean|string)`.

- `boundary`: default `clippingParents`; accepted type `(string|element)`.

- `display`: default `dynamic`; accepted type `string`.

- `offset`: default `0, 2`; accepted type `(array|string|function)`.

- `popperConfig`: default `null`; accepted type `(null|object|function)`.

- `reference`: default `toggle`; accepted type `(string|element|object)`.

Source: https://getbootstrap.com/docs/5.3/components/dropdown/

### Plugin Modal

Instance methods: `dispose()`, `handleUpdate()`, `hide()`, `show()`, `toggle()`.

- `backdrop`: default `true`; accepted type `(boolean|string)`.

- `focus`: default `true`; accepted type `boolean`.

- `keyboard`: default `true`; accepted type `boolean`.

Source: https://getbootstrap.com/docs/5.3/components/modal/

### Plugin Offcanvas

Instance methods: `dispose()`, `hide()`, `show()`, `toggle()`.

- `backdrop`: default `true`; accepted type `(boolean|string)`.

- `keyboard`: default `true`; accepted type `boolean`.

- `scroll`: default `false`; accepted type `boolean`.

Source: https://getbootstrap.com/docs/5.3/components/offcanvas/

### Plugin Popover

Instance methods: `disable()`, `dispose()`, `enable()`, `hide()`, `setContent()`, `show()`, `toggle()`, `toggleEnabled()`, `update()`.

- `allowList`: default `*: class, dir, id, lang, role, /^aria-[\w-]*$/i; a: target, href, title, rel; area: ; b: ; br: ; col: ; code: ; dd: ; div: ; dl: ; dt: ; em: ; hr: ; h1: ; h2: ; h3: ; h4: ; h5: ; h6: ; i: ; img: src, srcset, alt, title, width, height; li: ; ol: ; p: ; pre: ; s: ; small: ; span: ; sub: ; sup: ; strong: ; u: ; ul: `; accepted type `object`.

- `animation`: default `true`; accepted type `boolean`.

- `boundary`: default `clippingParents`; accepted type `(string|element)`.

- `container`: default `false`; accepted type `(string|element|boolean)`.

- `customClass`: default ``; accepted type `(string|function)`.

- `delay`: default `0`; accepted type `(number|object)`.

- `fallbackPlacements`: default `top, right, bottom, left`; accepted type `array`.

- `html`: default `false`; accepted type `boolean`.

- `offset`: default `0, 8`; accepted type `(array|string|function)`.

- `placement`: default `right`; accepted type `(string|function)`.

- `popperConfig`: default `null`; accepted type `(null|object|function)`.

- `sanitize`: default `true`; accepted type `boolean`.

- `sanitizeFn`: default `null`; accepted type `(null|function)`.

- `selector`: default `false`; accepted type `(string|boolean)`.

- `template`: default `<div class="popover" role="tooltip"><div class="popover-arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>`; accepted type `string`.

- `title`: default ``; accepted type `(string|element|function)`.

- `trigger`: default `click`; accepted type `string`.

- `content`: default ``; accepted type `(null|string|element|function)`.

Source: https://getbootstrap.com/docs/5.3/components/popover/

### Plugin ScrollSpy

Instance methods: `dispose()`, `refresh()`.

- `offset`: default `null`; accepted type `(number|null)`.

- `rootMargin`: default `0px 0px -25%`; accepted type `string`.

- `smoothScroll`: default `false`; accepted type `boolean`.

- `target`: default `null`; accepted type `element`.

- `threshold`: default `0.1, 0.5, 1`; accepted type `array`.

Source: https://getbootstrap.com/docs/5.3/components/scrollspy/

### Plugin Tab

Instance methods: `dispose()`, `show()`.

Configurable default options: none on this constructor.

Source: https://getbootstrap.com/docs/5.3/components/tab/

### Plugin Toast

Instance methods: `dispose()`, `hide()`, `isShown()`, `show()`.

- `animation`: default `true`; accepted type `boolean`.

- `autohide`: default `true`; accepted type `boolean`.

- `delay`: default `5000`; accepted type `number`.

Source: https://getbootstrap.com/docs/5.3/components/toast/

### Plugin Tooltip

Instance methods: `disable()`, `dispose()`, `enable()`, `hide()`, `setContent()`, `show()`, `toggle()`, `toggleEnabled()`, `update()`.

- `allowList`: default `*: class, dir, id, lang, role, /^aria-[\w-]*$/i; a: target, href, title, rel; area: ; b: ; br: ; col: ; code: ; dd: ; div: ; dl: ; dt: ; em: ; hr: ; h1: ; h2: ; h3: ; h4: ; h5: ; h6: ; i: ; img: src, srcset, alt, title, width, height; li: ; ol: ; p: ; pre: ; s: ; small: ; span: ; sub: ; sup: ; strong: ; u: ; ul: `; accepted type `object`.

- `animation`: default `true`; accepted type `boolean`.

- `boundary`: default `clippingParents`; accepted type `(string|element)`.

- `container`: default `false`; accepted type `(string|element|boolean)`.

- `customClass`: default ``; accepted type `(string|function)`.

- `delay`: default `0`; accepted type `(number|object)`.

- `fallbackPlacements`: default `top, right, bottom, left`; accepted type `array`.

- `html`: default `false`; accepted type `boolean`.

- `offset`: default `0, 6`; accepted type `(array|string|function)`.

- `placement`: default `top`; accepted type `(string|function)`.

- `popperConfig`: default `null`; accepted type `(null|object|function)`.

- `sanitize`: default `true`; accepted type `boolean`.

- `sanitizeFn`: default `null`; accepted type `(null|function)`.

- `selector`: default `false`; accepted type `(string|boolean)`.

- `template`: default `<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>`; accepted type `string`.

- `title`: default ``; accepted type `(string|element|function)`.

- `trigger`: default `hover focus`; accepted type `string`.

Source: https://getbootstrap.com/docs/5.3/components/tooltip/


## 28 Compiled SCSS and CSS side by side

Each row pair below comes from an actual successful compiler run. The left column is the source; the right column is expanded emitted CSS. File boundaries in a module example are shown as comments. The code blocks in Part 9 and lab sources remain the convenient copyable form; these comparison tables expose the build-time transformation directly. Sass abstractions disappear into ordinary CSS; a shorter source file does not guarantee a smaller stylesheet.


### case-01 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.notice {` |
| `// Input: spacing.scss` | `  padding: 0.75rem;` |
| `$space: 0.75rem;` | `  margin-block-end: 1.5rem;` |
| `.notice {` | `}` |
| `  padding: $space;` |   |
| `  margin-block-end: $space * 2;` |   |
| `}` |   |


### case-02 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// _tokens.scss` | `.panel {` |
| `$space: 0.75rem !default;` | `  padding: 1rem;` |
| `$ink: #172b4d !default;` | `  color: #172b4d;` |
| `// app.scss` | `}` |
| `@use "tokens" with ($space: 1rem);` |   |
| `.panel { padding: tokens.$space; color: tokens.$ink; }` |   |


### case-03 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `:root {` |
| `$brand: #174ea6;` | `  --brand: #174ea6;` |
| `:root { --brand: #{$brand}; }` | `}` |
| `.action { color: var(--brand); }` |   |
|   | `.action {` |
|   | `  color: var(--brand);` |
|   | `}` |


### case-04 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.panel {` |
| `@use "sass:math";` | `  padding: 1rem;` |
| `@use "sass:map";` | `  aspect-ratio: 1.5;` |
| `@use "sass:list";` | `  margin-block: 1rem;` |
| `$spaces: (small: 0.5rem, medium: 1rem, large: 1.5rem);` | `}` |
| `$ratio: math.div(3, 2);` |   |
| `.panel {` |   |
| `  padding: map.get($spaces, medium);` |   |
| `  aspect-ratio: $ratio;` |   |
| `  margin-block: list.nth((0.5rem, 1rem), 2);` |   |
| `}` |   |


### case-05 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.card {` |
| `.card {` | `  padding: 1rem;` |
| `  padding: 1rem;` | `}` |
| `  &__title { margin-block: 0 0.5rem; }` | `.card__title {` |
| `  &:focus-within { outline: 0.125rem solid #111; }` | `  margin-block: 0 0.5rem;` |
| `  [dir="rtl"] & { text-align: right; }` | `}` |
| `}` | `.card:focus-within {` |
|   | `  outline: 0.125rem solid #111;` |
|   | `}` |
|   | `[dir=rtl] .card {` |
|   | `  text-align: right;` |
|   | `}` |


### case-06 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.action:focus-visible {` |
| `@mixin focus-ring($color: #111, $offset: 0.2rem) {` | `  outline: 0.1875rem solid #111;` |
| `  &:focus-visible {` | `  outline-offset: 0.2rem;` |
| `    outline: 0.1875rem solid $color;` | `}` |
| `    outline-offset: $offset;` |   |
| `  }` | `.layout {` |
| `}` | `  display: grid;` |
| `@mixin at-width($width) {` | `}` |
| `  @media (min-width: $width) { @content; }` | `@media (min-width: 48rem) {` |
| `}` | `  .layout {` |
| `.action { @include focus-ring; }` | `    grid-template-columns: 1fr 2fr;` |
| `.layout {` | `  }` |
| `  display: grid;` | `}` |
| `  @include at-width(48rem) { grid-template-columns: 1fr 2fr; }` |   |
| `}` |   |


### case-07 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.panel {` |
| `@use "sass:math";` | `  padding: 1rem;` |
| `@function space($step, $unit: 0.25rem) {` | `  gap: 0.75rem;` |
| `  @if not math.is-unitless($step) { @error "space step must be unitless"; }` | `}` |
| `  @if $step < 0 { @error "space step must be nonnegative"; }` |   |
| `  @return $step * $unit;` |   |
| `}` |   |
| `.panel { padding: space(4); gap: space(3); }` |   |


### case-08 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.notice, .card {` |
| `%surface {` | `  background: #fff;` |
| `  background: #fff;` | `  border: 0.0625rem solid #526170;` |
| `  border: 0.0625rem solid #526170;` | `}` |
| `}` |   |
| `.card { @extend %surface; padding: 1rem; }` | `.card {` |
| `.notice { @extend %surface; padding: 0.75rem; }` | `  padding: 1rem;` |
|   | `}` |
|   |   |
|   | `.notice {` |
|   | `  padding: 0.75rem;` |
|   | `}` |


### case-09 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.panel {` |
| `$enable-border: true;` | `  border: 0.0625rem solid #526170;` |
| `@if $enable-border {` | `}` |
| `  .panel { border: 0.0625rem solid #526170; }` |   |
| `}` | `.space-1 {` |
| `@for $i from 1 through 3 {` | `  padding: 0.25rem;` |
| `  .space-#{$i} { padding: $i * 0.25rem; }` | `}` |
| `}` |   |
| `@each $name, $value in (compact: 0.5rem, roomy: 1rem) {` | `.space-2 {` |
| `  .density-#{$name} { gap: $value; }` | `  padding: 0.5rem;` |
| `}` | `}` |
| `$i: 1;` |   |
| `@while $i <= 2 {` | `.space-3 {` |
| `  .width-step-#{$i} { max-inline-size: $i * 10rem; }` | `  padding: 0.75rem;` |
| `  $i: $i + 1;` | `}` |
| `}` |   |
|   | `.density-compact {` |
|   | `  gap: 0.5rem;` |
|   | `}` |
|   |   |
|   | `.density-roomy {` |
|   | `  gap: 1rem;` |
|   | `}` |
|   |   |
|   | `.width-step-1 {` |
|   | `  max-inline-size: 10rem;` |
|   | `}` |
|   |   |
|   | `.width-step-2 {` |
|   | `  max-inline-size: 20rem;` |
|   | `}` |


### case-10 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// abstracts/_index.scss` | `.card {` |
| `@forward "tokens";` | `  padding: 1.25rem;` |
| `// abstracts/_tokens.scss` | `}` |
| `$space: 1rem !default;` |   |
| `// app.scss` |   |
| `@use "abstracts" with ($space: 1.25rem);` |   |
| `@use "components/card";` |   |
| `// components/_card.scss` |   |
| `@use "../abstracts" as design;` |   |
| `.card { padding: design.$space; }` |   |


### case-11 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// abstracts/_index.scss` | `body {` |
| `$space:1rem !default;` | `  margin: 0;` |
| `// app.scss` | `}` |
| `// main.scss; each referenced partial is an actual project dependency.` |   |
| `@use "abstracts";` | `.stack > * + * {` |
| `@use "vendors";` | `  margin-block-start: 1rem;` |
| `@use "base";` | `}` |
| `@use "layout";` |   |
| `@use "components";` | `.card {` |
| `@use "pages";` | `  padding: 1rem;` |
| `@use "themes";` | `}` |
| `// base/_index.scss` |   |
| `body { margin:0; }` | `.curriculum-page {` |
| `// components/_index.scss` | `  max-inline-size: 75rem;` |
| `.card { padding:1rem; }` | `  margin-inline: auto;` |
| `// layout/_index.scss` | `}` |
| `.stack > * + * { margin-block-start:1rem; }` |   |
| `// pages/_index.scss` | `:root {` |
| `.curriculum-page { max-inline-size:75rem; margin-inline:auto; }` | `  --ink:#172b4d;` |
| `// themes/_index.scss` | `}` |
| `:root { --ink:#172b4d; }` |   |
| `// vendors/_index.scss` |   |
| `// Vendor CSS is loaded by the HTML lab, not duplicated here.` |   |


### case-12 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `.panel {` |
| `$space: 1rem;` | `  padding: 1rem;` |
| `.panel {` | `}` |
| `  padding: $space;` | `.panel:focus-within {` |
| `  &:focus-within { outline: 2px solid #111; }` | `  outline: 2px solid #111;` |
| `}` | `}` |


### case-13 source and result

| SCSS source | Compiled CSS |
| --- | --- |
| `// app.scss` | `@media (min-width: 48rem) {` |
| `@use "sass:meta";` | `  .card {` |
| `@mixin at-breakpoint($name, $width) {` | `    --layout-label: wide;` |
| `  @media (min-width: $width) { @content($name); }` | `    padding: 2rem;` |
| `}` | `  }` |
| `@mixin space-variants($options...) {` | `}` |
| `  @each $name, $value in meta.keywords($options) {` | `.card-label {` |
| `    .space-#{$name} { padding: $value; }` | `  font-weight: 700;` |
| `  }` | `}` |
| `}` |   |
| `.card {` | `.space-compact {` |
| `  @include at-breakpoint(wide, 48rem) using ($label) {` | `  padding: 0.5rem;` |
| `    --layout-label: #{$label};` | `}` |
| `    padding: 2rem;` |   |
| `  }` | `.space-roomy {` |
| `  @at-root .card-label { font-weight: 700; }` | `  padding: 1rem;` |
| `}` | `}` |
| `@include space-variants($compact: 0.5rem, $roomy: 1rem);` |   |


## 29 Complete runnable lab source

Create the files under one lab directory, preserving the filenames shown below. Use Node.js 22.18 or a compatible maintained Node runtime. Install the pinned Sass and Bootstrap dependencies locally. Copy Bootstrap distribution assets into vendor as shown; its license is retained with the copied assets. Launch a local static server and open the named HTML files. The labs have no remote data endpoint and perform no account, payment or persistent server mutation.

The Markdown is the canonical source for copying code. The PDF visually wraps long lines to fit the page; do not treat a printed line wrap inside a string as a required source newline. Bootstrap minified distribution files are installed, not reproduced as thousands of opaque lines. All authored lab source is included.

```sh
npm init -y
npm install --save-exact sass@1.105.2 bootstrap@5.3.8
mkdir -p vendor
cp node_modules/bootstrap/dist/css/bootstrap.min.css vendor/bootstrap.min.css
cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js vendor/bootstrap.bundle.min.js
cp node_modules/bootstrap/LICENSE vendor/BOOTSTRAP-LICENSE.txt
npx sass --load-path=node_modules bootstrap-custom.scss bootstrap-custom.css
python3 -m http.server 8080
```

Visit http://localhost:8080/workbench.html, http://localhost:8080/bootstrap.html and http://localhost:8080/apis.html. The local server is a development convenience; deploy through the application's actual secure asset pipeline. The selected custom Bootstrap stylesheet is a separate compilation exercise and is not a replacement for the full framework CSS used by the component lab.


### File lab.css

```css
* , *::before, *::after { box-sizing: border-box; }
:root { color-scheme: light; --ink: #172b4d; --surface: #fff; --accent: #174ea6; }
body { margin: 0; color: var(--ink); background: var(--surface); font: 1rem/1.6 system-ui, sans-serif; }
body[data-theme="dark"] { color-scheme: dark; --ink: #f1f5f9; --surface: #17212f; --accent: #a8c8ff; }
a { color: var(--accent); }
button, input, select { font: inherit; }
button { color: var(--ink); background: var(--surface); border: 2px solid var(--accent); border-radius: .35rem; padding: .5rem .8rem; min-block-size: 2.75rem; cursor: pointer; }
input, select { max-inline-size: 100%; min-block-size: 2.75rem; border: 2px solid #526170; border-radius: .25rem; padding: .4rem; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
[hidden] { display: none !important; }
.skip { position: absolute; inset-inline-start: .5rem; inset-block-start: .5rem; transform: translateY(-160%); background: var(--surface); padding: .5rem; z-index: 100; }
.skip:focus { transform: none; }
header, main, footer { inline-size: min(100% - 2rem, 75rem); margin-inline: auto; padding-block: 1rem; }
h1 { font-size: clamp(1.75rem, 1.25rem + 2vw, 2.5rem); line-height: 1.2; }
h2, h3 { line-height: 1.3; }
.workbench { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1.5rem; }
.workbench > * { min-inline-size: 0; }
@media (min-width: 60rem) { .workbench { grid-template-columns: minmax(15rem, 1fr) minmax(0, 3fr); } }
.cluster { display: flex; flex-wrap: wrap; gap: .75rem; align-items: center; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); gap: 1rem; list-style: none; padding: 0; }
.card { border: 1px solid #526170; border-radius: .5rem; padding: 1rem; overflow-wrap: anywhere; }
label { display: block; font-weight: 700; }
.field { margin-block: 1rem; }
.api-readout { overflow-wrap: anywhere; }
learning-panel { display: block; margin-block: 1rem; --panel-accent: var(--accent); }
learning-panel::part(panel) { border-radius: .5rem; }
/* Theme foreground and background change together to avoid transient low contrast. */
@media (forced-colors: active) { button, .card { border-color: ButtonText; } }
@media print { .skip, .interactive { display: none; } .workbench { display: block; } }

```


### File workbench.html

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Responsive learning workbench</title>
<link rel="stylesheet" href="lab.css">

</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header><h1>Responsive learning workbench</h1><p>Local curriculum demonstration. No account or payment action occurs.</p></header>
<main id="main" tabindex="-1">
<div class="workbench">
<aside aria-labelledby="filter-heading">
<h2 id="filter-heading">Choose a practice language</h2>
<form id="filter-form">
<div class="field"><label for="language">Language</label>
<select id="language" name="language"><option value="all">All languages</option><option value="js">JavaScript</option><option value="java">Java</option></select></div>
<button type="submit">Apply filter</button>
</form>
<h2>Practice help</h2>
<button id="help-toggle" type="button" aria-expanded="false" aria-controls="help-panel">Show practice help</button>
<div id="help-panel" hidden><p>Choose a course, read the fundamentals, then attempt an exercise before revealing a solution.</p></div>
</aside>
<section aria-labelledby="results-heading"><h2 id="results-heading">Practice courses</h2>
<p id="results-status" role="status">3 courses available.</p>
<ul class="cards" id="courses">
<li class="card" data-language="js"><h3>JavaScript values</h3><p>Practice primitive values and conversions.</p><a href="#course-details">Read JavaScript values details</a></li>
<li class="card" data-language="java"><h3>Java collections</h3><p>Practice collection interfaces and iteration.</p><a href="#course-details">Read Java collections details</a></li>
<li class="card" data-language="js"><h3>JavaScript queues</h3><p>Practice a queue with a textual operation trace.</p><a href="#course-details">Read JavaScript queues details</a></li>
</ul>
<h2 id="course-details">Course details</h2><p>This page demonstrates interface filtering. Executable problem fixtures are a separate curriculum concern.</p>
</section></div></main>
<footer><p>Use keyboard navigation and browser zoom to inspect this example.</p></footer>
<script src="workbench.js" defer></script>
</body>
</html>

```


### File workbench.js

```javascript
const form = document.getElementById('filter-form');
const language = document.getElementById('language');
const cards = [...document.querySelectorAll('#courses > li')];
const status = document.getElementById('results-status');
form.addEventListener('submit', event => {
  event.preventDefault();
  let count = 0;
  for (const card of cards) {
    const visible = language.value === 'all' || card.dataset.language === language.value;
    card.hidden = !visible;
    if (visible) count++;
  }
  status.textContent = `${count} ${count === 1 ? 'course' : 'courses'} available.`;
});
const help = document.getElementById('help-toggle');
const panel = document.getElementById('help-panel');
help.addEventListener('click', () => {
  const expanded = help.getAttribute('aria-expanded') !== 'true';
  help.setAttribute('aria-expanded', String(expanded));
  panel.hidden = !expanded;
  help.textContent = expanded ? 'Hide practice help' : 'Show practice help';
});

```


### File bootstrap.html

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bootstrap learning-plan review</title>
<link rel="stylesheet" href="vendor/bootstrap.min.css">
<script src="vendor/bootstrap.bundle.min.js" defer></script>
<link rel="stylesheet" href="lab.css">
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header><h1>Bootstrap learning-plan review</h1><p>Local curriculum demonstration. No account or payment action occurs.</p></header>
<main id="main" tabindex="-1" class="container py-4">
<section aria-labelledby="plan-heading"><h2 id="plan-heading">Review a learning plan</h2>
<div class="row g-3"><div class="col-12 col-lg-7">
<form id="plan-form" class="card card-body">
<div class="mb-3"><label for="plan-name" class="form-label">Plan name</label>
<input id="plan-name" name="plan" class="form-control" required maxlength="80" autocomplete="off" aria-describedby="plan-help">
<div id="plan-help" class="form-text">Use a short name describing your current practice goal.</div></div>
<button id="review-trigger" class="btn btn-primary" type="submit">Review plan</button></form>
</div><div class="col-12 col-lg-5">
<div class="accordion" id="plan-help-group"><div class="accordion-item">
<h3 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#plan-answer" aria-expanded="false" aria-controls="plan-answer">What does this example save?</button></h3>
<div id="plan-answer" class="accordion-collapse collapse" data-bs-parent="#plan-help-group"><div class="accordion-body">It records a local confirmation message only. No data is sent to a server.</div></div>
</div></div></div></div>
<p id="plan-status" class="mt-3" role="status">No plan confirmed.</p></section>
<div class="modal fade" id="review-modal" tabindex="-1" aria-labelledby="review-heading" aria-describedby="review-summary" aria-hidden="true">
<div class="modal-dialog"><div class="modal-content"><div class="modal-header">
<h2 class="modal-title fs-5" id="review-heading">Review learning plan</h2>
<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close review"></button></div>
<div class="modal-body"><p id="review-summary"></p><p>This confirmation is local to this page.</p></div>
<div class="modal-footer"><button id="review-return" type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Return to editing</button>
<button id="confirm-plan" type="button" class="btn btn-primary">Confirm local plan</button></div>
</div></div></div>
</main>
<footer><p>Use keyboard navigation and browser zoom to inspect this example.</p></footer>
<script src="bootstrap-lab.js" defer></script>
</body>
</html>

```


### File bootstrap-lab.js

```javascript
const planForm = document.getElementById('plan-form');
const planName = document.getElementById('plan-name');
const modalElement = document.getElementById('review-modal');
const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
const summary = document.getElementById('review-summary');
const planStatus = document.getElementById('plan-status');
const opener = document.getElementById('review-trigger');
let reviewedName = '';
planForm.addEventListener('submit', event => {
  event.preventDefault();
  reviewedName = planName.value.trim();
  if (!reviewedName) {
    planName.setCustomValidity('Enter a plan name containing a non-space character.');
    planName.reportValidity();
    return;
  }
  summary.textContent = `Plan: ${reviewedName}`;
  modal.show();
});
planName.addEventListener('input', () => planName.setCustomValidity(''));
modalElement.addEventListener('shown.bs.modal', () => document.getElementById('review-return').focus());
modalElement.addEventListener('hidden.bs.modal', () => opener.focus());
document.getElementById('confirm-plan').addEventListener('click', () => {
  planStatus.textContent = `Local plan confirmed: ${reviewedName}.`;
  modal.hide();
});

```


### File apis.html

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Style and Web API lifecycle laboratory</title>
<link rel="stylesheet" href="lab.css">

</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header><h1>Style and Web API lifecycle laboratory</h1><p>Local curriculum demonstration. No account or payment action occurs.</p></header>
<main id="main" tabindex="-1">
<div class="cluster interactive"><button id="theme-toggle" type="button" aria-pressed="false">Dark theme</button>
<button id="tone-toggle" type="button">Toggle panel tone</button><button id="mount-toggle" type="button" aria-pressed="false">Detach panel</button></div>
<div id="panel-host"><learning-panel id="learning-panel"><span slot="title">JavaScript queue practice</span><p>Enqueue adds at the back; dequeue removes from the front.</p></learning-panel></div>
<p id="lifecycle-status" role="status">Panel connected.</p>
<h2>Measurement and observation</h2><p id="width-output" class="api-readout">Measuring the laboratory width.</p>
<button id="measure-button" type="button">Set the sample to 240 CSS pixels</button>
<div id="measure-sample" class="card" style="max-width:100%">This sample demonstrates a typed or string inline style write.</div>
<p id="measure-status" role="status">No inline width set.</p>
<p id="mutation-output">Disclosure state: closed.</p>
</main>
<footer><p>Use keyboard navigation and browser zoom to inspect this example.</p></footer>
<script src="apis.js" defer></script>
</body>
</html>

```


### File apis.js

```javascript
// Complete function; call with an existing HTMLElement and a finite pixel value.
function setInlineMeasure(element, pixels) {
  if (!Number.isFinite(pixels) || pixels < 0) {
    throw new TypeError('pixels must be a finite nonnegative number');
  }
  if (element.attributeStyleMap && globalThis.CSS?.px) {
    try {
      element.attributeStyleMap.set('width', CSS.px(pixels));
      return 'typed';
    } catch {
      // A supported interface may still reject this property/value combination.
    }
  }
  element.style.width = `${pixels}px`;
  return 'string';
}

// Complete controller; output is a separate non-sizing text node in the page.
function reportWidth(target, output) {
  if (typeof globalThis.ResizeObserver !== 'function') {
    output.textContent = 'Automatic measurement is unavailable.';
    return () => {};
  }
  const observer = new ResizeObserver(entries => {
    const entry = entries.find(item => item.target === target);
    if (!entry) return;
    const text = `${Math.round(entry.contentRect.width)} CSS px wide`;
    if (output.textContent !== text) output.textContent = text;
  });
  observer.observe(target, { box: 'content-box' });
  return () => observer.disconnect();
}

// Complete observer utility for third-party markup integration.
function watchExpanded(button, onState) {
  const read = () => onState(button.getAttribute('aria-expanded') === 'true');
  const observer = new MutationObserver(read);
  observer.observe(button, { attributes: true, attributeFilter: ['aria-expanded'] });
  read();
  return () => observer.disconnect();
}

// Complete helper for a synchronous, idempotent DOM update.
async function updateView(update) {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!document.startViewTransition || reduced) {
    update();
    return;
  }
  let began = false;
  let transition;
  try {
    transition = document.startViewTransition(() => {
      began = true;
      update();
    });
  } catch (error) {
    if (!began) update();
    else throw error;
    return;
  }
  // Consume capture failures separately from the application's update result.
  transition.ready.catch(() => {});
  const finished = transition.finished.catch(() => {});
  await transition.updateCallbackDone;
  await finished;
}

class LearningPanel extends HTMLElement {
  static observedAttributes = ['tone'];
  #controller;
  #observer;
  constructor() {
    super();
    const root = this.attachShadow({ mode: 'open' });
    root.innerHTML = `<style>
      :host { display:block; color:inherit; }
      section { border:2px solid var(--panel-accent,#174ea6); padding:1rem; }
      :host([tone="strong"]) section { border-width:4px; }
      h2 { margin-block:0 1rem; font:700 1.25rem/1.3 system-ui,sans-serif; }
      button { font:inherit; min-height:2.75rem; padding:.5rem .75rem; color:inherit; background:transparent; border:2px solid var(--panel-accent,#174ea6); border-radius:.3rem; }
      button:focus-visible { outline:3px solid var(--panel-accent,#174ea6); outline-offset:3px; }
      [hidden] { display:none !important; }
      @media(forced-colors:active) { section,button {border-color:ButtonText;} }
    </style><section part="panel"><h2><slot name="title">Practice panel</slot></h2>
    <button type="button" aria-expanded="false" aria-controls="panel-content">Show queue explanation</button>
    <div id="panel-content" hidden><slot></slot></div></section>`;
  }
  connectedCallback() {
    this.#controller?.abort();
    this.#observer?.disconnect();
    this.#controller = new AbortController();
    const button = this.shadowRoot.querySelector('button');
    const content = this.shadowRoot.getElementById('panel-content');
    button.addEventListener('click', () => {
      const expanded = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(expanded));
      content.hidden = !expanded;
      button.textContent = expanded ? 'Hide queue explanation' : 'Show queue explanation';
      this.dispatchEvent(new CustomEvent('panel-toggle', { bubbles: true, composed: true, detail: { expanded } }));
    }, { signal: this.#controller.signal });
    this.#observer = new MutationObserver(() => this.dataset.observedTone = this.getAttribute('tone') || 'normal');
    this.#observer.observe(this, { attributes:true, attributeFilter:['tone'] });
  }
  disconnectedCallback() { this.#controller?.abort(); this.#observer?.disconnect(); }
  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'tone' && oldValue !== newValue) this.dataset.toneState = newValue || 'normal';
  }
}
customElements.define('learning-panel', LearningPanel);
const panel = document.getElementById('learning-panel');
const host = document.getElementById('panel-host');
const lifecycle = document.getElementById('lifecycle-status');
const mountButton = document.getElementById('mount-toggle');
let stopMutation = watchExpanded(panel.shadowRoot.querySelector('button'), expanded => {
  document.getElementById('mutation-output').textContent = `Disclosure state: ${expanded ? 'open' : 'closed'}.`;
});
mountButton.addEventListener('click', () => {
  const detach = panel.isConnected;
  if (detach) { stopMutation(); panel.remove(); }
  else {
    host.append(panel);
    stopMutation = watchExpanded(panel.shadowRoot.querySelector('button'), expanded => {
      document.getElementById('mutation-output').textContent = `Disclosure state: ${expanded ? 'open' : 'closed'}.`;
    });
  }
  mountButton.setAttribute('aria-pressed', String(detach));
  mountButton.textContent = detach ? 'Reconnect panel' : 'Detach panel';
  lifecycle.textContent = detach ? 'Panel disconnected; component resources released.' : 'Panel reconnected; resources restored.';
});
document.getElementById('tone-toggle').addEventListener('click', () => {
  panel.setAttribute('tone', panel.getAttribute('tone') === 'strong' ? 'normal' : 'strong');
});
document.getElementById('theme-toggle').addEventListener('click', async event => {
  const button = event.currentTarget;
  try {
    await updateView(() => {
      const dark = document.body.dataset.theme !== 'dark';
      document.body.dataset.theme = dark ? 'dark' : 'light';
      button.setAttribute('aria-pressed', String(dark));
    });
  } catch { lifecycle.textContent = 'The theme update could not be completed.'; }
});
let stopResize = reportWidth(document.getElementById('main'), document.getElementById('width-output'));
document.getElementById('measure-button').addEventListener('click', () => {
  const path = setInlineMeasure(document.getElementById('measure-sample'), 240);
  document.getElementById('measure-status').textContent = `Sample width set using ${path} access.`;
});
window.addEventListener('pagehide', () => { stopResize(); stopMutation(); });
window.addEventListener('pageshow', event => {
  if (!event.persisted) return;
  stopResize = reportWidth(document.getElementById('main'), document.getElementById('width-output'));
  if (panel.isConnected) {
    stopMutation = watchExpanded(panel.shadowRoot.querySelector('button'), expanded => {
      document.getElementById('mutation-output').textContent = `Disclosure state: ${expanded ? 'open' : 'closed'}.`;
    });
  }
});

```


### File bootstrap-custom.scss

```scss
// bootstrap-custom.scss; compile with node_modules on the Sass load path.
@use "sass:map";
@import "bootstrap/scss/functions";
$primary: #174ea6;
$enable-negative-margins: false;
@import "bootstrap/scss/variables";
@import "bootstrap/scss/variables-dark";
$theme-colors: map.merge($theme-colors, ("learning": #174ea6));
@import "bootstrap/scss/maps";
@import "bootstrap/scss/mixins";
@import "bootstrap/scss/utilities";
$utilities: map.merge($utilities, (
  "reading-width": (
    property: max-width,
    class: reading-width,
    values: (prose: 70ch),
    responsive: true
  )
));
@import "bootstrap/scss/root";
@import "bootstrap/scss/reboot";
@import "bootstrap/scss/type";
@import "bootstrap/scss/containers";
@import "bootstrap/scss/grid";
@import "bootstrap/scss/buttons";
@import "bootstrap/scss/helpers";
@import "bootstrap/scss/utilities/api";

```


### File sass/validated-function.scss

```scss
@use "sass:meta";
@use "sass:math";
@function space($step, $unit: 0.25rem) {
  @if meta.type-of($step) != "number" { @error "step must be numeric"; }
  @if not math.is-unitless($step) { @error "step must be unitless"; }
  @if $step < 0 { @error "step must be nonnegative"; }
  @return $step * $unit;
}
.panel { padding: space(4); }

```


### File sass/indented-1.sass

```sass
$space: 1rem
.panel
  padding: $space
  &:focus-within
    outline: 2px solid #111

```


### Sass workshop file boundaries

The side-by-side source tables show every workshop source line. Save each case in its own directory to avoid mixing independent module configurations. Compile its app.scss with `npx sass app.scss compiled.css`. Cases 02 and 10 need the named partials shown in their tables; case 11 supplies the complete 7-1 directory facade. The separate validated-function.scss demonstrates type, unit and negative-value rejection.


## 30 Source provenance, coverage and verification

The guide was prepared against sources retrieved on October 16, 2026. CSS metadata comes from W3C Webref @webref/css 8.7.7; this package consolidates the latest levels and applies extraction fixes, so it is a source index rather than a frozen browser baseline. The CSS Snapshot index used for classification comes from the CSSWG editor version of CSS Snapshot 2025, linked alongside the published note. Exact source fields are preserved in the supporting inventory; eight metadata gaps are supplemented from canonical aliases or the linked primary definition tables and marked beside their records. Explanations, use cases, exercises and application labs are original teaching material. Grammar, initial values, inheritance flags, API names and package option data are factual reference metadata attributed to their defining sources.


### Coverage contract

- 752 non-vendor CSS property records, each with its extracted grammar and a primary definition link; 302 also appear as current records in the retrieved Snapshot index.
- 13 additional historical/index-placeholder names are explicitly separated; the open-ended custom-property family is explained separately.
- 97 Bootstrap utility generator entries and 12 plugin constructors have source/runtime-derived reference tables.
- 118 exposed Sass module functions across 7 built-in modules are listed, including deprecated compatibility functions that remain exposed.
- Every stylesheet example uses the ordinary browser cascade after compilation; no source inventory is a support, WCAG or performance certificate.


### Observed test results

- Dart Sass: 13 independent workshop entry points compiled; no owned-code warnings were emitted. The indented .sass entry point also compiled with its expected output. Three deliberately invalid function calls were rejected. The selected Bootstrap build emitted the expected custom utility, responsive variant and theme button and omitted the unselected modal component.
- Bootstrap dependency compilation emitted 21 captured warning/log messages, including the compiler's summary that further repetitive deprecations were omitted. These are upstream @import/global-function/color-function compatibility warnings; they remain migration work, not silent passes under a no-deprecations policy.
- Browser: Google Chrome 155.0.8059.84, headless on the local host. All 18 recorded responsive/interaction/fallback assertions passed. The three complete HTML labs were checked for page-wide horizontal overflow at 320, 768 and 1280 CSS pixels.
- axe-core 4.14.0: 6 tested states, zero violations and zero incomplete results in the selected WCAG 2 A/AA, 2.1 A/AA and 2.2 AA rule tags. This is the result of that automated subset in that engine, not full conformance certification.
- No uncaught page JavaScript errors were recorded in the primary test page. Explicit tests cover filter state, keyboard disclosure, modal entry/Escape/confirmation/focus return, accordion state, Shadow DOM disconnection/reconnection, typed/string style access, mutation observation, view transition/reduced motion and missing-API fallbacks.


### Remaining acceptance work

Firefox, Safari/WebKit, real mobile browsers, VoiceOver/NVDA/JAWS, manual 200/400 percent zoom, forced colors, touch target measurements, localization/RTL, long-content stress, CSP deployment and production performance traces were not certified by these runs. View Transition failure guards were exercised with a mocked API, and persisted-page observer restoration was exercised with synthetic lifecycle events. These checks do not certify real back/forward-cache eligibility or every browser capture failure. No app ingestion, backend change, subscription change or DSA evaluator admission was performed. A PDF visual layout review and extraction/coverage checks are recorded in the supporting verification file; the PDF itself is not claimed as a tagged accessible-PDF conformance deliverable.


### Primary reference map

- CSS module overview: https://www.w3.org/TR/css-2025/
- CSSWG snapshot editor index: https://drafts.csswg.org/css-2025/
- Webref package provenance: https://github.com/w3c/webref/tree/main/packages/css
- Sass language and modern APIs: https://sass-lang.com/documentation/
- Bootstrap 5.3 documentation: https://getbootstrap.com/docs/5.3/getting-started/introduction/
- Bootstrap pinned source: https://github.com/twbs/bootstrap/tree/v5.3.8
- CSS Typed OM: https://drafts.css-houdini.org/css-typed-om-1/
- ResizeObserver: https://www.w3.org/TR/resize-observer/
- DOM and MutationObserver: https://dom.spec.whatwg.org/
- View Transitions: https://www.w3.org/TR/css-view-transitions-1/
- Custom Elements: https://html.spec.whatwg.org/multipage/custom-elements.html
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/

Element-specific CSS definition links appear beside every property and inventory entry. Package licenses apply to redistributed upstream code; Bootstrap is MIT licensed. These references are source authorities, not instructions that override the learner's task.
