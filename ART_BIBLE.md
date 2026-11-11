# Sandlot Home Run Derby — Art Bible (first pass)

All art generated locally with ComfyUI on Bill's PC (Z-Image Turbo fp8, Qwen3-4B text encoder, 9 steps, cfg 1), keyed to alpha with `art_src/keyer2.py`. Nothing drawn in code, no line art. No real people, no film actors/names/logos/frames. Kid-friendly: everything is cute, nothing scary. Contact sheet: `art/contact_sheet.png`. Prompts/scripts: `art_src/`.

## Look
Warm painted storybook cartoon, gouache/watercolor texture, big-head chunky kids, dark-brown outline **#3a1d08** (sprites carry a 3 px #3a1d08 stroke added by the keyer). Backdrops are the same painted look with thinner outlines. 1962 summer: jeans (rolled cuffs), striped tees, ball caps, canvas high-tops.

**UI palette (code-drawn UI only):** gold `#ffd34d #f3b51c` · cream `#fff6b0 #fff4cf` · brown `#3a1d08 #6b4a2e` · wood `#c98a4b #e9c97e` · accents `#ff7a7a #ff6040`.

**Formats:** PNG with true alpha for sprites/props; JPEG for opaque backdrops/textures/title art; icons are opaque PNG. No WebP (iPadOS 13 safe).

