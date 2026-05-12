# Results — What Each Stakeholder Gained

This document records the concrete outcome for each leadership stakeholder served by the project. It pairs the project's deliverables to the business questions they answer, and captures the headline insight each stakeholder can take into a leadership review.

## CFO — Margaret

**Question:** *What is our gross margin by product line, region, and season — and where are we underpriced relative to cost?*

**Deliverable:** Power BI **Sales & Margin** dashboard with the margin heatmap (product line × country, color-coded by margin %, labeled with revenue).

**Headline finding:**
- **Road bikes** generate **49%** of revenue but carry the **lowest** gross margin at **~36%** — surprisingly thin given they are the brand-anchoring product line.
- **Other Sales** (accessories, peripherals) carry the **highest** margin at **~50%**, but represent only **2%** of revenue.
- **Mountain** sits comfortably in the middle at **~45%** margin on **29%** of revenue.

**Strategic implication for the executive team:** Road bikes are the customer-acquisition product; the margin sits in the accessory attach-rate. Pricing pressure on road bikes should not be answered by raising bike prices but by improving accessory attachment in the checkout flow.

## CMO — David

**Question:** *Which customer segments drive premium-bike revenue, and how should we allocate marketing spend across them?*

**Deliverables:**
- Power BI **Customer Intelligence** dashboard with RFM segmentation (Whales, Everyday, At Risk, New Passions).
- Python K-Means clustering, validating the RFM segments with statistical agreement of [TBD]%.
- Premium-bike buyer profile by age band and country.

**Headline finding:**
- The **35–54 age band** over-indexes on premium-bike purchases.
- **Germany and the UK** are the regional markets where premium buyers are most concentrated, even though absolute revenue is highest in the US.
- The **Whales segment** (high R, high F, high M) represents [TBD]% of customers but [TBD]% of revenue — the obvious priority for retention marketing.

**Strategic implication:** Reallocate marketing budget from broad geographic reach toward demographic targeting in Germany and the UK. The Whales segment merits a dedicated retention program with personalized maintenance and accessory offers.

## COO — Priya

**Question:** *What is our fulfillment performance by region and product line, and where do we have systematic shipping delays?*

**Deliverable:** Power BI **Operations & Fulfillment** dashboard with order-to-ship lag by region, seasonal patterns, and a maintenance-eligible base count.

**Headline finding:**
- **Australia and France** consistently exceed the 7-day SLA threshold at **~8–9 days** average ship lag.
- **Seasonality** is brutal — order volume in May–July is roughly **3×** the November–December baseline, and ship lag spikes correspondingly when volume peaks.
- The pattern is **predictable**, which means it is **plannable**.

**Strategic implication:** The carrier renegotiation can be supported with quantified delay data by region. Seasonal staffing curves should flex more aggressively than the current "last year plus a percentage" approach.

## VP Merchandising — Robert

**Question:** *How much will we sell next quarter and next year, by product line and region, so we can plan inventory and staffing accordingly?*

**Deliverables:**
- Power BI **Sales & Margin** dashboard with active-catalogue filtering (discontinued products excluded by default).
- Python Prophet baseline forecast at monthly granularity by product line × country.
- Python LSTM forecast as a deep learning comparison.

**Headline finding:**
- Forecast MAPE on the top five product lines: **~[TBD]%** on Prophet, **~[TBD]%** on LSTM.
- The forecast captures yearly seasonality cleanly, with confidence intervals widening on long-horizon predictions.
- For the upcoming product year, the forecast indicates **[TBD]** growth in Mountain and **[TBD]** in Road, with regional variation.

**Strategic implication:** Purchase orders for the next product year can now be made against a documented, auditable forecast rather than category-level rules of thumb. Inventory planning at the subcategory level is unlocked.

## Customer Service Director — Aisha

**Question:** *Which customers should the service team prioritize for maintenance outreach — those whose installed base is approaching service intervals?*

**Deliverable:** Python prescriptive layer combining customer segmentation with the ERP product maintenance flag, producing a ranked outreach list.

**Headline finding:**
- **~[TBD]** customers own maintenance-eligible products and have not had recent service contact.
- The top **500** by recency × segment-value × installed-base score are flagged for proactive outreach in the next quarter.

**Strategic implication:** A quarterly outreach cadence is now feasible against a defensible ranking. Early estimates suggest [TBD]% incremental service-bay revenue from proactive outreach vs the current reactive baseline.

---

## Cross-Stakeholder Outcome

The deeper outcome — the one the CIO actually bought — is the shift in how decisions get made in the executive review. From *"whose number is right?"* to *"what should we do about the number?"* The project's measurable success is not the dashboards or the models individually but the leadership conversation that they enabled.
