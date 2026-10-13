# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = []
# ///
"""resolve-ctl: thin, safe bridge from Claude Code to DaVinci Resolve Studio (external scripting).

Rules: read commands are free; write commands print a dry-run plan and only act with --apply;
nothing is ever deleted or overwritten; every write is appended to <log>.jsonl.

Usage:
  uv run --python 3.12 resolve_ctl.py status
  uv run --python 3.12 resolve_ctl.py projects
  uv run --python 3.12 resolve_ctl.py api                      # list methods the running Resolve exposes
  uv run --python 3.12 resolve_ctl.py clips [--bin NAME] [--csv OUT]
  uv run --python 3.12 resolve_ctl.py timelines
  uv run --python 3.12 resolve_ctl.py markers-from-csv SELECTS.csv [--apply] [--log LOG]
  uv run --python 3.12 resolve_ctl.py timeline-from-csv SELECTS.csv --name NAME [--apply] [--log LOG]
  uv run --python 3.12 resolve_ctl.py snapshot --out DIR [--timeline NAME] [--apply]
  uv run --python 3.12 resolve_ctl.py render --preset NAME --out DIR --file NAME [--timeline NAME] [--apply]

Resolve must be running with Preferences > System > General > External scripting using = Local.
SELECTS.csv columns: clip,in,out[,speaker,quote,ring,score,reason]
  clip = media pool clip name (or file name); in/out = seconds (12.5) or source timecode (01:02:03:04).
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
from pathlib import Path

MAC_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
MAC_LIB = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
RING_COLORS = {"1": "Blue", "2": "Green", "3": "Yellow", "": "Cream"}  # dalga halkası -> marker rengi


# ---------- connection ----------

def connect():
    api = os.environ.setdefault("RESOLVE_SCRIPT_API", MAC_API)
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", MAC_LIB)
    sys.path.append(os.path.join(api, "Modules"))
    try:
        import DaVinciResolveScript as dvr  # noqa: N813
    except ImportError as e:
        sys.exit(f"!! DaVinciResolveScript not importable ({e}). Is Resolve Studio installed?")
    resolve = dvr.scriptapp("Resolve")
    if resolve is None:
        sys.exit("!! Resolve not reachable. Open Resolve and set External scripting = Local "
                 "(Preferences > System > General).")
    return resolve


def project_of(resolve):
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if proj is None:
        sys.exit("!! No project open in Resolve.")
    return pm, proj


# ---------- helpers ----------

def walk_folders(folder, path=""):
    name = folder.GetName()
    here = f"{path}/{name}" if path else name
    yield here, folder
    for sub in folder.GetSubFolderList() or []:
        yield from walk_folders(sub, here)


def all_clips(media_pool, only_bin=None):
    for path, folder in walk_folders(media_pool.GetRootFolder()):
        if only_bin and folder.GetName() != only_bin:
            continue
        for clip in folder.GetClipList() or []:
            yield path, clip


def clip_index(media_pool):
    """name -> clip and file-name -> clip; duplicate names keep the first and warn."""
    idx = {}
    for _, clip in all_clips(media_pool):
        keys = {clip.GetName(), Path(clip.GetClipProperty("File Path") or "").name}
        for k in keys:
            if k and k in idx and idx[k] is not clip:
                print(f"?? duplicate clip name '{k}', using the first one", file=sys.stderr)
                continue
            if k:
                idx[k] = clip
    return idx


def fps_of(clip):
    try:
        return float(clip.GetClipProperty("FPS"))
    except (TypeError, ValueError):
        return 25.0


def tc_to_frames(tc, fps):
    hh, mm, ss, ff = (int(x) for x in tc.replace(";", ":").split(":"))
    base = round(fps)
    return ((hh * 60 + mm) * 60 + ss) * base + ff


def to_source_frame(value, clip):
    """seconds -> frame offset; timecode -> offset from the clip's Start TC."""
    fps = fps_of(clip)
    value = value.strip()
    if ":" in value:
        start = clip.GetClipProperty("Start TC") or "00:00:00:00"
        return tc_to_frames(value, fps) - tc_to_frames(start, fps)
    return round(float(value) * fps)


def read_selects(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("clip") or "").strip()]
    if not rows:
        sys.exit(f"!! no rows in {path}")
    return rows


def log_write(log, action, **data):
    if not log:
        return
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "action": action, **data}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def plan(apply, lines):
    head = "APPLY" if apply else "DRY-RUN (add --apply to execute)"
    print(f"== {head}")
    for line in lines:
        print("  " + line)


# ---------- read commands ----------

def cmd_status(resolve, a):
    print(f"Resolve: {resolve.GetProductName()} {resolve.GetVersionString()}")
    print(f"Page: {resolve.GetCurrentPage()}")
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if proj:
        tl = proj.GetCurrentTimeline()
        print(f"Project: {proj.GetName()} · timelines: {proj.GetTimelineCount()}"
              f" · current: {tl.GetName() if tl else '-'}")
        print(f"Timeline res/fps: {proj.GetSetting('timelineResolutionWidth')}x"
              f"{proj.GetSetting('timelineResolutionHeight')} @ {proj.GetSetting('timelineFrameRate')}")


