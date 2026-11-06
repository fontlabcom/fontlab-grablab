---
this_file: src_docs/md/svg-and-icons.md
---

# SVG and icons

## Host-free SVG processing

Install `fontlab-grablab[svg]` outside FontLab for postprocessing. Pillow decodes PNG pixels; pure-Python svgelements
measures transformed SVG geometry. Neither dependency loads during native capture or ordinary `import grablab`.

```python
import json
from pathlib import Path
from grablab import svg

root = svg.read_svg("panel.svg")
index = svg.build_raster_index("assets-manifest.json", source_dirs=["source-pngs"])
mapping = svg.map_images(root, index)  # JSON-serializable URI -> candidates/status
stats = {"icons": svg.process_images(root, mapping)}
stats["widgets"] = svg.tag_widgets(root, json.loads(Path("panel.json").read_text()))
svg.write_svg(root, "panel-processed.svg")  # refuses any existing output
svg.restyle(root, wireframe=True, background="white")
svg.write_svg(root, "panel-wireframe.svg")
```

Every data URI must match known decoded PNG dimensions and 8-bit premultiplied RGBa pixels exactly. This preserves Qt's
rendered pixels despite lossy PNG unpremultiplication at translucent edges; it is not fuzzy or alpha-only matching.
Index schema 2 records `pixel_format="RGBa8"`; rebuild older indexes before use. Candidates disclose
`match="pixel-exact"` for exported PNG matches and `match="source-name"` for authoritative source PNGs associated by
unique original asset name (only `@2x` is normalized). The latter preserves provenance but does not claim the new vector
renders exactly like the old PNG. Multiple distinct SVG candidates are ambiguous and stay rasterized; unknown,
unsupported and malformed images also remain untouched. Retain mapping and index JSON as receipts; paths may contain
local/private information.

Nested SVGs retain image viewport/aspect ratio, ancestor transforms and clipping; local IDs, fragment/url references and
CSS classes are namespaced. `tag_widgets` tags original elements in place using transformed bounds and the smallest
containing `extensions.widgets[].rect`, preserving paint order and existing IDs. Equal-area ties require one proven
descendant through the recorded parent chain; otherwise elements stay untagged, with sorted candidate IDs in ambiguity
stats. New IDs derive from widget IDs; `data-widget` records the exact widget identity. Text uses its transformed
anchor, disclosed by `data-widget-method="text-anchor"`, rather than invented font metrics. Bounds containment is
approximate ownership: clipping, text extents, use-instance ownership and arbitrary CSS are not inferred.
Unsupported/unmatched counts and limits remain in returned stats.

`compose([(path, x, y), ...], width=..., height=...)` uses explicit logical positions, input paint order, source viewBox
sizes and collision-free local IDs. `restyle` changes stroke/fill/width/background/font (`system-ui` by default),
including inline CSS. Documents containing `<mask>` are refused before any mutation, including font-only changes:
inherited paint and text geometry affect mask opacity. Wireframe keeps readable monochrome text and outlines on opaque
surfaces. Monochrome applies a root grayscale filter, preserving luminance and existing filter effects. It refuses
author stylesheets, important root filters and CSS-wide root-filter values before mutation. Wireframe alone wraps
retained rasters with grayscale groups; combining rasters with author stylesheets is refused because wrapping can change
selectors. Stylesheet-only vector inputs remain supported for wireframe and ordinary restyling. Image bytes/geometry
remain intact; filtered_images reports the affected raster count. CSS grayscale needs a supporting SVG renderer.
Ordinary color changes preserve effective `none` from presentation attributes, class/ID CSS and inline styles using
specificity, source order, inheritance and `!important`. Conditional stylesheet rules and unresolved contextual paints
fail before mutation. cssselect2/tinycss2 provide the selector and declaration parsing. External resources, global CSS
selectors and `!important` rules need separate review; helpers target trusted Qt captures and the known Illustrator
assets.

Optional `deduplicate_paths` removes only consecutive identical opaque fill-only paths without IDs, strokes or inherited
opacity/effects. Repeated antialiased edges can differ; compare processed renders or leave cleanup disabled when exact
pixels matter. Raw inputs remain separate. Host-free tests and asset indexing do not establish native screenshot
fidelity.

## Icon representation modes

`process_images(root, mapping=None, icon_mode="inline-svg", output=None)` returns mode, linked/inlined/retained counts,
retained reasons and resolved targets. The existing `inline_images` API is unchanged. Modes:

- `base64`: retain every image without indexing assets; mapping is optional.
- `png-url`: link a matching exported PNG, preferring exact pixels; ties use
  sorted paths. Source-name matches use the manifest's standard PNG (then the
  first sorted PNG variant). This is provenance, not visual equivalence.
- `svg-url`: link the unique matched SVG without inserting its paths.
- `inline-svg` (default): retain the existing namespaced vector substitution.

URL modes require `output`, the destination SVG filename, and emit escaped relative URLs to the original named assets.
They do not copy/rename resources. Keep the referenced asset tree available when moving or serving the result. Both href
forms are read with SVG2 href precedence; a replaced image has only href. Geometry, transforms, clipping, opacity and
aspect ratio stay intact. Missing/invalid targets and ambiguous/unknown images are retained with reasons. Base64 mode
preserves even malformed image URIs without decoding them. Pass `output` to `compose` as well when its directory differs
from the panels; it rebases relative image URLs, preserving queries/fragments and remote URLs. These helpers target
trusted Qt captures without XML base overrides.

Linked SVG interiors cannot inherit screenshot paint or font changes. Mono filters the rendered image; wireframe keeps a
grayscale image rather than converting its paths. Open linked screenshots directly or use HTML iframe/object. HTML img
embedding restricts external resources, so an SVG load event alone does not prove its icons loaded. See the [SVG2
processing modes](https://www.w3.org/TR/SVG2/conform.html#secure-static-mode) and [image
element](https://www.w3.org/TR/SVG2/embedded.html#ImageElement).
