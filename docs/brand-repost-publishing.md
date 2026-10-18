# Brand sharing: publication standard

Internal editorial and implementation guidance. Do not publish this document, its templates, strategy or results records as reader-facing content. Effective 18 October 2026, following the owner's request to analyze what would make brands repost stories like Congdon’s and improve future posts.

## Editorial objective

Give the featured brand a useful, accurate story it can pass to its own customers with little additional work. The working editorial hypothesis is that a recognizable real moment, a specific reader benefit and finished sharing materials make sharing easier. This is a design rationale, not measured evidence that a brand will repost, increase reach or send customers.

For each new comparable place, outing or product story, identify one genuine detail the brand would recognize and one reason its audience would save or open the story. A photograph of an ordinary enjoyable visit plus a practical choice board is sufficient. Do not invent praise, special service, a favorite flavor, use of a resource, quiet conditions or a result. Preserve the family voice and full independent verdict.

The hero should name the place/product and location where useful, pair the true story with an original or authorized photograph, and make the takeaway clear in the dek. Social title and description should be understandable outside the site. A warm editorial h1 may stay; the social preview can spell out the free resource or specific practical benefit.

## Minimum package for a new comparable story

| Element | Publication requirement |
| --- | --- |
| Story and evidence | Real observations distinguished from official information and unanswered questions; useful takeaway; source links and checked date where facts can change. |
| Opening and preview | Brand/place recognizable; location and audience benefit clear; original or authorized hero; reviewed Open Graph/Twitter title, description and image. |
| Suggested caption | Story-specific, ready to copy, accurate by itself; place/product and reader benefit; one clear action, canonical story link and An AUsome Life credit. Use third-person attribution when another account will publish it. |
| Story copy | A short caption and destination URL; qualifications needed to keep it truthful. Do not claim there is already an Instagram Story. |
| Social graphics | Reviewed static files suited to a feed and a tall Story when intended rights are cleared. Actual file dimensions, ordinary download links, readable layout and any necessary disclosure. |
| Descriptions | Meaningful preview alt text and copyable descriptions matching the final exported graphics. |
| Usage permission | Scope limited to the exact approved files and specified use, with credit/link requirements. Other assets retain their own terms. |
| Internal registration | Page registered in `docs/story-sharing-approvals.json`, pointing to reviewed provenance whose allowed files, output hashes and dimensions match the package's downloadable graphics. |
| Identity | Brand accounts verified separately by platform from current official evidence. Record exact URL, verification source and checked date internally. |
| Delivery status | Website, downloads, native social publication and external notices each reported according to the action actually completed. |

If the available evidence does not support a favorable recommendation, publish the honest account. A sharing package must not change the verdict. If an asset lacks sharing rights, use a cleared original typographic/resource graphic or an ordinary story link while resolving the specific gap; do not silently license the uncertain asset.

## Standalone accuracy and dignity

Read every caption and graphic without the article. They must remain true in that setting.

- Keep material access, ingredient and experience limitations. State what was observed, what the venue says and what still needs checking. A family visit is not a complete access audit.
- Generic food pictures are illustrations, not brand product photographs or an official menu. Avoid logos or artwork without appropriate rights. Disclose independently made resources and actual paid/gifted/hosted relationships where relevant; do not invent either a relationship or a “not sponsored” history.
- State when a tool is for a future visit. Do not imply it helped during a photographed visit unless actual use and effect are documented.
- Preserve communication agency, refusal and alternatives. Do not frame “no,” “break” or “all done” as failures to overcome. Keep ordinary pleasure free of pity, inspiration, staged distress or diagnosis-led promotion.
- A visible happy moment does not prove that a venue is typically quiet, fully accessible, welcoming to every disability, or providing a therapeutic benefit. Do not present a brand repost as endorsement, a partnership, bookings or measured reach.
- Use An AUsome Life for authorship and credit. Follow the owner's privacy and family-photo directions across captions, images, alt text, metadata and download contents.

## Assets and exact-file rights

Create a resource or story promotion graphic separately from a functional communication board. The social graphic can show a representative preview and one clear next step; the full board remains the practical download. Current Congdon’s export choices are 1080 × 1350 for the feed and 1080 × 1920 for Stories. These are this project's design choices, not a claim about every platform's current requirements.

Use the approved cream, navy and pine palette, strong contrast and readable labels. Preserve original photograph proportions and pixels; do not add synthetic family imagery, invent a product photograph or turn a documentary hero into a communication card. For Congdon’s, the approved social downloads contain resource artwork and no family photographs.

Review every final export and record asset paths, dimensions, provenance, intended use and hashes in its internal rights record. Permission must be tied to those reviewed assets. A source link, credit, existing publication or AI origin alone does not grant third-party rights.

