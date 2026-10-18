# Reader growth follow-through — 18 October 2026

## Changes and evidence

This continuation uses the current publication and its existing first-person notes, not a claim that a completed Deep Research report was retrieved. It preserves the main-branch growth/press release, reader tools, author privacy, actual photographs, journal pins and GitHub Pages hosting.

Three article summaries separate: purchased-and-used coffee taste notes; a one-off milk/straw experiment that is explicitly not a product recommendation; and purchase records which explicitly do not establish hands-on verdicts. Each summary checks for supporting source phrases before publishing and preserves the original article, anchors, disclosures and photographs.

A generated reviews.html hub makes the distinctions easy to find. follow.html and feed.xml provide a real RSS follow path drawn from the journal's recent-story selection. Feed GUIDs are canonical permalinks, not changing build IDs, and no artificial publication dates are created. These are not email newsletter subscriptions. Both pages enter the sitemap and finished-edition search index. Footer and relevant-page links avoid adding the media kit to top navigation.

## Measurement is NOT activated

The existing GA4 measurement ID is blank. Connected account discovery did not establish a matching An AUsome Life property; Search Console discovery returned no accessible sites. No unrelated property is reused. The new bridge remains inactive unless a valid measurement ID AND analyticsEnabled=true AND analyticsPrivacyReviewed=true are explicitly configured. Visitor opt-in is also required. Global Privacy Control and Do Not Track override opt-in. Unknown and pre-consent events are dropped; allowed events use a small fixed vocabulary. No free-text fields, tool inputs, inquiry fields, link bodies, URL queries/fragments or referrer URLs are forwarded by this bridge. Sensitive tool/article paths are excluded. A contact click must not be reported as a submitted lead, and no historical traffic is backfilled.

Before activation: establish the correct property/stream and permissions; disable automatic enhanced measurement, signals, advertising and unreviewed integrations in that property; review cookie/retention settings and update the privacy notice for the chosen configuration. Verify actual browser network payloads and withdrawal behavior against that live property. Tests with mocks do not certify the behavior of Google's remote script. No new ID, property or tag container is invented in this change.

## Email signup remains a separate dependency

Resend has a verified sending domain and one General list. The existing studio API project has no configured environment variables. This release neither exposes an API key nor repurposes that studio service. No contacts were imported, no readers were subscribed, no broadcast was sent and no paid service was enabled. A secure signup service still needs confirmed opt-in, abuse protection, unsubscribe/suppression handling, suitable sender details and an end-to-end delivery test before a public email form is advertised.

## Validation

Eight Python regression tests passed locally using the existing full publication fixture: source evidence, link destinations, stable repeated builds, unique headings/anchors, true RSS, sitemap entries and hidden inactive measurement controls. Node tests verify default-off configuration, consent, DNT/GPC, invalid/expired preferences, restricted routes, allowlisted event fields, no private values or backlog, withdrawal, and blocked storage/script load failure. Twelve offline browser page/width checks passed at 320/390/768/1440 pixels, plus RSS copy fallback and a JavaScript-disabled follow page. Existing styles and images were inlined; unrelated scripts and external requests were excluded. This is not a full hosted-browser or WCAG audit. A narrow no-JavaScript article masthead wrap fix resolves observed small-screen overflow without changing the illustrated navigation.

Both preview and production retain the entire existing validation suite and add the new tests. The final publication guard checks generated page/summary destinations including anchors created by the earlier media transform. Confirm CI, merge and live deployment separately before claiming these changes are published.
