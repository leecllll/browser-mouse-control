# Workflow Reference

This reference describes how to turn a manual browser task into a reliable CloakBrowser + Playwright/CDP workflow.

## 1. Plan Before Acting

Write down the browser route before coding:

- Entry URL.
- Required authorization state.
- Search or filter inputs.
- Buttons, menus, tabs, or detail links.
- Pagination or infinite scroll.
- Data fields to extract.
- Output format.
- Success and failure signals.

For risky or changing pages, also decide where to save checkpoints.

## 2. Observe First

Before writing a full crawler, open the site and capture:

- Current URL and title.
- Screenshot of the initial state.
- DOM around important controls.
- Input fields, buttons, list items, pagination, and detail links.
- Network requests when they help identify stable data sources.
- Visible error, login, consent, or rate-limit messages.

Screenshots are important because they let the agent compare what the code thinks happened with what the browser actually shows.

## 3. Choose A Speed Profile

### fast

Use for local pages, owned admin panels, internal tools, and stable interfaces.

Best for:

- Known selectors.
- Fixed layouts.
- Repeated button clicks.
- Internal dashboards.
- Local test pages.

Typical behavior:

- Minimal pauses.
- Minimal screenshots.
- Short mouse paths.
- DOM check after critical phases.
- Best throughput after the workflow is proven.

### natural

Use as the default for ordinary websites.

Best for:

- Search result pages.
- Product or article lists.
- Normal pagination.
- Detail-page collection.
- Lazy-loaded content.

Typical behavior:

- Curved mouse paths.
- Short human-like pauses.
- Phase screenshots.
- DOM checks after clicks, drags, scrolls, and navigation.
- Retry obvious transient failures.

### careful

Use for complex, changing, or sensitive flows where reliability matters more than speed.

Best for:

- Complicated widgets.
- Hover menus.
- Multi-step forms.
- Pages that shift during loading.
- Sites that change layout often.
- Runs that must be auditable.

Typical behavior:

- Slower mouse paths.
- More screenshots.
- More DOM checks.
- Retry failed phases.
- Keep trace logs and resume hints.

## 4. Tiny Loop

Run the smallest useful loop:

1. Navigate to the page.
2. Move to the first important control.
3. Click, type, drag, or scroll.
4. Wait for a specific state change.
5. Screenshot the result.
6. Extract one item.
7. Save a tiny output file.

Only scale after this loop is reliable.

Good tiny loops:

- Search one keyword and extract the first result.
- Open one detail page and extract one record.
- Scroll once and verify the list count increased.
- Open one menu and click one option.
- Download or save one known item.

## 5. Mouse Path Strategy

Use browser-layer mouse movement for controls that care about hover, pointer history, drag, or scroll focus. Direct locator clicks are acceptable when the page is stable and the goal is raw throughput.

For menus:

- Move into the menu trigger.
- Pause until the menu is visible.
- Move vertically into the menu area.
- Then move horizontally to the item.
- Avoid diagonal paths that leave the hover region.

For drag:

- Move to the center of the draggable item.
- Mouse down.
- Move through several intermediate points.
- Mouse up.
- Verify final DOM state or visual position.

For scroll:

- Click or hover the correct scroll container first.
- Use wheel events in chunks.
- Verify list count, scroll percentage, or new visible text.

## 6. Validation

Prefer state-based waits:

- URL changed.
- Selector visible.
- Text appeared.
- Button became enabled.
- List count increased.
- Network response completed.
- Screenshot changed.
- Extracted field is non-empty.

Avoid fixed sleeps except as small pacing between actions. A fixed wait should never be the only proof that a step worked.

## 7. Failure Handling

When a step fails:

1. Screenshot immediately.
2. Save the current URL and title.
3. Save a DOM excerpt for the failing area.
4. Log the step name and exception.
5. Retry only if the failure is likely transient.
6. Preserve partial outputs.
7. Save enough state to resume without starting from zero.

Common failure categories:

- Selector changed.
- Page loaded slowly.
- Click landed before the element was ready.
- Scroll targeted the wrong container.
- The page displayed login, consent, or verification.
- Lazy content did not load.
- Overlay blocked the target.

## 8. Scaling Up

After the tiny loop works:

1. Run 3 to 5 items.
2. Compare screenshots and extracted outputs.
3. Add duplicate detection.
4. Add retry limits.
5. Add checkpoint files.
6. Run the full job.
7. Export final data and a short run summary.

The fastest reliable workflow is usually:

- `careful` while discovering.
- `natural` for first real batches.
- `fast` only after the page is stable and proven.

## 9. Output Handoff

For completed collection tasks, hand off:

- Final data file path.
- Screenshot/log folder path.
- Count of successful items.
- Count of failed or skipped items.
- Any manual follow-up needed.

Cloud upload and email delivery should be handled only when credentials or authorized tools are available in the user's environment.