def cmd_projects(resolve, a):
    pm = resolve.GetProjectManager()
    print(f"Folder: {pm.GetCurrentFolder()}")
    for name in pm.GetProjectListInCurrentFolder() or []:
        print(f"  {name}")
    for sub in pm.GetFolderListInCurrentFolder() or []:
        print(f"  [{sub}/]")


def cmd_api(resolve, a):
    """Introspect what this Resolve build exposes (v21 adds methods; compare with README)."""
    pm, proj = project_of(resolve)
    objs = {"Resolve": resolve, "ProjectManager": pm, "Project": proj,
            "MediaPool": proj.GetMediaPool(), "Timeline": proj.GetCurrentTimeline()}
    tl = objs["Timeline"]
    if tl:
        items = tl.GetItemListInTrack("video", 1) or []
        if items:
            objs["TimelineItem"] = items[0]
            g = getattr(items[0], "GetNodeGraph", None)
            if g:
                objs["Graph"] = g()
    for name, obj in objs.items():
        if obj is None:
            continue
        methods = sorted(m for m in dir(obj) if m[:1].isupper())
        print(f"{name} ({len(methods)}): {', '.join(methods)}")


def cmd_clips(resolve, a):
    _, proj = project_of(resolve)
    props = ["File Path", "Resolution", "FPS", "Duration", "Start TC", "Video Codec",
             "Audio Ch", "Date Created"]
    rows = []
    for path, clip in all_clips(proj.GetMediaPool(), a.bin):
        p = clip.GetClipProperty() or {}
        rows.append({"bin": path, "clip": clip.GetName(), **{k: p.get(k, "") for k in props}})
    if a.csv:
        Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["bin", "clip"])
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} clips -> {a.csv}")
    else:
        for r in rows:
            print(f"{r['bin']}/{r['clip']} · {r['Resolution']} · {r['FPS']} · {r['Duration']}")
        print(f"{len(rows)} clips")


def cmd_timelines(resolve, a):
    _, proj = project_of(resolve)
    for i in range(1, proj.GetTimelineCount() + 1):
        tl = proj.GetTimelineByIndex(i)
        print(f"  {i}. {tl.GetName()} · V{tl.GetTrackCount('video')} A{tl.GetTrackCount('audio')}"
              f" · {tl.GetStartTimecode()}–{tl.GetEndFrame() - tl.GetStartFrame()}f")


# ---------- write commands (add-only) ----------

def cmd_markers_from_csv(resolve, a):
    _, proj = project_of(resolve)
    idx = clip_index(proj.GetMediaPool())
    rows, lines, todo = read_selects(a.csv), [], []
    for r in rows:
        clip = idx.get(r["clip"].strip())
        if clip is None:
            lines.append(f"SKIP {r['clip']}: not in media pool")
            continue
        start = to_source_frame(r["in"], clip)
        dur = max(1, to_source_frame(r["out"], clip) - start)
        ring = (r.get("ring") or "").strip()
        color = RING_COLORS.get(ring, "Cream")
        name = f"H{ring} {r.get('speaker', '')}".strip() if ring else (r.get("speaker") or "select")
        note = (r.get("quote") or "")[:240]
        todo.append((clip, start, color, name, note, dur, r))
        lines.append(f"{r['clip']} @{start}f +{dur}f {color} '{name}': {note[:60]}")
    plan(a.apply, lines)
    if not a.apply:
        return
    ok = 0
    for clip, start, color, name, note, dur, r in todo:
        if clip.GetMarkerByCustomData(f"sel:{start}"):
            continue  # idempotent: same marker already there
        if clip.AddMarker(start, color, name, note, dur, f"sel:{start}"):
            ok += 1
    log_write(a.log, "markers-from-csv", project=proj.GetName(), csv=a.csv, added=ok)
    print(f"added {ok} markers")


