import socket
import time

import panel as pn
from loguru import logger
from snakeviz.cli import main as snakeviz_main

from zorzak.common.files import AnalysisFile
from zorzak.common.threaded_output import ThreadedOutput

_USED_PORTS = set()
_MIN_PORT = 8081
_MAX_PORT = 65535


def _get_unused_port():
    for port in range(_MIN_PORT, _MAX_PORT):
        if port not in _USED_PORTS:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", port)) != 0:
                    _USED_PORTS.add(port)
                    return port
    raise ValueError("No available ports")


def _get_iframe(url: str) -> pn.pane.HTML:
    iframe_html = (
        f'<iframe src="{url}" style="height:100%; width:100%" frameborder="0"></iframe>'
    )

    return pn.pane.HTML(iframe_html, height=800, width=800)


def render_with_snakeviz(pstats_file: AnalysisFile):
    file_path = pstats_file.save_to_temporary_file()
    url_pattern = r"https?:\/\/.+(:[0-9]{4,5})?\/.*"

    with ThreadedOutput(
        target=snakeviz_main,
        args=(str(file_path), "--server", "--port", str(_get_unused_port())),
    ) as stdout:
        while True:
            match = stdout.check_output(url_pattern, timeout=5)
            if match:
                url = match.group()
                logger.debug(f"Found URL '{url}'")
                break
            else:
                time.sleep(0.1)
    frame = _get_iframe(url)
    return frame
