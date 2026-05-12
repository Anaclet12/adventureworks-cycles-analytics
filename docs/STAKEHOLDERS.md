# Stakeholders

This project serves five operating leaders plus a sponsor. Understanding who they are, what they care about, and which dashboard / model serves which need is essential to evaluating the project as a business product rather than a technical exercise.

## Organigram

```
                        Board of Directors
                                │
                                ▼
                              CEO
                                │
        ┌───────────┬───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼           ▼
       CFO         CMO         COO         CIO         CHRO
   (Finance) (Marketing) (Operations) (Tech/Data) (People — out of scope)
                                │
                  ┌─────────────┴────────────┐
                  ▼                          ▼
         VP Merchandising         Customer Service Director
       (Catalogue & pricing)        (Service & support)
```

- **CEO** — the broader sponsor; consumes the executive summary.
- **CIO** — the project sponsor; consumes everything and championed the initiative.
- **CFO, CMO, COO** — primary C-suite consumers, each with their own dashboard.
- **VP Merchandising, Customer Service Director** — operational consumers reporting to the COO.
- **CHRO** — out of scope for this analytics initiative.

## Core Differences

| Dimension | **CEO** | **CFO** | **CMO** | **COO** | **VP Merchandising** | **Customer Service Director** |
|---|---|---|---|---|---|---|
| **Primary focus** | The company | The money | The customer | The execution | The product catalogue | The post-sale relationship |
| **Question they ask** | Are we winning? | Where are we making money? | Who buys, and how do we get more? | Are we delivering? | What should we sell? | Are our customers cared for after they buy? |
| **Success metric** | Revenue, margin trend, market share | Gross margin %, EBITDA, working capital | CAC, LTV, conversion rate | On-time-delivery %, ship lag | Sell-through, turnover, weeks-of-supply | First-contact resolution, NPS, return rate |
| **Time horizon** | Multi-year strategy | Monthly close, quarterly board | Weeks to quarters | Daily ops, seasonal planning | 6–12 months out | Real-time to quarterly |
| **Decisions made** | Capital allocation, M&A, leadership | Pricing, budget, capex | Ad spend, segments, creative | Carriers, warehouses, staffing | Assortment, markdowns, discontinuations | Service plans, escalation, outreach |
| **Their dashboard** | Executive summary | Sales & Margin | Customer Intelligence | Operations & Fulfillment | Sales & Margin + forecast | Operations (maintenance) + outreach list |
| **Today's pain** | Different teams report different numbers | Margin reconciliation takes 2–3 days monthly | Campaigns are broadcasts; can't target | Date fields are integers; ship lag is hard | Reports include discontinued products | Maintenance flag never joined to purchase history |
| **What this project gives them** | Single source of truth | One agreed-upon margin view, auto-refreshed | Three actionable segments + premium-bike profile | Quantified shipping performance for renegotiation | Active-catalogue dashboard + forecast | Ranked outreach list refreshed quarterly |

## Hierarchy of Consumption

The closer to the top of the org chart, the more aggregated and time-compressed the view they need:

- The **CEO** wants the executive overview in **30 seconds**.
- The **C-suite chiefs** want their dashboard in **5 minutes**, with clear drill-down paths.
- The **department heads** will spend **an hour** working through their dashboard, exploring filters and exporting lists.

Same warehouse, six different views into it. That's the whole point of building gold once and serving it to everyone.

## Why This Matters for the Project

The analytics work touches every senior leader except HR. That's unusual for a single project — most data initiatives serve one function. The combination produces outputs that all four operating chiefs use to do their jobs better, which is what makes this a portfolio standout rather than a tool-learning exercise.
