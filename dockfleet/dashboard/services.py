import subprocess
import json
from datetime import datetime
from sqlmodel import Session, select
from dockfleet.health.models import Service as DBService, engine


def get_services():
    """
    Combine SQLite service data with docker container status.
    """

    services = {}

    # -------------------------
    # Step 1 — Load from SQLite
    # -------------------------
    with Session(engine) as session:

        db_services = session.exec(select(DBService)).all()

        for svc in db_services:

            services[svc.name] = {
                "name": svc.name,
                "status": svc.status or "unknown",
                "health_status": svc.health_status or "unknown",
                "image": svc.image,
                "ports": svc.ports_raw,
                "restart_policy": svc.restart_policy,
                "restart_count": svc.restart_count,
                "last_health_check": svc.last_health_check,
            }

    # -------------------------
    # Step 2 — Enrich with Docker
    # -------------------------
    try:

        result = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.strip().split("\n"):

            if not line:
                continue

            container = json.loads(line)

            name = container.get("Names")

            if name.startswith("dockfleet_"):
                name = name.replace("dockfleet_", "")

            # if service exists in DB
            if name in services:

                services[name]["status"] = "running"
                services[name]["image"] = container.get("Image")
                services[name]["ports"] = container.get("Ports")

    except Exception as e:

        print("Docker fetch failed:", e)

    return list(services.values())
