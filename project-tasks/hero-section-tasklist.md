# Hero Section Setup Development Tasks

## Specification Summary
**Original Requirements**: Create a modern, responsive Hero section for a portfolio site as the initial banner. Include name "Nikola Sae", title "Full-Stack Developer & AI Agent Builder", short description "Gradim stvari koje rade same.", CTA button "Pogledaj moje agente" (link can be #), dark/light mode toggle (sun/moon icon). Use Tailwind CSS + clean HTML (or React component if preferred). Be visually attractive, minimal, and modern.

**Technical Stack**: Tailwind CSS + clean HTML (or React component if preferred)
**Target Timeline**: Not specified

## Development Tasks

### [ ] Task 1: Basic HTML Structure
**Description**: Create the basic HTML structure for the hero section including name, title, description, and CTA button
**Acceptance Criteria**: 
- HTML elements for name, title, description, and button are present
- Basic layout without styling
- Button has placeholder link #

**Files to Create/Edit**:
- hero-section.html (or hero-section.jsx if React)

**Reference**: Requirements section of specification

### [ ] Task 2: Tailwind CSS Styling
**Description**: Apply Tailwind CSS classes to make the hero section visually attractive, minimal, and modern
**Acceptance Criteria**:
- Hero section looks clean and modern
- Proper spacing, typography, and colors
- Responsive layout basics

**Components**: None specified
**Reference**: "Be visually attractive, minimal, and modern" requirement

### [ ] Task 3: Dark/Light Mode Toggle Implementation
**Description**: Add dark/light mode toggle with sun/moon icon and implement the functionality
**Acceptance Criteria**:
- Toggle button with sun/moon icon is visible
- Clicking toggle switches between dark and light themes
- Theme persists or applies immediately

**Files to Create/Edit**:
- Add JavaScript or React state for toggle
**Reference**: "Add dark/light mode toggle (sun/moon icon)" requirement

### [ ] Task 4: Responsive Design
**Description**: Ensure the hero section is fully responsive across devices
**Acceptance Criteria**:
- Looks good on mobile, tablet, and desktop
- Text and button adjust appropriately
- No horizontal scroll

**Reference**: "Responsive design" deliverable

### [ ] Task 5: Final Integration and Testing
**Description**: Combine all elements into one file and test functionality
**Acceptance Criteria**:
- Complete code in one file
- Dark/light mode works
- Responsive and modern appearance
- All requirements met

**Files to Create/Edit**:
- Final hero-section file
**Reference**: "Complete code in one file" deliverable

## Quality Requirements
- [ ] Responsive design works on all screen sizes
- [ ] Dark/light mode functionality is working
- [ ] Clean, modern aesthetics achieved
- [ ] Code is in one file as specified
- [ ] No background processes in any commands - NEVER append `&`
- [ ] No server startup commands - assume development server running
- [ ] Images from approved sources (Unsplash, https://picsum.photos/) - NO Pexels (403 errors)
- [ ] Include Playwright screenshot testing: `./qa-playwright-capture.sh http://localhost:8000 public/qa-screenshots`

## Technical Notes
**Development Stack**: Tailwind CSS + clean HTML (or React component if preferred)
**Special Instructions**: Deliver complete code in one file
**Timeline Expectations**: Based on scope, approximately 2-4 hours total development time