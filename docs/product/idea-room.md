# FITWISE Idea Room

> Status: Proposed idea · Not approved for MVP · Not implemented  
> Related issue: [#9](https://github.com/kimwooyoung-wq/fitwise/issues/9)

This page keeps product ideas separate from committed requirements. An idea moves into the roadmap only after the problem, user evidence, privacy impact, and implementation cost have been reviewed.

## Idea 01 · Virtual wardrobe rack and garment inspection

### User problem

When someone owns many clothes, it is easy to forget what is already in the closet. That can lead to buying another item that is similar to something they already own, while existing clothes remain unused.

### Concept

Let a user organize owned garments in a private digital wardrobe displayed as a virtual rack. They can browse the rack or a searchable list and inspect a garment with a pointer hover on desktop. On touch devices, provide an explicit tap or drag interaction because there is no hover state.

The supplied reference images show a physical rack with garments hanging in a row. The digital concept should use that familiar arrangement as inspiration, while keeping item details readable and accessible.

### Intended value

- Recall owned clothing before making a purchase.
- Find a garment by category, color, season, or use.
- Notice similar items already owned and reconsider a duplicate purchase.
- Build future outfit or recommendation flows around the user's actual wardrobe, if users find that useful.

The feature should support practical purchasing decisions rather than encourage adding more clothes.

## Candidate first slice (not yet a commitment)

1. Manually add a garment with a name, category, color, season, wear frequency, and optional storage location.
2. Allow an optional image, with edit and delete controls.
3. Offer both a rack view and a compact list/grid view with search and filters.
4. On desktop, test hover-to-inspect. On mobile, test tap-to-select and drag-to-rotate only when the asset supports it.
5. Before shopping, let users compare a candidate with similar garments they already own.

Start with synthetic/sample garments. Decide image storage, limits, and cost only after validating the core retrieval problem.

## Motion and image constraints

A single flat 2D photo cannot reveal parts of a garment that were never photographed. Rotating a single cutout can be a decorative effect, but it does not show the true back or sides.

For genuine multi-angle inspection, the product would need one of:

- Multiple user-provided views (for example front, back, and side) and a controlled image sequence.
- A real 3D garment asset, with its creation and maintenance cost.
- A clearly labeled lightweight visual effect that does not imply unseen details are accurate.

The first prototype should compare a simple image switch/2D treatment with a multi-view interaction before choosing 3D.

## Privacy and data handling questions

Garment photos and wardrobe details can reveal personal habits and preferences. Before using real user content, specify:

- Private-by-default access and per-user authorization.
- Explicit image upload consent, file type/size limits, and metadata stripping (including EXIF).
- Edit, delete, and export behavior, plus retention and backup deletion expectations.
- Private storage paths and access expiry; never put private image URLs in public issue text or logs.
- Synthetic assets for demos and usability sessions unless participants explicitly consent.

No real wardrobe photos, body measurements, purchases, credentials, or production data belong in this idea document.

## Validation plan

Use a small, consent-based usability session before including this in the MVP.

### Tasks

1. Add a sample garment.
2. Locate a named item in the wardrobe.
3. Before a hypothetical purchase, identify whether a similar owned item exists.
4. Inspect the same item using the rack interaction and the list/grid alternative.

### Evidence to collect (anonymized)

- Task completion and time to find an item.
- Whether participants recognize a similar item before the hypothetical purchase.
- Confusion, accessibility issues, and preference between rack and list/grid.
- Perceived usefulness and likelihood of maintaining the wardrobe.

Do not infer market demand from a handful of prototype sessions. Record sample size and limitations.

## Decision gate

Keep the idea in backlog until user evidence supports the problem and a low-cost interaction test. Then decide whether to:

- Drop the idea.
- Keep wardrobe inventory but omit rotation.
- Prototype multi-angle images.
- Invest in actual 3D garment assets.

### Open questions

- Is the primary value remembering owned items, reducing duplicate purchases, or outfit planning?
- Will users maintain a manually entered wardrobe?
- How much information is necessary for retrieval without making item entry burdensome?
- Is a rack view materially more useful than a searchable grid?
- What is the simplest truthful inspection motion for the image assets users can provide?
- What private storage and deletion guarantees are practical for the first release?

## Scope boundary

This is a proposal, not an accepted requirement or implementation. It does not expand the active mobile search prototype (PR #4) or database/catalog foundation (PR #6). Any implementation should have its own approved issue and acceptance criteria.
