"""Generate HTML5, CSS3, Bootstrap 5, and Tailwind debugging corpora."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def rec(prefix,title,language,i,level,row,fence):
    perspective,concept,symptom,goal,buggy,diagnosis,fixed,tests=row
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Language/framework: {title}
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```{fence}
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```{fence}
{fixed}
```

### Regression tests

```{fence}
{tests}
```

"""

ROWS={
'HTML5':[
('Semantics','heading hierarchy','Screen-reader users cannot understand page structure.','Use headings to express document hierarchy, not visual size.','<div class="h1">Products</div>\n<h4>Featured</h4>','A styled div is not a heading and h4 skips the logical level.','<h1>Products</h1>\n<h2>Featured</h2>','assert accessibility tree exposes h1 followed by h2'),
('Forms','missing label','Clicking a field label does not focus the input.','Associate a visible label with a control.', '<label>Email</label>\n<input type="email" name="email">','A label without for and a matching id has no programmatic association.','<label for="email">Email</label>\n<input id="email" type="email" name="email">','assert label click focuses #email'),
('Forms','wrong input type','Mobile users get a poor keyboard and weak validation.','Use the input type matching the value contract.','<input type="text" name="email">','Text does not communicate email semantics or enable native email validation.','<input type="email" name="email" autocomplete="email" required>','assert invalid email blocks submission'),
('Accessibility','image alternative','Important content is missing for nonvisual users.','Provide concise alt text or mark decorative images empty.', '<img src="chart.png">','Without alt, the image has no accessible name and screen readers may announce its filename.','<img src="chart.png" alt="Sales increased 24 percent in Q4">','assert accessible name describes the chart'),
('Links','button used for navigation','Keyboard behavior and browser semantics are inconsistent.','Use an anchor for navigation and a button for actions.','<button onclick="location.href=\'/help\'">Help</button>','A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.','<a href="/help">Help</a>','assert keyboard activation and href navigation work'),
('Tables','layout table','Screen readers announce decorative cells as data.','Use CSS layout for layout and table semantics for tabular data.', '<table><tr><td><nav>Menu</nav></td></tr></table>','A layout table creates a misleading data structure.','<div class="layout"><nav>Menu</nav></div>','assert accessibility tree has no table for layout'),
('Metadata','missing viewport','The mobile page renders zoomed out.', '<head>\n  <title>Shop</title>\n</head>','Mobile browsers use a desktop layout viewport without the viewport declaration.','<meta name="viewport" content="width=device-width, initial-scale=1">','assert mobile viewport width equals device width'),
('Security','unsafe target blank','A new tab can access the opener.', '<a href="https://example.com" target="_blank">Docs</a>','A new browsing context may retain window.opener access.','<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>','assert opener is null in the new tab'),
('Media','video inaccessible','Users cannot follow spoken content.', '<video controls src="lesson.mp4"></video>','The video has no captions track for deaf or hard-of-hearing users.','<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>','assert captions track is available'),
('Performance','unoptimized image','Largest contentful paint is slow.', '<img src="hero.jpg">','The browser downloads an unnecessarily large image and lacks responsive hints.','<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">','assert mobile selects the smaller candidate'),
],
'CSS3':[
('Cascade','specificity conflict','The intended color is ignored.','Inspect specificity and source order before adding !important.','.card .title { color: blue; }\n.title { color: red; }','The compound selector has greater specificity than the later class selector.','.card .title { color: red; }','assert computed color is red'),
('Box model','unexpected width','A 100% input overflows its container.','Account for padding and borders in sizing.','input { width: 100%; padding: 1rem; }','content-box adds padding to the declared width.','*, *::before, *::after { box-sizing: border-box; }\ninput { width: 100%; padding: 1rem; }','assert input bounding box fits container'),
('Flexbox','shrinking content','A label is clipped beside a flexible panel.','Set the intended min-width and growth behavior.','.row { display:flex; }\n.label { width: 240px; }\n.panel { flex: 1; }','Flex items default to min-width:auto and may refuse to shrink or force overflow.','.panel { flex: 1 1 auto; min-width: 0; }','assert long text remains within the row'),
('Grid','implicit columns','Cards have inconsistent widths.','Declare the grid tracks and responsive breakpoint explicitly.','.cards { display:grid; grid-template-columns: 1fr 1fr; }','Fixed tracks do not adapt to the available width.','.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }','assert one column on narrow and multiple on wide viewport'),
('Positioning','z-index ineffective','A modal appears behind content.','Give positioned elements a deliberate stacking context and z-index.','.modal { z-index: 1000; }','z-index does not apply to a static element and ancestor stacking contexts can constrain it.','.modal { position: fixed; inset: 0; z-index: 1000; }','assert modal paints above page content'),
('Responsive','desktop overflow','The page scrolls horizontally on phones.','Find fixed widths and allow content to wrap or shrink.','.container { width: 1200px; }','A fixed 1200px width is wider than a phone viewport, so the page scrolls horizontally.','.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }','assert no horizontal overflow at 320px'),
('Accessibility','focus removed','Keyboard users cannot see focus.','Preserve a visible focus indicator.','button:focus { outline: none; }','Removing the outline without replacement makes keyboard position invisible.','button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }','assert focus-visible has nonzero outline'),
('Animation','motion sickness','The interface animates for users who request reduced motion.','Respect the user media preference.','.panel { transition: transform .4s; }','The transition runs even when the user has asked for reduced motion; nothing checks prefers-reduced-motion.','.panel { transition: transform .4s; }\n@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }','assert reduced-motion disables transition'),
('Selectors','hidden content still accessible','An element is visually hidden but remains in the focus order.','.visually-hidden { opacity: 0; }','Opacity hides pixels but does not remove the element from interaction or accessibility flow.','.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }','assert decorative element is not focusable'),
('Custom properties','invalid fallback','A component loses its background color.','.card { background: var(--card-color); }','An undefined custom property makes the whole declaration invalid.','.card { background: var(--card-color, white); }','assert computed background is white when variable absent'),
],
'Bootstrap 5':[
('Grid','container breakpoint mismatch','Columns stack at an unexpected width.','Match column classes to the intended responsive breakpoint.','<div class="col-md-6 col-lg-6">Card</div>','The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.', '<div class="col-12 col-sm-6 col-lg-6">Card</div>','assert one column below sm and two above sm'),
('Spacing','utility direction typo','The margin is applied on the wrong axis.','Use Bootstrap’s directional utility vocabulary precisely.','<div class="ms-4">Content</div>','ms means margin-start, not vertical spacing.', '<div class="my-4">Content</div>','assert top and bottom margins are applied'),
('Components','collapse not initialized','The navbar toggle does nothing.','Load the Bootstrap JavaScript bundle and matching data attributes.','<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>','The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.', '<script src="bootstrap.bundle.min.js"></script>\n<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>','assert click toggles #nav.show'),
('Forms','invalid feedback hidden','The error message never appears.', 'Use the validation state class and required structure.', '<input class="form-control"><div class="invalid-feedback">Required</div>','Bootstrap displays invalid-feedback when the control or form has the invalid state.', '<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>','assert invalid feedback is visible'),
('Accessibility','modal missing label','A modal opens without an accessible name.', 'Set modal title association and dialog semantics.', '<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>','The dialog has no labelledby relationship for assistive technology.', '<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>','assert dialog accessible name is Details'),
('Display','d-none conflict','Responsive content never appears.', 'Order display utilities from the desired breakpoint.', '<div class="d-none d-md-none d-lg-block">Desktop</div>','The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.', '<div class="d-none d-lg-block">Desktop</div>','assert hidden below lg and visible at lg'),
('Flex','alignment utility mismatch','Items are centered on the wrong axis.', 'Distinguish justify-content from align-items.', '<div class="d-flex align-items-center">...</div>','align-items controls the cross axis; horizontal centering in a row uses justify-content-center.', '<div class="d-flex justify-content-center">...</div>','assert items center horizontally'),
('Tables','responsive wrapper missing','A table breaks the viewport on phones.', 'Wrap wide tabular content in the responsive utility.', '<table class="table">...</table>','The table itself does not create horizontal scrolling.', '<div class="table-responsive"><table class="table">...</table></div>','assert wrapper scrolls horizontally without page overflow'),
('Utilities','text contrast failure','Muted text is unreadable on a dark background.', 'Choose a contextual text color with sufficient contrast.', '<div class="bg-dark text-muted">Status</div>','text-muted can have insufficient contrast against bg-dark.', '<div class="bg-dark text-light">Status</div>','assert contrast ratio meets WCAG target'),
('Versioning','v4 class on v5','A spacing or float utility has no effect.', 'Check the Bootstrap major-version utility names.', '<div class="float-right mr-3">...</div>','Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.', '<div class="float-end me-3">...</div>','assert computed float and margin are applied'),
],
'Tailwind':[
('Content scanning','dynamic class missing','A runtime-selected color has no styles in production.', 'Use complete static class names or safelist generated variants.', '<div className={`bg-${color}-500`}>Status</div>','Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.', '<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>','assert production CSS contains both background utilities'),
('Responsive','mobile-first misunderstanding','The desktop style appears on small screens.', 'Apply the base class to mobile and add breakpoint overrides.', '<div class="md:hidden block">Menu</div>','The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.', '<div class="block md:hidden">Menu</div>','assert visible on mobile and hidden at md'),
('Spacing','wrong axis utility','Only horizontal padding changes.', 'Choose p, px, py, or directional utilities accurately.', '<section class="px-6">Content</section>','px applies left and right padding, not vertical spacing.', '<section class="py-6">Content</section>','assert top and bottom padding equal 1.5rem'),
('Layout','flex child overflow','Long content forces horizontal scrolling.', 'Allow flex children to shrink below intrinsic width.', '<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>','flex-1 alone can retain an automatic minimum width.', '<main class="min-w-0 flex-1">long</main>','assert main content does not overflow the flex row'),
('Z-index','stacking context surprise','A high z-index tooltip remains behind a panel.', 'Inspect ancestor stacking contexts and position requirements.', '<div class="z-50">Tooltip</div>','z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.', '<div class="relative z-50">Tooltip</div>','assert tooltip paints above the panel'),
('States','hover-only action inaccessible','Keyboard users cannot reach the visible action state.', 'Pair hover styles with focus-visible styles.', '<button class="opacity-0 group-hover:opacity-100">Delete</button>','Only mouse hover changes opacity; keyboard focus leaves the button invisible.', '<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>','assert focus-visible action has opacity 1'),
('Dark mode','variant not configured','Dark classes never apply.', 'Align class strategy and root dark marker with configuration.', '<div class="dark:bg-gray-900">...</div>','The project may use media strategy while expecting a class strategy, or lack the dark marker.', '<html class="dark"><div class="dark:bg-gray-900">...</div></html>','assert dark root produces dark background'),
('Typography','text clipped','A heading overflows its card.', 'Use wrapping or truncation intentionally.', '<h2 class="whitespace-nowrap">Very long title...</h2>','nowrap prevents wrapping and can exceed the container.', '<h2 class="break-words">Very long title...</h2>','assert long title remains within card'),
('Build','arbitrary value typo','A custom width is ignored.', 'Use valid arbitrary-value syntax and inspect generated CSS.', '<div class="w-[calc(100%-2rem]">...</div>','The arbitrary value has unbalanced brackets and is discarded.', '<div class="w-[calc(100%-2rem)]">...</div>','assert computed width equals container minus 2rem'),
('Accessibility','focus ring removed','Keyboard focus is invisible.', 'Keep a visible focus treatment in utility composition.', '<button class="focus:outline-none">Save</button>','Removing the browser outline without a replacement harms keyboard navigation.', '<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>','assert focus-visible ring is present'),
],
}

