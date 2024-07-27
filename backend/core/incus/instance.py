from dataclasses import dataclass
import datetime
import uuid
import aiohttp

from core.incus.limits import IncusLimits

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

        await self.stop(forced, timeout)

        return await self.start(forced, timeout)
            
    async def get_state(self):
        """
        This function is used to get the state of an instance.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances/{self.instance_id}/state',
                                   headers=self.headers) as response:
                return await response.json()
    
    async def rebuild(self, empty='none'):
        """
            This function is used to rebuild an instance.
            - Default value for empty is 'none', which clears the instance root directory.
        """

        payload = {
            {
                "source": {
                    "type": empty
                }
            }
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
    
    async def update(self, name: str = None, description: str = None, owner_id = None, limits: IncusLimits = None):
        """
        This function is used to update an instance.

        Args:
            name (str): The name of the instance.
            description (str): The description of the instance.
            owner_id (int): The ID of the owner of the instance.
            limits (IncusLimits): The limits for the instance.
        """
        if not name and not description and not limits:
            raise ValueError('At least one of name, description, or limits must be provided.')
        
        payload = {}

        if name:
            payload['config']['volatile.metadata']['name'] = name
        if description:
            payload['config']['volatile.metadata']['description'] = description
        if owner_id:
            payload['config']['volatile.metadata']['owner_id'] = owner_id
        
        if limits:
            for limit in limits.to_dict():
                if not limit:
                    continue
                payload['config'][f'limits.{limit}'] = limits.to_dict()[limit]

        async with aiohttp.ClientSession() as session:
            async with session.put(f'{self.REST_endpoint_url}/instances/{self.instance_id}',
                                   headers=self.headers, json=payload) as response:
                return await response.json()
    
    async def create_backup(self, expires_at: datetime.datetime=datetime.datetime.now() + datetime.timedelta(days=360)):
        """
        This function is used to create a backup of an instance.

        Args:
            expires_at (datetime.datetime): The time the backup expires.
        """

        backup_id = str(uuid.uuid4()) + "_" + self.owner_id

        payload = {
            "compression_algorithm": "gzip",
            "expires_at": str(expires_at),
            "instance_only": True,
            "name": backup_id,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.REST_endpoint_url}/instances/{self.instance_id}/backups',
                                    headers=self.headers, payload=payload) as response:
                return await response.json()
    
    async def delete_backup(self, backup_id: str):
        """
        This function is used to delete a backup of an instance.

        Args:
            backup_id (str): The ID of the backup to delete
        """

        async with aiohttp.ClientSession() as session:
            async with session.delete(f'{self.REST_endpoint_url}/instances/{self.instance_id}/backups/{backup_id}',
                                      headers=self.headers) as response:
                return await response.json()
    
    async def export_backup(self, backup_id: str) -> bytes:
        """
        This function is used to export a backup of an instance.

        Args:
            backup_id (str): The ID of the backup to export
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances/{self.instance_id}/backups/{backup_id}/export',
                                   headers=self.headers) as response:
                ## return the octet stream
                return await response.read()
    
    async def backups(self):
        """
        This function is used to get the backups of an instance.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.REST_endpoint_url}/instances/{self.instance_id}/backups',
                                   headers=self.headers) as response:
                return await response.json()
    

    