## Roster (8 original kids; stances face RIGHT toward the pitcher; busts face slightly right)
| id | Name (nickname) | Archetype | Personality | Suggested stats (1–10) |
|---|---|---|---|---|
| milo | Milo | The new kid | Shy, eager, grows on you (white new cap, plaid shirt) | Power 4 · Contact 5 · Speed 5 · Luck 6 — gains +1 to a stat every 3 hits ("Learning") |
| duke | Duke | Star slugger | Confident, easy grin (red cap, red/white tee) | Power 10 · Contact 6 · Speed 5 · Luck 4 |
| tank | Tank | Big catcher | Gentle, sleepy giant (orange cap + catcher's mask, orange/cream tee) | Power 8 · Contact 4 · Speed 2 · Luck 5 — wide sweet spot |
| pearl | Pearl "Zip" | Fast leadoff | Springy, always running (yellow cap, red-brown braid) | Power 3 · Contact 8 · Speed 10 · Luck 5 |
| ricky | Ricky "Mouth" | Trash-talker | Cheeky, gum bubbles (navy cap tipped back, orange tee) | Power 6 · Contact 5 · Speed 6 · Luck 7 — "Hype" meter fills faster on streaks |
| walt | Walt "Specs" | Glasses kid | Thoughtful, precise (round glasses, blue cap, suspenders) | Power 3 · Contact 10 · Speed 4 · Luck 5 — easy timing window |
| peewee | Pip "Peewee" | Little kid | Tiny, giant grin, missing tooth (huge purple cap) | Power 2 · Contact 6 · Speed 7 · Luck 9 — small strike zone, lucky bounces |
| lou | Lou "Lefty" | Left-handed kid | Lanky, goofy cowlick (brown cap, mustard tee, patched jeans) | Power 6 · Contact 6 · Speed 6 · Luck 6 — curveballs break the other way for him |

**CPU pitcher: Chuck** — freckled, gray cap, gray/white tee, lefty glove (windup, release, idle). **Giant dog: Biscuit** — gentle English Mastiff (fawn, black mask, red bandana); idle-on-fence and excited-with-ball poses plus a sitting pose.

Raw consistency note: busts and stances were generated from the same character description with matched seeds' wording (the model has no reference-image input in this workflow), so outfits/colors match, small face details vary slightly.

## Files (`art/`)
| File | Size | Purpose |
|---|---|---|
| char_{milo,duke,tank,pearl,ricky,walt,peewee,lou}_stance.png | ~610–730 × 900 | Batting-stance sprite, transparent |
| char_{…}_bust.png | ~590–780 × ~700–770 | Character-select portrait (head + chest, soft bottom fade), transparent |
| pitcher_windup.png / pitcher_release.png / pitcher_idle.png | ~485–706 × 900 | CPU pitcher Chuck, faces left, transparent |
| dog_idle_fence.png | 1016 × 900 | Biscuit peeking over green plank fence (fence planks are part of the sprite), transparent |
| dog_excited.png | 610 × 700 | Biscuit leaping with baseball in mouth, transparent |
| dog_sit.png | 644 × 900 | Biscuit sitting (extra), transparent |
| bg_sandlot_day.jpg | 2048 × 1152 | Wide backdrop from home plate: dusty infield, outfield, green plank fence, houses, tree house, golden hour; bottom third is simple dirt for HUD |
| bg_sandlot_night.jpg | 2048 × 1152 | Same layout, Fourth-of-July night with fireworks, lit windows, string lights on tree house |
| sky_golden.jpg / sky_fireworks.jpg | 2048 × 1152 | Sky-only layers (day / fireworks night) |
| houses_row.png | 1554 × 343 | Row of five 1960s ranch/stucco houses, transparent, for parallax |
| fence_tile.jpg | 512 × 512 | Green plank fence tile (edge-blended; tile in X) |
| treehouse_tree.png | 816 × 994 | Big tree + tree house, transparent |
| window_1…6.png | ~330 × 360 | Intact glowing windows (targets), transparent |
| window_broken_1…3.png | ~280 × 360 | Cracked cartoon windows with sparkle (shatter-flash swap), transparent |
| tex_dirt.jpg / tex_grass.jpg | 512 × 512 | Tileable infield dirt / lawn textures |
| title_landscape.jpg | 1600 × 900 | Key art (landscape); empty sky for logo, no text |
| title_portrait.jpg | 1080 × 1920 | Key art (portrait); empty sky at top for logo, no text |
| icon_1024.png, icon_512.png, apple-touch-icon.png | 1024 / 512 / 180 | Game icon (opaque, no alpha) |
| ball_clean.png, ball_scuffed.png, bat.png, glove.png | 256 / 256 / 647×433 / 435×384 | Props, transparent |
| contact_sheet.png | 1800 × 2390 | Labeled overview of everything |

Not made (optional): "pickle"/rundown mini-mode scene.

## References consulted (look research only; nothing copied into assets)
- https://www.sltrib.com/sports/2023/08/21/sandlot-is-beloved-piece-salt/ — how the film's built-from-scratch dirt lot, backstop, fence and moved tree/tree house sat behind ordinary houses.
- https://www.cityweekly.net/ae/its-been-30-years-since-the-sandlot-filmed-in-salt-lakes-glendale-neighborhood-20393415 — premise and set construction notes (tree dug up and moved; replica lot).
- https://www.deseret.com/2013/7/11/20522433/outdoor-movies-utah-will-celebrate-20-years-of-the-sandlot-this-summer/ — crew built the diamond, fences, telephone poles and alley on an empty lot.
- https://www.tigerdroppings.com/rant/o-t-lounge/has-anyone-tried-to-visit-the-the-sandlot-baseball-field-from-the-movie-in-slc/101817965/ — layout: older working-class houses along the field edge, power poles, big empty lot.
- https://calisphere.org/item/10ff8642c2b773f9195d0831a32d4358/ — 1958 ranch house in West Hills, San Fernando Valley.
- https://www.laconservancy.org/learn/historic-places/westridge-park-ranch-houses/ — Valley ranch tract houses: low roofs, wide eaves, picture windows/expanses of glass, quarter-acre lots.
- https://www.royalkennelclub.com/breed-standards/working/mastiff/ — Mastiff: fawn/apricot coat, black muzzle/ears/nose and mask, square head, big jowls (used for Biscuit's design, softened/cartoonized).
- https://en.wikipedia.org/wiki/English_Mastiff — size, colors, gentle temperament.
- http://collectorgene.com/2015/03/vintage-pf-flyers-superpowers-for-kids/ — early-60s kids' canvas sneakers (PF Flyers era).
- https://keymancollectibles.com/bats/louisvilleslugger125bb.htm — 1960s Little League wooden bat with taped grip.
- https://www.craftunionvintage.store/listing/1510643210/1950s-60s-wool-letter-baseball-cap — 1950s–60s kids' wool baseball cap.
- https://www.ericdavisimages.com/image/I00003VDFHlmLwLQ — fireworks bursting over a suburban neighborhood (night glow reference).
- https://www.istockphoto.com/photos/flaking-green-paint-on-old-wooden-fence — weathered green plank fence reference.
