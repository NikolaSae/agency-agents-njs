# Agency Dashboard Development Tasks

## Specification Summary
**Original Requirements**: Build a modern agency dashboard portal with live task overview, ongoing project summaries, agent roster, department grouping, and dark/light mode.
**Technical Stack**: Tailwind CSS, vanilla HTML, vanilla JavaScript.

## Development Tasks

### [ ] Task 1: Create dashboard page structure
**Description**: Build a single HTML dashboard page with main sections for tasks, projects, agents, and departments.
**Acceptance Criteria**:
- Page loads without errors in a browser.
- Sections are present: Live Tasks, Projects, Agents, Departments, Theme.
- Layout is responsive on desktop and mobile.

### [ ] Task 2: Add live task overview
**Description**: Add a task status panel showing tasks in progress and status badges.
**Acceptance Criteria**:
- At least three sample tasks are shown.
- Tasks include status tags and progress indicators.
- Section is visually distinct and easy to scan.

### [ ] Task 3: Add project summary cards
**Description**: Add cards for ongoing projects with progress bars and owner info.
**Acceptance Criteria**:
- At least three project cards are visible.
- Each card shows project title, status, and progress.
- Cards layout adapts to screen width.

### [ ] Task 4: Add agent roster by person and department
**Description**: Add individual agent cards and a department breakdown view.
**Acceptance Criteria**:
- Individual agent cards show name, role, and department.
- Department section groups agents by division.
- Section is clear and readable.

### [ ] Task 5: Implement dark/light mode toggle
**Description**: Add a theme toggle button with sun/moon icon and localStorage persistence.
**Acceptance Criteria**:
- Clicking toggle switches theme instantly.
- Page remembers theme between reloads.
- Icons update correctly for active theme.

### [ ] Task 6: Final polish and QA
**Description**: Review layout, spacing, headings, and responsiveness.
**Acceptance Criteria**:
- Page looks modern and minimal.
- Text contrast is good in both themes.
- Layout remains usable on mobile widths.

## Quality Requirements
- Use Tailwind utility classes only.
- Avoid external JavaScript frameworks.
- Keep HTML semantic and accessible.
- Include a clear CTA or status highlight for portal usage.
