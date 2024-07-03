import aiohttp

class DaemonInteractor:
    def __init__(self, daemon_url: str, authentication: str):
        if not daemon_url:
            raise ValueError('Daemon URL is required')

        if not authentication:
            raise ValueError('Authentication is required')

        if not authentication.startswith('Bearer '):
            authentication = f'Bearer {authentication}'

        self.daemon_url = daemon_url
        self.authentication = authentication

        self.http_client = aiohttp.ClientSession(
            base_url=f"{daemon_url}/api",
            headers={
                'Authorization': authentication
            }
        )

    async def create_server(self, data: dict):
        async with self.http_client.post('/server', data=data) as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()
        
    async def get_server(self, server_id: str):
        async with self.http_client.get(f'/server/{server_id}') as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()
    
    async def delete_server(self, server_id: str):
        async with self.http_client.delete(f'/server/', data={'server_id': server_id}) as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()
    
    async def edit_server(self, server_id: str, data: dict):
        async with self.http_client.patch(f'/server/{server_id}', data=data) as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()
    
    async def server_power_action(self, server_id: str, action: str):
        async with self.http_client.post(f'/api/server/action', data={'action': action, 'server_id': server_id}) as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()
    
    async def get_server_status(self, server_id: str):
        async with self.http_client.get(f'/api/server/action', data={'server_id': server_id}) as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()

    async def send_server_command(self, server_id: str, command: str):
        async with self.http_client.post(f'/server/action', data={'command': command, 'server_id': server_id}) as response:
            ## handle errors
            response.raise_for_status()
            return await response.json()

    async def access_server_console(self, server_id: str):
        # connect to the websocket without affecting the rest of the code and the server client
        # its at https://github.com/Daftscientist/LittleWings/blob/main/src/api/websocket.py
        async with self.http_client.ws_connect(f'/ws') as ws:
            await ws.send_json(
                {
                    'type': 'connect',
                    'server_id': server_id
                }
            )
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = msg.json()
                    if data['type'] == 'heartbeat_reminder':
                        await ws.send_json(
                            {
                                'type': 'heartbeat',
                                'server_id': server_id
                            }
                        )
                    elif data['type'] == 'log':
                        ## stream the log results to the client through returns
                        yield data['data']
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    raise Exception('Websocket connection error')

if __name__ == '__main__':
    daemon = DaemonInteractor('http://localhost:8000', 'Bearer dghjhsdfhsgdjh')
    print(daemon.create_server({'name': 'test'}))
    print(daemon.get_server('test'))
    print(daemon.delete_server('test'))
    print(daemon.edit_server('test', {'name': 'test2'}))
    print(daemon.server_power_action('test', 'start'))
    print(daemon.get_server_status('test'))
    print(daemon.send_server_command('test', 'test'))
    print(daemon.access_server_console('test'))
    