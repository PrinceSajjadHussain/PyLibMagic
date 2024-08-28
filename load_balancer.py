# from fastapi import FastAPI, Request
# import httpx
# from itertools import cycle
# import json
# import ssl

# from starlette.responses import Response

# app = FastAPI()
# ssl._create_default_https_context = ssl._create_unverified_context

# # Function to load configuration
# def load_config():
#     with open("config.json") as f:
#         return json.load(f)

# # Load servers from the configuration file
# config = load_config()
# servers = config.get("servers", [])

# # Create a round-robin iterator for the servers
# server_iterator = cycle(servers)

# @app.middleware("http")
# async def round_robin_middleware(request: Request, call_next):
#     # Get the next server in the round-robin cycle
#     next_server = next(server_iterator)
#     print("next_server :::::::::::::", next_server)
    
#     # Create a client to forward the request
#     async with httpx.AsyncClient(verify=False) as client:  # Set verify to True for production
#         try:
#             # Forward the request to the selected server
#             response = await client.request(
#                 request.method,
#                 next_server + request.url.path,
#                 headers={k.decode(): v.decode() for k, v in request.headers.raw},
#                 data=await request.body(),
#                 params=dict(request.query_params)  # Forward query parameters for GET requests
#             )
#         except httpx.HTTPStatusError as e:
#             # Handle HTTP errors (e.g., 404, 500)
#             print(f"SERVER HIT {next_server}")
#             return Response(content=str(e), status_code=e.response.status_code)
#         except httpx.RequestError as e:
#             # Handle request errors (e.g., network problems)
#             print(f"SERVER HIT {next_server}")
#             return Response(content=str(e), status_code=500)

#     # Create a Starlette Response object
#     return Response(
#         content=response.content,
#         status_code=response.status_code,
#         headers=dict(response.headers)  # Forward the response headers
#     )

# # Define a root endpoint for testing
# @app.post("/")
# async def root():
#     return {"message": "Welcome to the FastAPI server!"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=7000,
#         ssl_certfile=r"C:\Users\Makhshaf.Haider\Desktop\load_balancer\certfile.pem",
#         ssl_keyfile=r"C:\Users\Makhshaf.Haider\Desktop\load_balancer\keyfile.pem",
#     )



from fastapi import FastAPI, Request
import httpx
from itertools import cycle
import json
import ssl
from starlette.responses import Response
from starlette.requests import Request
import app_global
from logging_setup import *
app = FastAPI()
ssl._create_default_https_context = ssl._create_unverified_context

# Function to load configuration
def load_config():
    with open("config.json") as f:
        return json.load(f)

# Load servers from the configuration file
config = load_config()
servers = config.get("servers", [])

# Create a round-robin iterator for the servers
server_iterator = cycle(servers)


@app.middleware("http")
@log_function_execution
async def round_robin_middleware(request: Request, call_next):
    # Get the next server in the round-robin cycle
    next_server = next(server_iterator)
    print("Next server:", next_server)
    
    # Create a client to forward the request
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(60.0)) as client:  # 60 seconds timeout
        try:
            # Forward the request to the selected server
            response = await client.request(
                request.method,
                next_server + request.url.path,
                headers={k.decode(): v.decode() for k, v in request.headers.raw},
                data=await request.body(),
                params=dict(request.query_params)  # Forward query parameters for GET requests
            )
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors (e.g., 404, 500)
            print(f"Server {next_server} returned HTTP error: {e}")
            return Response(content=str(e), status_code=e.response.status_code)
        except httpx.RequestError as e:
            # Handle request errors (e.g., network problems)
            print(f"Request error with server {next_server}: {e}")
            return Response(content="Request error", status_code=500)

    # Create a Starlette Response object
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)  # Forward the response headers
    )



if __name__ == "__main__":
    app_global.logger=setup_logging()
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7010,
        ssl_certfile=r"C:\Users\Makhshaf.Haider\Desktop\load_balancer\certfile.pem",
        ssl_keyfile=r"C:\Users\Makhshaf.Haider\Desktop\load_balancer\keyfile.pem",
        
    )

