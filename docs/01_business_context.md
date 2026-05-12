# Business Context

## The Company

**AdventureWorks Cycles** is a fictional specialty cycling retailer with roots in manufacturing. The company started decades ago producing high-end road and mountain bikes for independent dealers, expanded into direct-to-consumer e-commerce roughly ten years ago, and today operates across three channels: an online storefront serving customers in North America, Europe, and Australia; a network of company-owned retail stores in major metropolitan areas; and a wholesale dealer program supplying independent bike shops worldwide.

The catalogue is organized into four broad categories:

- **Bikes** — Road, Mountain, and Touring lines (the brand-anchoring products, highest unit margin)
- **Components** — drivetrains, brake systems, wheels, frames
- **Clothing** — jerseys, shorts, socks, gloves, caps
- **Accessories** — helmets, bottles, hydration packs, racks, tires, fenders

By the numbers (as captured in this dataset):

- **~60,000** sales transactions
- **~18,500** unique customers
- **~400** active products
- **36** subcategories
- **6** countries (US, Australia, UK, Germany, France, Canada)
- **2010–2014** transaction window

## The Business Problem

Three years of growth have outpaced the analytics function. The CEO opened the last quarterly review by asking what now feels like a routine question: *"What's our gross margin by product line, broken down by region, for the last twelve months?"* It took the analytics team eleven days to answer, and when they did, the CFO's office produced a different number using the same source data. Neither team was wrong. They were pulling from different systems with different rules, and nobody had reconciled them.

This is not an isolated incident. It is the daily reality.

The **CFO** cannot close the books with confidence because product cost (held in the back-office ERP) and product revenue (held in the front-office CRM) live in disconnected systems whose product keys do not match cleanly.

The **CMO** is running customer acquisition campaigns without segmentation. The CRM holds order history but no demographics; the ERP holds demographics but no order history.

The **COO** cannot measure on-time shipping performance because the date fields in the source sales table are stored as integers in `YYYYMMDD` format.

The **VP of Merchandising** keeps publishing reports that include discontinued products because nobody enforces a rule that filters out historical catalogue versions.

The **Customer Service Director** cannot identify which customers own products eligible for the maintenance program, even though there is a "maintenance" flag sitting in the ERP product master.

Every one of these is a data integration problem masquerading as an analytics problem.

## Why the Data Looks Like This

AdventureWorks runs on two systems:

The **CRM platform** was built when the company launched its e-commerce channel. Its design priorities were checkout speed and customer experience — demographic fields were left optional at signup. The CRM holds customer registrations, the product catalogue as customers browse it, and sales orders.

The **ERP platform** is older, inherited from the manufacturing side of the business. Its table names follow a legacy module-and-version naming convention (`erp_loc_a101`, `erp_cust_az12`, `erp_px_cat_g1v2`). The ERP holds enriched customer demographics from warranty registrations and the loyalty program, the manufacturing-grade product hierarchy (category, subcategory, maintenance flag), and shipping-country data from the logistics module.

Neither system was wrong for its purpose. Together, they leave the analytics team in the position of constantly bridging gaps that should have been bridged once, in a single place, and made queryable for everyone.

## What This Project Delivers

A single source of truth that unifies the two systems, surfaces insights neither could produce alone, and lays the foundation for predictive and prescriptive analytics.

The deliverable is not "a data warehouse." The deliverable is the answer to five questions leadership has been asking for years, and a platform that keeps answering them automatically.

The five questions:

1. What is our gross margin by product line, region, and season — and where are we underpriced relative to cost?
2. Which customer segments drive premium-bike revenue, and how should we allocate marketing spend across them?
3. What is our fulfillment performance by region and product line, and where do we have systematic shipping delays?
4. How much will we sell next quarter and next year, by product line and region, so we can plan inventory and staffing accordingly?
5. Which customers should the service team prioritize for maintenance outreach — those whose installed base is approaching service intervals?

Questions 1–3 are descriptive and diagnostic — they need a clean warehouse and good dashboards. Question 4 is predictive — it needs a forecasting model. Question 5 is prescriptive — it needs a model that ranks customers by expected response and combines that with the maintenance flag to produce an actionable outreach list.

## How This Project Is Structured

Four sequential phases, each building on the previous:

| Phase | Tooling | Deliverable |
|---|---|---|
| 1 | PostgreSQL, plpgsql | Medallion data warehouse (bronze, silver, gold) |
| 2 | Power BI | Three executive-ready dashboards |
| 3 | Python (scikit-learn, Prophet, PyTorch) | Segmentation + forecasting + recommendations |
| 4 | FastAPI, Docker, Prometheus, Grafana | Production-deployable inference service |

See [`docs/02_architecture.md`](02_architecture.md) for the technical architecture.
See [`docs/STAKEHOLDERS.md`](STAKEHOLDERS.md) for the stakeholder map and organigram.
