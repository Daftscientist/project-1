import yaml
from core.incus.node import IncusNode


class IncusManager:
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
            'name': egg.get('name', 'myEgg'),
            'description': egg.get('description', 'This is a custom chicken - loaded from an egg.'),
            'author': egg.get('author', 'BlendPanel'),
            'image': '',
            'type': 'OCI', ## default to OCI - all pterodactyl eggs are OCI
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
    
    async def get_node(self, node_id: int) -> IncusNode:
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
