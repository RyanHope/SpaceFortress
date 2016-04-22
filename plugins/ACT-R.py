"""
This is an example plugin which can listen for
events and register new config options.
"""

try:

	import sys
	from actr6_jni import Dispatcher, JNI_Server, Chunk, VisualChunk
	import pygame
	import pygl2d
	import webcolors
	import time


	SDLK_SCANCODE_MASK = 1 << 30

	def SDL_SCANCODE_TO_KEYCODE(x):
		"""Converts the passed scancode to a keycode value."""
		return x | SDLK_SCANCODE_MASK

	class TokenChunk(VisualChunk):
		def get_visual_location(self):
			chunk = super(TokenChunk, self).get_visual_location()
			for s, v in self.slots.iteritems():
				if s in ["orientation", "velocity"]:
					chunk["slots"][s] = v
			return chunk

	class RectChunk(VisualChunk):
		def get_visual_location(self):
			chunk = super(RectChunk, self).get_visual_location()
			for s, v in self.slots.iteritems():
				if s in ["top","bottom","left","right"]:
					chunk["slots"][s] = v
			return chunk

	def RenderTextToChunk(name, text, rect, **kwargs):
		return VisualChunk(name, rect.centerx, rect.centery,
						kind = ":text",
						width = rect.width,
						height = rect.height,
						color = webcolors.rgb_to_name(text.color),
						value = text.text,
						**kwargs)

	def ShipToChunk(ship, **kwargs):
		return TokenChunk("ship", ship.position.x, ship.position.y,
						kind =  ":ship",
						width = ship.get_width(),
						height = ship.get_height(),
						color = "yellow",
						orientation = ship.orientation,
						velocity = ship.get_velocity(),
						**kwargs)

	def FortressToChunk(fortress, **kwargs):
		return TokenChunk("fortress", fortress.position.x, fortress.position.y,
						kind = ":fortress",
						width = fortress.get_width(),
						height = fortress.get_height(),
						color = "yellow",
						orientation = fortress.orientation,
						velocity = fortress.get_velocity(),
						**kwargs)

	def ShellToChunk(shell, **kwargs):
		return TokenChunk("shell%d" % shell._id, shell.position.x, shell.position.y,
						kind = ":shell",
						width = shell.get_width(),
						height = shell.get_height(),
						color = "red",
						orientation = shell.orientation,
						velocity = shell.get_velocity(),
						**kwargs)

	def MissileToChunk(missile, **kwargs):
		return TokenChunk("missile%d" % missile._id, missile.position.x, missile.position.y,
						kind = ":missile",
						width = missile.get_width(),
						height = missile.get_height(),
						color = "red",
						orientation = missile.orientation,
						velocity = missile.get_velocity(),
						**kwargs)

	def MineToChunk(mine, **kwargs):
		return TokenChunk("mine%d" % mine._id, mine.position.x, mine.position.y,
						kind = ":mine",
						width = mine.get_width(),
						height = mine.get_height(),
						color = "red",
						orientation = mine.orientation,
						velocity = mine.get_velocity(),
						**kwargs)

	def RectToChunk(rect, name, color, **kwargs):
		return RectChunk(name, rect.centerx, rect.centery,
						width = rect.width,
						height = rect.height,
						top = rect.top,
						bottom = rect.bottom,
						left = rect.left,
						right = rect.right,
						color=color,
						**kwargs)

	class SF5Plugin(object):

		d = Dispatcher()

		name = 'ACT-R'

		def __init__(self, app):
			super(SF5Plugin, self).__init__()
			self.app = app
			self.actr = None
			self.config = True

		def ready(self):
			if self.app.config[self.name]['enabled']:
				self.actr = JNI_Server(self)
				self.actr.addDispatcher(self.d)
				self.app.reactor.listenTCP(int(self.app.config[self.name]['port']), self.actr)
				self.app.state = self.app.STATE_WAIT_CONNECT

		##################################################################
		# Handle game events
		##################################################################

		def eventCallback(self, *args, **kwargs):

			if args[3] == 'config' and args[4] == 'load':

				if args[5] == 'defaults':
					self.app.config.add_setting(self.name, 'enabled', False, type=2, alias="Enable", about='Enable ACT-R model support')
					self.app.config.add_setting(self.name, 'port', '5555', type=3, alias="Incoming Port", about='ACT-R JNI Port')

			if self.actr:

				if args[3] == 'session':

					if args[4] == 'ready':
						self.actr_waiting = pygl2d.font.RenderText('Waiting for ACT-R', (255, 0, 0), self.app.font2)
						self.actr_waiting_rect = self.actr_waiting.get_rect()
						self.actr_waiting_rect.center = (self.app.SCREEN_WIDTH / 2, self.app.SCREEN_HEIGHT / 2)
						self.model_waiting = pygl2d.font.RenderText('Waiting for Model', (0, 255, 0), self.app.font2)
						self.model_waiting_rect = self.model_waiting.get_rect()
						self.model_waiting_rect.center = (self.app.SCREEN_WIDTH / 2, self.app.SCREEN_HEIGHT / 2)

				elif args[3] == 'game':

					if args[4] == 'setstate':

						if args[5] == self.app.STATE_GAMENO:
							self.actr.display_new([RenderTextToChunk(None,self.app.game_title,self.app.game_title_rect,number=self.app.current_game)])
						elif args[5] == self.app.STATE_IFF:
							chunks = [RenderTextToChunk(None,foe[0],foe[1]) for foe in self.app.foe_letters]
							chunks += [
									RenderTextToChunk(None,self.app.foe_top,self.app.foe_top_rect),
									RenderTextToChunk(None,self.app.foe_midbot,self.app.foe_midbot_rect),
									RenderTextToChunk(None,self.app.foe_bottom,self.app.foe_bottom_rect)
									]
							self.actr.display_new(chunks)
						elif args[5] == self.app.STATE_PLAY:
							if not self.resume:
								chunks = [
										RectToChunk(self.app.world, "world-border", "green", kind=":world-border"),
										ShipToChunk(self.app.ship)
										]
								if self.app.config['Fortress']['fortress_exists']:
									chunks.append(FortressToChunk(self.app.fortress))
								self.actr.display_new(chunks)

				elif args[3] == 'score+':
					if args[4] == 'pnts':
						self.actr.trigger_reward(args[5])
				elif args[3] == 'score-':
					if args[4] == 'pnts':
						self.actr.trigger_reward(-args[5])

				elif args[3] == 'press':
					if args[5] == 'user':
						if args[4] == pygame.K_ESCAPE:
							self.actr.trigger_event(":break")

				elif args[3] == 'fire':

					if args[4] == 'fortress':
						self.actr.display_add(ShellToChunk(self.app.shell_list[-1]))

				elif args[3] == 'shell':

					if args[4] == 'removed':

						self.actr.display_remove(name="shell%d-loc" % args[5])

				elif args[3] == 'display':

					if args[4] == 'preflip':

						if self.app.state == self.app.STATE_WAIT_CONNECT:
							self.draw_actr_wait_msg()
						elif self.app.state == self.app.STATE_WAIT_MODEL:
							self.draw_model_wait_msg()
						elif self.app.state == self.app.STATE_PLAY:
							chunks = [ShipToChunk(self.app.ship)]
							if self.app.config['Fortress']['fortress_exists']:
								chunks.append(FortressToChunk(self.app.fortress))
								for shell in self.app.shell_list:
									chunks.append(ShellToChunk(shell))
							self.actr.display_update(chunks)


		##################################################################
		# Misc routines
		##################################################################

		def draw_actr_wait_msg(self):
			"""Display Waiting for ACT-R msg"""
			self.actr_waiting.draw(self.actr_waiting_rect.topleft)

		def draw_model_wait_msg(self):
			"""Display Waiting for Model msg"""
			self.model_waiting.draw(self.model_waiting_rect.topleft)

		##################################################################
		# Begin JNI Callbacks
		##################################################################

		@d.listen('connectionMade')
		def ACTR6_JNI_Event(self, model, params):
			print("Connection Made")
			self.app.setState(self.app.STATE_WAIT_MODEL)
			self.app.current_game = 0
			self.actr.setup(self.app.screen_size[0], self.app.screen_size[1])

		@d.listen('connectionLost')
		def ACTR6_JNI_Event(self, model, params):
			print("Connection Lost", params)
			self.app.setState(self.app.STATE_WAIT_CONNECT)

		@d.listen('reset')
		def ACTR6_JNI_Event(self, model, params):
			print("Reset")
			self.app.setState(self.app.STATE_WAIT_MODEL)
			self.app.current_game = 0

		@d.listen('model-run')
		def ACTR6_JNI_Event(self, model, params):
			if params['resume']:
				self.resume = True
				self.app.setState(self.oldstate)
				self.app.gametimer.unpause()
			else:
				for c in params["config"].keys():
					for s in params["config"][c].keys():
						self.app.config.update_setting_value(c, s, params["config"][c][s]['value'])
				slots = {}
				slots['setting-mine-exists'] = self.app.config['Mine']['mine_exists']
				slots['setting-fortress-exists'] = self.app.config['Fortress']['fortress_exists']
				slots['setting-bonus-exists'] = self.app.config['Bonus']['bonus_exists']
				self.actr.add_dm(Chunk("settings", **slots))
				self.resume = False
				self.app.setState(self.app.STATE_SETUP)

		@d.listen('model-stop')
		def ACTR6_JNI_Event(self, model, params):
			self.app.gametimer.pause()
			self.oldstate = self.app.state
			self.app.setState(self.app.STATE_PAUSED)

		@d.listen('keydown')
		def ACTR6_JNI_Event(self, model, params):
			pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key":params['keycode']}))

		@d.listen('keyup')
		def ACTR6_JNI_Event(self, model, params):
			pygame.event.post(pygame.event.Event(pygame.KEYUP, {"key":params['keycode']}))

		@d.listen('mousemotion')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress

		@d.listen('mousedown')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress

		@d.listen('mouseup')
		def ACTR6_JNI_Event(self, model, params):
			pass # No mouse in Space Fortress

except ImportError as e:
	sys.stderr.write("Failed to load 'ACT-R JNI' plugin, missing dependencies. [%s]\n" % e)
	sys.stderr.flush()
