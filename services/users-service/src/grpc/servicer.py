import grpc

from protos import helloworld_pb2, helloworld_pb2_grpc


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    async def SayHello(
        self,
        request: helloworld_pb2.HelloRequest,
        context: grpc.aio.ServicerContext,
    ) -> helloworld_pb2.HelloReply:
        return helloworld_pb2.HelloReply(message="Hello, %s!" % request.name)
