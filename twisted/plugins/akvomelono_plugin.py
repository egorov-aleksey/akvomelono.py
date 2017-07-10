from twisted.application import service
from twisted.application.service import IServiceMaker
from twisted.logger import Logger
from twisted.plugin import IPlugin
from twisted.python import usage
from zope.interface import implementer

from akvomelono.ClientSlot import ClientFactory
from akvomelono.DeviceSlot import DeviceFactory

log = Logger()


class Options(usage.Options):
    pass
    optParameters = [
        ['cfg', 'c', 'akvomelono.yml', 'The config file.'],
    ]


class DeviceSlotService(service.Service):
    name = 'DeviceSlot'
    interface = None
    ports = []

    factory = None

    def __init__(self, interface, ports):
        self.interface = interface
        self.ports = ports

    def startService(self):
        factory = DeviceFactory()

        self.factory = factory

        for p in self.ports:
            try:
                from twisted.internet import reactor
                reactor.listenTCP(p, factory, interface=self.interface)

                log.info("Device slot: Listening on port %d" % p)
            except Exception as e:
                log.failure("Device slot: Listening error on port %d: %s" % (p, e))

        service.Service.startService(self)

    def stopService(self):
        service.Service.stopService(self)


class ClientSlotService(service.Service):
    name = 'ClientSlot'
    interface = None
    ports = []

    def __init__(self, interface, ports):
        self.interface = interface
        self.ports = ports

    def startService(self):
        factory = ClientFactory(self)

        for p in self.ports:
            try:
                from twisted.internet import reactor
                reactor.listenTCP(p, factory, interface=self.interface)

                log.info("Client slot: Listening on port %d" % p)
            except Exception as e:
                log.failure("Client slot: Listening error on port %d: %s" % (p, e))

        service.Service.startService(self)

    def stopService(self):
        service.Service.stopService(self)


@implementer(IServiceMaker, IPlugin)
class AkvomelonoServiceMaker(object):
    tapname = "akvomelono"
    description = "Special gateway."
    options = Options

    def makeService(self, options):
        mainService = service.MultiService()

        ports = [8000, 8001]

        device_slot_service = DeviceSlotService('127.0.0.1', ports)
        device_slot_service.setServiceParent(mainService)

        client_slot_service = ClientSlotService('127.0.0.2', ports)
        client_slot_service.setServiceParent(mainService)

        return mainService


serviceMaker = AkvomelonoServiceMaker()
