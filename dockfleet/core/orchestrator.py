from dockfleet.core.docker import DockerManager
from dockfleet.health.status import (
    mark_service_running,
    mark_service_stopped
)
from dockfleet.health.seed import bootstrap_from_config

class Orchestrator:

    def __init__(self, config):
        self.config = config
        self.docker = DockerManager()
        self.network = "dockfleet_net"

    def container_name(self, service):
        return f"dockfleet_{service}"

    def start_service(self, name, svc):

        container_name = self.container_name(name)
        ports = svc.ports or []

        try:

            self.docker.remove_container(container_name)

            self.docker.run_container(
                image=svc.image,
                name=container_name,
                ports=ports,
                network=self.network
            )

            mark_service_running(name)

            print(f" Started service: {name}")

        except Exception as e:

            print(f" Failed to start {name}")
            print(e)

    def stop_service(self, name):

        container_name = self.container_name(name)

        try:

            self.docker.stop_container(container_name)
            self.docker.remove_container(container_name)

            mark_service_stopped(name)

            print(f" Stopped service: {name}")

        except Exception as e:

            print(f" Failed to stop {name}")
            print(e)

    def restart(self, service_name):

        if service_name not in self.config.services:
            print(f"Service {service_name} not found")
            return

        svc = self.config.services[service_name]

        print(f"Restarting service: {service_name}")

        self.stop_service(service_name)
        self.start_service(service_name, svc)

    def up(self):
        print("Starting services...\n")
        
        bootstrap_from_config(self.config)
        print(" DB bootstrapped & services seeded")
       
        self.docker.create_network(self.network)
        for name, svc in self.config.services.items():
            self.start_service(name, svc)

    def down(self):

        print("Stopping services...\n")

        for name in self.config.services.keys():
            self.stop_service(name)

    def ps(self):

        print("Running containers:\n")

        self.docker.list_containers()