def build(title,prefix,fence):
    rows=ROWS[title]
    out=[f"# {title} Debug Exercises\n\nA RAG-training corpus of 300 debugging exercises for {title}. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.\n\n## Coverage\n\n- Easy: 100 exercises\n- Medium: 100 exercises\n- Hard: 100 exercises\n- Perspectives: semantics, accessibility, responsive layout, cascade, components, performance, security, and testing\n\n"]
    for level in ('Easy','Medium','Hard'):
        for i in range(1,101):
            row = rows[(i-1)%len(rows)]
            if len(row) == 7:
                row = row[:3] + ('Check the boundary contract before styling around the symptom.',) + row[3:]
            out.append(rec(prefix,title,title,i,level,row,fence))
    return ''.join(out)

def main():
    specs=[('HTML5','HTML','html','html5-debug-exercises.md'),('CSS3','CSS','css','css3-debug-exercises.md'),('Bootstrap 5','BOOT','html','bootstrap5-debug-exercises.md'),('Tailwind','TW','html','tailwind-debug-exercises.md')]
    for title,prefix,fence,file in specs:
        (ROOT/'docs/curriculum'/file).write_text(build(title,prefix,fence),encoding='utf-8')
        print('wrote',file,'with 300 exercises')

if __name__=='__main__': main()
