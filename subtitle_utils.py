from subtitle.video_caption import Subtitle
from subtitle.generic import Style
import os
from pathlib import Path


def file_ext(file):
    return Path(file).suffix


def change_ext(file, new_ext):
    file_path = Path(file)
    return file_path.with_suffix(new_ext)


def to_smi_timestamp(total_seconds):
    return str(int(total_seconds * 1000))


def to_srt_timestamp(total_seconds):
    hours = int(total_seconds / 3600)
    minutes = int(total_seconds / 60 - hours * 60)
    seconds = int(total_seconds - hours * 3600 - minutes * 60)
    milliseconds = round((total_seconds - seconds - hours * 3600 - minutes * 60)*1000)

    return '{:02d}:{:02d}:{:02d},{:03d}'.format(hours, minutes, seconds, milliseconds)


def subtitle_captions(file):
    ext = file_ext(file)
    if ext == '.srt':
        captions = Subtitle().from_srt(file)
    elif ext == '.sbv':
        captions = Subtitle().from_sbv(file)
    elif ext == '.vtt':
        captions = Subtitle().from_vtt(file)
    elif ext == '.smi' or ext == '.sami':
        captions = Subtitle().from_smi(file)
    else:
        raise Exception('Unknown subtitle format - {}'.format(ext))

    times = []
    texts = []
    for caption in captions:
        times.append([caption.start, caption.end])
        texts.append(caption.text)

    return texts, times


def _normalize(content):
    content = content.replace('\n', ' ')
    content = content.strip()
    return content


def save_to_smi(file, times, source, target, both='False', extension='smi'):
    smi_style = """
    <STYLE TYPE="text/css">
    <!--
    P { margin-left:8pt; margin-right:8pt; margin-bottom:2pt;
        margin-top:2pt; font-size:20pt; text-align:center;
        font-family:arial, sans-serif; font-weight:normal; color:white;
        }
    .KRCC {Name:Korean; lang:ko-KR; SAMIType:CC;}
    .ENCC {Name:English; lang:EN-US; SAMIType:CC;}
    -->
    </STYLE>
    """
    style = Style()
    style.lines = smi_style
    subtitle = Subtitle(styles=style)
    for time, src, tgt in zip(times, source, target):
        if both.lower() == 'true':
            subtitle.add(time[0], time[1], '<P class=KRCC>{}</P><BR><P class=ENCC>{}'.format(tgt, _normalize(src)))
        else:
            subtitle.add(time[0], time[1], tgt)
    return subtitle.save_as_smi(file, extension)


def save_to_srt(filename, texts, times):
    subtitle = Subtitle()
    for time, text in zip(times, texts):
        if (text == "&nbsp;") or (not text.strip()):
            continue
        text = text.replace('<br>', '\n')
        subtitle.add(time[0], time[1], text)

    return subtitle.save_as_srt(filename)


def save_as_srt(filename, captions):
    subtitle = Subtitle()
    for caption in captions:
        if caption.text == "&nbsp;":
            continue
        subtitle.add(caption.start, caption.end, caption.text)

    return subtitle.save_as_srt(filename)


def save_to_vtt(filename, texts, times):
    subtitle = Subtitle()
    for time, text in zip(times, texts):
        if (text == "&nbsp;") or (not text.strip()):
            continue
        text = text.replace('<br>', '\n')
        subtitle.add(time[0], time[1], text)

    return subtitle.save_as_vtt(filename)
