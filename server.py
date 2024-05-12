import asyncio
import ssl
import websockets

# Config
ssl_crt_url = '/etc/nginx/SSL/xxx.crt'
ssl_key_url = '/etc/nginx/SSL/xxx.key'

# Store connected clients in a dictionary based on channel
connected_clients = {}

# Process client connection asynchronously
async def handle_client(websocket, path):
    # Default channel setting
    channel = "channel1"

    # Add the new client to the default channel
    if channel not in connected_clients:
        connected_clients[channel] = set()
    connected_clients[channel].add(websocket)

    try:
        # Receive and process messages from the client
        async for message in websocket:
            # If the message is a channel change, move the client to that channel
            if message in ["channel1", "OM", "BPM"]:
                connected_clients[channel].remove(websocket)
                channel = message
                if channel not in connected_clients:
                    connected_clients[channel] = set()
                connected_clients[channel].add(websocket)
            else:
                # Broadcast the message to all clients in the current channel
                for client in connected_clients[channel]:
                    await client.send(message)
    finally:
        # When the client disconnects, remove it from the current channel
        if websocket in connected_clients[channel]:
            connected_clients[channel].remove(websocket)

# Create the main event loop
async def main():
    # Set up SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_crt_url, ssl_key_url)
    
    # Start the WebSocket server with SSL
    server = await websockets.serve(handle_client, "", 8080, ssl=ssl_context)
    await server.wait_closed()

# Run the main event loop
asyncio.run(main())
