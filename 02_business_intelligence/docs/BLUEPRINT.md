# Dashboard Blueprint

This document captures the design rationale for the three dashboards: who each one serves, what business questions it answers, what visuals appear on each page, and why those choices were made. It is the link between the [business context](../../docs/01_business_context.md) and the implementation in the ``.pbix``.

## Design Principles

Before any visual was placed, three principles drove the design:

### 1. One Dashboard per Persona
Each dashboard targets a specific stakeholder. The CFO sees margin first. The CMO sees customers first. The COO sees operations first. A single mega-dashboard would force everyone through someone else's view.

### 2. Top-Left Tells the Headline
F-pattern reading research applies to dashboards too. The most important KPIs go in the top-left. Secondary visuals fan out to the right and below. A leader who only spends 10 seconds on the dashboard still gets the headline.

### 3. Filter Once, See Everything
Every dashboard has a Year and a Country filter at the top, applied to every visual on the page. No filter buttons hidden in submenus.

---

## Dashboard 1 — Sales & Margin

### Audience
**Primary:** CFO (Margaret), VP Merchandising (Robert)
**Secondary:** CEO (executive overview)

### Business Questions Answered
1. *"What is our gross margin by product line, region, and season?"*
2. *"Where are we underpriced relative to cost?"*

### Layout (Reading Top-Left to Bottom-Right)

| Position | Visual | Measure(s) | Why it's here |
|---|---|---|---|
| Top-left | **Revenue KPI card** | ``[Revenue]`` | The single most-asked number in any review |
| Top-center | **Gross Margin % KPI** | ``[Gross Margin %]`` + ``[Gross Margin % YoY pts]`` | Margin trend is the CFO's daily concern |
| Top-right | **Quantity Sold KPI** | ``[Quantity Sold]`` | Volume context for the revenue number |
| Middle-left | **Margin heatmap** (matrix) | Rows: Product Line × Cols: Country, colored by ``[Gross Margin %]``, labeled with ``[Revenue]`` | The "where are we underpriced" answer is a single glance |
| Middle-right | **Revenue trend by month** | Line: ``[Revenue]`` vs ``[Revenue LY]`` | Seasonality and YoY at a glance |
| Bottom-left | **Top 10 products** (bar) | Y: product name, X: ``[Revenue]``, color: ``[Gross Margin %]`` | What's selling and is it profitable |
| Bottom-right | **Revenue vs Margin scatter** | X: ``[Revenue]``, Y: ``[Gross Margin %]``, point size: ``[Quantity Sold]`` | Identify the high-revenue / low-margin quadrant |

### Key Insight This Dashboard Surfaces
**Road bikes generate 49% of revenue but carry the lowest gross margin (~36%) of any product line.** Accessories ("Other Sales") carry the highest margin (~50%) at only 2% of revenue. The bike is the customer-acquisition product; the margin lives in the accessory attach-rate. Pricing pressure on bikes should not be answered by raising bike prices but by improving accessory attach in the checkout flow.

---

## Dashboard 2 — Customer Intelligence

### Audience
**Primary:** CMO (David)
**Secondary:** CEO, VP Merchandising

### Business Questions Answered
1. *"Which customer segments drive premium-bike revenue?"*
2. *"How should we allocate marketing spend across them?"*

### Layout