Register each new authored sharing page in `docs/story-sharing-approvals.json` under `packages["page-filename.html"]`, with `provenance` pointing to the internal record and `reviewed` giving the review date. The record's `scoped_organic_sharing_intent.assets_only` must list the exact approved graphic paths. Each `outputs` entry must supply `path`, `sha256` and `dimensions` for the reviewed export. The package's downloads must match that set; do not add an original family photograph or another asset merely because it is already present on the site. After changing a graphic, review the new export and deliberately update its provenance before publication. Do not update a hash simply to bypass a failed check without reviewing the changed file.

The Congdon’s permission allows the two named social graphics to be shared unchanged in organic social posts or Stories with An AUsome Life / @anausomelife credit and a link to the free board. It does not license the family photographs, the archive, paid advertising, edits or other reuse. Future packages need their own asset review and explicit scope; copying the HTML does not transfer permission to other files.

## Authored sharing section: implementation contract

The working reference is `congdons-doughnuts-wells-maine.html#share-this-story`, enhanced by `assets/story-share.js`. Use one static `.aal-story-share` inside `main`, after the useful story/practical information and before related reading. The shared script enhances an authored section; it creates a generic link-sharing fallback only when no authored section exists on a recognized story. The fallback is appropriate for existing archive pages awaiting individual review, not the editorial package for a new comparable story.

| Markup | Meaning and requirement |
| --- | --- |
| `.aal-story-share` | One authored sharing section with a visible heading and `aria-labelledby`. Do not pre-set `data-aal-share-ready`; the script owns its initialization flag. |
| `data-share-summary` | A short, reviewed summary used by native sharing. It is not a license or a claim that a social post was published. |
| `[data-share-caption]` | Visible, complete suggested caption. The script copies its text, including credit and link. Keep intentional paragraph breaks. |
| `[data-copy-caption]`, `[data-copy-link]` | Optional enhancement buttons with `type="button"` and initially `hidden`. The script reveals and binds them. |
| `[data-share-native]` | Optional initially hidden native-share button. The script reveals it only where supported. |
| `.aal-share-status[role="status"]` | Required status output for copying/sharing results. |
| `[data-share-fallback]` | Required initially hidden container with a labelled readonly textarea for selection when clipboard copying is unavailable. |
| `[data-copy-share-text="source-id"]` | Optional initially hidden button that copies the nonempty text of that ID inside the sharing section; use unique IDs beginning with a letter and containing letters, digits, underscores or hyphens. |
| `data-copy-status` | Optional concise success message on a copy-by-ID button. |
| `[data-reuse-link]` | Optional ordinary link with a useful static href; enhancement points to the media reuse section with the canonical story prefilled. |
| Static preview/downloads/permission | Real images and links with actual dimensions, alt text, credit and exact-file terms. Keep these and the caption readable without JavaScript. |

The script reads the page's canonical HTTPS URL, h1 and story markup. Keep the canonical clean and on anausomelife.com. A clipboard fallback needs its status element, fallback container and textarea even when the page normally copies successfully. Use the maintained shared loader; do not insert duplicate scripts or duplicate sharing sections.

### Starting structure

This is an internal structural template. Replace every bracketed value, finish all captions and permissions, and link only reviewed existing files before using it in a page. The current Congdon’s source shows the full layout, graphics, Story caption and alt-text disclosure.

```html
<section class="aal-story-share" id="share-this-story"
  aria-labelledby="aal-share-title" data-share-summary="[Reviewed summary]">
  <h2 id="aal-share-title">[Specific reader benefit]</h2>
  <p>[One useful invitation, with an ordinary link to the story or resource.]</p>
  <div class="aal-story-actions">
    <button type="button" data-share-native hidden>Share story</button>
    <button type="button" data-copy-link hidden>Copy story link</button>
    <button type="button" data-copy-caption hidden>Copy suggested caption &amp; credit</button>
    <a href="[Real resource URL]">[Open the resource]</a>
  </div>
  <p class="aal-share-status" role="status"></p>
  <div data-share-fallback hidden>
    <label for="aal-share-copy">Select and copy this text</label>
    <textarea id="aal-share-copy" readonly></textarea>
  </div>
  <details class="aal-share-package">
    <summary>Download social graphics &amp; see the captions</summary>
    [Reviewed preview figures and download links, with actual dimensions and alt text.]
    <p class="aal-share-permission">[Permission for the exact listed files and use.]</p>
    <h3>A suggested caption</h3>
    <p class="aal-share-copy-text" id="story-share-caption" data-share-caption>
[Complete reviewed caption, canonical story URL, credit and necessary disclosure.]
    </p>
    <h3>A short Story caption</h3>
    <p class="aal-share-copy-text" id="short-story-caption">[Finished copy and link.]</p>
    <button type="button" data-copy-share-text="short-story-caption" hidden>Copy Story caption</button>
    <details class="aal-share-alt">
      <summary>Image descriptions to copy</summary>
      <p id="feed-image-description">[Accurate final graphic description.]</p>
      <button type="button" data-copy-share-text="feed-image-description" hidden>Copy image description</button>
    </details>
    <p class="brand-note">[Relevant attribution/disclosure for this package.]</p>
  </details>
</section>
```

