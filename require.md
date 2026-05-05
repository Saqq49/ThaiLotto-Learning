# Lotto Dashboard - Requirements & User Stories

## How to Use This File

**📌 IMPORTANT**: Every AI (Claude, Codex, Gemini) should read this file at the start of their work session.

This file contains:
- What the user wants to build (requirements)
- User stories and use cases
- Specific features needed
- Constraints and guidelines
- Definition of "done"

Use this file together with `plan.md` to ensure all work aligns with the user's vision.

---

## Project Vision

Create an **interactive web dashboard for Thai Lottery historical data** that:
- Shows winning numbers from past 5-10 years
- Displays probability statistics and patterns
- Is fun, engaging, and educational
- **Clearly communicates that lottery is random and unpredictable**

---

## Core Requirements

### Data Display
- [ ] Display Thai lottery winning numbers and dates
- [ ] Support historical data range of 5-10 years
- [ ] Show draw frequency (e.g., twice monthly)
- [ ] Display both 3-digit and 6-digit numbers (if applicable)
- [ ] Show results sorted by date (newest first)

### Statistics & Analysis
- [ ] Calculate number frequency (how often each number appears)
- [ ] Identify "hot numbers" (frequently drawn)
- [ ] Identify "cold numbers" (rarely drawn)
- [ ] Show basic probability calculations
- [ ] Display statistical insights per number
- [ ] **MUST include disclaimer**: "Results are random, history doesn't predict future"

### User Interaction
- [ ] Search/filter by number
- [ ] Filter by date range
- [ ] Compare statistics across different periods
- [ ] View individual number history
- [ ] (Optional) Time-series visualization of number frequency

### User Experience
- [ ] Clean, intuitive interface
- [ ] Responsive design (works on mobile/tablet/desktop)
- [ ] Fast loading and smooth interactions
- [ ] Clear navigation
- [ ] Accessible (readable colors, proper contrast)

---

## Technical Requirements

### Frontend
- **Framework**: React (preferred) or Vue.js
- **Visualization**: D3.js, Chart.js, or Recharts for graphs
- **Styling**: Tailwind CSS or styled-components
- **State Management**: React Context or simple state (avoid over-engineering)

### Data Source
- **Historical Data**: Must find reliable Thai lottery API or dataset
  - Options: API, public datasets, web scraping (if allowed)
  - Must verify data accuracy
  - Must handle updates (new draws)
- **Data Format**: JSON or database
- **Refresh Strategy**: Auto-update or manual refresh

### Backend (if needed)
- **Option 1**: Serverless (Vercel, Netlify) - simplest
- **Option 2**: Node.js/Express with database - more control
- **Decision**: Start with frontend-only if data source allows, add backend later if needed

### Testing
- [ ] Unit tests for calculation functions
- [ ] Integration tests for data fetching
- [ ] UI tests for critical user flows
- [ ] Manual testing on multiple browsers/devices

---

## User Stories

### User Story 1: Browse Historical Numbers
**As a** lottery enthusiast  
**I want to** see all winning lottery numbers from the past 10 years  
**So that** I can explore historical results

**Acceptance Criteria**:
- [ ] Can view winning numbers with dates
- [ ] Numbers are displayed clearly
- [ ] Can scroll/paginate through results
- [ ] Loading states are shown

### User Story 2: Find Hot Numbers
**As a** curious data explorer  
**I want to** see which numbers have appeared most frequently  
**So that** I can understand number distribution

**Acceptance Criteria**:
- [ ] Hot numbers are ranked and highlighted
- [ ] Frequency count is shown for each number
- [ ] Can sort by frequency
- [ ] Visual representation (chart) is clear

### User Story 3: Search by Number
**As a** someone interested in a specific number  
**I want to** search for a number and see its history  
**So that** I can track a particular number's performance

**Acceptance Criteria**:
- [ ] Search box works smoothly
- [ ] Results show all occurrences of the number
- [ ] Dates are shown for each occurrence
- [ ] Statistics for that number are displayed

### User Story 4: Understand Randomness
**As a** someone new to lottery statistics  
**I want to** see educational content about probability  
**So that** I understand the lottery is random and unpredictable