| Position | Visual | Measure(s) | Why it's here |
|---|---|---|---|
| Top-left | **New Customers KPI card** | ``[New Customers CARD]`` + ``[#Customers YoY %]`` (with arrow) | Acquisition is the CMO's primary metric |
| Top-center | **Active Customers KPI** | ``[Active Customers]`` | The denominator for everything below |
| Top-left below | **Customer LTV KPI** | ``[Customer LTV]`` | Value per customer |
| Top-far-left below | **Repeat Customer Rate KPI** | ``[Repeat Customer Rate]`` | Retention health |
| Right side (main) | **Customer Acquisition Trend** | Line: ``[Active Customers]`` and ``[Acquisition Revenue]`` by month | New customer cohorts over time |
| Middle-left | **Behavioral Segments (RFM treemap)** | Sized by customer count, colored by segment | Visual segment proportions |
| Middle-right | **LTV and AOV by Age Band** | Bars: ``[Customer LTV]`` vs ``[Average Order Value]``, grouped by age band | Which demographics deliver highest value |

### Key Design Decision — RFM as a Treemap
The four segments (Whales, Everyday, At Risk, New Passions) are shown as a treemap. The treemap proportions communicate two things simultaneously:
- **Size** = number of customers in the segment
- **Color** = segment identity (consistent across the report)

This makes it immediately obvious whether Whales are a sliver of customers (likely) or a large group (unusual).

### Key Insight This Dashboard Surfaces
The **35–54 age band** over-indexes on premium-bike purchases. The **Whales segment** is small in customer count but disproportionately large in revenue. Marketing budget should shift toward retention of the Whales segment and toward demographic targeting within the 35–54 age band — not broad geographic reach.

---

## Dashboard 3 — Operations & Fulfillment

### Audience
**Primary:** COO (Priya), Customer Service Director (Aisha)
**Secondary:** VP Merchandising (planning lead times)

### Business Questions Answered
1. *"What is our fulfillment performance by region and product line?"*
2. *"Where do we have systematic shipping delays?"*
3. *"Which customers need maintenance outreach?"*

### Layout

| Position | Visual | Measure(s) | Why it's here |
|---|---|---|---|
| Top-left | **% Shipped On Time** | ``[% Shipped On Time]`` | The SLA headline |
| Top-center | **Ship Lag (avg days)** | ``[Ship Lag (days)]`` | Average performance |
| Top-right | **SLA Breach Rate** | ``[SLA Breach Rate %]`` | The inverse, often easier to react to |
| Far-right | **Maintenance Outreach Priority** | ``[Maintenance Outreach Priority]`` | Count of customers eligible for proactive service |
| Middle-left | **Ship Lag by Country** (bar) | Bars: ``[Ship Lag (days)]`` by country, colored by SLA status | Where to focus carrier renegotiation |
| Middle-right | **Ship Lag by Product Line** | Similar bar by product line | Are bulky bikes the bottleneck? |
| Bottom | **Seasonality heatmap** | Year × Month, colored by ``[Order Count]`` | When the volume spikes hit |

### Key Insight This Dashboard Surfaces
**Australia and France consistently exceed the 7-day SLA** at ~8-9 days average. Volume in May-July is roughly 3× the November-December baseline, and ship lag spikes correspondingly when volume peaks. The pattern is **predictable**, which means it is **plannable** — supporting both carrier renegotiation conversations and seasonal staffing curves.

---

## Cross-Dashboard Design Choices

### Consistent Color Semantics
Across all three dashboards:
- **Green:** above target / improving / positive YoY
- **Red:** below target / declining / negative YoY
- **Teal (#1F4E5F):** primary brand color, neutral data
- **Gray:** secondary / context data

A leader switching between dashboards never has to recalibrate what colors mean.

### Consistent Slicers
Year and Country slicers appear in the same position (top of page) on every dashboard. Slicer state does NOT sync between pages — each dashboard maintains its own filter state.

### Visual Density
Each dashboard fits on a single page without scrolling at 1920×1080 resolution. The COO doesn't need to scroll. The CMO doesn't need to scroll. This was a deliberate constraint and required some sacrifice (e.g., not showing every drill-down level on the main page).

### Tooltips Over Drill-Throughs
Where additional context is needed, custom tooltips appear on hover rather than requiring a drill-through to a detail page. This keeps the main view clean while preserving access to details.

---

## What This Dashboard Set Does NOT Include

Some things were deliberately scoped out, to be revisited in Phase 3 or beyond:

- **Forecasted revenue** — Power BI's built-in forecasting is limited. Forecasting is handled in Python (Phase 3) and the results will be loaded back into Power BI as a separate dataset.
- **Cohort retention curves** — true retention analysis requires longitudinal cohort logic that is brittle in DAX. Python (Phase 3) handles this with native cohort tooling.
- **Customer-level drill-through** — a customer detail page exists in the model but is not in the published page set. Used internally by Customer Service via slicer-driven export.
- **Real-time data** — the data refreshes on report open; no streaming connection. Streaming would require Phase 4 deployment.