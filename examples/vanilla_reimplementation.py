"""
This is a old version of the vanilla reimplementation.
It has been moved to https://github.com/BeeCrew/VanilaReimplementation
"""

"""
A vanilla reimplementation made using BeeMineAPI.
This should NOT be used in Production.
It is not complete.
"""
from beemineapi import BeeProtocol, BeeFactory, BeeAPI, reactor
import sys
true, false = True, False
c = '§'
beeapi = BeeAPI()

def exit(exit_code: int=0):
	try:
		sys.exit(exit_code)
	except:
		quit()

def packet_chat_message(self, buff):
	p_text = buff.unpack_string()
	fmt = f"<{self.display_name}> {p_text}"
	print(f'[CHAT] {fmt}')
	beeapi.sendMessage(fmt)
	buff.discard()

def getHelpMsg():
	return f"""{c}cThis is a placeholder."""

def packet_chat_command(self, buff):
	command = buff.unpack_string()
	commands = command.split()
	cmd = commands[0]
	args = commands
	args.remove(cmd)
	print(f'{self.display_name} sent command: {command}')
	if cmd == "help":
		beeapi.sendMessage(getHelpMsg(), self)
	elif cmd == "eval":
		beeapi.sendMessage(f'{c}7Executing...', self)
		executes = ''
		for arg in args:
			executes += f' {arg}'
		try:
			got = eval(executes)
		except Exception as e:
			exname = str(type(e)).replace(' ', '').replace('<', '>').replace('>', '').replace('class', '').replace('\'', '')
			beeapi.sendMessage(f'{c}c{exname}: {e}', self)
	else:
		beeapi.sendMessage(f'{c}cInvalid Command! Use /help for help.', self)
	buff.discard()

class VanillaFactory(BeeFactory):
	protocol = BeeProtocol
	motd = 'A Minecraft Server\nBeeMineAPI Vanilla Reimplementation'
	protocol.packet_chat_message = packet_chat_message
	protocol.packet_chat_command = packet_chat_command

try:
	factory = VanillaFactory()
	host, port="", 25565
	addr=(host, port)
	beeapi = BeeAPI(factory)
	factory.listen(*addr)
	reactor.run()
except Exception as e:
	exit()