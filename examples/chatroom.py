"""
This is a simple Chat Room example.
It does not contain 1.19.1+ chat signing features.
To avoid them. It will send chat messages as system messages.
"""
from beemineapi import BeeProtocol, BeeFactory, reactor, BeeAPI
import sys
true, false = True, False
c = "§"

def exit(exit_code: int=0):
	try:
		sys.exit(exit_code)
	except:
		quit(0)

def chat_message(self, buff):
	p_text = buff.unpack_string()
	if not p_text.startswith('.'):
		fmt = f"<{self.display_name}> {p_text}"
		print(f"[CHAT] {fmt}")
		beeapi.sendMessage(fmt)
	else:
		pass
	buff.discard()

class ChatRoomFactory(BeeFactory):
	#Setup
	protocol = BeeProtocol
	protocol.gamemode = 3
	protocol.prev_gamemode = 3

	#Metadata
	motd = 'Chat Room Example'

	#Protocol Setup
	protocol.packet_chat_message = chat_message

try:
	factory = BeeFactory()
	host, port = "", 25565
	addr = (host, port)
	beeapi = BeeAPI(factory)
	factory.listen(*addr)
	reactor.run()
except KeyboardInterrupt:
	exit()