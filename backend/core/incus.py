
import json
import uuid
import aiohttp
import yaml
from dataclasses import dataclass

@dataclass
class IncusLimits:
    """
    This class is used to represent the limits of an instance.

    Args:
        cpu (int): The CPU limit.
        memory (int): The memory limit.
        disk (int): The disk limit.
        swap (int): The swap limit.
        io (int): The IO limit
    """
    cpu: int
    memory: int
    disk: int
    swap: int
    io: int

    def to_dict(self):
        return {
            'cpu': self.cpu,
            'memory': self.memory,
            'disk': self.disk,
            'swap': self.swap,
            'io': self.io
        }

@dataclass
class IncusInstance:
    """
    This class is used to represent an instance on a node.

    Args:
        instance_id (str): The ID of the instance.
        name (str): The name of the instance.
        description (str): The description of the instance.
        owner_id (int): The ID of the owner of the instance.
        limits (IncusLimits): The limits for the instance.
        node_id (int): The ID of the node the instance is on.
        status (str): The status of the instance.
        ip (str): The IP address of the instance.
        port (int): The port of the instance.
    """
    instance_id: str
    name: str
    description: str
    owner_id: int
    limits: IncusLimits
    node_id: int
    status: str
    ip: str
    port: int

    def to_dict(self):
        return {
            'instance_id': self.instance_id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'limits': self.limits.to_dict(),
            'node_id': self.node_id,
            'status': self.status,
            'ip': self.ip,
            'port': self.port
        }
    
    async def start(self, forced=False, timeout=0):
        """
        This function is used to start an instance.

        Args:
            forced (bool): Whether to force the stop.
            timeout (int): The timeout for the stop.
        
        Returns:
            dict: The response from the instance.
        """

        payload = {
            'action': 'start',
            'forced': forced,
            'timeout': timeout
        }

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.REST_endpoint_url}/instances/{self.instance_id}/state',
                                    headers=self.headers, json=payload) as response:
                return await response.json()
    
    async def stop(self, forced=False, timeout=0):
        """
        This function is used to stop an instance.

        Args:
            forced (bool): Whether to force the stop.
            timeout (int): The timeout for the stop.
        
        Returns:
            dict: The response from the instance.
        """

        payload = {
            'action': 'stop',
            'forced': forced,
            'timeout': timeout
        }

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.REST_endpoint_url}/instances/{self.instance_id}/state',
                                    headers=self.headers, json=payload) as response:
                return await response.json()
    
    async def restart(self, forced=False, timeout=0):
        """
        This function is used to restart an instance.

        Args:
            forced (bool): Whether to force the restart.
            timeout (int): The timeout for the restart.
        
        Returns:
            dict: The response from the instance.
        """

        payload = {
            'action': 'stop',
            'forced': forced,
            'timeout': timeout
        }

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.REST_endpoint_url}/instances/{self.instance_id}/state',
                                    headers=self.headers, json=payload) as response:
                return await response.json()
            
    async def get_state(self):
        """
        This function is used to get the state of an instance.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances/{self.instance_id}/state',
                                   headers=self.headers) as response:
                return await response.json()
    
    async def rebuild(self):
        """
        This function is used to rebuild an instance.
        """

        payload = {

        }

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.REST_endpoint_url}/instances/{self.instance_id}/rebuild',
                                    headers=self.headers, json=payload) as response:
                return await response.json()
    
    async def get_sftp(self):
        """
        This function is used to get the SFTP details for an instance.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances/{self.instance_id}/sftp',
                                   headers=self.headers) as response:
                return await response.json()
    
    async def execute_command(self, command: str|list):
        """
        This function is used to execute a command on an instance.

        Args:
            command (str|list): The command to execute.
        
        Returns:
            dict: The response from the instance.
        """

        payload = {
            'command': [command] if isinstance(command, str) else command
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.REST_endpoint_url}/instances/{self.instance_id}/command',
                                    headers=self.headers, json=payload) as response:
                return await response.json()
    
    async def delete(self):
        """
        This function is used to delete an instance.
        """

        async with aiohttp.ClientSession() as session:
            async with session.delete(f'{self.REST_endpoint_url}/instances/{self.instance_id}',
                                      headers=self.headers) as response:
                return await response.json()

@dataclass
class IncusNode:
    """
    This class is used to represent a node.

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
            "limits.cpu": "2",
            "limits.memory": "2GB",
            "limits.disk": "10GB",
            "volatile.metadata": json.dumps({
                "name": name,
                "description": description,
                "owner_id": owner_id            
            }),
            "user.user-data": f"#cloud-config runcmd: {chicken_dict.get('scripts', {}).get('startup', '')}",
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



class ServerManager:
    def __init__(self):
        pass

    def egg_to_chicken(self, egg: dict) -> str:
        """
        This function is used to convert a pterodactyl egg to a chicken (yaml config file for this panel).

        Args:
            egg (str): The egg to convert.
        
        Returns:
            str: The chicken (yaml config file).
        """
    
        # Define the structure for the output YAML
        blendpanel_egg = {
            'name': egg.get('name', 'eggy'),
            'description': egg.get('description', 'hello'),
            'author': egg.get('author', 'leoj@gmail.com'),
            'image': '',
            'scripts': {
                'startup': egg.get('startup', ''),
                'install': egg.get('scripts', {}).get('installation', {}).get('script', '')
            },
            'env_variables': {}
        }
    
        # Get the latest docker image
        docker_images = egg.get('docker_images', {})
        image_list = list(docker_images.values())
        blendpanel_egg['image'] = image_list[-1] if image_list else None

        # Populate environment variables
        for var in egg.get('variables', []):
            blendpanel_egg['env_variables'][var['name']] = {
                'name': var['name'],
                'env_name': var['env_variable'],
                'user_editable': var['user_editable'],
                'default_value': var['default_value'],
                'type': var['field_type']
            }

        # Convert to YAML
        return yaml.dump(blendpanel_egg, sort_keys=False)
    
    async def get_node(self, node_id: int):
        """
        Get a node from the database and return a IncusNode object

        Args:
            node_id (int): The ID of the node to get.
        
        Returns:
            IncusNode: The node object.
        """
        
        # Get the node from the database
        node = await self.db.get_node(node_id)
        
        # Return the node object
        return IncusNode(node)

