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
[ ] captions do not split Thai words
[ ] captions obey max length policy
[ ] caption gold baseline looks correct
[ ] zoom motion is subtle and does not move frame borders
[ ] BGM is licensed/royalty-free if used
[ ] BGM loop/fade is smooth if used
[ ] voice remains clearly louder than BGM if used
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
[ ] captions remain visible and readable
[ ] key spoken terms are audible
[ ] soft cuts do not sound abrupt
[ ] zoom motion supports emphasis and is not distracting
[ ] BGM does not cover speech and fades out cleanly
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
