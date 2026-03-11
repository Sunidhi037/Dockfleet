import subprocess
from subprocess import PIPE, STDOUT


def stream_container_logs(container_name: str):
    """
    Stream logs from a Docker container using docker logs -f.
    Yields log lines continuously as they appear.
    """

    process = subprocess.Popen(
        ["docker", "logs", "-f", container_name],
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
        bufsize=1
    )

    try:
        # Read logs line-by-line
        for line in iter(process.stdout.readline, ""):
            yield line.strip()

    except Exception as e:
        yield f"[ERROR] {str(e)}"

    finally:
        # Ensure process is terminated
        process.kill()