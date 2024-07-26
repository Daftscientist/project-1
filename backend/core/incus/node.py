from dataclasses import dataclass
import json
import uuid
import aiohttp
import yaml

from core.incus.instance import IncusInstance
from core.incus.limits import IncusLimits


@dataclass
class IncusNode:
    """
    This class is used to represent a node or an Incus server.

    Args:
        node_id (int): The ID of the node.
        name (str): The name of the node.
        description (str): The description of the node.
        location (str): The location of the node.
        REST_endpoint_url (str): The REST endpoint URL of the node.
        bearer (str): The bearer token for the node.
        os_type (str): The OS type of the node.
    """
    node_id: int
    name: str
    description: str
    location: str
    REST_endpoint_url: str
    bearer: str
    os_type: str

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer}'
    }

    def _to_dict(self):
        return {
            'node_id': self.node_id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'REST_endpoint_url': self.REST_endpoint_url
        }

    async def get_resources(self):
        """
        This function is used to get the resources of the node.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/resources',
                                   headers=self.headers) as response:
                return await response.json()

    async def create_instance_oci(self, chicken: str, name: str, description: str, owner_id: int, limits: IncusLimits):
        """
        This function is used to create an OCI instance on the node.

        Args:
            chicken (str): The chicken to create the instance from.
            name (str): The name of the instance.
            description (str): The description of the instance.
            owner_id (int): The ID of the owner of the instance.
            limits (IncusLimits): The limits for the instance.
        """

        ## turn chicken yml string to dict
        chicken_dict = yaml.safe_load(chicken)

        instance_uuid = str(uuid.uuid4())

        ## take image from chicken and split it to server and alias
        image = chicken_dict['image']
        image = image.split('/', 1)

        payload = {
            "name": instance_uuid,  # Use the UUID as the instance name
            "source": {
                "type": "image",
                "alias": image[1],  # Using the docker image `python` from the Docker registry
                "protocol": "oci",
                "server": image[0]
            },
        "profiles": ["default"],
        "config": {
            "limits.cpu": limits.cpu,
            "limits.memory": limits.memory,
            "limits.disk": limits.disk,
            "limits.swap": limits.swap,
            "limits.io": limits.io,
            "volatile.metadata": json.dumps({
                "name": name,
                "description": description,
                "owner_id": owner_id            
            }),
            "user.user-data": f"#cloud-config runcmd: {chicken_dict.get('scripts', {}).get('startup', '')}",
            "user.vendor-data": f"#cloud-config runcmd: {chicken_dict.get('scripts', {}).get('install', '')}"
        },
        "devices": {
            "root": {
                "type": "disk",
                "pool": "default",
                "path": "/",
            }
        },
        "environment": {
            item['env_name']: item['default_value'] for item in chicken_dict['env_variables']
        }
    }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.REST_endpoint_url}/instances',
                                     json=payload, headers=self.headers) as response:
                return await response.json()

    async def get_instance(self, instance_id: str):
        """
        This function is used to get an instance from the node.

        Args:
            instance_id (str): The ID of the instance to get.
        
        Returns:
            IncusInstance: The instance object.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances/{instance_id}',
                                   headers=self.headers) as response:
                instance = await response.json()

                return IncusInstance(
                    instance_id=instance['id'],
                    name=instance['metadata']['name'],
                    description=instance['metadata']['description'],
                    owner_id=instance['metadata']['owner_id'],
                    limits=IncusLimits(
                        cpu=instance['metadata']['limits']['cpu'],
                        memory=instance['metadata']['limits']['memory'],
                        disk=instance['metadata']['limits']['disk'],
                        swap=instance['metadata']['limits']['swap'],
                        io=instance['metadata']['limits']['io']
                    ),
                    node_id=self.node_id,
                    status=instance['status'],
                    ip=instance['ip'],
                    port=instance['port']
                )
            
    async def get_instances(self):
        """
        This function is used to get all instances from the node.

        Returns:
            list: A list of incus instance internal URLs objects.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances',
                                   headers=self.headers) as response:
                instances = await response.json()

                return instances
"""                return [IncusInstance(
                    instance_id=instance['id'],
                    name=instance['metadata']['name'],
                    description=instance['metadata']['description'],
                    owner_id=instance['metadata']['owner_id'],
                    limits=IncusLimits(
                        cpu=instance['metadata']['limits']['cpu'],
                        memory=instance['metadata']['limits']['memory'],
                        disk=instance['metadata']['limits']['disk'],
                        swap=instance['metadata']['limits']['swap'],
                        io=instance['metadata']['limits']['io']
                    ),
                    node_id=self.node_id,
                    status=instance['status'],
                    ip=instance['ip'],
                    port=instance['port']
                ) for instance in instances]"""
