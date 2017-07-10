from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol, ServerFactory
from twisted.python import log


__author__ = 'a.egorov'


class ClientProtocol(Protocol):
    host = None
    device_factory = None
    device = None

    def makeConnection(self, transport):
        self.host = transport.getHost()

        device_service = self.factory.service.parent.getServiceNamed('DeviceSlot')

        self.device_factory = device_service.factory

        if self.host.port in self.device_factory.device_list:
            self.device = self.device_factory.device_list[self.host.port]
            Protocol.makeConnection(self, transport)
        else:
            transport.loseConnection()

    def connectionMade(self):
        # self.factory.device_list[self.host.port] = self

        log.msg('New client is connected on %s' % (self.transport.getPeer()))

        # self.transport.write("Welcome to chat!\nEnter your name: ")
        # self.transport.loseConnection()

        # log.msg(self.factory.device_list)

    # def connectionLost(self, reason):
    # del self.factory.device_list[self.host.port]
    #
    # log.msg('Client is disconnected on %s' % (self.transport.getPeer()))
    # log.msg(self.factory.device_list)

    def dataReceived(self, data):
        d = Deferred()
        d.addCallback(self.transport.write)
        self.device.sendData(data, d)


class ClientFactory(ServerFactory):
    protocol = ClientProtocol
    service = None

    client_list = {}

    def __init__(self, service):
        self.service = service

    def buildProtocol(self, addr):
        protocol = ServerFactory.buildProtocol(self, addr)

        # log.msg(protocol)

        # self.client_list[protocol.id] = protocol

        return protocol
