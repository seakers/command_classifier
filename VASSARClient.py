from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from VASSARInterface import VASSARInterface

class VASSARClient():
    def __init__(self):
        # Make socket
        self.transport = TSocket.TSocket('localhost', 9090)

        # Buffering is critical. Raw sockets are very slow
        self.transport = TTransport.TBufferedTransport(self.transport)

        # Wrap in a protocol
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        # Create a client to use the protocol encoder
        self.client = VASSARInterface.Client(self.protocol)

    def startConnection(self):
        # Connect
        self.transport.open()

    def endConnection(self):
        # Close
        self.transport.close()
