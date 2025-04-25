import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import asyncio
import logging as log

import grpc

from protos import helloworld_pb2_grpc

from src.config import settings
from src.grpc.servicer import Greeter


log.basicConfig(level=log.INFO)


class AsyncGRPCServer:
    def __init__(self, url: str = "localhost:50051") -> None:
        self.url = url
        self.server = None

    async def serve(self) -> None:
        self.server = grpc.aio.server()
        helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), self.server)
        self.server.add_insecure_port(self.url)
        await self.server.start()
        try:
            log.info(f"gRPC: Server started on {self.url}, waiting for termination...")
            await self.server.wait_for_termination()
        except asyncio.CancelledError:
            log.info("gRPC: Server stopped by cancel.")
        finally:
            log.info("gRPC: Stopping server...")
            await self.server.stop(grace=0)
            log.info("gRPC: Server stopped successfully.")


grpc_server = AsyncGRPCServer(url=f"{settings.GRPC_HOST}:{settings.GRPC_PORT}")

if __name__ == "__main__":
    try:
        asyncio.run(grpc_server.serve())
    except KeyboardInterrupt:
        pass
