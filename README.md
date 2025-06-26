# **Streamlit Application Publishing Framework**

This repository contains the infrastructure and workflow for an automated, on-demand Streamlit application publishing platform.


## **Application Taxonomy**

Each application is assigned to a category and an optional sub-category via its manifest.yml file. This ensures all tools are discoverable in the central UI.

**Example manifest.yml:**
```
appName: "Geo-Budget Allocator"
description: "Allocate a national budget across states or DMAs."
category: "Strategic Planning & Forecasting"
subcategory: "Investment & Budget Allocation"
entryPoint: app.py
requirements: requirements.txt
```

If a subcategory is not specified, the app will appear directly under the parent category.


### **Category 1: Foundational Intelligence & Research**

*Tools designed to answer the question: "What is the landscape and where are the opportunities?"*



* **Audience Understanding:** Focuses on defining, sizing, and understanding the target consumer.
* **Competitive Intelligence:** Centers on analyzing competitor messaging, media presence, and strategy.
* **Market & Trend Analysis:** Deals with identifying broader market dynamics, cultural shifts, and emerging trends.
* **Platform & Channel Insights:** Focuses on understanding the specific nuances and audience behaviors on different media platforms.


### **Category 2: Strategic Planning & Forecasting**

*Tools for making forward-looking decisions on how to allocate resources to achieve specific goals.*



* **Investment & Budget Allocation:** Aids in high-level budget setting and allocation across channels or markets.
* **Performance Forecasting & Goal Setting:** Focuses on translating budgets into expected outcomes and setting realistic KPIs.
* **Audience & Channel Strategy:** Centers on reach/frequency modeling and strategic rationale for channel selection.
* **Scenario & Sensitivity Modeling:** Enables "what if" analysis to understand the potential impact of changing variables.


### **Category 3: Activation & Operational Efficiency**

*Tools for streamlining the translation of strategy into flawless campaign execution.*



* **Campaign & Ad Setup:** Focuses on the bulk creation of campaigns, ad groups, ads, and keywords.
* **Audience Management:** Centers on creating, segmenting, and managing audience lists for targeting.
* **Tracking & Naming Conventions:** Aids in generating consistent tracking parameters and names to ensure data integrity.
* **Quality Assurance (QA):** Provides pre- and post-launch checklists and automated scans to prevent errors.


### **Category 4: Advanced Measurement & Analytics**

*Tools designed to answer the question: "What worked, why, and how do we prove it?"*



* **Causality & Incrementality:** Focuses on lift testing to prove marketing's true, causal impact.
* **Attribution & Journey Analysis:** Helps to understand the role of different touchpoints in the path to conversion.
* **Performance Diagnostics:** Enables deep-dive analysis to uncover the "why" behind performance changes.
* **Data Integrity & Modeling Prep:** Centers on cleaning, shaping, and validating data for use in complex models.


### **Category 5: Creative & Content Intelligence**

*Tools that bridge the gap between media analytics and creative performance.*



* **Creative Performance Analysis:** Analyzes past creative to identify which elements drive the best results.
* **Content & Copy Ideation:** Uses data to generate ideas and angles for new creative development.
* **Asset & Feed Management:** Provides utilities for managing large creative libraries or optimizing product feeds.
* **Landing Page & Conversion Funnel Optimization:** Analyzes the post-click experience to identify friction points.


### **Category 6: Agency Operations & Enablement**

*Internal-facing tools for running a smarter, more efficient agency.*



* **Client & Project Management:** Helps standardize reporting, monitor project status, and track client health.
* **Commercial & Financial Modeling:** Aids in scoping new projects, estimating resource needs, and analyzing profitability.
* **New Business & Pitch Support:** Accelerates the new business process by generating research and finding case studies.
