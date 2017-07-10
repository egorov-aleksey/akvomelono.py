from twisted.internet.protocol import Protocol, ServerFactory
from twisted.python import log

__author__ = 'a.egorov'


class DeviceProtocol(Protocol):
    host = None
    peer = None
    d = None

    def makeConnection(self, transport):
        self.host = transport.getHost()
        self.peer = transport.getPeer()

        if self.host.port in self.factory.device_list:
            transport.loseConnection()
        else:
            Protocol.makeConnection(self, transport)

    def connectionMade(self):
        self.factory.device_list[self.host.port] = self

        log.msg('New device is connected on %s' % self.peer)

        # self.transport.write("Welcome to chat!\nEnter your name: ")
        # self.transport.loseConnection()

    def connectionLost(self, reason):
        if self.factory.device_list[self.host.port].peer == self.peer:
            del self.factory.device_list[self.host.port]

        # todo
        # call loseConnection of all connected client?

        Protocol.connectionLost(self, reason)

    def dataReceived(self, data):
        self.d.callback((lambda d: d)(data))

    def sendData(self, data, d):
        self.d = d
        self.transport.write(data)


class DeviceFactory(ServerFactory):
    protocol = DeviceProtocol

    device_list = {}

    def buildProtocol(self, addr):
        protocol = ServerFactory.buildProtocol(self, addr)

        # self.client_list[protocol.id] = protocol

        return protocol
