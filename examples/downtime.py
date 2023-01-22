"""
For a downtime server i'd recommand directly using quarry.
BeeMineAPI is not supposed to be used for a down time server.
This is a quarry example.
"""
from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol
from quarry.types.uuid import UUID
from quarry.data.data_packs import data_packs, dimension_types
true, false = True, False
c = "§"

class DowntimeProtocol(ServerProtocol):
	def player_joined(self):
		ServerProtocol.player_joined(self)
		self.close(self.factory.motd)

class DowntimeFactory(ServerFactory):
	protocol = DowntimeProtocol
	motd = f'{c}4Maintenance'
	online_mode = false

factory = DowntimeFactory()
factory.listen("", 25565)
reactor.run()