def cmd_timeline_from_csv(resolve, a):
    _, proj = project_of(resolve)
    mp = proj.GetMediaPool()
    existing = {proj.GetTimelineByIndex(i).GetName() for i in range(1, proj.GetTimelineCount() + 1)}
    if a.name in existing:
        sys.exit(f"!! timeline '{a.name}' exists; pick a new name (never overwritten)")
    idx = clip_index(mp)
    infos, lines = [], []
    for r in read_selects(a.csv):
        clip = idx.get(r["clip"].strip())
        if clip is None:
            lines.append(f"SKIP {r['clip']}: not in media pool")
            continue
        s, e = to_source_frame(r["in"], clip), to_source_frame(r["out"], clip)
        if e <= s:
            lines.append(f"SKIP {r['clip']}: out <= in")
            continue
        infos.append({"mediaPoolItem": clip, "startFrame": s, "endFrame": e - 1})
        lines.append(f"{r['clip']} [{s}-{e}] {(r.get('quote') or '')[:60]}")
    lines.insert(0, f"new timeline '{a.name}' with {len(infos)} ranges")
    plan(a.apply, lines)
    if not a.apply or not infos:
        return
    tl = mp.CreateEmptyTimeline(a.name)
    if not tl:
        sys.exit("!! CreateEmptyTimeline failed")
    proj.SetCurrentTimeline(tl)
    items = mp.AppendToTimeline(infos) or []
    log_write(a.log, "timeline-from-csv", project=proj.GetName(), timeline=a.name,
              csv=a.csv, ranges=len(infos), appended=len(items))
    print(f"timeline '{a.name}': appended {len(items)}/{len(infos)}")


def find_timeline(proj, name):
    if not name:
        return proj.GetCurrentTimeline()
    for i in range(1, proj.GetTimelineCount() + 1):
        tl = proj.GetTimelineByIndex(i)
        if tl.GetName() == name:
            return tl
    sys.exit(f"!! timeline '{name}' not found")


def cmd_snapshot(resolve, a):
    """Version record: timeline -> OTIO + EDL, project -> .drp, all with a timestamp (never overwrites)."""
    pm, proj = project_of(resolve)
    tl = find_timeline(proj, a.timeline)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    out = Path(a.out)
    safe = tl.GetName().replace("/", "-")
    targets = [
        (out / f"{stamp}_{safe}.otio", "EXPORT_OTIO"),
        (out / f"{stamp}_{safe}.edl", "EXPORT_EDL"),
    ]
    drp = out / f"{stamp}_{proj.GetName().replace('/', '-')}.drp"
    plan(a.apply, [str(p) for p, _ in targets] + [str(drp)])
    if not a.apply:
        return
    out.mkdir(parents=True, exist_ok=True)
    for p, kind in targets:
        if p.exists():
            sys.exit(f"!! {p} exists")
        const = getattr(resolve, kind, None)
        sub = resolve.EXPORT_NONE if kind == "EXPORT_EDL" else None
        ok = tl.Export(str(p), const, sub) if sub is not None else tl.Export(str(p), const)
        print(f"{'ok' if ok else 'FAIL'} {p.name}")
    ok = pm.ExportProject(proj.GetName(), str(drp), False)
    print(f"{'ok' if ok else 'FAIL'} {drp.name}")
    log_write(a.log or str(out / "log.jsonl"), "snapshot", project=proj.GetName(),
              timeline=tl.GetName(), out=str(out))


def cmd_render(resolve, a):
    _, proj = project_of(resolve)
    tl = find_timeline(proj, a.timeline)
    out = Path(a.out)
    presets = [p if isinstance(p, str) else p.get("Name") for p in (proj.GetRenderPresetList() or [])]
    if a.preset not in presets:
        sys.exit(f"!! preset '{a.preset}' not found. Available: {', '.join(map(str, presets))}")
    hits = list(out.glob(f"{a.file}.*")) if out.exists() else []
    if hits:
        sys.exit(f"!! {hits[0]} exists; pick a new --file (never overwritten)")
    plan(a.apply, [f"timeline '{tl.GetName()}' preset '{a.preset}' -> {out / a.file}.*"])
    if not a.apply:
        return
    out.mkdir(parents=True, exist_ok=True)
    proj.SetCurrentTimeline(tl)
    proj.LoadRenderPreset(a.preset)
    proj.SetRenderSettings({"TargetDir": str(out), "CustomName": a.file})
    job = proj.AddRenderJob()
    if not job:
        sys.exit("!! AddRenderJob failed")
    proj.StartRendering([job], False)
    log_write(a.log or str(out / "render-log.jsonl"), "render", project=proj.GetName(),
              timeline=tl.GetName(), preset=a.preset, job=job, file=a.file)
    print(f"render started: job {job} -> {out}")


# ---------- cli ----------

def main():
    ap = argparse.ArgumentParser(prog="resolve-ctl", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("status", "projects", "api", "timelines"):
        sub.add_parser(name)
    p = sub.add_parser("clips")
    p.add_argument("--bin")
    p.add_argument("--csv")
    for name in ("markers-from-csv", "timeline-from-csv"):
        p = sub.add_parser(name)
        p.add_argument("csv")
        p.add_argument("--apply", action="store_true")
        p.add_argument("--log")
        if name == "timeline-from-csv":
            p.add_argument("--name", required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("--out", required=True)
    p.add_argument("--timeline")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--log")
    p = sub.add_parser("render")
    p.add_argument("--preset", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--timeline")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--log")
    a = ap.parse_args()
    resolve = connect()
    fn = globals()["cmd_" + a.cmd.replace("-", "_")]
    fn(resolve, a)


if __name__ == "__main__":
    main()
