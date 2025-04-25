import logging

import grpc

from protos import helloworld_pb2_grpc, helloworld_pb2


log = logging.getLogger(__name__)


class GRPCClientManager:
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.target = f"{host}:{port}"
        self.channel = None

    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(target=self.target)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()

    async def say_hello(self, name: str) -> str:
        stub = helloworld_pb2_grpc.GreeterStub(self.channel)
        response = await stub.SayHello(helloworld_pb2.HelloRequest(name=name))
        return response.message
