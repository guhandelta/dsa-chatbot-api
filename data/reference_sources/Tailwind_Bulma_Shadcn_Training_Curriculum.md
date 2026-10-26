# Tailwind CSS, Bulma and shadcn/ui

A technical curriculum for front-end architecture, component engineering and evidence-based AI tutoring. Edition: 16 October 2026. Separate framework sections share a common foundation, practice model and verification register.

## 1 Purpose, boundaries and learning routes

This curriculum follows the earlier HTML and CSS/Sass/Bootstrap material: mental model first, mechanism second, complete implementation third, then failure diagnosis and evidence. It teaches how to reason about a framework rather than memorize attractive snippets. Readers should already understand semantic HTML, the cascade, flex/grid, JavaScript events and basic React before the React-specific chapters.

Tailwind CSS is a utility compiler and design-token interface. Bulma is a CSS component and layout framework whose interaction code belongs to the application. shadcn/ui distributes source-owned components and supporting tooling; its behavioral dependencies and chosen primitive base remain essential. Calling all three interchangeable CSS libraries obscures these differences.

“Comprehensive” here means a structured treatment of the major shipped concepts, utility families, Bulma modules and shadcn component categories, with focused API records and working labs. Arbitrary values, generated permutations, third-party registries, commercial products and future releases cannot form a finite exhaustive list. The catalogue explains their grammar and extension points. Verify the installed source before accepting an unlisted prop or class.

A complete beginner follows chapters in order after the HTML/CSS prerequisites. A framework switcher starts with the comparison and reproduces the same study dashboard in each system. An experienced interview candidate completes the debugging cases and explains the underlying CSS/DOM behavior without relying on framework vocabulary. All routes use the same acceptance criteria; experience changes pacing, not correctness.

Each topic should be learned through fourteen lenses: purpose, mental model, setup, syntax, composition, state, layout, responsive behavior, tokens, accessibility, performance, failure modes, appropriate use and verification. A visual match alone cannot demonstrate a correct component.

This is candidate reference and practice material. It has not been ingested into the application or approved as an automatically graded curriculum. Tested examples are explicitly separated from conceptual exercises. Browser checks cover the recorded Chrome environment; manual screen-reader and cross-browser checks remain necessary.

## 2 Version contract and architectural comparison

Package metadata and official documentation were observed on 16 October 2026. Package versions below are a reproducibility snapshot, not a promise that every future registry item has the same API. The shadcn CLI version is not a runtime component version; copied files and primitive dependencies must be tracked separately.

| Package | Observed version |
| --- | --- |
| `tailwindcss` | `4.3.3` |
| `@tailwindcss/cli` | `4.3.3` |
| `bulma` | `1.0.4` |
| `shadcn` | `4.22.0` |
| `@base-ui/react` | `1.9.0` |
| `react` | `19.3.1` |
| `react-dom` | `19.3.1` |
| `vite` | `8.3.4` |
| `@vitejs/plugin-react` | `6.1.2` |
| `typescript` | `7.0.2` |
| `class-variance-authority` | `0.7.1` |
| `clsx` | `2.1.1` |
| `tailwind-merge` | `3.7.0` |
| `lucide-react` | `1.58.0` |

The runnable examples pin Tailwind CSS 4.3.3, Bulma 1.0.4, Base UI 1.9.0 and React 19.3.1. Their compiler deliberately pins TypeScript 5.9.3 and esbuild 0.25.12 rather than assuming that the newest tools work on every local Node installation. The complete dependency graph is in examples/package-lock.json. A clean install should use npm ci.

| System | Ownership and execution model |
| --- | --- |
| Tailwind CSS | Build-time scanning and utility generation; ordinary CSS in the browser; no interaction runtime required. |
| Bulma | Prebuilt CSS or modular Sass compiled to CSS; semantic class conventions; application supplies menus, dialogs and state. |
| shadcn/ui | Local React component source plus chosen primitives, utility compiler and token CSS; updates require reviewing owned code. |
| Shared responsibility | HTML semantics, data validation, accessible content, application state, persistence and product policy. |

For Tailwind v4, teach CSS-first configuration and the package-specific CLI/PostCSS/Vite adapters. Do not copy a v3 setup using only @tailwind directives and assume it is current. Bulma v1 introduces CSS-variable-driven themes and a modular Sass structure. shadcn/ui's July 2026 documentation makes Base UI the default while preserving Radix support; older tutorials commonly assume Radix. Record base, style, registry URL, copied-source hash and dependency versions for each installation.

Source: https://tailwindcss.com/docs/upgrade-guide

Source: https://bulma.io/documentation/start/overview/

Source: https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default

## 3 Common platform contract

Start with meaningful elements: links navigate, buttons act, forms collect data, headings structure content and tables express two-dimensional relationships. Framework styling does not change those contracts. Use type="button" for controls that must not submit their containing form. An anchor styled as a button still navigates. Never nest a button inside another button by composing two triggers incorrectly.

The cascade resolves origin, importance, layers, specificity and order; the order of class tokens inside className is not a general CSS priority mechanism. A class-merging helper can remove known conflicts, but cannot prove the computed cascade across arbitrary CSS, inline styles, pseudo-elements and plugins. Inspect the matched rules when a utility appears ineffective.

Keep the state owner explicit. React state or native DOM state should determine both the visible style and accessibility attributes. Changing aria-expanded alone does not hide a menu. Adding is-active alone does not trap dialog focus. CSS can react to a state but cannot implement every interaction protocol.

Accessibility acceptance includes keyboard operation, visible focus, correct names and relationships, logical source order, zoom/reflow, error recovery, reduced-motion preferences, forced-color behavior and sufficient contrast in every theme. Automated axe checks catch a useful subset. A zero-violation scan is not a WCAG conformance certificate.

Build responsive behavior from content constraints. Test at 320 CSS pixels, intermediate widths and large text, not merely five named devices. Let long translated labels wrap. A grid track with minmax(0, 1fr) and min-width: 0 children often prevents overflow that width: 100% alone cannot fix. Preserve reading order when rearranging layouts.

Source: https://www.w3.org/WAI/ARIA/apg/patterns/

## 4 Tailwind CSS - compiler, installation and source detection

Tailwind reads source text, recognizes complete candidate class names, resolves utilities and variants against the theme, then emits CSS. It does not run your JavaScript or infer the eventual result of arbitrary interpolation. The browser receives selectors and declarations, not a Tailwind layout engine.

A reproducible CLI workflow is useful for understanding the pipeline before adopting a framework adapter:

```sh
npm install -D tailwindcss@4.3.3 @tailwindcss/cli@4.3.3
npx @tailwindcss/cli -i ./src/app.css -o ./dist/app.css --minify
```

```css
@import "tailwindcss" source(none);
@source "./index.html";
@source "./components";
```

Automatic detection is convenient, but repository boundaries, ignored paths and external packages matter. Explicit sources make teaching examples reproducible. Paths in @source are relative to the stylesheet. Monorepos need intentional source roots; scanning the entire workspace can bloat output and obscure which package owns a candidate.

```tsx
const toneClasses = {
  success: "bg-emerald-700 text-white",
  danger: "bg-red-700 text-white",
};
function Notice({ tone }: { tone: keyof typeof toneClasses }) {
  return <p className={toneClasses[tone]}>Build completed</p>;
}
```

The complete strings above are visible to the scanner. A construction such as `bg-${tone}-700` is not a reliable source of CSS. Do not solve the problem by accepting arbitrary user-supplied classes. Map domain values to a bounded approved vocabulary. For genuinely continuous data, set a custom property and use a static utility such as `w-[var(--progress)]`, validating the numeric input separately.

@source inline("...") can deliberately include candidates not otherwise present. Keep the list narrow and document why it exists. It is not a substitute for a coherent component API. Build a production bundle in CI and inspect the emitted selectors for important dynamic states; development rendering alone can hide missing candidates.

Vite uses @tailwindcss/vite; PostCSS uses @tailwindcss/postcss; the CLI uses @tailwindcss/cli. Install the adapter actually used by the build. Browser CDN/playground tooling is useful for exploration but is not the pinned production workflow taught here. Tailwind v4 depends on modern CSS; check the official compatibility baseline and your product browser matrix before migration.

Source: https://tailwindcss.com/docs/installation/tailwind-cli

Source: https://tailwindcss.com/docs/detecting-classes-in-source-files

Source: https://tailwindcss.com/docs/compatibility

## 5 Tailwind CSS - utility grammar and layout reasoning

A candidate usually combines optional variants, a utility family and a value: `md:hover:bg-slate-800`. The colon separates variants, not CSS declarations. A bracketed arbitrary value supplies an escape hatch, for example `grid-cols-[16rem_1fr]`; underscores represent spaces where the class token cannot contain literal whitespace. A negative modifier is supported only by suitable utilities, such as -mt-2. A slash often supplies a modifier, such as text-base/6 or bg-black/50; its meaning depends on the family.

The spacing scale is a system rather than a list of pixel constants. With the default spacing unit, p-4 is 1rem. The result depends on the theme and the root font size. Utilities that use CSS properties such as color or font-family can participate in inheritance; width, margin, borders and display normally do not inherit. A class is not itself “inherited.” The property it sets determines inheritance.

Flexbox is appropriate for a navigation row or a one-dimensional action group. Grid expresses two-dimensional alignment and track constraints. `flex-1` cannot fix every overflowing child: use min-w-0 where the automatic minimum size is the issue. A `gap-*` class sets space between children; it does not create edge padding. `space-y-*` uses sibling relationships and is less suitable for wrapped or reordered layouts.

```html
<section aria-labelledby="courses" class="mx-auto max-w-5xl p-6">
  <h2 id="courses" class="text-2xl font-bold">Practice pathways</h2>
  <ul class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
    <li class="min-w-0 rounded-lg border border-slate-300 p-4">
      <h3 class="font-semibold">JavaScript fundamentals</h3>
      <p class="mt-2 break-words">Arrays, functions and objects.</p>
      <a href="/javascript" class="mt-3 inline-block underline
        focus-visible:outline-2 focus-visible:outline-offset-4">
        Open JavaScript pathway
      </a>
    </li>
  </ul>
</section>
```

This is a focused structural example; the runnable dashboard supplies real local actions. Semantic list structure survives the grid layout. Adding md:grid-cols-3 does not create or reorder content. Use span and start/end utilities for deliberate placement; avoid visual ordering that makes keyboard navigation appear to jump unpredictably.

Absolute positioning removes an element from normal flow and requires a containing-block strategy. z-50 is not a universal “above everything” guarantee: stacking contexts, transforms, opacity, isolation and the browser top layer can dominate. Debug the ancestor chain rather than escalating z-index without a model.

## 6 Tailwind CSS - responsive, container and state variants

Unprefixed utilities form the baseline. A breakpoint variant applies at its minimum width and above unless constrained by a maximum variant. Default viewport breakpoints are sm 40rem, md 48rem, lg 64rem, xl 80rem and 2xl 96rem. These values are theme configuration, not a taxonomy of physical devices. Use md:max-lg:* for an interval when that expresses the actual design requirement.

Container queries respond to an ancestor's available size. Mark the container with @container and apply @md:* to descendants. Named containers prevent a deeply nested component from accidentally observing the wrong ancestor. Container breakpoint names refer to the container-size scale, not automatically to viewport breakpoint values. A study card can therefore adapt inside a sidebar without treating the entire viewport as small.

State variants describe selectors and media conditions. hover:* is appropriate for enhancement, focus-visible:* for keyboard focus indication, disabled:* for a genuinely disabled control and aria-expanded:* for the declared expanded state. The data-[state=open]:* spelling targets a specific attribute value; a Base UI component might instead expose data-open, so inspect its actual DOM before choosing a selector.

```html
<button type="button" aria-expanded="false" aria-controls="details"
 class="rounded border px-4 py-2 aria-expanded:bg-slate-200
 focus-visible:outline-2 focus-visible:outline-offset-2">
  Show details
</button>
```

JavaScript must update the associated panel and aria-expanded together. A group parent enables group-hover:* and group-focus-within:* reactions on descendants; a peer usually affects suitable following siblings. Named groups/peers reduce ambiguity in nested components. Neither mechanism replaces a proper label, a correct tab order or application state.

Use motion-reduce:* or motion-safe:* to respect reduced-motion preferences. Use forced-colors:* and system colors where necessary to retain borders and focus indicators. print:* should preserve essential content and avoid printing hidden answer panels merely because a display utility was overridden carelessly.

Source: https://tailwindcss.com/docs/responsive-design

Source: https://tailwindcss.com/docs/hover-focus-and-other-states

## 7 Tailwind CSS - design tokens, dark mode and extensions

