import subprocess
import json

def getTracks(video_path):
    """Devuelve TODAS las pistas (video, audio, subs) de un archivo"""

    command = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        video_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE)
    data = json.loads(result.stdout)

    tracks = []

    for stream in data["streams"]:
        track = {
            "from": video_path,
            "index": stream["index"],
            "type": stream["codec_type"],
            "codec": stream.get("codec_name"),
            "language": stream.get("tags", {}).get("language", "unknown"),
            "title": stream.get("tags", {}).get("title", ""),
            "channels": stream.get("channels", None)
        }
        tracks.append(track)

    return tracks

def addSoftSub(video, subtitle, output):

    command = [
        "ffmpeg",
        "-i", video,
        "-i", subtitle,
        "-c", "copy",
        "-c:s", "srt",
        output
    ]

    subprocess.run(command)

def compare_tracks(video1, video2):
    tracks_1 = get_tracks(video1)
    tracks_2 = get_tracks(video2)

    result = {
        "video1": video1,
        "video2": video2,
        "tracks": {
            "video1": tracks_1,
            "video2": tracks_2
        }
    }

    return result


def create_custom_video(video1, video2, selection, output):
    """
    video1, video2    -> rutas de vídeo
    selection      -> array con selección de pistas
    output          -> nombre del nuevo vídeo

    selection = [
        {"file": 1, "type": "video", "id": 0},
        {"file": 1, "type": "audio", "id": 1},
        {"file": 2, "type": "subtitle", "id": 0}
    ]
    """
    streams = []
    videos = selection["video"]
    for video in videos:
        streams = streams + [video["from"],video["index"]]

    audios = selection["audio"]
    for audio in audios:
        streams = streams + [audio["from"]:audio["index"]]

    subs = selection["subtittles"]
    for sub in subs:
        streams = streams + [sub["from"]:sub["index"]]

    cmd = ["ffmpeg"]

    for i in range(len(streams):
        cmd += ["-i", streams[i][0]]
    for i in range(len(streams):
        cmd += ["-map", f"{i}:{streams[i][1]['index']}"]


    # Sin reconvertir, copia directa
    cmd += ["-c", "copy", output]

    print("COMANDO:", " ".join(cmd))
    subprocess.run(cmd)

