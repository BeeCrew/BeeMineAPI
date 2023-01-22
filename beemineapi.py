from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol
from quarry.types.uuid import UUID
from quarry.data.data_packs import data_packs, dimension_types
from typing import Callable
true, false = True, False

#Protocol
class BeeProtocol(ServerProtocol):
	def player_joined(self):
		ServerProtocol.player_joined(self)

		entity_id = 0
		hashed_seed = 42
		view_distance = 2
		simulation_distance = 2
		max_players = 0
		gamemode = 0
		prev_gamemode = gamemode
		is_hardcore = false
		is_respawn_screen = true
		is_reduced_debug = false
		is_debug = false
		is_flat = false
		keep_alive = true

		dimension_codec = data_packs[self.protocol_version]
		dimension_name = "minecraft:overworld"
		dimension_tag = dimension_types[self.protocol_version, dimension_name]
		world_count = 1
		world_name = "world"

		join_game = [
            self.buff_type.pack("i?Bb", entity_id, is_hardcore, gamemode, prev_gamemode),
            self.buff_type.pack_varint(world_count),
            self.buff_type.pack_string(world_name),
            self.buff_type.pack_nbt(dimension_codec),
        ]

		if self.protocol_version >= 759:  #1.19+ requires dimension name. <1.19 requires entire dimension nbt
			join_game.append(self.buff_type.pack_string(dimension_name))
		else:
			join_game.append(self.buff_type.pack_nbt(dimension_tag))

		join_game.append(self.buff_type.pack_string(world_name))
		join_game.append(self.buff_type.pack("q", hashed_seed))
		join_game.append(self.buff_type.pack_varint(max_players))
		join_game.append(self.buff_type.pack_varint(view_distance)),

		if self.protocol_version >= 757:  #1.18 requires simulation distance
			join_game.append(self.buff_type.pack_varint(simulation_distance))

		join_game.append(self.buff_type.pack("????", is_reduced_debug, is_respawn_screen, is_debug, is_flat))

		if self.protocol_version >= 759:  #1.19
			join_game.append(self.buff_type.pack("?", False))

		#Send the "Join Game" packet
		self.send_packet("join_game", *join_game)

		#Send the "Player Position And Look" Packet
		self.send_packet(
            "player_position_and_look",
            self.buff_type.pack("dddff?",
                0,                         # x
                500,                       # y  Must be >= build height to pass the "Loading Terrain" screen on 1.18.2
                0,                         # z
                0,                         # yaw
                0,                         # pitch
                0b00000),                  # flags
            self.buff_type.pack_varint(0), # teleport id
            self.buff_type.pack("?", True)) # Leave vehicle,

		if keep_alive:
			self.ticker.add_loop(20, self.update_keep_alive)

	def player_left(self):
		ServerProtocol.player_left(self)
	
	def update_keep_alive(self):
		#Send the "Keep Alive" packet.
		self.send_packet("keep_alive", self.buff_type.pack('Q', 0))

#Factory
class BeeFactory(ServerFactory):
	protocol = BeeProtocol
	motd = "A Minecraft Server"
	online_mode = false

#Utils
class BeeAPI:
	def __init__(self, factory: BeeFactory=None):
		if not factory:
			factory = BeeFactory()
		self.factory = factory
		self.protocol = self.factory.protocol
		return
	
	def sendMessage(self,message: str, selector=None, isActionMsg: bool=false):
		"""
		Send a message to someone. Or everyone!
		"""
		if not selector:
			for player in self.factory.players:
				if player.protocol_version >= 760: #1.19.1+ Uses a boolean for weather to show in action bar
					toActionbar = player.buff_type.pack("?", isActionMsg)
				else: #1.19- uses varint as normal.
					if isActionMsg:
						isActionMsg = 1
					else:
						isActionMsg = 0
					toActionbar = player.buff_type.pack_varint(isActionMsg)
				player.send_packet("system_message", 
					player.buff_type.pack_chat(message),
					toActionbar
				)
			return
		else:
			player = selector
			if player.protocol_version >= 760: #1.19.1+ Uses a boolean for weather to show in action bar
				toActionbar = player.buff_type.pack("?", false)
			else: #1.19- uses varint as normal.
				toActionbar = player.buff_type.pack_varint(0)
			player.send_packet("system_message", 
				player.buff_type.pack_chat(message),
				toActionbar
			)
			return
		return
	
	def loopallPlayers(self, func: Callable, *args, **kwargs):
		"""
		Execute a function for every online player.
		"""
		executed = 0
		for player in self.factory.players:
			func(player, *args, **kwargs)
			executed += 1
		return (executed, func)