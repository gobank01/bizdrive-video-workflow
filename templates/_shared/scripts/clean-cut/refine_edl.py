#!/usr/bin/env python3
"""
Refine an EDL using audio silence/speech detection.

Slots between editorial review (step 3) and apply_edits (step 4):
  transcribe → format → editorial review → refine_edl.py → apply_edits

Two refinements:
1. Boundary verification: extends segment starts/ends outward if speech is
   detected at the boundary, preventing clipped words. Prefers under-clipping.
2. Internal pause splitting: splits segments at silence gaps >= min_pause_ms.
   Catches the #1 user correction from previous edits.

Uses ffmpeg silencedetect — no extra Python dependencies required.

Usage:
  python3 refine_edl.py <input.mp4> <edl.json> [-o <refined_edl.json>]
"""

import argparse
import json
import re
import subprocess
import sys


def detect_silences(input_file, noise_db=-35, min_duration_s=0.3):
    """
    Run ffmpeg silencedetect on audio.
    Returns (silences, total_duration_ms).
    silences is a list of (start_ms, end_ms) tuples.
    """
    cmd = [
        'ffmpeg', '-i', input_file,
        '-af', f'silencedetect=noise={noise_db}dB:d={min_duration_s}',
        '-f', 'null', '-'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    starts = [float(x) * 1000 for x in re.findall(r'silence_start:\s*([\d.]+)', stderr)]
    ends = [float(x) * 1000 for x in re.findall(r'silence_end:\s*([\d.]+)', stderr)]

    # Total duration from ffmpeg output
    dur_match = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', stderr)
    total_ms = 0.0
    if dur_match:
        h, m, s = dur_match.groups()
        total_ms = int(h) * 3600000 + int(m) * 60000 + float(s) * 1000

    silences = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else total_ms
        silences.append((s, e))

    return silences, total_ms


def invert_to_speech(silences, total_ms):
    """Invert silence regions to get speech regions."""
    speech = []
    prev = 0.0
    for s_start, s_end in sorted(silences):
        if s_start > prev:
            speech.append((prev, s_start))
        prev = max(prev, s_end)
    if prev < total_ms:
        speech.append((prev, total_ms))
    return speech


def find_containing_region(time_ms, regions):
    """Find the region containing time_ms. Returns (start, end) or (None, None)."""
    for r_start, r_end in regions:
        if r_start <= time_ms <= r_end:
            return r_start, r_end
    return None, None


def refine_boundaries(segments, speech_regions, extend_ms=300):
    """
    Extend segment boundaries outward when speech is detected at the edge.
    Prevents clipping words. Caps extension at extend_ms to avoid grabbing
    adjacent takes.
    """
    refined = []
    for seg in segments:
        start = seg['start_ms']
        end = seg['end_ms']
        start_adj = 0
        end_adj = 0

        # Start boundary: if in speech, extend backward
        r_start, _ = find_containing_region(start, speech_regions)
        if r_start is not None:
            new_start = max(r_start, start - extend_ms)
            start_adj = round(new_start - start)
            start = new_start

        # End boundary: if in speech, extend forward
        _, r_end = find_containing_region(end, speech_regions)
        if r_end is not None:
            new_end = min(r_end, end + extend_ms)
            end_adj = round(new_end - end)
            end = new_end

        refined.append({
            'start_ms': round(start),
            'end_ms': round(end),
            '_start_adj': start_adj,
            '_end_adj': end_adj,
        })

    return refined


def split_at_pauses(segments, silences, min_pause_ms=500, min_seg_ms=300):
    """Split segments at internal silence gaps >= min_pause_ms."""
    output = []
    total_splits = 0

    for seg in segments:
        s = seg['start_ms']
        e = seg['end_ms']

        # Find silences fully inside this segment (with margin so we don't
        # create sub-segments shorter than min_seg_ms)
        internal = sorted([
            (ss, se) for ss, se in silences
            if ss >= s + min_seg_ms and se <= e - min_seg_ms
            and (se - ss) >= min_pause_ms
        ])

        if not internal:
            output.append({'start_ms': s, 'end_ms': e})
            continue

        cur = s
        for ss, se in internal:
            if ss - cur >= min_seg_ms:
                output.append({'start_ms': round(cur), 'end_ms': round(ss)})
                cur = se
                total_splits += 1

        if e - cur >= min_seg_ms:
            output.append({'start_ms': round(cur), 'end_ms': round(e)})

    return output, total_splits


def fix_overlaps(segments):
    """Resolve overlaps between consecutive segments after boundary extension."""
    for i in range(len(segments) - 1):
        if segments[i]['end_ms'] > segments[i + 1]['start_ms']:
            mid = (segments[i]['end_ms'] + segments[i + 1]['start_ms']) // 2
            segments[i]['end_ms'] = mid
            segments[i + 1]['start_ms'] = mid
    return segments


def drop_tiny_segments(segments, min_ms=300):
    """
    Remove segments shorter than min_ms that were created by splitting
    between two adjacent silence regions (brief noise blips, not real speech).
    """
    return [s for s in segments if s['end_ms'] - s['start_ms'] >= min_ms]


def merge_close(segments, gap_ms=100):
    """Merge segments closer than gap_ms apart."""
    if not segments:
        return segments
    merged = [segments[0].copy()]
    for seg in segments[1:]:
        if seg['start_ms'] - merged[-1]['end_ms'] < gap_ms:
            merged[-1]['end_ms'] = seg['end_ms']
        else:
            merged.append(seg.copy())
    return merged


def main():
    ap = argparse.ArgumentParser(
        description='Refine EDL using silence/speech detection')
    ap.add_argument('input', help='Source audio or video file')
    ap.add_argument('edl', help='Input EDL JSON file')
    ap.add_argument('-o', '--output',
                    help='Output path (default: overwrites input EDL)')
    ap.add_argument('--noise-db', type=int, default=-35,
                    help='Silence threshold in dB (default: -35)')
    ap.add_argument('--min-pause-ms', type=int, default=500,
                    help='Min internal pause to split at in ms (default: 500)')
    ap.add_argument('--extend-ms', type=int, default=300,
                    help='Max boundary extension in ms (default: 300)')
    ap.add_argument('--min-segment-ms', type=int, default=500,
                    help='Min segment duration after split in ms (default: 500)')
    ap.add_argument('--merge-gap-ms', type=int, default=100,
                    help='Merge segments closer than this in ms (default: 100)')
    ap.add_argument('--dry-run', action='store_true',
                    help='Show changes without writing output')
    args = ap.parse_args()

    # Load EDL
    with open(args.edl) as f:
        edl = json.load(f)
    segments = edl['segments']
    n_orig = len(segments)

    print(f'Input: {n_orig} segments')

    # Detect silences via ffmpeg
    print(f'Running silence detection (noise={args.noise_db}dB)...')
    silences, total_ms = detect_silences(
        args.input, noise_db=args.noise_db)
    speech = invert_to_speech(silences, total_ms)
    print(f'  {len(silences)} silence regions, {len(speech)} speech regions '
          f'in {total_ms / 1000:.1f}s audio')

    # 1. Refine boundaries
    segments = refine_boundaries(segments, speech, extend_ms=args.extend_ms)
    n_adjusted = 0
    for seg in segments:
        sa = seg.pop('_start_adj')
        ea = seg.pop('_end_adj')
        if sa or ea:
            n_adjusted += 1
            print(f'  Boundary {seg["start_ms"]}ms–{seg["end_ms"]}ms: '
                  f'start {sa:+d}ms, end {ea:+d}ms')
    print(f'Boundaries: {n_adjusted}/{n_orig} segments adjusted')

    # 2. Fix overlaps from extension
    segments = fix_overlaps(segments)

    # 3. Split at internal pauses
    segments, n_splits = split_at_pauses(
        segments, silences,
        min_pause_ms=args.min_pause_ms, min_seg_ms=args.min_segment_ms)
    print(f'Splits: {n_splits} internal pauses found and split')

    # 4. Drop tiny segments (noise blips between adjacent silences)
    before_drop = len(segments)
    segments = drop_tiny_segments(segments, min_ms=args.min_segment_ms)
    n_dropped = before_drop - len(segments)
    if n_dropped:
        print(f'Dropped: {n_dropped} segments < {args.min_segment_ms}ms')

    # 5. Merge segments that ended up very close together
    before = len(segments)
    segments = merge_close(segments, gap_ms=args.merge_gap_ms)
    n_merged = before - len(segments)
    if n_merged:
        print(f'Merged: {n_merged} segments merged (gap < {args.merge_gap_ms}ms)')

    # Summary
    kept_s = sum(s['end_ms'] - s['start_ms'] for s in segments) / 1000
    print(f'Output: {len(segments)} segments ({len(segments) - n_orig:+d}), '
          f'{kept_s:.1f}s kept')

    if args.dry_run:
        print('(dry run — no output written)')
        return

    # Write
    out_path = args.output or args.edl
    edl['segments'] = segments
    with open(out_path, 'w') as f:
        json.dump(edl, f, indent=2)
        f.write('\n')
    print(f'Saved: {out_path}')


if __name__ == '__main__':
    main()
