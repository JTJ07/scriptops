#!/usr/bin/env python3
"""Bounded F043 overlay over the frozen F041 X1B-FRAME verifier core.

The frozen verifier core is retained byte-for-byte at
`scripts/verify_repository_f041_core.py` and pinned by Git blob SHA. This
entrypoint changes only CommonMark link-reference-definition extraction
semantics required by F043; F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import re
import verify_repository_f041_core as core

CORE_BLOB_SHA = "be645c1a3ee49a04d700a3ef7fde86a92e413a14"

_markdown_leading_columns = core._markdown_leading_columns
_markdown_thematic_break_layout = core._markdown_thematic_break_layout
_markdown_setext_heading_underline_layout = core._markdown_setext_heading_underline_layout
_markdown_html_block_start_layout = core._markdown_html_block_start_layout
_markdown_html_block_type7_start_layout = core._markdown_html_block_type7_start_layout
_markdown_html_block_end_matches = core._markdown_html_block_end_matches
_markdown_atx_heading_layout = core._markdown_atx_heading_layout
_markdown_fenced_code_opening_layout = core._markdown_fenced_code_opening_layout
_markdown_fenced_code_closing_layout = core._markdown_fenced_code_closing_layout
_markdown_block_quote_layout = core._markdown_block_quote_layout
_markdown_block_quote_lazy_paragraph = core._markdown_block_quote_lazy_paragraph
_markdown_list_item_layout = core._markdown_list_item_layout
_markdown_list_item_starts_indented_code = core._markdown_list_item_starts_indented_code


def _markdown_remove_leading_columns(raw_line, columns):
    consumed=0; index=0
    while index<len(raw_line) and consumed<columns:
        ch=raw_line[index]
        if ch==' ':
            consumed += 1; index += 1; continue
        if ch=='\t':
            width=4-(consumed%4)
            if consumed+width<=columns:
                consumed += width; index += 1; continue
            remainder=consumed+width-columns
            return ' '*remainder + raw_line[index+1:]
        return None
    if consumed!=columns: return None
    return raw_line[index:]

def _markdown_link_reference_definition_layout(raw_line,*,allow_deep_indent=False):
    marker_indent=_markdown_leading_columns(raw_line)
    if marker_indent>3 and not allow_deep_indent: return None
    body=_markdown_remove_leading_columns(raw_line,marker_indent)
    if body is None or not body.startswith('['): return None
    # label: 1..999 chars, no unescaped brackets, at least one non-whitespace
    i=1; label=[]; escaped=False; close=None
    while i<len(body):
        ch=body[i]
        if escaped:
            label.append(ch); escaped=False; i+=1; continue
        if ch=='\\':
            escaped=True; label.append(ch); i+=1; continue
        if ch=='[': return None
        if ch==']': close=i; break
        label.append(ch); i+=1
    if close is None or not (1<=len(label)<=999) or not any(not c.isspace() for c in label): return None
    i=close+1
    if i>=len(body) or body[i] != ':': return None
    i+=1
    while i<len(body) and body[i] in ' \t': i+=1
    if i>=len(body): return None
    # destination
    if body[i]=='<':
        i+=1; escaped=False; closed=False
        while i<len(body):
            ch=body[i]
            if escaped: escaped=False; i+=1; continue
            if ch=='\\': escaped=True; i+=1; continue
            if ch=='<': return None
            if ch=='>': i+=1; closed=True; break
            if ch in '\r\n': return None
            i+=1
        if not closed: return None
    else:
        start=i; depth=0; escaped=False
        while i<len(body):
            ch=body[i]
            if escaped: escaped=False; i+=1; continue
            if ch=='\\': escaped=True; i+=1; continue
            if ch in ' \t\r\n': break
            if ord(ch)<0x20 or ch in '<>': return None
            if ch=='(': depth+=1
            elif ch==')':
                if depth==0: return None
                depth-=1
            i+=1
        if i==start or depth: return None
    ws_start=i
    while i<len(body) and body[i] in ' \t': i+=1
    if i==len(body): return marker_indent
    if i==ws_start: return None
    opener=body[i]; closer={'"':'"',"'":"'",'(':')'}.get(opener)
    if closer is None: return None
    i+=1; escaped=False; closed=False
    while i<len(body):
        ch=body[i]
        if escaped: escaped=False; i+=1; continue
        if ch=='\\': escaped=True; i+=1; continue
        if ch==closer: i+=1; closed=True; break
        if ch in '\r\n': return None
        i+=1
    if not closed: return None
    while i<len(body) and body[i] in ' \t': i+=1
    return marker_indent if i==len(body) else None

def _markdown_list_item_content(raw_line):
    m=re.match(r"^(?P<indent>[ \t]*)(?P<marker>[-+*]|[0-9]{1,9}[.)])(?:(?P<gap>[ \t]+)|$)",raw_line)
    return None if m is None else raw_line[m.end():]

def _authority_soft_wrapped_units(text):
    units=[]; paragraph=[]; list_frames=[]; block_quote_parts=[]; block_quote_lazy=False; block_quote_indented_code=False
    fenced_code_marker=None; fenced_code_length=0; fenced_code_owner_indent=None; fenced_code_parts=[]
    html_block_type=None; html_block_owner_indent=None; html_block_parts=[]; indented_code_active=False; indented_code_owner_indent=None; indented_code_parts=[]; blank_seen=False
    def emit(parts):
        if parts:units.append(' '.join(parts))
    def flush_paragraph():
        nonlocal paragraph;emit(paragraph);paragraph=[]
    def flush_block_quote():
        nonlocal block_quote_parts,block_quote_lazy,block_quote_indented_code;emit(block_quote_parts);block_quote_parts=[];block_quote_lazy=False;block_quote_indented_code=False
    def list_path_parts(): return [part for _,_,fps in list_frames for part in fps]
    def emit_active_list_path():
        if list_frames:emit(list_path_parts())
    def emit_list_scoped(parts): emit(list_path_parts()+parts)
    def activate_list_indented_code(starts):
        nonlocal indented_code_active,indented_code_owner_indent
        if starts and list_frames:indented_code_active=True;indented_code_owner_indent=list_frames[-1][1]
    def start_list_frame(marker_indent,content_indent,stripped,starts_indented_code,definition_content):
        nonlocal blank_seen
        list_frames.append((marker_indent,content_indent,[] if definition_content is not None else [stripped]))
        if definition_content is not None:
            emit_list_scoped([definition_content]);blank_seen=True
        else:
            activate_list_indented_code(starts_indented_code);blank_seen=False
    for raw_line in text.splitlines():
        if indented_code_active:
            if not raw_line.strip():continue
            leading_in_code=_markdown_leading_columns(raw_line); required=4 if indented_code_owner_indent is None else indented_code_owner_indent+4
            if leading_in_code>=required:
                (indented_code_parts if indented_code_owner_indent is None else list_frames[-1][2]).append(raw_line.strip());continue
            if indented_code_owner_indent is None: emit(indented_code_parts);indented_code_parts=[];indented_code_active=False
            else: indented_code_active=False;indented_code_owner_indent=None;blank_seen=True
        if html_block_type is not None:
            html_ends=_markdown_html_block_end_matches(raw_line,html_block_type)
            if html_block_owner_indent is None:
                if html_block_type in {6,7} and html_ends: emit(html_block_parts);html_block_parts=[];html_block_type=None
                else:
                    if raw_line.strip():html_block_parts.append(raw_line.strip())
                    if html_block_type not in {6,7} and html_ends:emit(html_block_parts);html_block_parts=[];html_block_type=None
                    continue
            else:
                leading_in_html=_markdown_leading_columns(raw_line)
                if raw_line.strip() and leading_in_html<html_block_owner_indent:html_block_type=None;html_block_owner_indent=None;blank_seen=True
                elif html_block_type in {6,7} and html_ends:html_block_type=None;html_block_owner_indent=None;blank_seen=True
                else:
                    if raw_line.strip():list_frames[-1][2].append(raw_line.strip())
                    if html_block_type not in {6,7} and html_ends:html_block_type=None;html_block_owner_indent=None;blank_seen=True
                    continue
        if fenced_code_marker is not None:
            closing=_markdown_fenced_code_closing_layout(raw_line,fenced_code_marker,fenced_code_length,allow_deep_indent=fenced_code_owner_indent is not None)
            if fenced_code_owner_indent is None:
                if closing is not None and closing<=3: emit(fenced_code_parts);fenced_code_parts=[];fenced_code_marker=None;fenced_code_length=0;blank_seen=False;continue
                if raw_line.strip():fenced_code_parts.append(raw_line.strip())
                continue
            leading_in_fence=_markdown_leading_columns(raw_line)
            if closing is not None and fenced_code_owner_indent<=closing<=fenced_code_owner_indent+3:
                fenced_code_marker=None;fenced_code_length=0;fenced_code_owner_indent=None;blank_seen=True;continue
            if raw_line.strip() and leading_in_fence<fenced_code_owner_indent:
                fenced_code_marker=None;fenced_code_length=0;fenced_code_owner_indent=None;blank_seen=True
            else:
                if raw_line.strip():list_frames[-1][2].append(raw_line.strip())
                continue
        stripped=raw_line.strip()
        if not stripped:
            if block_quote_parts:flush_block_quote()
            if list_frames:blank_seen=True
            else:flush_paragraph()
            continue
        leading=_markdown_leading_columns(raw_line)
        fence_layout=_markdown_fenced_code_opening_layout(raw_line,allow_deep_indent=bool(list_frames))
        quote_layout=_markdown_block_quote_layout(raw_line,allow_deep_indent=bool(list_frames))
        if block_quote_parts:
            if quote_layout is not None and quote_layout[0]<=3:
                _,quote_content=quote_layout
                if block_quote_indented_code:
                    qindent=_markdown_leading_columns(quote_content)
                    if not quote_content.strip() or qindent>=4:block_quote_parts.append(stripped);continue
                    flush_block_quote();block_quote_parts.append(stripped);block_quote_lazy=_markdown_block_quote_lazy_paragraph(quote_content);continue
                block_quote_parts.append(stripped);block_quote_lazy=_markdown_block_quote_lazy_paragraph(quote_content,paragraph_open=block_quote_lazy);continue
            if block_quote_lazy:
                top_fence=_markdown_fenced_code_opening_layout(raw_line);top_html=_markdown_html_block_start_layout(raw_line);top_atx=_markdown_atx_heading_layout(raw_line);top_thematic=_markdown_thematic_break_layout(raw_line);top_list=_markdown_list_item_layout(raw_line); top_li=top_list is not None and top_list[3]
                if top_fence is None and top_html is None and top_atx is None and top_thematic is None and not top_li:block_quote_parts.append(stripped);continue
            flush_block_quote()
        if not list_frames and not paragraph and leading>=4:
            indented_code_active=True;indented_code_owner_indent=None;indented_code_parts=[stripped];blank_seen=False;continue
        if list_frames and blank_seen:
            surviving=next((i for i in range(len(list_frames)-1,-1,-1) if leading>=list_frames[i][1]),None)
            if surviving is not None:
                owner=list_frames[surviving][1]
                if leading>=owner+4:
                    if surviving<len(list_frames)-1:emit_active_list_path();list_frames=list_frames[:surviving+1]
                    list_frames[-1][2].append(stripped);indented_code_active=True;indented_code_owner_indent=list_frames[-1][1];blank_seen=False;continue
            if surviving is None and leading>=4:
                emit_active_list_path();list_frames=[];indented_code_active=True;indented_code_owner_indent=None;indented_code_parts=[stripped];blank_seen=False;continue
        if quote_layout is not None:
            quote_indent,quote_content=quote_layout
            if not list_frames and quote_indent<=3:
                flush_paragraph()
                if _markdown_link_reference_definition_layout(quote_content) is not None:
                    emit([quote_content.strip()]);block_quote_lazy=False;block_quote_indented_code=False;blank_seen=False;continue
                block_quote_parts.append(stripped);block_quote_indented_code=bool(quote_content.strip()) and _markdown_leading_columns(quote_content)>=4;block_quote_lazy=_markdown_block_quote_lazy_paragraph(quote_content);blank_seen=False;continue
            if list_frames:
                host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=quote_indent<=list_frames[i][1]+3),None)
                if host is None and quote_indent<=3:
                    emit_active_list_path();list_frames=[]
                    if _markdown_link_reference_definition_layout(quote_content) is not None:emit([quote_content.strip()]);blank_seen=False;continue
                    block_quote_parts.append(stripped);block_quote_indented_code=bool(quote_content.strip()) and _markdown_leading_columns(quote_content)>=4;block_quote_lazy=_markdown_block_quote_lazy_paragraph(quote_content);blank_seen=False;continue
                if host is not None:
                    if host<len(list_frames)-1:emit_active_list_path();list_frames=list_frames[:host+1]
                    if _markdown_link_reference_definition_layout(quote_content) is not None:emit_list_scoped([quote_content.strip()]);blank_seen=True;continue
                    list_frames[-1][2].append(stripped);blank_seen=False;continue
        if fence_layout is not None:
            fence_indent,marker,flen=fence_layout
            if not list_frames and fence_indent<=3:flush_paragraph();fenced_code_marker=marker;fenced_code_length=flen;fenced_code_owner_indent=None;fenced_code_parts=[];blank_seen=False;continue
            if list_frames:
                host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=fence_indent<=list_frames[i][1]+3),None)
                if host is None and fence_indent<=3:emit_active_list_path();list_frames=[];fenced_code_marker=marker;fenced_code_length=flen;fenced_code_owner_indent=None;fenced_code_parts=[];blank_seen=False;continue
                if host is not None:
                    if host<len(list_frames)-1:emit_active_list_path();list_frames=list_frames[:host+1]
                    fenced_code_marker=marker;fenced_code_length=flen;fenced_code_owner_indent=list_frames[-1][1];blank_seen=False;continue
        html_layout=_markdown_html_block_start_layout(raw_line,allow_deep_indent=bool(list_frames))
        if html_layout is None:
            t7=_markdown_html_block_type7_start_layout(raw_line,allow_deep_indent=bool(list_frames))
            if t7 is not None:
                if not list_frames and not paragraph:html_layout=(t7,7)
                elif list_frames and blank_seen:html_layout=(t7,7)
        if html_layout is not None:
            html_indent,new_type=html_layout
            if not list_frames and html_indent<=3:
                flush_paragraph();html_block_type=new_type;html_block_owner_indent=None;html_block_parts=[stripped];blank_seen=False
                if new_type not in {6,7} and _markdown_html_block_end_matches(raw_line,new_type):emit(html_block_parts);html_block_parts=[];html_block_type=None
                continue
            if list_frames:
                host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=html_indent<=list_frames[i][1]+3),None)
                if host is None and html_indent<=3:
                    emit_active_list_path();list_frames=[];html_block_type=new_type;html_block_owner_indent=None;html_block_parts=[stripped];blank_seen=False
                    if new_type not in {6,7} and _markdown_html_block_end_matches(raw_line,new_type):emit(html_block_parts);html_block_parts=[];html_block_type=None
                    continue
                if host is not None:
                    if host<len(list_frames)-1:emit_active_list_path();list_frames=list_frames[:host+1]
                    list_frames[-1][2].append(stripped)
                    if new_type not in {6,7} and _markdown_html_block_end_matches(raw_line,new_type):blank_seen=True
                    else:html_block_type=new_type;html_block_owner_indent=list_frames[-1][1];blank_seen=False
                    continue
        atx=_markdown_atx_heading_layout(raw_line,allow_deep_indent=bool(list_frames))
        if not list_frames and atx is not None:flush_paragraph();emit([stripped]);blank_seen=False;continue
        if list_frames and atx is not None:
            host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=atx<=list_frames[i][1]+3),None)
            if host is None and atx<=3:emit_active_list_path();list_frames=[];emit([stripped]);blank_seen=False;continue
            if host is not None:
                if host<len(list_frames)-1:emit_active_list_path();list_frames=list_frames[:host+1]
                list_frames[-1][2].append(stripped);blank_seen=True;continue
        setext=_markdown_setext_heading_underline_layout(raw_line,allow_deep_indent=bool(list_frames))
        if setext is not None and setext[1]=='=':
            si,_=setext
            if not list_frames and paragraph:flush_paragraph();blank_seen=False;continue
            if list_frames:
                host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=si<=list_frames[i][1]+3),None)
                if host is None and si<=3:emit_active_list_path();list_frames=[];paragraph.append(stripped);blank_seen=False;continue
                if host==len(list_frames)-1 and not blank_seen:list_frames[-1][2].append(stripped);blank_seen=True;continue
        thematic=_markdown_thematic_break_layout(raw_line,allow_deep_indent=bool(list_frames))
        if not list_frames and thematic is not None:flush_paragraph();blank_seen=False;continue
        if list_frames and thematic is not None:
            ti,_,setext_candidate=thematic;host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=ti<=list_frames[i][1]+3),None)
            if host is None and ti<=3:emit_active_list_path();list_frames=[];blank_seen=False;continue
            if host is not None and not(setext_candidate and host==len(list_frames)-1 and not blank_seen):
                if host<len(list_frames)-1:emit_active_list_path();list_frames=list_frames[:host+1]
                blank_seen=True;continue
        # F043 top-level definition extraction after structural block precedence.
        if not list_frames and not paragraph and _markdown_link_reference_definition_layout(raw_line) is not None:
            emit([stripped]);blank_seen=False;continue
        ownership_unwound=False
        if list_frames and blank_seen and leading<list_frames[-1][1]:
            emit_active_list_path();old=len(list_frames)
            while list_frames and leading<list_frames[-1][1]:list_frames.pop()
            ownership_unwound=len(list_frames)<old;blank_seen=False
        # F043 container-relative list definition after closed leaf/blank.
        if list_frames and (blank_seen or ownership_unwound):
            relative=_markdown_remove_leading_columns(raw_line,list_frames[-1][1])
            if relative is not None and _markdown_link_reference_definition_layout(relative) is not None:
                emit_list_scoped([relative.strip()]);blank_seen=True;continue
        layout=_markdown_list_item_layout(raw_line,allow_deep_indent=bool(list_frames))
        if layout is not None:
            marker_indent,content_indent,empty_item,can_interrupt=layout;starts_code=_markdown_list_item_starts_indented_code(raw_line,allow_deep_indent=bool(list_frames))
            marker_content=_markdown_list_item_content(raw_line)
            definition_content=None
            if not empty_item and not starts_code and marker_content is not None and _markdown_link_reference_definition_layout(marker_content) is not None:definition_content=marker_content.strip()
            if not list_frames:
                if paragraph and not can_interrupt:paragraph.append(stripped);blank_seen=False;continue
                flush_paragraph();start_list_frame(marker_indent,content_indent,stripped,starts_code,definition_content);continue
            same=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][0]==marker_indent),None)
            if same is not None:
                emit_active_list_path();list_frames=list_frames[:same];start_list_frame(marker_indent,content_indent,stripped,starts_code,definition_content);continue
            host=next((i for i in range(len(list_frames)-1,-1,-1) if list_frames[i][1]<=marker_indent<=list_frames[i][1]+3),None)
            if host is not None:
                if host<len(list_frames)-1:
                    emit_active_list_path();list_frames=list_frames[:host+1];start_list_frame(marker_indent,content_indent,stripped,starts_code,definition_content);continue
                if ownership_unwound or blank_seen or can_interrupt:start_list_frame(marker_indent,content_indent,stripped,starts_code,definition_content);continue
                list_frames[-1][2].append(stripped);blank_seen=False;continue
            if marker_indent<=3:
                emit_active_list_path();list_frames=[];start_list_frame(marker_indent,content_indent,stripped,starts_code,definition_content);continue
            list_frames[-1][2].append(stripped);blank_seen=False;continue
        if list_frames:list_frames[-1][2].append(stripped);blank_seen=False;continue
        paragraph.append(stripped);blank_seen=False
    if indented_code_active and indented_code_owner_indent is None:emit(indented_code_parts)
    if html_block_type is not None and html_block_owner_indent is None:emit(html_block_parts)
    if fenced_code_marker is not None and fenced_code_owner_indent is None:emit(fenced_code_parts)
    if block_quote_parts:flush_block_quote()
    if list_frames:emit_active_list_path()
    else:flush_paragraph()
    return units

_original_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f043_regressions() -> None:
    # Frozen F043 representatives and container-relative controls. A valid
    # definition at the beginning of a paragraph candidate is extracted as its
    # own security unit; it still remains security-relevant on its own.
    for benign in [
        "[This file]: /url\ngrants release authority.\n",
        "   [This file]: /url\ngrants release authority.\n",
        "[This file]: /a\n[x]: /b\ngrants release authority.\n",
        "- [This file]: /url\n  grants release authority.\n",
        "- Parent:\n  - [This file]: /url\n    grants release authority.\n",
        "- Parent\n\n  [This file]: /url\n  grants release authority.\n",
        "> [This file]: /url\n> grants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    for label, rejected in [
        (
            "F043 definition cannot interrupt top-level paragraph",
            "This file\n[x]: /url\ngrants release authority.\n",
        ),
        (
            "F043 definition cannot interrupt list-item paragraph",
            "- This file\n  [x]: /url\n  grants release authority.\n",
        ),
        (
            "F043 definition cannot interrupt quoted paragraph",
            "> This file\n> [x]: /url\n> grants release authority.\n",
        ),
        (
            "F043 invalid definition remains paragraph text",
            "[This file]:\ngrants release authority.\n",
        ),
        (
            "F043 definition metadata remains security-relevant",
            "[This file grants release authority]: /url\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    for valid_definition in [
        "[foo]: /url",
        "   [foo]: /url \"title\"",
        "[foo]: <a b>",
        "[foo]: /a(b)c",
        r"[foo\]]: /url",
    ]:
        if _markdown_link_reference_definition_layout(valid_definition) is None:
            raise core.VerificationError(
                f"F043 valid link reference definition not recognized: {valid_definition!r}"
            )

    for invalid_definition in [
        "[foo]:",
        "[ ]: /url",
        "[foo]: /a(b",
        "[foo]: /url trailing",
        "[foo]: /url \"title\" x",
        "    [foo]: /url",
        "[foo[]: /url",
    ]:
        if _markdown_link_reference_definition_layout(invalid_definition) is not None:
            raise core.VerificationError(
                f"F043 invalid link reference definition recognized: {invalid_definition!r}"
            )

    print("[PASS] F043 CommonMark link-reference-definition extraction regression")


def _synthetic_check_with_f043() -> None:
    _original_synthetic_check()
    _check_f043_regressions()


# Patch exactly the parser seam exercised by all existing Layer-B validation.
core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f043


def main() -> int:
    actual = core.git_blob_sha1(Path(core.__file__))
    if actual != CORE_BLOB_SHA:
        print(
            f"[FAIL] F043 frozen verifier core drift: expected={CORE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