A native disclosure can be opened without JavaScript. The enhancement buttons begin hidden because their actions require JavaScript; the caption, image description and download links do not depend on those buttons.

## Account verification and separate social publication

Use an official website's social links or metadata, or another current authoritative brand source, to verify each account. Record the exact platform, profile URL, evidence URL and check date. Matching names alone are insufficient; a Facebook handle is not proof of an Instagram handle. Leave an unverified brand handle out while using its ordinary business name.

For the 18 October 2026 Congdon’s work, the official contact-page metadata supports the Facebook profile `https://www.facebook.com/ilovecongdons/`. The Instagram account remained unverified and must not be guessed. Source: `https://congdons.com/contact/`. Recheck before future tagging or contact. This account record is not evidence of a repost or brand response.

Meta's 6 August 2025 announcement describes native Instagram reposts for public feed posts and Reels, with credit to the original poster and potential distribution to the reposter's followers. It does not establish that publishing a website article creates an Instagram post or that any particular account has reposted it. Source checked 18 October 2026: [Meta, “New Instagram Features to Help You Connect”](https://about.fb.com/news/2025/08/new-instagram-features-help-you-connect/).

Maintain separate status for the live website article, downloadable graphics, An AUsome Life's own native social post, a brand's native repost or separately uploaded organic post, and any notice sent to the brand. Use a real post URL or other direct evidence for a completed social action. Do not report that content is on Instagram because graphics exist on the website. Native posting and external messages follow the user's actual authorization; the sharing package itself sends nothing.

## Publication gate

The publication review must confirm that **every new comparable story has its own reviewed package**. `python tools/check_story_sharing.py` checks authored packages that exist; it does not determine editorial relevance or guarantee that every new story has one. This requires editorial judgment, not an additional user approval step; an assistant carrying out authorized publication work can complete the review.

Before release:

1. Read the story, each standalone caption and each graphic for truth, scope, privacy, dignity, link/credit accuracy and actual asset permissions. Check official facts and account evidence when relevant.
2. Inspect final feed/Story graphics and any practical downloads. Compare visible text, image descriptions and file dimensions. Preserve the distinction between a preview and the complete usable resource.
3. Verify the authored package is readable without JavaScript; with enhancement, check copying, clipboard fallback, correct copy targets and native sharing where available. Check small-screen readability and keyboard access.
4. Run `python tools/check_story_sharing.py` and the applicable existing publication checks, including editorial rights and social metadata. The sharing checker covers caption/credit/canonical links, previews and PNG dimensions/decodability, status/fallback elements, copy targets, hidden enhancement controls and explicit organic-sharing scope. It also checks the page's approval-registry entry and matches package downloads against the provenance's allowed asset paths, hashes and dimensions. It is not legal clearance, an accessibility audit or a semantic guarantee of truthful claims.
5. Validate the prepared public artifact, optionally using `python tools/check_story_sharing.py --root [prepared-site-path]`, and verify the actual live URLs after successful publication. Keep internal Markdown, `docs/`, provenance, templates and results records out of the hosted artifact and search index.

After a page generator, follow the existing photography and headline cleanup instructions, then rebuild the search index. Do not let a generator reinstate the superseded automatic family-photo communication-card instruction. Changes to an older page do not grant new reuse rights to any archive asset.

## Minimal outcome record

Use an internal manual log when an actual share or response occurs. A compact record is enough:

| Field | Record |
| --- | --- |
| Story | Canonical article/resource URL and package review date. |
| Our social publication | Platform, actual post URL and publication date, or “not published” / “unverified.” |
| Observed brand/community share | Exact account, platform, repost/post URL, observation date and post date if visible. For an expiring Story, retain permitted evidence with its observation time. |
| Kind of response | Repost, link share, comment, correction or direct inquiry, described accurately. A like is not a repost. |
| First-party results, when available | Source, reporting period, metric name and value for attributable referrals or resource downloads. State measurement limitations. |
| Follow-up | Relevant authorized next step or correction, without inventing a commitment or scheduling work automatically. |

At this standard's creation, `data/site-config.json` has an empty `ga4MeasurementId`. Do not claim website tracking is enabled or that referrals/downloads are already measured. Analytics source code alone is not an active measurement configuration. Use first-party metrics only after the relevant source is configured, verified and available; otherwise record “unavailable,” not zero. Do not infer reach from followers, likes, national statistics or a promised share. Review actual repost links and inquiries before attributing improvement to this packaging.
