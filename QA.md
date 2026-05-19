# Bizdrive Video QA

## Before Render

```text
[ ] top/bottom roles confirmed
[ ] top is muted
[ ] bottom is main audio
[ ] bottom audio is treated as master timeline
[ ] user is notified if top/bottom duration, start offset, or drift mismatch is found
[ ] top/bottom trim timestamps match
[ ] top/bottom clean durations match
[ ] no remaining dead air longer than policy
[ ] audio polish completed
[ ] loudness checked
[ ] transcript generated from polished audio
[ ] key terms marked
[ ] context index created
[ ] context index matches required schema fields
[ ] key terms preserved in keep segments
[ ] key term checker has been run when context cut changes speech
[ ] B-roll slots selected from context
[ ] B-roll candidates QA checked
[ ] selected B-roll manifest exists
[ ] selected B-roll re-encoded render-safe
[ ] B-roll transition metadata exists for every selected slot
[ ] B-roll spacing is not too dense: no two B-roll starts closer than 6s and at least 3s real top footage between inserts
[ ] npm run check:transition passes after B-roll timing/composition changes
[ ] captions do not split Thai words
[ ] captions obey max length policy
[ ] caption gold baseline looks correct
[ ] zoom motion is subtle and does not move frame borders
[ ] npm run check:motion passes after zoom/motion changes
[ ] top frame shell and bottom frame have no transform/scale/x/y animation
[ ] BGM stock index checked before generating new music if BGM is used
[ ] npm run select:bgm report exists if BGM is used
[ ] selected BGM style is based on title/transcript/context
[ ] npm run check:bgm passes if BGM stock is used
[ ] default fallback is mixkit-480 Curiosity if clip style is unclear
[ ] BGM source/license is documented if used
[ ] BGM is licensed/royalty-free/generated-with-rights if used
[ ] BGM starts at 5% default unless user approved a different level
[ ] BGM is barely audible and felt more than heard
[ ] BGM melody does not pull attention from the speech
[ ] BGM mix command/report exists if BGM is used
[ ] BGM loop/fade is smooth if used
[ ] voice remains clearly louder than BGM if used
[ ] BGM has been tested on the final rendered MP4, not only on bottom source
[ ] npm run qa:bgm report exists if BGM is used
[ ] original final MP4 loudness and BGM final MP4 loudness are compared
[ ] original/BGM preview clips are created for listening comparison
[ ] index.html durations updated
[ ] npm run check passes
```

## B-roll QA

Reject and replace if any selected B-roll has:

```text
[ ] visible unrelated text
[ ] logo
[ ] watermark
[ ] other brand
[ ] distracting graphic
[ ] poor relevance to context
[ ] wrong orientation/crop after re-encode
[ ] audio track that was not removed
```

Required artifacts:

```text
candidate contact sheet
selected B-roll contact sheet
output B-roll contact sheet
optimized manifest.json
```

## Render QA

```text
[ ] output MP4 exists
[ ] output is 1080x1920
[ ] output duration matches expected plan
[ ] output has one audio track
[ ] audio is from bottom polished
[ ] top video is muted
[ ] B-roll replaces only top frame
[ ] bottom circle remains visible during B-roll
[ ] B-roll pacing is comfortable and never feels like B-roll/top/B-roll flashing inside a few seconds
[ ] B-roll entry/exit transition is smooth
[ ] jump-cover B-roll slots use bridge transition
[ ] transition mix does not move top/bottom frame borders
[ ] captions do not fade/pan with B-roll transition
[ ] captions remain visible and readable
[ ] key spoken terms are audible
[ ] soft cuts do not sound abrupt
[ ] zoom motion supports emphasis and is not distracting
[ ] zoom/motion is slow inner-media movement only; top/bottom frames remain fixed
[ ] BGM source/license is documented in final report if used
[ ] BGM does not cover speech and fades out cleanly
[ ] BGM mixed output is used as bottom source when BGM is enabled
[ ] no obvious frame freeze/seek issue
[ ] no text/logo/brand in B-roll output
```

## Final Delivery

```text
[ ] final report written
[ ] output path reported
[ ] version reported
[ ] metadata reported
[ ] npm run check result reported
[ ] B-roll downloaded/generated/reused/optimized/rejected counts reported
[ ] B-roll keyword/provider/source per slot reported
[ ] QA artifacts reported
[ ] WORKFLOW/CONFIG/STEPS updated if rules changed
[ ] CHANGELOG updated if version changed
```
