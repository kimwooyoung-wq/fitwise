# AI in Fashion: Official Product and Operations Examples

**Checked:** 2026-11-22  
**Purpose:** Use publicly documented apparel-industry examples to decide whether, where, and under what conditions FITWISE should use AI. This is a bounded benchmark, not a full competitor analysis.

## Summary

Fashion businesses report AI use across different jobs: customer discovery and styling, size and fit guidance, review synthesis, demand planning, and creative production. These examples show that AI can support a workflow; they do not prove that AI is required for FITWISE or that a particular model or deployment location is right for this project.

| Company | Publicly described use | FITWISE takeaway |
|---|---|---|
| Amazon Fashion | ML-based personalized size recommendations; review insights about size/fit; product information and visual tools to support discovery | Size guidance needs product data and comparable evidence. Keep measurements and factual attributes grounded in catalog/review records. |
| Mango | Mango Stylist conversational assistant gives product suggestions, styling tips, trend discovery, and outfit combinations | Natural-language discovery and outfit suggestions are plausible AI-assisted experiences. For FITWISE, first test whether guided fields/rules solve the user's task. |
| H&M Group | Its 2023 sustainability disclosure describes a size-demand model used across nearly half of teams to predict demand by clothing size and market, aiming to improve availability and limit excess stock | AI can support ERP-like planning and inventory allocation, but this is a retailer operations problem, not an MVP consumer feature. |
| Zalando | Describes proprietary AI models for product search, recommendations, visual discovery, and size advice; its assistant adds a conversational layer | Separate retrieval/ranking models and structured size evidence from the chat interface. A conversational layer should not own factual decisions. |
| Mango (creative) | A 2024 company release describes generative AI for a Teen campaign and design-team inspiration | Generative imagery is a marketing/design workflow; it is outside FITWISE's decision-support MVP. |

## Recommended FITWISE boundary

### MVP: no generative AI required

1. Store consented catalog fields in a normalized, permission-aware database.
2. Apply deterministic SQL/code hard filters for budget, availability, size availability, category, and explicit exclusions.
3. Rank surviving candidates with versioned, explainable feature scores.
4. Show source, freshness, reasons, limitations, and missing evidence.
5. Use structured inputs or a small rules-based parser for the first usable flow.

### Evaluate only if user evidence supports it

- **Intent extraction:** optionally map free text to a proposed schema (occasion, budget, style, avoid list). The user confirms and edits it; schema validation and filters stay deterministic.
- **Review synthesis:** later summarize authorized, size-relevant review evidence with counts, recency, contradictions, and links to source reviews. Fall back to source evidence if generation fails.
- Do not add trend generation, outfit generation, body-image scoring, product scraping, autonomous purchases, or generated price/stock/measurements to the MVP.

## Decision gates before an AI feature

- A usability test identifies a concrete task failure or repeated friction that a non-AI alternative does not solve.
- A rules-only baseline and a synthetic evaluation set are defined first.
- Compare task success, field accuracy, user correction rate, unsupported claims, latency, operating cost, and privacy exposure.
- Do not ship unless AI improves a user-valued metric without violating evidence or privacy constraints.
- Confirm model/provider terms, retention, data location, and deletion behavior before sending any user data. Start with synthetic inputs.
- Preserve a rules-only fallback and log only minimized, non-sensitive evaluation data.

## Source quality and limits

These are first-party company pages or reports, so they are useful for describing what companies say they deployed. They are not independent audits, controlled product comparisons, or proof that the feature caused better business outcomes. The H&M operations example is specifically from its 2023 disclosure and should not be presented as a newly launched feature.

## Official sources

1. Amazon, “How Amazon Fashion is using AI to help you find the perfect fit,” describes personalized size recommendations and fit-review insights: https://www.aboutamazon.com/news/retail/how-amazon-is-using-ai-to-help-customers-shop
2. Mango, “Mango launches Mango Stylist, its new AI-powered fashion assistant,” published 2025-07-02: https://mangofashiongroup.com/en/w/mango-lanza-mango-stylist-su-nuevo-asistente-de-moda-que-utiliza-ia-2
3. H&M Group, Sustainability Disclosure 2023, describes size-demand forecasting by market: https://hmgroup.com/wp-content/uploads/2024/03/HM-Group-Sustainability-Disclosure-2023.pdf
4. Zalando, “More personal and smarter - the Zalando Assistant with enhanced capabilities,” published 2025-03-27: https://corporate.zalando.com/en/technology/more-personal-and-smarter-zalando-assistant-enhanced-capabilities-inspire-customers
5. Zalando, “From conversational tool to a lifestyle agent: how the Zalando Assistant has grown up,” documents proprietary search, recommendation, visual discovery, and size-advice models: https://corporate.zalando.com/en/technology/conversational-tool-lifestyle-agent-how-zalando-assistant-has-grown
6. Mango, “Mango creates its first campaign generated with artificial intelligence for its Teen line,” describes a creative workflow: https://mangofashiongroup.com/en/w/mango-crea-la-primera-campa%C3%B1a-generada-con-inteligencia-artificial-para-su-l%C3%ADnea-teen