Separate primitive tokens from semantic roles. A blue palette entry describes a color; --action describes an application purpose. A semantic foreground/background pair should be evaluated together in every theme. A token name is not evidence that its contrast is acceptable.

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
:root { --action: #1d4ed8; --surface: #ffffff; --ink: #172033; }
.dark { --action: #93c5fd; --surface: #111827; --ink: #f8fafc; }
@theme inline {
  --color-action: var(--action);
  --color-surface: var(--surface);
  --color-ink: var(--ink);
}
@theme { --breakpoint-wide: 90rem; --radius-panel: 0.8rem; }
@utility content-auto { content-visibility: auto; }
```

@theme makes tokens participate in utility generation. Ordinary :root variables remain normal CSS variables. @theme inline is useful when a theme token aliases another variable and the utility should resolve that alias at the point of use. @theme static requests emission of theme variables even when their associated utilities are not used. Resetting a namespace to initial intentionally removes its default token-driven utilities, so treat that as a compatibility change.

@utility registers a utility that can participate in variants. @custom-variant names a reusable selector/media condition. @variant applies variants inside authored CSS. @apply expands existing utility declarations inside a selector; it does not turn CSS into a general programming language or remove the need to understand the cascade. @reference provides context to independently processed styles without importing a second copy of all CSS. @config and @plugin support compatibility/plugin workflows; read their v4 limitations instead of assuming every old configuration option is supported.

Custom CSS belongs in an intentional cascade layer. Tailwind's layer order is theme, base, components, utilities. Normal unlayered author CSS can outrank normal layered utilities even at lower specificity. Importing Bulma unlayered beside Tailwind can therefore change expectations dramatically. Scope or separate the systems rather than assuming class names alone isolate them.

A dark-mode selector must reach portaled overlays. If the theme exists only on a nested app div while a dialog portal renders under body, the overlay may inherit different tokens. Put the theme on an appropriate common ancestor or provide a supported portal container. Persist user preference defensively and consider the OS preference when no explicit choice exists; storage can fail and server rendering can flash the wrong theme.

Source: https://tailwindcss.com/docs/theme

Source: https://tailwindcss.com/docs/functions-and-directives

Source: https://tailwindcss.com/docs/dark-mode

## 8 Tailwind CSS - production architecture and debugging

Extract a component when a domain concept or repeated behavior deserves an API. Repetition of three utility tokens alone is weak evidence for abstraction. A CourseCard component can own a heading relationship, progress semantics and loading state; a class string cannot enforce those contracts.

Keep finite variants in a lookup or a variant helper. Reject contradictory domain states such as simultaneously busy and ready-to-submit. Do not remove focus styles because a default ring clashes with a theme; replace them with an equally usable indicator. A disabled button prevents an action but may make an explanation unreachable, so offer nearby text when the user needs to understand why.

Tailwind is not automatically “smaller” than every alternative. Measure the production CSS, repeated markup, component JavaScript and user-perceived rendering costs. Excessive arbitrary values dilute design consistency; broad source inclusion can inflate CSS. Conversely, deleting every repeated utility through @apply can make the system harder to trace. Optimize a measured bottleneck.

Debug in this order: confirm candidate text exists; confirm the compiler saw that file; confirm the emitted selector exists; confirm its variant condition matches; inspect cascade precedence; inspect layout constraints; then inspect browser feature support. Reordering classes at random skips the causal chain.

A v3-to-v4 migration should inventory build adapters, configuration, custom plugins, renamed utilities, default border/ring behavior, variant stacking and browser support. Upgrade in a branch, compare representative screens and interactions, and inspect generated CSS. Do not run a migration tool against an unrelated application merely to illustrate a curriculum.

Source: https://tailwindcss.com/docs/adding-custom-styles

## 9 Bulma - CSS architecture, installation and naming

Bulma provides visual building blocks through ordinary class names. It can style server-rendered HTML, React, Vue, static pages or Web Components with appropriate CSS scope. It does not ship a JavaScript interaction engine. A navbar burger, dropdown, tab set or modal must be wired to real state and accessibility behavior by the application.

```sh
npm install bulma@1.0.4
```

```html
<link rel="stylesheet" href="./node_modules/bulma/css/bulma.css">
<button type="button" class="button is-link">Start practice</button>
```

The base class identifies the component, child classes identify its anatomy, and is-*/has-* modifiers describe variants or helper behavior. A modifier only works where the CSS defines it. is-large does not resize every arbitrary element; has-text-centered sets alignment but does not give a control an accessible name.

Bulma's reset/base rules have global effects. Loading only the classes you think you need is not always sufficient because component modules depend on shared utilities, variables and themes. Begin with a working full build, then reduce imports with measured visual and behavior checks. Do not combine two global resets blindly.

Use the source package as the authoritative list for the pinned release. Documentation can evolve independently. The reference chapters below cover layout, elements, forms, components, helpers and theme architecture; they do not treat every generated color/spacing permutation as a separate concept.

## 10 Bulma - columns, grid, containers and responsive layout

columns is the row-like wrapper and column its children. Equal columns share available space; fractional and twelve-part width modifiers express explicit proportions. Mobile stacking is the usual baseline. is-mobile requests a horizontal column arrangement even at small widths, which can be inappropriate for long forms. is-multiline allows wrapping; is-gapless removes gutters; is-vcentered changes alignment rather than the semantic reading order.

```html
<div class="columns is-multiline">
  <div class="column is-full-mobile is-half-tablet is-one-third-desktop">
    <article class="box">
      <h2 class="title is-4">Arrays</h2>
      <p>Practice indexing and iteration before two-pointer problems.</p>
    </article>
  </div>
</div>
```

Bulma's default breakpoints are mobile through 768px, tablet from 769px, desktop from 1024px, widescreen from 1216px and fullhd from 1408px, subject to Sass customization and feature switches. Width helpers and visibility helpers may support different suffix sets. A rule that works at desktop-and-above differs from one constrained to desktop-only.

The v1 smart grid uses grid with cell children and minimum-column-width/gap helpers, allowing the number of columns to follow available space. fixed-grid provides explicit column-count control. A grid is still CSS Grid; spanning cells, intrinsic minimums and source order follow platform behavior. Choose columns for familiar flex-based composition and grid for track-based constraints rather than nesting columns to imitate every grid pattern.

container constrains and centers content; section supplies page spacing; hero composes a prominent content region; level aligns compact horizontal groups; media aligns a figure with text. None defines landmarks automatically. Use header/main/section/article according to document meaning and add headings where appropriate.

Source: https://bulma.io/documentation/columns/basics/

Source: https://bulma.io/documentation/grid/smart-grid/

## 11 Bulma - forms, validation and feedback

The field wrapper groups a label, control and help text. control handles the input layout, including icons or loading decoration. input, textarea and select style the underlying native elements. A styled select wrapper still requires an actual select element; a decorative icon must not replace a visible or programmatic label.

```html
<div class="field">
  <label class="label" for="practice-email">Email</label>
  <div class="control">
    <input class="input" id="practice-email" name="email" type="email"
      autocomplete="email" required aria-describedby="email-help">
  </div>
  <p class="help" id="email-help">We use this for progress reminders.</p>
</div>
```

For an error, add is-danger to the appropriate control, set aria-invalid="true", attach an error description and explain how to recover. Do not rely on red alone. Clear the error when validation succeeds and keep help/error identifiers stable. Native required/type/min/max constraints provide useful behavior, but authoritative validation remains necessary wherever data is persisted.

Grouped fields, addons and horizontal forms solve visual arrangements. They do not create a label relationship or keyboard group automatically. A radio group needs a fieldset and legend when a shared question must be conveyed. Native disabled and readonly have different submission and interaction semantics; is-static is presentation, not an authorization control.

A loading spinner should accompany a clear busy label or status. is-loading does not prevent repeated submission. Set the actual disabled property where appropriate and preserve understandable feedback. Async errors must reach the relevant control or summary without moving focus unpredictably after every keystroke.

Source: https://bulma.io/documentation/form/general/

## 12 Bulma - interactive components and application-owned behavior

A Bulma navbar contains navbar-brand, navbar-burger and navbar-menu; menu sections contain navbar-start/navbar-end and navbar-item. Use a real button for the burger with aria-controls and aria-expanded, then toggle is-active on both the button and menu. Preserve normal link semantics. A desktop hover menu needs an equivalent keyboard/touch interaction if it contains essential navigation.

A modal is more than .modal.is-active. An accessible implementation must move focus inside, keep background interaction unavailable, support an appropriate Escape policy, expose a name/description and restore focus on close. The runnable lab uses a native dialog with Bulma visual parts, relying on showModal() for top-layer modality. Do not add a second, conflicting focus trap around native dialog.

Dropdown menus need deliberate semantics. A simple disclosure of navigation links can remain ordinary links inside a region. An ARIA menu requires the full menu keyboard model, not just role="menu". Tabs similarly require selected state, panel relationships and correct keyboard interaction if implemented as an ARIA tab widget; a row of navigation links styled as tabs is a different valid pattern.

Message and notification components communicate status; choose live regions only when updates need announcement. A static explanation need not interrupt assistive technology. A delete-style close button needs an explicit name such as “Dismiss progress notice.” Pagination should identify the navigation region and mark the current page; disabled-looking anchors must not keep navigating.

Source: https://bulma.io/documentation/components/navbar/

Source: https://bulma.io/documentation/components/modal/

## 13 Bulma - modular Sass, CSS variables and themes

Sass configuration determines what CSS is built. CSS custom properties determine values at runtime. Use Sass to select modules and establish foundational scales; use scoped custom properties for supported runtime adjustments. Changing a Sass variable in a browser does nothing because Sass no longer exists there.

```scss
@use "bulma/sass" with (
  $family-primary: 'Arial, sans-serif',
  $primary: #2456a6
);
```

Use @use configuration before a module is loaded; Sass modules are evaluated once per compilation. Reconfiguring an already-loaded module can fail. A modular build can import utilities, base/themes and selected elements/components, but exact dependencies must be checked against the installed version. Preserve ordering and compare compiled output after reducing modules.

Bulma's CSS variables use a --bulma- prefix by default. Many colors are represented through hue/saturation/lightness and derived role values; overriding a single final color can leave hover, border or contrast variables inconsistent. Inspect the component's local variables and derived properties before designing a custom theme.

```css
[data-theme="dark"] { color-scheme: dark; }
.practice-scope { --bulma-primary-h: 218deg; }
```

The hue example affects descendants using that token; it does not guarantee every component becomes a coherent new theme. Themes can follow system preference or explicit data-theme/class selectors. Scope overrides deliberately and inspect both light and dark states. Do not treat a theme switch as permission to discard contrast, disabled-state readability or focus indication.

Spacing helpers cover margin and padding directions and scale values; typography/color/flex/visibility helpers provide targeted overrides. Helpers can clash with component styles or each other. Prefer one intentional rule over accumulating opposing modifiers and then depending on stylesheet order accidentally.

Source: https://bulma.io/documentation/customize/with-modular-sass/

Source: https://bulma.io/documentation/features/css-variables/

Source: https://bulma.io/documentation/features/dark-mode/

## 14 shadcn/ui - source ownership, primitive bases and installation

shadcn/ui supplies source that becomes part of your project, together with CLI/registry conventions. You own the resulting customization and review burden. A package update to a primitive dependency does not automatically merge improvements into copied component source. A registry refresh may change both visuals and behavioral composition, so review the diff like application code.

The current default base is Base UI. Radix remains relevant for existing projects and explicit installations. A Base UI trigger commonly composes through a render prop; Radix examples often use asChild. These are distinct APIs. Inspect the copied component's imports and type signature before translating a tutorial.

```tsx
// Base UI composition through a source-owned wrapper:
<DialogTrigger render={<Button />}>Open learning plan</DialogTrigger>
```

```tsx
// Radix-only counterpart; do not pass asChild to an unrelated wrapper:
<DialogTrigger asChild>
  <Button>Open learning plan</Button>
</DialogTrigger>
```

The examples are API contrasts, not interchangeable components. The complete lab uses Base UI throughout. Render composition must preserve forwarded props, event handlers, refs and native element semantics; a custom component that swallows a ref or onClick can break focus restoration and activation.

A normal project setup establishes a React-capable build, Tailwind CSS, token CSS, aliases and components.json, then initializes the CLI and adds selected components. Use a pinned CLI in a reproducible workflow:

```sh
npx shadcn@4.22.0 init
npx shadcn@4.22.0 add button dialog accordion
```

These commands mutate the selected project and may install dependencies. Run them in the intended clean project, inspect generated files and commit the lockfile. CLI options and generated style defaults can change; inspect --help and the project configuration rather than treating this pair of commands as a complete universal installation recipe.

Source: https://ui.shadcn.com/docs/installation/vite

Source: https://ui.shadcn.com/docs/cli

## 15 shadcn/ui - component anatomy, variants and data contracts

A source-owned component often combines a primitive, a utility class recipe, a merging helper and a typed public interface. The primitive manages interaction state and accessibility mechanics; the wrapper supplies design-system defaults; the application supplies content and domain behavior. The boundaries matter when a bug appears: a missing label belongs to the application even if focus trapping belongs to the primitive.

class-variance-authority maps finite variant values to class strings. clsx assembles conditional classes; tailwind-merge resolves known utility conflicts. Neither validates accessibility or computes browser styles. Extend the merge configuration if your custom utility families require it, and test the extension rather than assuming every arbitrary class is recognized.

```tsx
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...values: ClassValue[]) {
  return twMerge(clsx(values));
}
```

A local Button should expose a small semantic variant set such as primary, secondary and destructive. Size is independent of purpose. A danger-looking button should describe the destructive action in text, not only by color. An icon-only control needs an accessible name and adequate target size. A tooltip is useful supplementary help, not a reliable replacement for the name.

Use data-slot and component-specific data attributes as styling hooks where actually provided. Do not infer that Base UI and Radix emit identical attributes. Controlled state uses a value/open prop with the corresponding change callback; uncontrolled state uses a default value. Do not switch modes unintentionally when async data first arrives.

A compound component needs its full anatomy. Dialog requires a root, trigger, portal/backdrop/popup arrangement, title and suitable close behavior. Accordion requires an item value, header/trigger and panel relationship. Select and combobox differ in editable input behavior. A menu command is not the same as a navigation link.

Source: https://ui.shadcn.com/docs/components/base/button

Source: https://base-ui.com/react/handbook/composition

## 16 shadcn/ui - tokens, overlays, forms and data-heavy screens

Map semantic CSS variables to Tailwind theme tokens using @theme inline. Typical roles include background/foreground, card/card-foreground, popover/popover-foreground, primary/primary-foreground, secondary, muted, accent, destructive, border, input and ring. Radius and chart/sidebar roles extend the system. Preserve pairings in every theme, including overlays mounted outside the local subtree.

Dialog and Sheet expose modal content; Popover exposes contextual content; Tooltip offers brief nonessential help; Alert Dialog asks for a consequential decision. Choose the interaction model before selecting the visual style. A form inside a dialog needs explicit cancel/submit buttons, error association and focus management after submission. Opening a second overlay requires testing escape handling, stacking and focus restoration across the nested lifecycle.

Forms can use native controls and React state, or integrate a form library and a validation schema. Those libraries solve different problems: field state, validation and visual composition must remain coherent. Mark invalid fields semantically, attach errors through stable IDs, and preserve values after recoverable errors. Server/API validation cannot be replaced by client styling.

Data Table is typically a composition around a table engine, not a universal one-prop grid. Sorting, filtering, selection, pagination and virtualization have separate state models. Preserve a semantic table where appropriate, name selection controls, expose sort state and announce meaningful result changes. Virtualization changes the rendered DOM and requires careful keyboard/screen-reader testing.

Calendar and Date Picker depend on date semantics and locale. Persisting a calendar date differs from persisting an instant with a time zone. Chart components require readable legends and text/table alternatives; a colored line is not sufficient access to the data. Carousel needs pause/control behavior where motion is automatic, and its content must remain reachable without dragging.

Source: https://ui.shadcn.com/docs/theming

Source: https://ui.shadcn.com/docs/components/base/dialog

## 17 shadcn/ui - registries, configuration and maintenance

components.json is tool configuration, not a runtime theme provider. Important concerns include the chosen style/base where supported, CSS entrypoint, CSS-variable policy, TypeScript/React mode and import aliases. An alias must agree with the bundler and TypeScript configuration; a string in components.json alone cannot make imports resolve.

A registry item describes files, dependencies, related registry items and optional CSS/configuration changes. Treat a registry as a source-code supplier. Inspect URLs, file targets, dependency additions, scripts and licensing before installation. A familiar-looking component name is not a trust boundary. Private registry authentication belongs in an appropriate secret mechanism rather than committed config.

Record the source URL and SHA-256 of copied items. Keep upstream source distinct from local adaptations. Review updates in a clean branch, inspect changes to primitive props and data attributes, run type checking/builds and repeat interaction tests. Blindly overwriting modified source can destroy product-specific accessibility or validation work.

The current registry templates may contain placeholders intended for CLI transformation, including alias and icon placeholders. Raw JSON is not necessarily drop-in application code. The lab intentionally uses compact locally authored wrappers on the same Base UI/Tailwind stack; it does not claim to be an unmodified generated registry installation. Registry snapshots are retained as provenance references, separate from the tested lab source.

Source: https://ui.shadcn.com/docs/components-json

Source: https://ui.shadcn.com/docs/registry/registry-item-json

## 18 Symbiotic integration - DOM, attributes, APIs and rendering

The runtime lifecycle starts with a meaningful DOM, applies CSS, responds to user input, updates state and then allows the browser to recalculate style, layout, paint and compositing as required. Tailwind and Bulma ultimately provide CSS declarations; source-owned React components also coordinate behavior and state. Sass is absent at runtime.

Attribute selectors connect semantic state to presentation. aria-expanded can drive a chevron rotation, aria-invalid can drive an error border and data-state can drive a transition. Attribute changes do not implement the semantic behavior automatically. Keep the panel visibility, enabled state and accessibility relationships in sync with the same state owner.

ResizeObserver observes element size changes after layout. Prefer CSS container queries for purely visual adaptation; use an observer when JavaScript needs the measured size, such as a chart renderer. Batch state changes and avoid resizing an observed element in a way that causes a loop. Disconnect observers on teardown. A MutationObserver watches DOM mutations, not computed style or every pixel-size change; React state is usually a better source of truth for React-owned changes.

CSS Typed OM can represent supported CSS values structurally. Feature-detect attributeStyleMap and CSSUnitValue before using them and retain a normal style.setProperty fallback. This is useful for carefully controlled numeric values, not for bypassing validation of user input or assuming every property is implemented.

View Transitions coordinates visual snapshots around DOM changes when supported. Respect reduced motion, keep the actual state update correct without the API, and handle asynchronous work/errors without stranding the interface. Do not depend on a decorative transition for error feedback or navigation correctness.

Shadow DOM creates a style boundary. Global Tailwind/Bulma CSS does not automatically style descendants inside a shadow root. Ship appropriate styles into the root or expose stable ::part/custom-property contracts. Inherited custom properties can cross the boundary; ordinary global selectors cannot pierce it. Portals and shadow roots also alter which ancestors provide theme variables and container-query context.

React effects should clean up event listeners, observers, timers and subscriptions. Strict Mode can reveal missing cleanup by exercising setup/teardown cycles. Read layout in a batch and write changes in another phase when possible; repeatedly alternating measurements and writes can force unnecessary synchronous layout.

Source: https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver

Source: https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver

Source: https://developer.mozilla.org/en-US/docs/Web/API/CSS_Typed_OM_API

Source: https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API

Source: https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM

## 19 Choosing and combining systems responsibly

Choose Tailwind for a custom visual language with explicit utility/token composition. Choose Bulma for a productive class-based CSS baseline across different rendering stacks. Choose shadcn/ui when source ownership and composable React primitives match the team's maintenance capacity. A static documentation page may need no interactive component stack at all.

Tailwind and shadcn/ui fit naturally because the copied source uses utility classes and semantic tokens. Bulma and Tailwind can coexist during migration, but resets, unlayered rules, generic class names and token scopes require a plan. A prefix can reduce class collisions but does not automatically isolate global element selectors. Separate documents, shadow boundaries or carefully tested cascade layers may be more predictable than loading two complete frameworks globally.

A migration should move one coherent feature at a time. Inventory behavior and semantics, define token mappings, implement the replacement, compare layouts at representative widths and repeat keyboard/error-state tests. Do not declare success merely because a screenshot matches the default light theme.

Use a decision record: required rendering stack, browser matrix, interaction complexity, brand customization, team CSS skills, source-maintenance capacity, expected bundle costs and accessibility verification plan. Record why a system fits the product, then revisit the decision when those constraints change.

## 20 Tailwind CSS reference - utility families

Each record gives representative syntax, the underlying CSS contract and an engineering check. These are families, not every possible arbitrary value. Numeric/token values depend on the active theme. Square-bracket expressions must contain a value valid for the resulting CSS property. Unless a property is inherited by CSS itself, styling the parent does not automatically style its children.

### TW-01 Display and visibility

Representative candidates: `block, inline, inline-block, flex, grid, hidden, invisible, sr-only`.

Mechanism: display controls box generation; visibility can preserve occupied space; sr-only visually clips content while leaving an accessibility use case.

Engineering check: Do not hide a required focus target with hidden, or put a focusable control inside an invisible disclosure. Test both visual display and keyboard reachability.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/display

### TW-02 Position and insets

Representative candidates: `relative, absolute, fixed, sticky, inset-0, top-4, start-0`.

Mechanism: Positioning changes participation in flow and the containing-block relationship. Logical start/end adapt to direction. Sticky needs a threshold and a compatible scroll ancestor.

Engineering check: Check ancestor overflow before declaring sticky broken. Fixed content must not cover focused fields at zoom.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/position

### TW-03 Stacking and isolation

Representative candidates: `z-10, z-50, isolate, isolation-auto`.

Mechanism: z-index participates within stacking contexts. isolate establishes a new context; transforms and opacity can also establish contexts.

Engineering check: Inspect the complete ancestor chain and portaled overlay placement. A larger number in a lower context cannot necessarily outrank a sibling context.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/z-index

### TW-04 Overflow and scroll boundaries

Representative candidates: `overflow-auto, overflow-x-auto, overflow-hidden, overscroll-contain`.

Mechanism: Overflow chooses clipping/scroll behavior by axis. Overscroll controls boundary propagation rather than the existence of a scrollbar.

Engineering check: Retain access to overflowing code blocks using keyboard and pointer. Clipping focus outlines is a regression even when a screenshot appears tidy.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/overflow

### TW-05 Box sizing and aspect ratio

Representative candidates: `box-border, box-content, aspect-square, aspect-video, aspect-[4/3]`.

Mechanism: Box sizing determines whether declared dimensions include borders/padding. Aspect ratio supplies a preferred ratio and interacts with explicit dimensions.

Engineering check: Reserve media space without forcing images into a distorted ratio. Use object-fit to choose cropping behavior explicitly.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/aspect-ratio

### TW-06 Flex direction and wrapping

Representative candidates: `flex-row, flex-col, flex-wrap, flex-nowrap`.

Mechanism: Direction selects the main axis; wrapping permits multiple lines. The cross axis changes when direction changes.

Engineering check: Do not use row-reverse as a shortcut for semantic order. Test a long translated action label before choosing nowrap.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/flex-direction

### TW-07 Flex sizing

Representative candidates: `flex-1, flex-auto, flex-none, grow, shrink-0, basis-1/2`.

Mechanism: The shorthand coordinates grow, shrink and basis. Automatic minimum sizing can prevent a child from shrinking despite flex-1.

Engineering check: Add min-w-0 only where text should be allowed to shrink; then provide wrapping or overflow behavior rather than silently losing content.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/flex

### TW-08 Order

Representative candidates: `order-first, order-last, order-2`.

Mechanism: Order changes visual placement inside flex/grid without rewriting DOM order. It normally does not change tab or reading order.

Engineering check: Use it only where the resulting source/visual relationship remains understandable. Test sequential keyboard traversal.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/order

### TW-09 Grid templates

Representative candidates: `grid-cols-3, grid-cols-subgrid, grid-rows-2, grid-cols-[16rem_1fr]`.

Mechanism: Explicit tracks define the grid. Fractional tracks distribute remaining space; subgrid can align descendant tracks with an ancestor.

Engineering check: Inspect intrinsic minimum sizes and narrow containers. Repeat/minmax patterns are often safer than fixed tracks for unknown content.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/grid-template-columns

### TW-10 Grid placement

Representative candidates: `col-span-2, col-start-2, col-end-4, row-span-2`.

Mechanism: Line numbers and spans place items in tracks. Implicit tracks may be created when placement exceeds the explicit grid.

Engineering check: Check that the layout is understandable in DOM order. Dense packing can create visually surprising reading order.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/grid-column

### TW-11 Grid auto flow

Representative candidates: `grid-flow-row, grid-flow-col, grid-flow-dense, auto-rows-fr`.

Mechanism: Auto placement fills remaining cells; implicit row/column sizing controls tracks created outside the explicit template.

Engineering check: Dense packing can backfill holes but should not be used to scramble a sequential curriculum. Check keyboard order.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/grid-auto-flow

### TW-12 Gaps and alignment

Representative candidates: `gap-4, gap-x-6, items-center, justify-between, place-items-center`.

Mechanism: Gap separates tracks/items. Align generally acts on the cross/block axis; justify acts on the main/inline axis according to layout mode.

Engineering check: Space-between does not add edge gutters. Verify the behavior when only one item remains and when the row wraps.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/gap

### TW-13 Padding and margin

Representative candidates: `p-4, px-6, py-2, ps-4, m-auto, -mt-2, mx-auto`.

Mechanism: Padding is internal space; margin is external. Logical directions adapt to writing direction. Margins can collapse in normal block flow.

Engineering check: Use container padding for page edges and gap for sibling spacing. Confirm negative margins do not create horizontal overflow.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/padding

### TW-14 Width and inline sizing

Representative candidates: `w-full, w-auto, w-1/2, w-64, size-10, min-w-0, max-w-prose`.

Mechanism: Width constraints interact with the parent formatting context. size-* sets width and height together. Percentage sizes require a suitable containing block.

Engineering check: A full-width child plus extra content-box padding can overflow; inspect box sizing. Do not fix form widths in pixels without a reason.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/width

### TW-15 Height and viewport units

Representative candidates: `h-auto, h-full, min-h-screen, min-h-dvh, max-h-96`.

Mechanism: A percentage height needs a definite containing height in relevant cases. Dynamic viewport units respond to browser UI changes.

Engineering check: Use a minimum height for content pages so zoom/translation can increase content. Test mobile browser controls and on-screen keyboards.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/height

### TW-16 Font family and style

Representative candidates: `font-sans, font-mono, italic, not-italic, font-semibold`.

Mechanism: These set inheritable font properties. A font token does not download a font or guarantee identical metrics across platforms.

Engineering check: Provide fallbacks and load fonts intentionally. Compare layout before and after font loading for visible shifts.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/font-family

### TW-17 Text scale and rhythm

Representative candidates: `text-sm, text-xl, text-base/7, leading-relaxed, tracking-wide`.

Mechanism: Font size, line-height and letter spacing combine to determine readability and fit. Slash line-height modifiers belong to the text-size family.

Engineering check: Avoid fixed-height text containers. Test enlarged text and scripts with different glyph metrics.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/font-size

### TW-18 Text flow

Representative candidates: `text-left, text-start, text-balance, text-pretty, whitespace-pre-wrap, break-words`.

Mechanism: Alignment, wrapping and whitespace are separate properties. Logical alignment follows direction. Preserved whitespace is useful for code but can increase overflow.

Engineering check: Never truncate the only accessible form of essential instructions. If truncation is intentional, expose a usable expansion mechanism.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/text-wrap

### TW-19 Decoration and casing

Representative candidates: `underline, no-underline, decoration-2, underline-offset-4, uppercase`.

Mechanism: Text decoration can identify links; transformation changes presentation rather than the stored string.

Engineering check: Keep links distinguishable without relying solely on color. Uppercase long passages can reduce readability.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/text-decoration-line

### TW-20 Lists and line clamping

Representative candidates: `list-disc, list-decimal, list-inside, line-clamp-3`.

Mechanism: List utilities restore or customize marker presentation. Clamping visually limits lines and can hide meaningful content.

Engineering check: Keep semantic ul/ol elements. Provide an expansion option when clamping summaries containing decisions or instructions.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/line-clamp

### TW-21 Background color and images

Representative candidates: `bg-slate-100, bg-black/50, bg-[url(/texture.svg)], bg-cover, bg-center`.

Mechanism: Backgrounds are decoration and do not expose alternative text. Slash opacity modifies the color rather than the entire element.

Engineering check: Put essential images in img with appropriate alt. Overlay text contrast must remain sufficient across the image region.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/background-color

### TW-22 Gradients

Representative candidates: `bg-linear-to-r, from-blue-800, via-indigo-800, to-purple-900`.

Mechanism: Gradient stops form a generated background image. Color interpolation and stop placement affect the resulting visual field.

Engineering check: Test text contrast at the weakest region, not only against a nominal brand color. Supply a solid-color fallback where required.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/background-image

### TW-23 Borders and radius

Representative candidates: `border, border-2, border-slate-300, rounded-lg, rounded-full`.

Mechanism: Border width/style/color are independent; radius changes corners rather than layout geometry.

Engineering check: A rounded container does not necessarily clip its children. Add overflow clipping only when it does not cut off focus or menus.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/border-width

### TW-24 Outlines and rings

Representative candidates: `outline-2, outline-offset-4, ring-2, ring-blue-700`.

Mechanism: Outlines do not occupy layout space; ring utilities are implemented through shadow-related composition.

Engineering check: Do not remove browser focus without a visible substitute. Verify focus in forced colors where shadows can disappear.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/outline-width

### TW-25 Shadows and opacity

Representative candidates: `shadow-sm, shadow-xl, inset-shadow-sm, opacity-50`.

Mechanism: Shadow suggests depth without changing layout size. Opacity affects the entire composited element, including descendants.

Engineering check: Use translucent backgrounds when text should remain opaque. Never use opacity alone to encode disabled semantics.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/box-shadow

### TW-26 Filters and backdrop filters

Representative candidates: `blur-sm, grayscale, brightness-110, backdrop-blur-sm`.

Mechanism: Filters operate on the element rendering; backdrop filters affect content behind a translucent surface.

Engineering check: Measure paint costs on large moving areas and preserve legibility. A decorative blur must not hide essential state.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/filter

### TW-27 Masks and blending

Representative candidates: `mask-linear-from-black, mix-blend-multiply, bg-blend-overlay`.

Mechanism: Masks alter visibility; blend modes combine colors with a backdrop and can depend on stacking/isolation.

Engineering check: Validate the actual emitted mask syntax for the pinned compiler. Provide an understandable fallback and do not mask keyboard focus.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/mask-image

### TW-28 Transforms

Representative candidates: `translate-x-1/2, -translate-y-1/2, rotate-45, scale-105, origin-center`.

Mechanism: Transforms change rendering and can create stacking/containing-block effects without reflowing normal siblings.

Engineering check: Use transforms for subtle motion, not to fake layout that must reserve space. Check transformed text legibility and overlay anchoring.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/transform

### TW-29 3D transforms

Representative candidates: `perspective-normal, transform-3d, backface-hidden`.

Mechanism: Perspective and preserve-3d affect spatial rendering and descendants. These do not establish meaningful content order.

Engineering check: Keep core information available without a flip animation. Test reduced motion and browser support before using 3D navigation.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/perspective

### TW-30 Transitions

Representative candidates: `transition-colors, duration-150, ease-out, delay-75`.

Mechanism: Transition declarations define which changed properties animate and how. They do not initiate a state change.

Engineering check: Prefer a narrow property set over transition-all. Respect motion preferences and avoid animating layout continuously without measuring cost.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/transition-property

### TW-31 Animation

Representative candidates: `animate-spin, animate-pulse, animate-none, motion-reduce:animate-none`.

Mechanism: Animations reference keyframes through theme tokens or arbitrary definitions. They can run independently of user input.

Engineering check: A spinner requires a meaningful busy status; it is not the status itself. Avoid indefinite distracting motion around essential content.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/animation

### TW-32 Forms and native appearance

Representative candidates: `accent-blue-700, appearance-none, caret-blue-700, field-sizing-content`.

Mechanism: These customize native controls with different levels of browser support. Removing appearance can remove familiar affordances.

Engineering check: Retain focus/checked/disabled indicators and native semantics. Feature-test advanced sizing and use a usable fallback.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/appearance

### TW-33 Interaction and hit testing

Representative candidates: `cursor-pointer, pointer-events-none, select-none, touch-pan-y`.

Mechanism: Cursor and hit testing are presentation/interaction hints; pointer-events does not necessarily remove keyboard activation.

Engineering check: Use the actual disabled attribute where appropriate. Do not disable text selection globally on instructional material.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/pointer-events

### TW-34 Scroll alignment

Representative candidates: `scroll-smooth, scroll-mt-24, snap-x, snap-mandatory, snap-start`.

Mechanism: Scroll margins offset target alignment; snapping controls stopping positions within a scroll container.

Engineering check: Prevent sticky headers from covering focus targets. Respect reduced motion and avoid trapping users in mandatory snap areas.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/scroll-margin

### TW-35 Tables

Representative candidates: `table-auto, table-fixed, border-collapse, border-spacing-2, caption-bottom`.

Mechanism: Table layout determines column sizing and border behavior; it does not create semantic table relationships.

Engineering check: Use caption and headers in markup. Allow horizontal scrolling for genuinely wide tabular data without hiding whole columns silently.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/table-layout

### TW-36 SVG

Representative candidates: `fill-current, fill-none, stroke-current, stroke-2`.

Mechanism: Utilities style SVG paint; currentColor links icon paint to inherited text color. Stroke width is independent of CSS border width.

Engineering check: Decorative inline SVG should be hidden from assistive technology; meaningful graphics need an accessible name and explanation.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/fill

### TW-37 Performance hints

Representative candidates: `will-change-transform, content-visibility via custom utility`.

Mechanism: Rendering hints can influence browser resource allocation but are not guaranteed optimizations. Excess use can increase memory or alter containment.

Engineering check: Measure before adding hints. Check focus, find-in-page and intrinsic sizing when using content-visibility.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/will-change

### TW-38 Forced colors and color scheme

Representative candidates: `forced-color-adjust-auto, scheme-dark, forced-colors:outline`.

Mechanism: Color scheme informs native control styling; forced-color adjustment affects user high-contrast processing.

Engineering check: Prefer preserving user settings. Test system colors and avoid opting out merely to preserve a brand palette.

Practice: place this family in the study dashboard, inspect its computed properties at two widths and explain which browser rule determines the result. Record the exact candidate and active variant; do not infer support from a similar-looking class name.

Source: https://tailwindcss.com/docs/forced-color-adjust

## 21 Bulma reference - modules, anatomy and modifiers

These records cover the major module families in Bulma 1.0.4. Color and size modifiers are component-specific. Use the shipped Sass/CSS to confirm support rather than applying is-* indiscriminately. Elements inherit typography/color through CSS, while layout and component borders are generally local.

### BU-01 Button

Anatomy and representative classes: `button; is-primary/is-link/is-danger; is-small/is-medium/is-large; is-outlined/is-light/is-fullwidth/is-loading`.

Implementation contract: Use button for actions and a for navigation. Loading presentation does not prevent double submission; set native disabled or an intentional pending-state policy.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/button/

### BU-02 Box

Anatomy and representative classes: `box`.

Implementation contract: A padded surface for arbitrary content. It provides no heading, landmark or interaction semantics. Avoid nesting surfaces so deeply that hierarchy depends only on shadows.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/box/

### BU-03 Content

Anatomy and representative classes: `content`.

Implementation contract: Opt-in styling for rich text such as rendered Markdown. Sanitize untrusted HTML separately. Confirm headings, lists and code remain readable at zoom and in dark mode.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/content/

### BU-04 Delete

Anatomy and representative classes: `delete; size modifiers`.

Implementation contract: A compact close affordance with no inherent action or accessible name. Use a button with type=button and an explicit label describing the dismissed item.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/delete/

### BU-05 Icon

Anatomy and representative classes: `icon; icon-text`.

Implementation contract: A sizing/alignment wrapper, not an icon library. Supply the graphic yourself. Hide decoration from assistive technology and keep meaningful labels as real text.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/icon/

### BU-06 Image

Anatomy and representative classes: `image; is-square/is-16by9 and fixed-size helpers`.

Implementation contract: Ratio and size wrappers reserve layout space. Add an img with appropriate alt; decide whether object-fit cropping is acceptable. A ratio class does not provide alternative text.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/image/

### BU-07 Notification

Anatomy and representative classes: `notification; is-primary/is-light`.

Implementation contract: A visual status surface. Dismissal requires your own logic. Use a live region only for updates that need announcement and ensure dismissed content can be recovered when important.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/notification/

### BU-08 Progress

Anatomy and representative classes: `progress; color/size modifiers`.

Implementation contract: Use the native progress element with value and max when determinate, and an accessible label. Do not invent progress numbers for an unknown-length task.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/progress/

### BU-09 Table

Anatomy and representative classes: `table; is-striped/is-bordered/is-hoverable/is-fullwidth; table-container`.

Implementation contract: Apply to a semantic table with caption/header relationships. A scroll wrapper can preserve wide data. Hover highlighting is supplementary and must not be the only selection indicator.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/table/

### BU-10 Tag

Anatomy and representative classes: `tag; tags; has-addons/is-delete`.

Implementation contract: Short labels and grouping. A removable tag needs a real named button and state update; status cannot depend only on tag color. Keep long translated labels usable.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/tag/

### BU-11 Title and subtitle

Anatomy and representative classes: `title; subtitle; is-1 through is-6`.

Implementation contract: Visual sizes are independent of heading rank. Choose h1/h2/etc for structure, then apply the desired size class. Do not choose an h4 merely to make text smaller.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/title/

### BU-12 Block

Anatomy and representative classes: `block`.

Implementation contract: A simple vertical grouping/spacing convention. It does not establish a landmark or a component boundary; use meaningful markup according to the content.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/elements/block/

### BU-13 Input and textarea

Anatomy and representative classes: `input; textarea; is-danger/is-success; is-static`.

Implementation contract: Style native controls; label each one and connect help/errors. Styling static appearance does not create readonly behavior. Native type and validation rules remain active.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/form/input/

### BU-14 Select

Anatomy and representative classes: `select; is-multiple/is-fullwidth/is-loading`.

Implementation contract: The wrapper styles a native select. Label the select itself and supply meaningful option values. A decorative loading state must not obscure the selected value.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/form/select/

### BU-15 Checkbox and radio

Anatomy and representative classes: `checkbox; radio`.

Implementation contract: Retain native inputs and visible labels. Group related choices using fieldset/legend. Do not replace native controls with decorative spans unless implementing the complete interaction model.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/form/checkbox/

### BU-16 File

Anatomy and representative classes: `file; file-label/file-input/file-cta/file-name; has-name/is-boxed`.

Implementation contract: The file input is the functional control; the surrounding structure supplies presentation. Reflect selected filenames safely with textContent and validate file content server-side where relevant.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/form/file/

### BU-17 Field and control

Anatomy and representative classes: `field; control; label; help; is-grouped/has-addons/is-horizontal`.

Implementation contract: Anatomy supports spacing and layout but does not connect labels automatically. Stable IDs, name attributes and describedby relationships remain application responsibilities.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/form/general/

### BU-18 Breadcrumb

Anatomy and representative classes: `breadcrumb; is-centered/is-right; separator modifiers`.

Implementation contract: Use a named nav and ordered list. Identify the current page with aria-current. Decorative separators should not become noisy text in the accessibility tree.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/breadcrumb/

### BU-19 Card

Anatomy and representative classes: `card; card-header/card-content/card-image/card-footer`.

Implementation contract: Compose a surface with optional image/header/footer regions. A card containing multiple actions should not be wrapped in one giant link that nests other interactive controls.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/card/

### BU-20 Dropdown

Anatomy and representative classes: `dropdown; dropdown-trigger/dropdown-menu/dropdown-content; is-active/is-right/is-up`.

Implementation contract: Toggling is-active controls presentation only. Decide whether the content is a disclosure of links or a true menu and implement the matching keyboard/focus model.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/dropdown/

### BU-21 Menu

Anatomy and representative classes: `menu; menu-label/menu-list`.

Implementation contract: A sidebar navigation hierarchy using lists and links. This is not automatically the ARIA menu widget. Mark the current destination and preserve understandable nested structure.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/menu/

### BU-22 Message

Anatomy and representative classes: `message; message-header/message-body`.

Implementation contract: Group a heading and explanation. An optional close control needs behavior and a name. Static help normally should not use an interruptive alert role.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/message/

### BU-23 Modal

Anatomy and representative classes: `modal; modal-background/modal-content/modal-close; modal-card`.

Implementation contract: The CSS overlay requires application-owned modality, focus management, Escape policy and restoration. A native dialog with Bulma visual parts can simplify this contract, as the lab demonstrates.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/modal/

### BU-24 Navbar

Anatomy and representative classes: `navbar; navbar-brand/navbar-burger/navbar-menu/navbar-item`.

Implementation contract: A responsive navigation presentation. Wire actual expanded state and menu visibility together. Confirm touch, keyboard and narrow-screen operation; hover alone is insufficient.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/navbar/

### BU-25 Pagination

Anatomy and representative classes: `pagination; pagination-previous/pagination-next/pagination-list/pagination-link`.

Implementation contract: Use a named navigation region and current-page state. Represent unavailable actions appropriately. Maintain filters/sort context in URLs or application state when pages change.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/pagination/

### BU-26 Panel

Anatomy and representative classes: `panel; panel-heading/panel-tabs/panel-block`.

Implementation contract: A compact navigational or control surface. Each block can be a link, label or other appropriate element. Ensure icon-only blocks and selection controls have names.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/panel/

### BU-27 Tabs

Anatomy and representative classes: `tabs; is-boxed/is-toggle/is-fullwidth`.

Implementation contract: A visual row can represent page navigation or a true tab widget. For widgets implement tablist/tab/tabpanel roles, selection, relationships and expected keyboard navigation.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/components/tabs/

### BU-28 Columns

Anatomy and representative classes: `columns; column; is-multiline/is-gapless; width and offset modifiers`.

Implementation contract: Flex-based layout with responsive width conventions. Avoid nonsemantic visual reordering and test content pressure before forcing mobile columns horizontally.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/columns/basics/

### BU-29 Smart and fixed grid

Anatomy and representative classes: `grid; cell; fixed-grid; has-*-cols and minimum-width helpers`.

Implementation contract: CSS Grid-based layout with adaptive or explicit track counts. Confirm exact helper spellings in the release; do not transpose twelve-column flex modifiers into grid APIs.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/grid/smart-grid/

### BU-30 Container and section

Anatomy and representative classes: `container; section; is-fluid and size variants where supported`.

Implementation contract: Page-width constraints and spacing. These are CSS classes, not landmarks. Use main/section with a heading when document structure calls for them.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/layout/container/

### BU-31 Hero

Anatomy and representative classes: `hero; hero-head/hero-body/hero-foot; size/color variants`.

Implementation contract: A prominent region composed from optional header/body/footer areas. Keep the primary heading meaningful and avoid viewport-height clipping at zoom.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/layout/hero/

### BU-32 Level and media

Anatomy and representative classes: `level; level-left/level-right/level-item; media-left/media-content/media-right`.

Implementation contract: Compact alignment and image/text composition. They do not dictate semantic order. Long labels and flexible content need overflow and wrapping checks.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/layout/level/

### BU-33 Footer

Anatomy and representative classes: `footer`.

Implementation contract: Page-ending spacing/background conventions. Apply to a real footer where appropriate and name multiple navigation groups so repeated links remain understandable.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/layout/footer/

### BU-34 Spacing and typography helpers

Anatomy and representative classes: `m-*/p-* direction helpers; has-text-*; is-size-*`.

Implementation contract: Targeted single-purpose adjustments. Scales and suffix support are release-dependent. Avoid contradictory helper combinations and verify computed styles instead of assuming token order decides priority.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/helpers/spacing-helpers/

### BU-35 Visibility and flex helpers

Anatomy and representative classes: `is-hidden-*; is-flex; is-flex-direction-*; is-align-items-*`.

Implementation contract: Presentation helpers for responsive visibility and flex configuration. Hiding must match the intended accessibility state; layout helpers do not change reading order semantics.

Verification task: build the smallest meaningful example, test narrow and wide layouts, then inspect the accessibility tree. If the component has state, test a keyboard-only path and confirm that visual classes and semantic attributes change together.

Source: https://bulma.io/documentation/helpers/visibility-helpers/

## 22 shadcn/ui reference - component and pattern catalogue

The official component index is a moving catalogue. These records distinguish small visual wrappers, behavioral primitives and larger compositions. Names below describe the observed documentation surface; availability and exact exports can differ by primitive base, style and registry. They are not a promise of identical props or dependency-free installation. Read the corresponding current component page and installed TypeScript types before implementation.

For each record, acceptance means both the stated component-specific check and the common checks: meaningful names, keyboard operation, visible focus, theme contrast, responsive reflow and correct controlled/uncontrolled state. Only the complete labs in chapter 23 carry the automated evidence recorded in chapter 26; this catalogue is an instructional reference, not a claim that every component was executed.


### SH-01 Accordion

Purpose and ownership: Expandable sections with item, header/trigger and panel anatomy.

Component-specific acceptance: Use stable item values, test keyboard activation and arrow navigation as defined by the chosen primitive, and keep heading levels meaningful. Do not treat an accordion as a prerequisite for reading every essential instruction.

Source: https://ui.shadcn.com/docs/components/accordion

### SH-02 Alert

Purpose and ownership: A static or dynamic message surface with title and description.

Component-specific acceptance: Choose alert/live-region semantics only for content requiring timely announcement. Static explanatory content should not repeatedly interrupt a reader. Provide a recoverable next action for errors.

Source: https://ui.shadcn.com/docs/components/alert

### SH-03 Alert Dialog

Purpose and ownership: A focused decision about a consequential action.

Component-specific acceptance: Give the decision a clear title, consequence and cancel path. Test initial focus, Escape policy, background isolation and focus restoration. Do not use it as a decorative toast.

Source: https://ui.shadcn.com/docs/components/alert-dialog

### SH-04 Aspect Ratio

Purpose and ownership: A wrapper preserving a preferred width/height proportion.

Component-specific acceptance: Reserve media space and choose cropping intentionally. Provide image alternatives in actual markup; aspect ratio does not communicate content or guarantee a video player is accessible.

Source: https://ui.shadcn.com/docs/components/aspect-ratio

### SH-05 Attachment

Purpose and ownership: A file-oriented presentation for uploaded or linked material.

Component-specific acceptance: Expose filename, type, size and action as appropriate. Validate downloads/uploads separately, use safe text rendering and name remove/download controls distinctly for each attachment.

Source: https://ui.shadcn.com/docs/components/attachment

### SH-06 Avatar

Purpose and ownership: An image/fallback identity presentation.

Component-specific acceptance: Choose alt behavior according to nearby text to avoid duplicate names. Test missing/loading images and a meaningful fallback; initials alone may not be sufficiently identifying in every context.

Source: https://ui.shadcn.com/docs/components/avatar

### SH-07 Badge

Purpose and ownership: A compact label for a category or status.

Component-specific acceptance: Keep important state understandable without color. If interactive, use an appropriate link/button instead of attaching clicks to a decorative span. Long labels must remain readable.

Source: https://ui.shadcn.com/docs/components/badge

### SH-08 Breadcrumb

Purpose and ownership: A hierarchical location trail with links and current item.

Component-specific acceptance: Use a named navigation region and ordered list. Mark the current page and hide decorative separators from assistive technology. Avoid truncating the only useful location context.

Source: https://ui.shadcn.com/docs/components/breadcrumb

### SH-09 Bubble

Purpose and ownership: A message-like visual surface in conversational layouts.

Component-specific acceptance: Associate speaker and content clearly, preserve chronological reading order and distinguish status from message text. A speech-bubble shape alone cannot identify author, timing or delivery failure.

Source: https://ui.shadcn.com/docs/components/bubble

### SH-10 Button

Purpose and ownership: An action control with finite visual and size variants.

Component-specific acceptance: Default to native button semantics, specify type inside forms and name icon-only actions. Base render composition and Radix asChild differ; inspect the local wrapper before composing triggers.

Source: https://ui.shadcn.com/docs/components/button

### SH-11 Button Group

Purpose and ownership: A visual grouping of related actions.

Component-specific acceptance: Use a group name when relationships need explanation. Preserve individual names and focus indicators. A visual group does not automatically implement toolbar arrow-key navigation or mutually exclusive selection.

Source: https://ui.shadcn.com/docs/components/button-group

### SH-12 Calendar

Purpose and ownership: A date-selection surface with navigation and day cells.

Component-specific acceptance: Verify locale, week starts, disabled dates, keyboard movement and date-only persistence. Distinguish a calendar date from an instant and avoid time-zone conversion that changes the selected day.

Source: https://ui.shadcn.com/docs/components/calendar

### SH-13 Card

Purpose and ownership: A surface with optional header, title, description, content and footer.

Component-specific acceptance: Use meaningful headings and avoid nested interactive elements inside an all-card link. Preserve hierarchy without relying exclusively on borders or shadows and allow content-driven height.

Source: https://ui.shadcn.com/docs/components/card

### SH-14 Carousel

Purpose and ownership: A collection shown through a constrained viewport with navigation.

Component-specific acceptance: Provide usable previous/next controls and preserve content access without dragging. If auto-rotation is added, include pause behavior and respect reduced motion; do not hide focused slides.

Source: https://ui.shadcn.com/docs/components/carousel

### SH-15 Chart

Purpose and ownership: A styling/composition layer around a charting implementation.

Component-specific acceptance: Provide text/table equivalents for important data, understandable labels and non-color distinctions. Test resize behavior and tooltip access. A chart theme does not validate the statistical interpretation.

Source: https://ui.shadcn.com/docs/components/chart

### SH-16 Checkbox

Purpose and ownership: A binary or indeterminate selection control.

Component-specific acceptance: Associate a visible label and expose mixed state where relevant. Parent select-all state must derive from children. Decide how indeterminate/unchecked values map to form submission.

Source: https://ui.shadcn.com/docs/components/checkbox

### SH-17 Code Block

Purpose and ownership: A structured code presentation, often with copy/highlighting controls.

Component-specific acceptance: Render untrusted code as text and label language/copy actions. Preserve keyboard scrolling for long lines, announce copy success modestly and keep line highlighting distinct without color alone.

Source: https://ui.shadcn.com/docs/components/code-block

### SH-18 Collapsible

Purpose and ownership: A single disclosure controlled by a trigger.

Component-specific acceptance: Keep expanded state and panel visibility synchronized. If focus is inside a panel being closed, restore it appropriately. A simple disclosure does not need the entire accordion interaction model.

Source: https://ui.shadcn.com/docs/components/collapsible

### SH-19 Combobox

Purpose and ownership: An input or selection control with a related option popup.

Component-specific acceptance: Implement naming, expanded state, active-option relationships, filtering and keyboard selection through the chosen primitive. Empty results and async loading need distinct feedback; a styled input plus div is insufficient.

Source: https://ui.shadcn.com/docs/components/combobox

### SH-20 Command

Purpose and ownership: A searchable command palette or command list composition.

Component-specific acceptance: Separate commands from navigation results, name the search field and verify keyboard selection. Destructive commands need appropriate confirmation and shortcuts must not conflict with typing or assistive technology.

Source: https://ui.shadcn.com/docs/components/command

### SH-21 Context Menu

Purpose and ownership: A menu opened through contextual activation.

Component-specific acceptance: Provide an alternative visible path to essential actions. Test keyboard invocation, item navigation, dismissal and focus restoration. Right-click alone excludes touch and keyboard users.

Source: https://ui.shadcn.com/docs/components/context-menu

### SH-22 Data Table

Purpose and ownership: A composition of table semantics and stateful table-engine features.

Component-specific acceptance: Specify sorting/filtering/pagination ownership, stable row IDs and selection rules. Mark sort direction and name row controls. Virtualization requires extra checks because not all rows exist in the DOM.

Source: https://ui.shadcn.com/docs/components/data-table

### SH-23 Date Picker

Purpose and ownership: A date input paired with a calendar popup.

Component-specific acceptance: Allow an understandable text-entry or alternate interaction where appropriate. Explain format, validate impossible/out-of-range values and test popup focus return. Keep locale display separate from stored date representation.

Source: https://ui.shadcn.com/docs/components/date-picker

### SH-24 Dialog

Purpose and ownership: A modal/nonmodal dialog composition using the chosen primitive.

Component-specific acceptance: Supply title and description when useful, test focus containment/restoration and explicit close behavior. Portaled content needs correct tokens and stacking. Do not mix primitive bases within the same compound anatomy.

Source: https://ui.shadcn.com/docs/components/dialog

### SH-25 Direction

Purpose and ownership: A direction context for bidirectional layouts.

Component-specific acceptance: Set the document language/direction correctly and test logical spacing, icon direction and keyboard conventions. A provider alone does not translate content or repair hard-coded left/right assumptions.

Source: https://ui.shadcn.com/docs/components/direction

### SH-26 Drawer

Purpose and ownership: An edge-based overlay composition, often with gesture behavior.

Component-specific acceptance: Treat modality/focus behavior as a contract, not an animation. Include explicit close controls and avoid requiring drag gestures. Test scrolling inside the drawer and reduced-motion behavior.

Source: https://ui.shadcn.com/docs/components/drawer

### SH-27 Dropdown Menu

Purpose and ownership: A menu of actions opened by a trigger.

Component-specific acceptance: Use menu keyboard semantics from the primitive, distinguish links/actions and test nested menus. A dropdown of ordinary navigation links may be better represented as a simpler disclosure.

Source: https://ui.shadcn.com/docs/components/dropdown-menu

### SH-28 Empty

Purpose and ownership: A presentation for an absence of results or content.

Component-specific acceptance: Explain the state and provide an appropriate recovery action. Distinguish no results, not-yet-created content, permission restrictions and network failure rather than using one vague empty illustration.

Source: https://ui.shadcn.com/docs/components/empty

### SH-29 Field

Purpose and ownership: Form layout and labeling/error composition.

Component-specific acceptance: Attach the label and descriptions to the actual control. Stable identifiers and invalid state matter across library integrations. A visually adjacent error message is not automatically announced.

Source: https://ui.shadcn.com/docs/components/field

### SH-30 Hover Card

Purpose and ownership: Supplementary contextual content shown around a trigger.

Component-specific acceptance: Do not place essential actions or instructions exclusively behind hover. Verify keyboard/focus behavior and touch alternatives; use a dialog/popover when users need sustained interaction.

Source: https://ui.shadcn.com/docs/components/hover-card

### SH-31 Input

Purpose and ownership: A styled native text-like input.

Component-specific acceptance: Use a real label, correct type/autocomplete/inputmode and a name where submission requires it. Password/email/number inputs have different semantics; visual similarity does not make them interchangeable.

Source: https://ui.shadcn.com/docs/components/input

### SH-32 Input Group

Purpose and ownership: A control with adjacent icons, text or action addons.

Component-specific acceptance: Keep one clear label for the input and name addon buttons. Decorative prefixes/suffixes should not become confusing duplicate announcements. Verify flex sizing and error placement at narrow widths.

Source: https://ui.shadcn.com/docs/components/input-group

### SH-33 Input OTP

Purpose and ownership: A segmented one-time-code entry composition.

Component-specific acceptance: Support paste, appropriate autocomplete, predictable focus and clear error recovery. Do not announce sensitive values unnecessarily. Avoid a design that prevents password-manager or platform code suggestions.

Source: https://ui.shadcn.com/docs/components/input-otp

### SH-34 Item

Purpose and ownership: A flexible row-like content/action composition.

Component-specific acceptance: Choose semantic list/link/button elements according to behavior. Multiple nested actions need distinct targets and names; a general-purpose wrapper cannot decide the domain semantics for you.

Source: https://ui.shadcn.com/docs/components/item

### SH-35 Kbd

Purpose and ownership: A visual representation of keyboard input.

Component-specific acceptance: Use meaningful shortcut text and platform conventions. Displaying a shortcut does not register it; test actual event handling and provide equivalent visible controls.

Source: https://ui.shadcn.com/docs/components/kbd

### SH-36 Label

Purpose and ownership: A visual/programmatic label wrapper.

Component-specific acceptance: Associate it with the correct input ID or supported primitive relation. Do not use labels as section headings or placeholders as the sole label. Verify clicking the label reaches the control.

Source: https://ui.shadcn.com/docs/components/label

### SH-37 Marker

Purpose and ownership: A compact marker/annotation-oriented visual primitive.

Component-specific acceptance: Inspect the current source contract before assigning behavior. If it marks position or status, expose the same information textually and avoid relying on a tiny colored symbol alone.

Source: https://ui.shadcn.com/docs/components/marker

### SH-38 Menubar

Purpose and ownership: A persistent row of application-style menus.

Component-specific acceptance: Use the complete menubar keyboard model and test transitions among menus. Ordinary site navigation does not automatically need menubar semantics; pick the simplest model appropriate to the task.

Source: https://ui.shadcn.com/docs/components/menubar

### SH-39 Message

Purpose and ownership: A message/content composition used in conversational interfaces.

Component-specific acceptance: Preserve author, content and state relationships. Render model output safely, distinguish user/model/system content clearly and avoid announcing the entire transcript on every streaming token.

Source: https://ui.shadcn.com/docs/components/message

### SH-40 Message Scroller

Purpose and ownership: A scrolling conversation viewport with follow/position behavior.

Component-specific acceptance: Do not drag a user back to the bottom while they read history. Expose new-message state and a return-to-latest control; preserve focus and scroll position when older messages load.

Source: https://ui.shadcn.com/docs/components/message-scroller

### SH-41 Native Select

Purpose and ownership: A native select styled to fit the system.

Component-specific acceptance: Prefer it when platform selection behavior meets the need. Retain label and option semantics and test mobile UI; a custom select should justify its additional interaction complexity.

Source: https://ui.shadcn.com/docs/components/native-select

### SH-42 Navigation Menu

Purpose and ownership: A navigation-specific compound component.

Component-specific acceptance: Use links and meaningful navigation labels. Test pointer, keyboard and touch access to subregions; do not confuse navigation semantics with action-menu semantics simply because both open a panel.

Source: https://ui.shadcn.com/docs/components/navigation-menu

### SH-43 Pagination

Purpose and ownership: Controls for moving through result pages.

Component-specific acceptance: Identify the current page and unavailable actions and preserve query context. A server-driven page link and a client button can both be valid when their navigation behavior is deliberate.

Source: https://ui.shadcn.com/docs/components/pagination

### SH-44 Popover

Purpose and ownership: A contextual floating region anchored to a trigger.

Component-specific acceptance: Choose an appropriate focus/dismissal strategy and expose relationships. A popover is a positioning/interaction container; its content still needs semantics and an escape route.

Source: https://ui.shadcn.com/docs/components/popover

### SH-45 Progress

Purpose and ownership: A visual indicator of known or unknown progress.

Component-specific acceptance: Expose a meaningful label and accurate value range for determinate work. Do not manufacture percentages for unknown-duration requests; pair indeterminate progress with concise status text.

Source: https://ui.shadcn.com/docs/components/progress

### SH-46 Questionnaire

Purpose and ownership: A structured multi-question interaction composition.

Component-specific acceptance: Define question/answer schemas, validation, navigation and persistence explicitly. Preserve unfinished answers and announce step/error changes without losing focus. Verify the current package/API separately from simple visual components.

Source: https://ui.shadcn.com/docs/components/questionnaire

### SH-47 Radio Group

Purpose and ownership: A mutually exclusive choice set.

Component-specific acceptance: Provide a shared group label and individual option labels. Test arrow-key behavior and required/error state. Persist a stable domain value rather than an index tied to display ordering.

Source: https://ui.shadcn.com/docs/components/radio-group

### SH-48 Resizable

Purpose and ownership: Adjacent panels with a movable divider.

Component-specific acceptance: Support keyboard resizing and meaningful minimums, preserve focus and prevent essential content from becoming unreachable. Expose separator semantics and test viewport changes after a user resize.

Source: https://ui.shadcn.com/docs/components/resizable

### SH-49 Scroll Area

Purpose and ownership: A styled scrolling viewport.

Component-specific acceptance: Keep content keyboard reachable and avoid hiding all scroll affordances. Confirm focus visibility and wheel/touch behavior; a custom scrollbar should not be required for understanding the content.

Source: https://ui.shadcn.com/docs/components/scroll-area

### SH-50 Select

Purpose and ownership: A custom selection popup using behavioral primitives.

Component-specific acceptance: Verify trigger naming, selected value, keyboard typeahead and disabled options. Distinguish selection from editable filtering; a Select and Combobox are not interchangeable APIs.

Source: https://ui.shadcn.com/docs/components/select

### SH-51 Separator

Purpose and ownership: A visual or semantic division.

Component-specific acceptance: Use decorative semantics when it is only visual. If it communicates a meaningful thematic break, preserve that meaning. Vertical presentation needs an orientation-aware contract.

Source: https://ui.shadcn.com/docs/components/separator

### SH-52 Sheet

Purpose and ownership: A dialog-style overlay anchored to a screen edge.

Component-specific acceptance: Retain dialog naming, background isolation, Escape and focus return. Responsive positioning must not remove the only close control or hide focused content behind a virtual keyboard.

Source: https://ui.shadcn.com/docs/components/sheet

### SH-53 Sidebar

Purpose and ownership: A navigation/application-shell composition.

Component-specific acceptance: Name navigation groups, mark the current route and test collapsed/mobile states. Persisted width/open state must not trap a small viewport in an unusable desktop layout.

Source: https://ui.shadcn.com/docs/components/sidebar

### SH-54 Skeleton

Purpose and ownership: A placeholder approximating pending content.

Component-specific acceptance: Keep placeholders out of meaningful reading order where appropriate and expose a concise loading state. Avoid announcing each decorative skeleton and disable distracting pulse motion when requested.

Source: https://ui.shadcn.com/docs/components/skeleton

### SH-55 Slider

Purpose and ownership: A continuous or stepped value input.

Component-specific acceptance: Provide a name, range, current value and units where needed. Test keyboard adjustment and a precise-entry alternative for values difficult to select by dragging. Multi-thumb sliders need distinct names.

Source: https://ui.shadcn.com/docs/components/slider

### SH-56 Spinner

Purpose and ownership: An animated busy indicator.

Component-specific acceptance: Pair it with understandable status text and a pending-action policy. Stop animation when work completes or fails. A spinner that runs forever can conceal an error or duplicate request bug.

Source: https://ui.shadcn.com/docs/components/spinner

### SH-57 Switch

Purpose and ownership: A binary setting control.

Component-specific acceptance: Use a persistent label and reflect checked state. Distinguish an immediately applied setting from a form checkbox whose effect waits for submission; the visual metaphor should match behavior.

Source: https://ui.shadcn.com/docs/components/switch

### SH-58 Table

Purpose and ownership: A styled native table anatomy.

Component-specific acceptance: Supply caption, headers and scope/relationships according to complexity. Do not replace a simple table with a div grid merely for styling; complex interactive grids have a larger keyboard contract.

Source: https://ui.shadcn.com/docs/components/table

### SH-59 Tabs

Purpose and ownership: A selected panel among related peer panels.

Component-specific acceptance: Provide tablist/tab/tabpanel relationships and expected keyboard behavior. Decide whether focus activates immediately or requires confirmation, especially when loading is expensive.

Source: https://ui.shadcn.com/docs/components/tabs

### SH-60 Textarea

Purpose and ownership: A multiline text input.

Component-specific acceptance: Label it, preserve useful resizing and describe constraints. Auto-growth must not move focus unexpectedly or create a feedback loop. Validate length/content independently of the visual size.

Source: https://ui.shadcn.com/docs/components/textarea

### SH-61 Toast

Purpose and ownership: A transient notification pattern with evolving package choices.

Component-specific acceptance: Verify whether the current page recommends another notifier such as Sonner. Avoid putting essential irreversible decisions only in an expiring toast; use measured live-region urgency and a usable dismissal policy.

Source: https://ui.shadcn.com/docs/components/toast

### SH-62 Toggle

Purpose and ownership: A pressed/unpressed action control.

Component-specific acceptance: Expose aria-pressed or the primitive equivalent and retain a stable name. A toggle controls an action mode; it is not always interchangeable with a switch setting or radio choice.

Source: https://ui.shadcn.com/docs/components/toggle

### SH-63 Toggle Group

Purpose and ownership: Related toggles with single/multiple selection semantics.

Component-specific acceptance: Define whether choices are exclusive and test the correct keyboard model. Provide a group label and meaningful selected states; do not infer semantics only from a segmented visual shape.

Source: https://ui.shadcn.com/docs/components/toggle-group

### SH-64 Tooltip

Purpose and ownership: Brief supplementary information associated with a trigger.

Component-specific acceptance: Ensure pointer and keyboard access and suitable dismissal. Keep essential instructions in normal content and name icon-only controls independently; interactive content belongs in a different pattern.

Source: https://ui.shadcn.com/docs/components/tooltip

### SH-65 Trace

Purpose and ownership: A structured trace/step presentation, often for developer or AI workflows.

Component-specific acceptance: Separate observed events from generated explanations, redact sensitive payloads and preserve readable status/timing text. Inspect the current API; it does not establish that displayed reasoning is a faithful execution trace.

Source: https://ui.shadcn.com/docs/components/trace

### SH-66 Typography

Purpose and ownership: Reusable text presentation conventions.

Component-specific acceptance: Choose real heading/list/quote/code semantics first. A typography recipe should preserve link distinction, wrapping, contrast and zoom rather than treating document structure as decoration.

Source: https://ui.shadcn.com/docs/components/typography

## 23 Complete implementation labs

Two complete labs accompany this document. The React study studio combines Tailwind CSS with locally authored, source-owned Base UI wrappers in the shadcn architectural style. The Bulma studio uses compiled Sass and application-owned JavaScript, including native dialog behavior. The React wrapper is deliberately not labeled as an unmodified shadcn registry component; the retrieved templates require CLI transformations and are retained separately as source references.

The examples do not send email, persist user accounts, charge peppercorns or reveal actual problem solutions. A successful form submission is local demonstration state. No application functionality was changed by creating these files.

Copy the following files into the same examples directory, with build.cjs in a sibling support directory as shown. The downloadable Markdown is the canonical copy source; PDF code may wrap visually. Use a current Node 22 installation that satisfies the installed packages' engine constraints. The supplied lockfile in the local examples directory records transitive dependencies; use npm ci when reproducing that directory. Without a lockfile, npm install resolves a new dependency graph and is not the identical recorded environment.

```text
framework-training/
  examples/
    package.json
    package-lock.json
    tsconfig.json
    app.css
    ui.tsx
    app.tsx
    index.html
    bulma.scss
    bulma.html
    bulma.js
  support/
    build.cjs
```

```sh
cd examples
npm ci
npm run typecheck
npm run build
python3 -m http.server 8769 --bind 127.0.0.1
```

Open http://127.0.0.1:8769/index.html for the React studio and http://127.0.0.1:8769/bulma.html for the Bulma studio. The local server serves only the example folder. Ctrl+C stops it. If you reconstruct the files without the provided lockfile, run npm install once before the other commands and record the resulting lockfile.

The build compiles Tailwind candidates from explicit sources, bundles React/Base UI, and compiles Bulma Sass. It deliberately avoids loading Bulma into the React document, preserving independent cascade/reset contracts. The forms validate locally for demonstration; production forms require the relevant application-side validation and delivery/persistence flow.

### Source file: package.json

```json
{
  "private": true,
  "name": "framework-curriculum-labs",
  "version": "1.0.0",
  "scripts": {
    "build": "node ../support/build.cjs",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@base-ui/react": "1.9.0",
    "@tailwindcss/cli": "4.3.3",
    "@types/react": "19.2.2",
    "@types/react-dom": "19.2.2",
    "bulma": "1.0.4",
    "class-variance-authority": "0.7.1",
    "clsx": "2.1.1",
    "esbuild": "0.25.12",
    "react": "19.3.1",
    "react-dom": "19.3.1",
    "sass": "1.105.2",
    "tailwind-merge": "3.7.0",
    "tailwindcss": "4.3.3",
    "typescript": "5.9.3"
  },
  "devDependencies": {
    "prettier": "3.6.2"
  }
}
```

### Source file: tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true,
    "lib": ["ES2022", "DOM"],
    "esModuleInterop": true
  },
  "include": ["*.tsx"]
}
```

### Source file: app.css

```css
@import "tailwindcss" source(none);
@source "./app.tsx";
@source "./ui.tsx";
@custom-variant dark (&:where(.dark, .dark *));
:root {
  --surface: #ffffff;
  --ink: #172033;
  --action: #1d4ed8;
}
.dark {
  --surface: #111827;
  --ink: #f8fafc;
  --action: #93c5fd;
}
@theme inline {
  --color-surface: var(--surface);
  --color-ink: var(--ink);
  --color-action: var(--action);
}
@layer base {
  body {
    margin: 0;
    background: var(--surface);
    color: var(--ink);
    font-family: Arial, sans-serif;
  }
  button {
    cursor: pointer;
  }
}
```

### Source file: ui.tsx

```tsx
import * as React from "react";
import { Dialog as D } from "@base-ui/react/dialog";
import { Accordion as A } from "@base-ui/react/accordion";
import { Button as B } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...v: ClassValue[]) {
  return twMerge(clsx(v));
}
const recipe = cva(
  "rounded-md border px-4 py-2 font-semibold focus-visible:outline-2 focus-visible:outline-offset-4 disabled:opacity-60",
  {
    variants: {
      tone: {
        primary: "bg-action text-white dark:text-slate-950",
        secondary: "bg-surface text-ink border-current",
      },
    },
    defaultVariants: { tone: "primary" },
  },
);
export function Button({
  className,
  tone,
  ...props
}: B.Props & VariantProps<typeof recipe>) {
  return <B className={cn(recipe({ tone }), className)} {...props} />;
}
export function PlanDialog() {
  return (
    <D.Root>
      <D.Trigger render={<Button />}>Open learning plan</D.Trigger>
      <D.Portal>
        <D.Backdrop className="fixed inset-0 z-40 bg-black/60" />
        <D.Popup className="fixed left-1/2 top-1/2 z-50 w-[min(90vw,30rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border bg-surface p-6 text-ink shadow-xl">
          <D.Title className="text-xl font-bold">
            Your learning plan
          </D.Title>
          <D.Description className="my-4">
            Complete fundamentals before tackling array patterns.
          </D.Description>
          <D.Close render={<Button tone="secondary" />}>
            Close learning plan
          </D.Close>
        </D.Popup>
      </D.Portal>
    </D.Root>
  );
}
export function Topics() {
  return (
    <A.Root className="mt-6 rounded border" aria-label="Practice topics">
      <A.Item value="arrays">
        <A.Header>
          <A.Trigger className="w-full p-4 text-left font-semibold focus-visible:outline-2 data-panel-open:bg-slate-100 dark:data-panel-open:bg-slate-800">
            Array preparation
          </A.Trigger>
        </A.Header>
        <A.Panel className="px-4 pb-4">
          Use indexing and iteration before optimizing with two pointers.
        </A.Panel>
      </A.Item>
    </A.Root>
  );
}
```

### Source file: app.tsx

```tsx
import * as React from "react";
import { createRoot } from "react-dom/client";
import { Button, PlanDialog, Topics } from "./ui";
const tones = {
  ready: "bg-emerald-700 text-white",
  paused: "bg-slate-700 text-white",
};
function App() {
  const [dark, setDark] = React.useState(false);
  const [email, setEmail] = React.useState("");
  const [error, setError] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  React.useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    return () => document.documentElement.classList.remove("dark");
  }, [dark]);
  return (
    <>
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:z-50 focus:bg-surface focus:p-4"
      >
        Skip to content
      </a>
      <main id="main" tabIndex={-1} className="mx-auto max-w-5xl p-6">
        <h1 className="text-3xl font-bold">Framework study studio</h1>
        <p className="my-4">
          A source-owned Base UI composition with Tailwind CSS.
        </p>
        <div className="flex flex-wrap gap-4">
          <Button
            tone="secondary"
            aria-pressed={dark}
            onClick={() => setDark(!dark)}
          >
            Dark theme
          </Button>
          <PlanDialog />
        </div>
        <section aria-labelledby="pathways" className="mt-6">
          <h2 id="pathways" className="text-2xl font-bold">
            Pathways
          </h2>
          <ul
            id="cards"
            className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3"
          >
            {["JavaScript", "Java", "TypeScript"].map((x) => (
              <li key={x} className="min-w-0 rounded-lg border p-4">
                <h3 className="font-semibold">{x}</h3>
                <p className="mt-2">Practice language fundamentals.</p>
                <span
                  className={
                    "mt-2 inline-block rounded px-2 py-1 " + tones.ready
                  }
                >
                  Ready
                </span>
              </li>
            ))}
          </ul>
        </section>
        <Topics />
        <form
          noValidate
          className="mt-6 max-w-md"
          onSubmit={(e) => {
            e.preventDefault();
            const invalid = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
            setError(invalid);
            setSaved(!invalid);
            if (invalid) document.getElementById("email")?.focus();
          }}
        >
          <h2 className="text-xl font-bold">Practice reminder</h2>
          <label className="mt-4 block font-semibold" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setError(false);
              setSaved(false);
            }}
            aria-invalid={error}
            aria-describedby="email-help email-error"
            className="mt-2 w-full rounded border bg-surface px-3 py-2 text-ink aria-invalid:border-red-700 focus-visible:outline-2 focus-visible:outline-offset-2"
          />
          <p id="email-help" className="mt-2">
            Local demonstration; no data is sent.
          </p>
          <p
            id="email-error"
            className="mt-2 font-semibold"
            aria-live="polite"
          >
            {error ? "Enter a complete email address." : ""}
          </p>
          <Button className="mt-4" type="submit">
            Save reminder
          </Button>
          <p role="status" className="mt-2">
            {saved ? "Reminder saved for this demonstration." : ""}
          </p>
        </form>
      </main>
    </>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

### Source file: index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Framework study studio</title>
    <link rel="stylesheet" href="app-built.css" />
  </head>
  <body>
    <div id="root"></div>
    <script src="app-built.js"></script>
  </body>
</html>
```

### Source file: bulma.scss

```scss
@use "bulma/sass" with (
  $family-primary: "Arial, sans-serif",
  $primary: #2456a6
);
.practice-dialog {
  border: 0;
  border-radius: 0.75rem;
  max-width: min(90vw, 32rem);
  padding: 0;
}
.practice-dialog::backdrop {
  background: rgb(0 0 0 / 0.65);
}
.skip {
  position: absolute;
  left: -10000px;
}
.skip:focus {
  left: 1rem;
  top: 1rem;
  padding: 1rem;
  background: white;
  color: black;
  z-index: 100;
}
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 3px solid #2456a6;
  outline-offset: 4px;
}
```

### Source file: bulma.html

```html
<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Bulma practice studio</title>
    <link rel="stylesheet" href="bulma-built.css" />
  </head>
  <body>
    <a class="skip" href="#main">Skip to content</a>
    <nav class="navbar" aria-label="Primary">
      <div class="navbar-brand">
        <a class="navbar-item" href="#main">Practice studio</a
        ><button
          class="navbar-burger"
          type="button"
          aria-label="Toggle navigation"
          aria-expanded="false"
          aria-controls="navigation"
        >
          <span aria-hidden="true"></span><span aria-hidden="true"></span
          ><span aria-hidden="true"></span><span aria-hidden="true"></span>
        </button>
      </div>
      <div id="navigation" class="navbar-menu">
        <div class="navbar-start">
          <a class="navbar-item" href="#topics">Topics</a>
        </div>
      </div>
    </nav>
    <main id="main" tabindex="-1" class="section">
      <div class="container">
        <h1 class="title">Bulma practice studio</h1>
        <p class="mb-5">
          CSS presentation with application-owned native behavior.
        </p>
        <button id="open" class="button is-link" type="button">
          Open practice guidance
        </button>
        <section id="topics" aria-labelledby="topic-title" class="mt-6">
          <h2 id="topic-title" class="title is-4">Practice topics</h2>
          <div class="columns is-multiline">
            <div class="column is-full-mobile is-half-tablet">
              <article class="box">
                <h3 class="title is-5">JavaScript arrays</h3>
                <p>Reason about indexes before optimization.</p>
              </article>
            </div>
            <div class="column is-full-mobile is-half-tablet">
              <article class="box">
                <h3 class="title is-5">Java collections</h3>
                <p>Choose the collection by its operation costs.</p>
              </article>
            </div>
          </div>
        </section>
        <form id="reminder" novalidate>
          <div class="field">
            <label class="label" for="b-email">Email</label>
            <div class="control">
              <input
                id="b-email"
                class="input"
                type="email"
                autocomplete="email"
                required
                aria-describedby="b-help b-error"
              />
            </div>
            <p class="help" id="b-help">
              Local demonstration; no data is sent.
            </p>
            <p class="help" id="b-error" aria-live="polite"></p>
          </div>
          <button class="button is-link" type="submit">
            Save reminder
          </button>
          <p id="b-status" role="status"></p>
        </form>
      </div>
    </main>
    <dialog
      id="guidance"
      class="practice-dialog"
      aria-labelledby="dialog-title"
    >
      <div class="box mb-0">
        <h2 id="dialog-title" class="title is-4">Practice guidance</h2>
        <p>
          Write a small example, explain the expected result, then test it.
        </p>
        <button id="close" class="button is-link mt-4" type="button">
          Close guidance
        </button>
      </div>
    </dialog>
    <script src="bulma.js"></script>
  </body>
</html>
```

### Source file: bulma.js

```javascript
const burger = document.querySelector(".navbar-burger");
const menu = document.getElementById("navigation");
burger.addEventListener("click", () => {
  const expanded = burger.getAttribute("aria-expanded") !== "true";
  burger.setAttribute("aria-expanded", String(expanded));
  burger.classList.toggle("is-active", expanded);
  menu.classList.toggle("is-active", expanded);
});
const dialog = document.getElementById("guidance");
const opener = document.getElementById("open");
opener.addEventListener("click", () => dialog.showModal());
document
  .getElementById("close")
  .addEventListener("click", () => dialog.close());
dialog.addEventListener("close", () => opener.focus());
const input = document.getElementById("b-email");
const error = document.getElementById("b-error");
const status = document.getElementById("b-status");
input.addEventListener("input", () => {
  input.removeAttribute("aria-invalid");
  input.classList.remove("is-danger");
  error.textContent = "";
  status.textContent = "";
});
document.getElementById("reminder").addEventListener("submit", (e) => {
  e.preventDefault();
  const invalid = !input.validity.valid;
  input.setAttribute("aria-invalid", String(invalid));
  input.classList.toggle("is-danger", invalid);
  error.textContent = invalid ? "Enter a complete email address." : "";
  status.textContent = invalid
    ? ""
    : "Reminder saved for this demonstration.";
  if (invalid) input.focus();
});
```

### Source file: support/build.cjs

```javascript
const path = require("path"),
  fs = require("fs"),
  cp = require("child_process");
const E = path.resolve(__dirname, "../examples");
const req = (p) => require(path.join(E, "node_modules", p));
cp.execFileSync(
  process.execPath,
  [
    path.join(E, "node_modules/@tailwindcss/cli/dist/index.mjs"),
    "-i",
    "app.css",
    "-o",
    "app-built.css",
    "--minify",
  ],
  { cwd: E, stdio: "inherit" },
);
req("esbuild").buildSync({
  entryPoints: [path.join(E, "app.tsx")],
  bundle: true,
  minify: true,
  outfile: path.join(E, "app-built.js"),
  platform: "browser",
  format: "iife",
  define: { "process.env.NODE_ENV": '"production"' },
});
const result = req("sass").compile(path.join(E, "bulma.scss"), {
  loadPaths: [path.join(E, "node_modules")],
  style: "compressed",
  silenceDeprecations: [
    "color-functions",
    "global-builtin",
    "if-function",
    "import",
  ],
});
fs.writeFileSync(path.join(E, "bulma-built.css"), result.css);
console.log("Built React/Tailwind and Bulma/Sass labs");
```

### How to reason about the compiled output

The authored Tailwind candidate p-6 becomes a padding declaration based on the spacing theme. md:grid-cols-3 becomes a media-conditioned grid-template-columns declaration. bg-surface references the semantic token mapped by @theme inline. The resulting CSS can be inspected in app-built.css; minification and framework internals may change exact serialization, so compare semantics rather than formatting.

Bulma's @use configuration resolves the Sass primary color and font before generating CSS. The runtime CSS variables and component rules then style the native markup. Inspect bulma-built.css and compare .button, .input, .columns and their media rules with the original Sass configuration. A Sass variable does not remain a mutable JavaScript value.

The source-owned React Button maps tone to complete class strings using a finite recipe. The generated bundle includes interaction dependencies, unlike a CSS-only Tailwind page. The dialog portal inherits tokens from the document root. This is why the theme state deliberately toggles the root element rather than a local component wrapper.

These mechanisms should be explained before optimizing bundle size. CSS minification, tree shaking, module selection and dependency splitting solve different problems; a smaller stylesheet does not necessarily mean a smaller or faster application overall.

## 24 Practice progression, diagnosis and instructor rubrics

Use the same progression for beginners, framework switchers and advanced candidates. Each exercise has a visible outcome and an explanation requirement. Hint content and reference repairs should be separate retrievable records; a tutor should not expose the repair simply because the learner requested orientation. This document contains both teaching prompts and instructor guidance, so indiscriminate chunking would spoil exercises.

### PR-01 Missing utility in production

Learner brief: A card uses `bg-${tone}-700` and has no background in the production build.

First hint: Do not begin by changing CSS specificity; first establish that the rule exists.

Instructor reference: Explain textual candidate detection. Replace interpolation with complete approved strings, rebuild, inspect the selector and verify both tones.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-02 Overflowing flex row

Learner brief: A long problem title forces an action group beyond a 320px viewport.

First hint: A fixed width or overflow-hidden may hide the symptom while losing content.

Instructor reference: Inspect automatic minimum sizing, apply min-w-0 where appropriate, choose wrapping/truncation deliberately and retain access to the complete title.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-03 Incorrect breakpoint assumption

Learner brief: A student expects sm:* to apply only on phones.

First hint: Use a content-driven interval if the style really should stop at another breakpoint.

Instructor reference: Explain mobile-first minimum-width variants and demonstrate baseline/sm/md behavior at boundary widths.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-04 Container-aware card

Learner brief: The same study card looks wrong inside a sidebar on a wide monitor.

First hint: Viewport queries cannot represent every local layout constraint.

Instructor reference: Use an explicit query container and descendant container variants, then compare two parent widths at one viewport width.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-05 Dark overlay mismatch

Learner brief: The page is dark but the dialog is light.

First hint: Increasing selector specificity cannot make an unrelated ancestor supply inherited variables.

Instructor reference: Trace the portal destination and token inheritance. Move theme scope to a common ancestor or configure a supported portal container.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-06 Focus disappears

Learner brief: A custom button removes outline and ring styles.

First hint: A hover shadow is not a keyboard focus state.

Instructor reference: Provide a visible focus indicator, test keyboard navigation and forced-color mode, and verify it is not clipped.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-07 Bulma burger without behavior

Learner brief: The burger changes color but the menu does not open.

First hint: A CSS framework does not register the click handler for you.

Instructor reference: Wire one state transition to aria-expanded and both is-active classes; test narrow and desktop states.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-08 Fake modal

Learner brief: A .modal.is-active surface lets Tab reach background controls.

First hint: An overlay with a large z-index is a visual effect, not modality.

Instructor reference: Implement the complete modality contract or use a suitable native dialog. Test initial focus, containment, Escape and restoration.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-09 Label mismatch

Learner brief: A Bulma label points to an obsolete input ID.

First hint: Visual proximity is not a programmatic relationship.

Instructor reference: Repair the explicit association, click the label to verify focus, and inspect describedby/error links.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-10 Sass configuration order

Learner brief: A Bulma module is configured after it was already loaded.

First hint: Sass module single-evaluation rules differ from repeated textual CSS imports.

Instructor reference: Configure the module before first use and simplify the import graph. Compile from a clean entrypoint.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-11 Mixed primitive APIs

Learner brief: A copied Base UI trigger receives a Radix asChild prop.

First hint: Do not suppress the type error and assume the DOM is correct.

Instructor reference: Inspect imports and TypeScript types, then use the correct composition model while forwarding props and ref.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-12 Nested buttons

Learner brief: A trigger and a custom Button each render their own button element.

First hint: Two visual layers do not justify invalid nested interactive markup.

Instructor reference: Compose through the supported render/asChild API for the selected base and inspect the resulting DOM.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-13 Invalid form feedback

Learner brief: A red input has no announced error explanation.

First hint: Color alone cannot identify the error or how to fix it.

Instructor reference: Set invalid state, connect a stable error ID, preserve the value and provide recovery guidance.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-14 Sorting state confusion

Learner brief: A data table sorts visually but exposes no sort direction.

First hint: Changing the caret icon alone does not expose the new state.

Instructor reference: Keep sorting state coherent, update the appropriate header semantics and verify keyboard operation.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-15 Theme contrast regression

Learner brief: A new semantic action color is readable only in light mode.

First hint: A token named primary-foreground is not intrinsically accessible.

Instructor reference: Test each foreground/background pair and interaction state in both themes, then repair tokens together.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-16 Untrusted registry update

Learner brief: A new registry item adds unexpected files and dependencies.

First hint: Component naming and polished previews do not establish source trust.

Instructor reference: Review source targets, dependency changes, scripts and license; compare hashes and apply only intended changes in an isolated branch.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-17 Resize loop

Learner brief: A ResizeObserver callback continually changes the observed size.

First hint: A requestAnimationFrame wrapper alone does not prove the feedback loop is logically resolved.

Instructor reference: Identify the feedback relation, use CSS for visual adaptation where possible and avoid size writes that re-trigger indefinitely.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-18 Shadow-root styling gap

Learner brief: Global utilities do not style markup inside a custom element.

First hint: A global !important cannot pierce a shadow boundary.

Instructor reference: Explain selector boundaries and provide root-local CSS or a deliberate parts/custom-property API.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-19 Reduced-motion oversight

Learner brief: A skeleton pulses and a page transition runs despite reduced-motion preference.

First hint: Removing motion must not remove the underlying state update.

Instructor reference: Disable nonessential motion while preserving understandable loading/navigation state and test the preference.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### PR-20 Cross-framework migration

Learner brief: A Bulma study card is replaced by a source-owned React component.

First hint: A screenshot-only review does not establish behavioral equivalence.

Instructor reference: Preserve headings, labels, state behavior and responsive constraints; map tokens, then compare keyboard/error/dark states.

Acceptance: demonstrate the failure before the repair, capture the relevant DOM/computed-style or build evidence, then explain why the change addresses the cause. A passing screenshot without causal reasoning earns only partial credit.

### Evaluation rubric

Score each dimension 0-3: 0 absent/incorrect, 1 partly correct with substantial prompting, 2 correct with a minor gap, 3 independently correct and supported by evidence. Dimensions are platform reasoning, semantic structure, state coherence, responsive layout, accessibility, source/build reproducibility and explanation quality. Do not let a high visual score cancel a critical inaccessible interaction or lost-data failure.

A satisfactory practice submission includes the reproduction, expected/actual result, relevant source, a bounded repair and the verification evidence. An advanced submission also discusses a plausible alternative and its tradeoff. Record an unfinished attempt as unfinished; reflection alone is not a verified solve. Cross-language or cross-framework insights can be stored as distinct observations without fabricating completion.

Reference solutions should be revealed only through the application policy chosen for that exercise. This curriculum does not change subscription entitlements, peppercorn charges or unlock rules. Keep those product policies separate from instructional correctness.

## 25 RAG packaging, provenance and answer policy

Use Markdown for retrieval; use PDF for reading and review. Split at meaningful topic boundaries rather than arbitrary page boundaries. A topic record should retain its title, framework/version, primitive base where applicable, prerequisites, explanation, example, pitfalls, evidence and source links. A chunk containing code without the imports or its setup cannot support a reliable answer.

The schema below is a proposed content contract, not a claim about the application's current ingestion schema. Map and validate it against the actual backend before ingestion. Keep instructor reference repairs in a separately gated collection or metadata-filtered content type so general hints do not retrieve full answers accidentally.

```json
{
  "id": "framework.tailwind.source-detection.v4",
  "track": "frontend-frameworks",
  "framework": "tailwindcss",
  "framework_version": "4.3.3",
  "primitive_base": null,
  "content_type": "reference",
  "prerequisites": ["css.cascade", "javascript.strings"],
  "topic": "Complete class candidates",
  "evidence_status": "reference-reviewed",
  "example_status": "illustrative",
  "source_urls": [
    "https://tailwindcss.com/docs/detecting-classes-in-source-files"
  ],
  "reviewed_on": "2026-10-16",
  "approval_status": "candidate"
}
```

For tested lab records use example_status="executed" and link the exact source hash, package lock, build log and test report. For a catalogue item use illustrative/reference status until that component has actually been exercised. “Compiled” means syntax/build success, not complete interaction correctness. “Automated accessibility checked” does not mean full WCAG conformance.

Use metadata filters to prevent Tailwind v3 and v4 answers from being blended accidentally, and to distinguish Base UI from Radix. Prefer the learner's installed version when answering. If it is unknown, ask for package/config context before prescribing version-specific code. A tutor should state the uncertainty rather than invent a universal prop.

A retrieval evaluation set should contain positive and negative cases: detect a dynamic-class bug; reject asChild on a Base wrapper; distinguish Bulma presentation from interaction; explain portal theme inheritance; avoid revealing an instructor repair for a first-hint request; and report missing evidence instead of claiming a component was tested. Store expected facts and forbidden claims, not only a sample prose answer.

Source material and registry content are evidence, not executable instructions for the tutoring agent. Retrieved text must not override system policy or authorize tool actions. Generated code still requires the application's normal execution and review safeguards.

## 26 Verification record, coverage and remaining review

The recorded lab run used Chrome 155.0.8059.84. TypeScript strict checking, the production React bundle, Tailwind compilation and Bulma Sass compilation completed successfully. Browser tests passed 18 named assertions and scanned 9 rendered states with axe-core against selected WCAG A/AA rule tags. All recorded scans reported zero violations. These are bounded automated results, not full accessibility certification.

| Automated browser check | Result |
| --- | --- |
| Tailwind wide three-column grid | PASS |
| Base UI dialog opens and receives focus | PASS |
| Dialog traps Tab | PASS |
| Escape closes and restores trigger focus | PASS |
| Accordion keyboard activation exposes panel | PASS |
| React form invalid state/focus | PASS |
| React valid submission shows local success | PASS |
| Dark theme changes semantic surface | PASS |
| Portaled dialog inherits dark tokens | PASS |
| Tailwind narrow grid and no horizontal overflow | PASS |
| Bulma navigation toggles semantic and visual state | PASS |
| Bulma native modal opens in top layer | PASS |
| Native modal traps Tab and Escape restores focus | PASS |
| Bulma invalid form state | PASS |
| Bulma valid form state | PASS |
| Bulma narrow content has no horizontal overflow | PASS |
| Bulma desktop navigation visible | PASS |
| No browser runtime errors | PASS |

| Accessibility scan state | Recorded violations |
| --- | --- |
| react-light | 0 |
| react-dialog | 0 |
| react-error | 0 |
| react-dark | 0 |
| react-narrow | 0 |
| bulma-narrow | 0 |
| bulma-dialog | 0 |
| bulma-error | 0 |
| bulma-wide | 0 |

Coverage includes 38 Tailwind utility-family records, 35 Bulma module/pattern records, 66 shadcn component/pattern records and 20 diagnostic exercises. Counts describe authored records, not individually executed combinations. The complete React/Tailwind/Base UI and Bulma/native-dialog labs carry execution evidence. The wider catalogue, cross-browser behavior, external registry installation and conceptual Web API integrations require further targeted execution before serving as graded reference solutions.

Manual review remains: screen-reader interaction with the target browser combinations; high-contrast/forced-color behavior; zoom and enlarged text beyond the automated viewport check; touch interaction on physical devices; locale/RTL stress cases; and the complete product browser support matrix. Practice prompts have instructor guidance but are not independently validated DSA test fixtures.

PDF verification checks document structure, text extraction, margins and rendered page appearance. Code in the PDF is for study; copy from Markdown to avoid visual line-wrapping artifacts. The retained support directory contains source snapshots/hashes, dependency versions, the lockfile, build/test scripts and test-results.json. No training content was automatically published to the application's vector database.

### Source register and refresh policy

Official framework documentation and npm package metadata were consulted for the observed versions. Direct local HTTP retrieval of Tailwind/Bulma pages returned 403; their documentation was read through the browser research tool instead. The source manifest honestly records those fetch failures rather than pretending a local snapshot exists. shadcn documentation and registry snapshots were retrieved and hashed successfully. Registry URLs are live; a future fetch may differ despite an unchanged CLI version.

On refresh, compare package major/minor changes, framework migration notes, component index differences, primitive base/style selection and emitted CSS. Repeat compilation and interaction checks for changed examples. Update evidence only after the new run succeeds. Preserve previous source hashes so a tutor answer can be traced to the content edition it used.

Source: https://tailwindcss.com/docs

Source: https://bulma.io/documentation/

Source: https://ui.shadcn.com/docs

Source: https://base-ui.com/react/overview/quick-start

Source: https://www.w3.org/WAI/ARIA/apg/patterns/

Source: https://www.w3.org/TR/WCAG22/