**Acceptance Criteria**:
- [ ] Disclaimer is prominently displayed
- [ ] Educational content explains randomness
- [ ] Cannot be misinterpreted as a prediction tool
- [ ] Graphics illustrate probability concepts

### User Story 5: Compare Time Periods
**As a** a data analyst  
**I want to** compare statistics across different time ranges  
**So that** I can see if patterns change over time

**Acceptance Criteria**:
- [ ] Can select date ranges
- [ ] Statistics update for selected range
- [ ] Side-by-side comparison is possible
- [ ] Differences are highlighted

---

## Feature Priorities

### MVP (Must Have)
1. Display historical lottery numbers (5-10 years)
2. Show basic statistics (frequency, hot/cold numbers)
3. Search by number
4. Prominent disclaimer about randomness
5. Responsive design

### Phase 2 (Should Have)
1. Advanced statistics (percentiles, trends)
2. Time range filtering
3. Interactive charts and visualizations
4. Number comparison tools
5. Export data functionality

### Phase 3 (Nice to Have)
1. User accounts and favorites
2. Notifications for new draws
3. Mobile app version
4. Advanced probability calculations
5. Community statistics sharing

---

## Constraints & Guidelines

### Ethical Constraints
- ✅ **DO**: Clearly label this as educational/entertainment
- ✅ **DO**: Explain that lottery is random
- ✅ **DO**: Show statistical reality (each number has equal chance)
- ❌ **DON'T**: Imply the dashboard can predict lottery results
- ❌ **DON'T**: Encourage gambling or spending money
- ❌ **DON'T**: Make it look like a "winning strategy" tool

### Technical Constraints
- Performance: Dashboard should load in < 2 seconds
- Accessibility: WCAG AA compliance minimum
- Browser Support: Last 2 versions of major browsers
- Data: Must be accurate and up-to-date

### Scope Constraints
- No user authentication required (v1)
- No payment processing
- No user data collection (privacy-first)
- Keep it simple - avoid feature creep

---

## Definition of Done

A feature is **complete** when:
- [ ] Code is written and tested
- [ ] Code review passed (Codex approval)
- [ ] All acceptance criteria are met
- [ ] No new bugs introduced
- [ ] Documentation is updated
- [ ] UI/UX is polished

A feature is **ready for release** when:
- [ ] All MVP features are complete
- [ ] Testing is comprehensive
- [ ] Code is optimized and clean
- [ ] Documentation is complete
- [ ] Team has approved (Claude + Codex + Gemini agreement)

---

## Questions to Resolve

**For Claude & Team**:
1. Which Thai lottery numbers format? (3-digit, 6-digit, both?)
2. Should we include prizes/payout information?
3. How far back should historical data go? (5 years? 10 years? More?)
4. Should users be able to export data?
5. Any specific statistics most important? (frequency? streaks? patterns?)
6. Mobile-first or desktop-first design?
7. Dark mode support?

**For Gemini (Research)**:
1. What Thai lottery APIs are available?
2. What historical datasets exist?
3. Best visualization library for this type of data?
4. Data accuracy verification methods?

---

## Success Metrics

- ✅ Dashboard displays accurate lottery data
- ✅ Statistics calculations are correct
- ✅ User can find what they need in < 30 seconds
- ✅ Dashboard works smoothly on mobile
- ✅ No confusion about "lottery is random"
- ✅ Code is maintainable and documented
- ✅ Page loads in < 2 seconds

---

## Notes for AI Team

1. **Read this first**: Before starting, all AIs should read `require.md`, `plan.md`, and `session.md`
2. **Alignment**: If you disagree with requirements, discuss and update this file
3. **Handoffs**: Update `session.md` after each major work unit
4. **Verification**: Use "Definition of Done" checklist before marking features complete
5. **Ethics**: Keep the educational/entertainment nature throughout development

---

## Revision History

| Date | Version | Changes | Updated By |
|------|---------|---------|------------|
| 2026-05-04 | 1.0 | Initial requirements | User |
| | | | |
