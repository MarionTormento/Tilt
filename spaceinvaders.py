# Space Invaders
# Created by Lee Robinson

#!/usr/bin/env python
from pygame import *
import sys
from random import shuffle, randrange, choice
import serial
import math 
import os
import datetime

#           R    G    B
WHITE 	= (255, 255, 255)
GREEN 	= (78, 255, 87)
YELLOW 	= (241, 255, 0)
BLUE 	= (80, 255, 239)
PURPLE 	= (203, 0, 255)
RED 	= (237, 28, 36)

SCREEN = display.set_mode((0,0),FULLSCREEN)
infoObject = display.Info()
SCREEN_W = infoObject.current_w #800-720
SCREEN_H = infoObject.current_h #600-480

# SCREEN_W = 630 #800-720
# SCREEN_H = 380; #600-480

# SCREEN 		= display.set_mode((SCREEN_W,SCREEN_H))
FONT = "fonts/space_invaders.ttf"
IMG_NAMES 	= ["ship", "ship", "mystery", "enemy1_1", "enemy1_2", "enemy2_1", "enemy2_2",
				"enemy3_1", "enemy3_2", "explosionblue", "explosiongreen", "explosionpurple", "laser", "enemylaser", "lefthand", "righthand"]
IMAGES 		= {name: image.load("images/{}.png".format(name)).convert_alpha()
				for name in IMG_NAMES}
port = 'COM4' #/dev/ttyACM0	
baudRate = 9600
path2 = "ClinicalData"
path1 = os.getcwd()

class ClinicalData(object):
	def __init__(self):
		self.time = []
		self.potentiometer = []
		self.lefthand = []
		self.righthand = []
		self.score = []
		self.lives = []
		self.stress = []
		self.now = datetime.datetime.now()
		# print(self.now)

		
	def update(self, time, pot, lefth, righth, score, lives, stress):
		self.time.append(time)
		self.potentiometer.append(pot)
		self.lefthand.append(lefth)
		self.righthand.append(righth)
		self.score.append(score)
		self.lives.append(lives)
		self.stress.append(stress)
		
	def report(self):
		today = str(self.now.strftime("%Y-%m-%d %H-%M"))
		title = "Time_data" + today + ".dat"
		file_time = open(title,"a") 
		title = "Pot_data" + today + ".dat"
		file_pot = open(title,"a") 
		title = "Left_data" + today + ".dat"
		file_left = open(title,"a") 	
		title = "Right_data" + today + ".dat"
		file_right = open(title,"a") 	
		title = "Score_data" + today + ".dat"
		file_score = open(title,"a") 
		title = "Lives_data" + today + ".dat"
		file_lives = open(title,"a") 
		title = "Stress_data" + today + ".dat"
		file_stress = open(title,"a") 

		# file_time = open("Time_data.dat","a") 
		# file_pot = open("Pot_data.dat","a")
		# file_left = open("Left_data.dat","a")
		# file_right = open("Right_data.dat","a")
		# file_score = open("Score_data.dat","a")
		# file_lives = open("Lives_data.dat","a")
		# file_stress = open("Stress_data.dat","a")
		for t in self.time:
			t = str(t) + '\n'
			file_time.write(t)
		for p in self.potentiometer:
			p = str(p) + '\n'
			file_pot.write(p)
		for hl in self.lefthand:
			hl = str(hl) + '\n'
			file_left.write(hl)
		for hr in self.righthand:
			hr = str(hr) + '\n'
			file_right.write(hr)
		for sc in self.score:
			sc = str(sc) + '\n'
			file_score.write(sc)
		for l in self.lives:
			l = str(l) + '\n'
			file_lives.write(l)
		for st in self.stress:
			st = str(st) + '\n'
			file_stress.write(st)

		file_time.close()
		file_pot.close()
		file_left.close()
		file_right.close()
		file_score.close()
		file_lives.close()
		file_stress.close()

class Ship(sprite.Sprite):
	def __init__(self):
		sprite.Sprite.__init__(self)
		self.image = IMAGES["ship"]
		self.image = transform.scale(self.image, (65, 65))
		self.rect = self.image.get_rect(topleft=(SCREEN_W/2-65/2, SCREEN_H-90))
		self.speed = 1
		self.potar = 0;
		self.desiredPos = math.ceil(SCREEN_W/2-50);
		self.conversionRatio = 4

	def update(self, keys, *args):
		self.desiredPos = int(math.ceil(self.potar*self.conversionRatio)+SCREEN_W/2-50)
		if self.desiredPos < 10:
			self.desiredPos = 10;
		elif self.desiredPos > (SCREEN_W-75):
			self.desiredPos = SCREEN_W-75
		while self.rect.x < self.desiredPos:
			self.rect.x += self.speed
		while self.rect.x > self.desiredPos:
			self.rect.x -= self.speed

		# if self.potentiometer>0 and self.rect.x > 10: #MODIF1 = left angle/right angle !!!
		# 	self.rect.x -= self.speed
		# if self.potentiometer<0  and self.rect.x < SCREEN_W-60:
		# 	self.rect.x += self.speed
		game.screen.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
	def __init__(self, xpos, ypos, direction, speed, filename, side):
		sprite.Sprite.__init__(self)
		self.image = IMAGES[filename]
		self.image = transform.scale(self.image, (8, 30))
		self.rect = self.image.get_rect(topleft=(xpos, ypos))
		self.speed = 1.5*speed
		self.direction = direction
		self.side = side
		self.filename = filename

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)
		self.rect.y += self.speed * self.direction
		if self.rect.y < 15 or self.rect.y > SCREEN_H:
			self.kill()


class Enemy(sprite.Sprite):
	def __init__(self, row, column):
		sprite.Sprite.__init__(self)
		self.row = row
		self.column = column
		self.images = []
		self.load_images()
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.direction = 1
		self.rightMoves = 11 # HARD CODED DEPENDS ON THE SCREEN SIZE
		self.leftMoves = 22 # HARD CODED DEPENDS ON THE SCREEN SIZE ADAPTED TO ROW 9
		self.moveNumber = 0
		self.moveTime = 600
		self.firstTime = True
		self.movedY = False;
		self.columns = [False] * 10
		self.aliveColumns = [True] * 10
		self.addRightMoves = False
		self.addLeftMoves = False
		self.numOfRightMoves = 0
		self.numOfLeftMoves = 0
		self.timer = time.get_ticks()

	def update(self, keys, currentTime, killedRow, killedColumn, killedArray):
		self.check_column_deletion(killedRow, killedColumn, killedArray)
		if currentTime - self.timer > self.moveTime:
			self.movedY = False;
			if self.moveNumber >= self.rightMoves and self.direction == 1:
				self.direction *= -1
				self.moveNumber = 0
				self.rect.y += 55
				self.movedY = True
				if self.addRightMoves:
					self.rightMoves += self.numOfRightMoves
				if self.firstTime:
					self.rightMoves = self.leftMoves;
					self.firstTime = False;
				self.addRightMovesAfterDrop = False
			if self.moveNumber >= self.leftMoves and self.direction == -1:
				self.direction *= -1
				self.moveNumber = 0
				self.rect.y += 55
				self.movedY = True
				if self.addLeftMoves:
					self.leftMoves += self.numOfLeftMoves
				self.addLeftMovesAfterDrop = False
			if self.moveNumber < self.rightMoves and self.direction == 1 and not self.movedY:
				self.rect.x += 30
				self.moveNumber += 1
			if self.moveNumber < self.leftMoves and self.direction == -1 and not self.movedY:
				self.rect.x -= 30
				self.moveNumber += 1

			self.index += 1
			if self.index >= len(self.images):
				self.index = 0
			self.image = self.images[self.index]

			self.timer += self.moveTime
		game.screen.blit(self.image, self.rect)

	def check_column_deletion(self, killedRow, killedColumn, killedArray):
		if killedRow != -1 and killedColumn != -1:
			killedArray[killedRow][killedColumn] = 1
			for column in range(10):
				if all([killedArray[row][column] == 1 for row in range(5)]):
					self.columns[column] = True

		for i in range(5):
			if all([self.columns[x] for x in range(i + 1)]) and self.aliveColumns[i]:
				self.leftMoves += 2
				self.aliveColumns[i] = False
				if self.direction == -1:
					self.rightMoves += 2
				else:
					self.addRightMoves = True
					self.numOfRightMoves += 2
					
		for i in range(5):
			if all([self.columns[x] for x in range(9, 8 - i, -1)]) and self.aliveColumns[9 - i]:
				self.aliveColumns[9 - i] = False
				self.rightMoves += 2
				if self.direction == 1:
					self.leftMoves += 2
				else:
					self.addLeftMoves = True
					self.numOfLeftMoves += 2

	def load_images(self):
		images = {0: ["1_2", "1_1"], # DECIDE THE ROW WE WANT TO SHOW SEE ROW/COLUMN
				  1: ["2_2", "2_1"], # ADAPTED TO COLUMN 4
				  2: ["2_2", "2_1"],
				  3: ["3_1", "3_2"],
				  4: ["3_1", "3_2"],
				 }
		img1, img2 = (IMAGES["enemy{}".format(img_num)] for img_num in images[self.row])
		self.images.append(transform.scale(img1, (60, 50)))
		self.images.append(transform.scale(img2, (60, 50)))


class Blocker(sprite.Sprite):
	def __init__(self, size, color, row, column):
	   sprite.Sprite.__init__(self)
	   self.height = size
	   self.width = size
	   self.color = color
	   self.image = Surface((self.width, self.height))
	   self.image.fill(self.color)
	   self.rect = self.image.get_rect()
	   self.row = row
	   self.column = column

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
	def __init__(self):
		sprite.Sprite.__init__(self)
		self.image = IMAGES["mystery"]
		self.image = transform.scale(self.image, (100, 50))
		self.rect = self.image.get_rect(topleft=(-80, 45))
		self.row = 5
		self.moveTime = 40000
		self.direction = 1
		self.timer = time.get_ticks()
		self.mysteryEntered = mixer.Sound('sounds/mysteryentered.wav')
		self.mysteryEntered.set_volume(0.3)
		self.playSound = True

	def update(self, keys, currentTime, *args):
		resetTimer = False
		if (currentTime - self.timer > self.moveTime) and (self.rect.x < 0 or self.rect.x > SCREEN_W) and self.playSound:
			self.mysteryEntered.play()
			self.playSound = False
		if (currentTime - self.timer > self.moveTime) and self.rect.x < SCREEN_W+50 and self.direction == 1:
			self.mysteryEntered.fadeout(4000)
			self.rect.x += 2
			game.screen.blit(self.image, self.rect)
		if (currentTime - self.timer > self.moveTime) and self.rect.x > -100 and self.direction == -1:
			self.mysteryEntered.fadeout(4000)
			self.rect.x -= 2
			game.screen.blit(self.image, self.rect)
		if (self.rect.x > SCREEN_W+40):
			self.playSound = True
			self.direction = -1
			resetTimer = True
		if (self.rect.x < -90):
			self.playSound = True
			self.direction = 1
			resetTimer = True
		if (currentTime - self.timer > self.moveTime) and resetTimer:
			self.timer = currentTime

	
class Explosion(sprite.Sprite):
	def __init__(self, xpos, ypos, row, ship, mystery, score):
		sprite.Sprite.__init__(self)
		self.isMystery = mystery
		self.isShip = ship
		if mystery:
			self.text = Text(FONT, 20, str(score), WHITE, xpos+20, ypos+6)
		elif ship:
			self.image = IMAGES["ship"]
			self.image = transform.scale(self.image, (65, 65))
			self.rect = self.image.get_rect(topleft=(xpos, ypos))
		else:
			self.row = row
			self.load_image()
			self.image = transform.scale(self.image, (40, 35))
			self.rect = self.image.get_rect(topleft=(xpos, ypos))
			game.screen.blit(self.image, self.rect)
			
		self.timer = time.get_ticks()
		
	def update(self, keys, currentTime):
		if self.isMystery:
			if currentTime - self.timer <= 200:
				self.text.draw(game.screen)
			if currentTime - self.timer > 400 and currentTime - self.timer <= 600:
				self.text.draw(game.screen)
			if currentTime - self.timer > 600:
				self.kill()
		elif self.isShip:
			if currentTime - self.timer > 300 and currentTime - self.timer <= 600:
				game.screen.blit(self.image, self.rect)
			if currentTime - self.timer > 900:
				self.kill()
		else:
			if currentTime - self.timer <= 100:
				game.screen.blit(self.image, self.rect)
			if currentTime - self.timer > 100 and currentTime - self.timer <= 200:
				self.image = transform.scale(self.image, (50, 45))
				game.screen.blit(self.image, (self.rect.x-6, self.rect.y-6))
			if currentTime - self.timer > 400:
				self.kill()
	
	def load_image(self):
		imgColors = ["purple", "blue", "blue", "green", "green"]
		self.image = IMAGES["explosion{}".format(imgColors[self.row])]

			
class Life(sprite.Sprite):
	def __init__(self, xpos, ypos):
		sprite.Sprite.__init__(self)
		self.image = IMAGES["ship"]
		self.image = transform.scale(self.image, (30, 30))
		self.rect = self.image.get_rect(topleft=(xpos, ypos))
		
	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)


class Text(object):
	def __init__(self, textFont, size, message, color, xpos, ypos):
		self.font = font.Font(textFont, size)
		self.surface = self.font.render(message, True, color)
		self.rect = self.surface.get_rect(topleft=(xpos, ypos))

	def draw(self, surface):
		surface.blit(self.surface, self.rect)

class ArduinoCom(object):
	def __init__(self):
		init()
		self.arduino = serial.Serial(port, baudRate, timeout = 5)
		self.handOnPos = False
		self.rightHand = False
		self.leftHand = True
		self.potar = 0
		self.potar0 = 702

	def event(self):
		running = True
		while running:
			data = self.arduino.readline()
			data = data.decode("utf-8")
			if len(data) > 5:
				running = False
		# print(data)
		a,b,c = data.split("<")
		self.potar = float(a)
		RightHand = float(b)
		LeftHand = float(c)
		if RightHand == 1 and LeftHand == 1:
			self.handOnPos = True
			self.rightHand = True
			self.leftHand = True
		elif RightHand == 1 and LeftHand == 0:
			self.handOnPos = False
			self.rightHand = True
			self.leftHand = False
		elif RightHand == 0 and LeftHand == 1:
			self.handOnPos = False
			self.rightHand = False
			self.leftHand = True
		else:
			self.handOnPos = False
			self.rightHand = False
			self.leftHand = False

class SpaceInvaders(object):
	def __init__(self):
		mixer.pre_init(44100, -16, 1, 512)
		init()
		self.caption = display.set_caption('Space Invaders')
		self.screen = SCREEN
		self.background = image.load('images/background.jpg').convert()
		self.background = transform.scale(self.background , (SCREEN_W, SCREEN_H))
		self.startGame = False
		self.startCalib = False
		self.handsOff = False
		self.mainScreen1 = True
		self.mainScreen2 = False
		self.gameOver = False
		# Initial value for a new game
		self.enemyPositionDefault = 40
		# Counter for enemy starting position (increased each new round)
		self.enemyPositionStart = self.enemyPositionDefault
		# Current enemy starting position
		self.enemyPosition = self.enemyPositionStart
		# Communicate with Arduino
		self.com = ArduinoCom()
		self.lastTime = 0
		self.strongRight = 0
		self.strongLeft = 0 
		self.bothOn = 0
		# Collect Clinical Data
		self.clinical_data = ClinicalData()


	def reset(self, score, lives, newGame=False):
		self.player = Ship()
		self.playerGroup = sprite.Group(self.player)
		self.explosionsGroup = sprite.Group()
		self.bullets = sprite.Group()
		self.mysteryShip = Mystery()
		self.mysteryGroup = sprite.Group(self.mysteryShip)
		self.enemyBullets = sprite.Group()
		self.reset_lives(lives)
		self.enemyPosition = self.enemyPositionStart
		self.make_enemies()
		# Only create blockers on a new game, not a new round
		if newGame:
			self.allBlockers = sprite.Group(self.make_blockers(0), self.make_blockers(1), self.make_blockers(2), self.make_blockers(3))
		self.keys = key.get_pressed()
		self.clock = time.Clock()
		self.timer = time.get_ticks()
		self.noteTimer = time.get_ticks()
		self.shipTimer = time.get_ticks()
		self.score = score
		self.lives = lives
		self.create_audio()
		self.create_text()
		self.killedRow = -1
		self.killedColumn = -1
		self.makeNewShip = False
		self.shipAlive = True
		self.killedArray = [[0] * 10 for x in range(5)]

	def make_blockers(self, number):
		blockerGroup = sprite.Group() # HARD CODED ADAPTED TO SCREEN
		if self.strongRight > self.strongLeft:
			for row in range(5):
				for column in range(12):
					blocker = Blocker(10, GREEN, row, column)
					blocker.rect.x = SCREEN_W/2 - 20 + (180 * number) + (column * blocker.width)
					blocker.rect.y = SCREEN_H - 150 + (row * blocker.height)
					blockerGroup.add(blocker)
		if self.strongRight < self.strongLeft:
			for row in range(5):
				for column in range(12):
					blocker = Blocker(10, GREEN, row, column)
					blocker.rect.x = 20 + (180 * number) + (column * blocker.width)
					blocker.rect.y = SCREEN_H - 150 + (row * blocker.height)
					blockerGroup.add(blocker)
		return blockerGroup
	
	def reset_lives_sprites(self):
		self.life1 = Life(SCREEN_W-110, 3)
		self.life2 = Life(SCREEN_W-75, 3)
		self.life3 = Life(SCREEN_W-40, 3)
		
		if self.lives == 3:
			self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)
		elif self.lives == 2:
			self.livesGroup = sprite.Group(self.life1, self.life2)
		elif self.lives == 1:
			self.livesGroup = sprite.Group(self.life1)
	
	def reset_lives(self, lives):
		self.lives = lives
		self.reset_lives_sprites()
	
	def create_audio(self):
		self.sounds = {}
		for sound_name in ["shoot", "shoot2", "invaderkilled", "mysterykilled", "shipexplosion"]:
			self.sounds[sound_name] = mixer.Sound("sounds/{}.wav".format(sound_name))
			self.sounds[sound_name].set_volume(0.2)

		self.musicNotes = [mixer.Sound("sounds/{}.wav".format(i)) for i in range(4)]
		for sound in self.musicNotes:
			sound.set_volume(0.5)

		self.noteIndex = 0

	def play_main_music(self, currentTime):
		moveTime = self.enemies.sprites()[0].moveTime
		if currentTime - self.noteTimer > moveTime:
			self.note = self.musicNotes[self.noteIndex]
			if self.noteIndex < 3:
				self.noteIndex += 1
			else:
				self.noteIndex = 0

			self.note.play()
			self.noteTimer += moveTime

	def create_text(self):
		self.titleText = Text(FONT, 90, "Space Invaders", WHITE, 250, 100)
		self.titleText2 = Text(FONT, 60, "Place both hands on the See-Saw", WHITE, 60, 240)
		self.titleText3 = Text(FONT, 60, "to start the calibration", WHITE, 200, 320)
		self.titleText4 = Text(FONT, 60, "Place both hands on to start", WHITE, 120, 240)

		self.gameOverText = Text(FONT, 90, "Game Over", WHITE, 400, 320)
		self.nextRoundText = Text(FONT, 90, "Next Round", WHITE, 370, 320)
		
		self.enemy1Text = Text(FONT, 50, "   =   10 pts", GREEN, 600, 370)
		self.enemy2Text = Text(FONT, 50, "   =  20 pts", BLUE, 600, 470)
		self.enemy3Text = Text(FONT, 50, "   =  30 pts", PURPLE, 600, 570)
		self.enemy4Text = Text(FONT, 50, "   =  ?????", RED, 600, 670)
		
		self.scoreText = Text(FONT, 25, "Score", WHITE, 5, 5)
		self.livesText = Text(FONT, 25, "Lives ", WHITE, SCREEN_W-200, 5)

		self.handsOffText1 = Text(FONT, 90, "Please take", WHITE, 300, 250)
		self.handsOffText2 = Text(FONT, 90, "your hands off !", WHITE, 200, 420)
		self.CalibText1 = Text(FONT, 60, "Place your strong hand", WHITE, 250, 100)
		self.CalibText2 = Text(FONT, 60, "on the see saw", WHITE, 420, 200)
		self.ReadyText = Text(FONT, 90, "Get ready to play !", WHITE, 140, 320)
	
	def check_input(self):
		self.com.event()
		self.player.potar = self.com.potar - self.com.potar0

		if self.com.handOnPos:
			if len(self.bullets) == 0 and self.shipAlive:
				if self.score < 1000:
					bullet = Bullet(self.player.rect.x+23, self.player.rect.y+5, -1, 15, "laser", "center")
					self.bullets.add(bullet)
					self.allSprites.add(self.bullets)
					self.sounds["shoot"].play()
				else:
					leftbullet = Bullet(self.player.rect.x+8, self.player.rect.y+5, -1, 15, "laser", "left")
					rightbullet = Bullet(self.player.rect.x+38, self.player.rect.y+5, -1, 15, "laser", "right")
					self.bullets.add(leftbullet)
					self.bullets.add(rightbullet)
					self.allSprites.add(self.bullets)
					self.sounds["shoot2"].play()

	def make_enemies(self):
		enemies = sprite.Group()
		for row in range(5): # ROW COLUMN ENEMIES
			for column in range(10):
				enemy = Enemy(row, column)
				enemy.rect.x = SCREEN_W/4 + (column * 70)
				enemy.rect.y = self.enemyPosition + (row * 60)
				enemies.add(enemy)
		
		self.enemies = enemies
		self.allSprites = sprite.Group(self.player, self.enemies, self.livesGroup, self.mysteryShip)

	def make_enemies_shoot(self):
		columnList = []
		for enemy in self.enemies:
			columnList.append(enemy.column)

		columnSet = set(columnList)
		columnList = list(columnSet)
		shuffle(columnList)
		column = columnList[0]
		enemyList = []
		rowList = []

		for enemy in self.enemies:
			if enemy.column == column:
				rowList.append(enemy.row)
		row = max(rowList)
		for enemy in self.enemies:
			if enemy.column == column and enemy.row == row:
				if (time.get_ticks() - self.timer) > 1000:
					self.enemyBullets.add(Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5, "enemylaser", "center"))
					self.allSprites.add(self.enemyBullets)
					self.timer = time.get_ticks() 

	def calculate_score(self, row):
		scores = {0: 30,
				  1: 20,
				  2: 20,
				  3: 10,
				  4: 10,
				  5: choice([50, 100, 150, 300])
				 }
					  
		score = scores[row]
		self.score += score
		return score

	def create_main_menu(self):
		self.enemy1 = IMAGES["enemy3_1"]
		self.enemy1 = transform.scale(self.enemy1 , (60, 60))
		self.enemy2 = IMAGES["enemy2_2"]
		self.enemy2 = transform.scale(self.enemy2 , (60, 60))
		self.enemy3 = IMAGES["enemy1_2"]
		self.enemy3 = transform.scale(self.enemy3 , (60, 60))
		self.enemy4 = IMAGES["mystery"]
		self.enemy4 = transform.scale(self.enemy4 , (120, 60))
		self.screen.blit(self.enemy1, (520, 370))
		self.screen.blit(self.enemy2, (520, 470))
		self.screen.blit(self.enemy3, (520, 570))
		self.screen.blit(self.enemy4, (490, 670))

		self.com.event()
		# if self.com.handOnPos == True:
		# 	self.bothOn += 1
		# else:
		# 	self.bothOn = 0
		if self.com.handOnPos:
		# if self.bothOn >= 10:
			self.mainScreen3 = True
			self.mainScreen2 = False
			self.timer = time.get_ticks()
	
	def update_enemy_speed(self):
		if len(self.enemies) <= 10:
			for enemy in self.enemies:
				enemy.moveTime = 400
		if len(self.enemies) == 1:
			for enemy in self.enemies:
				enemy.moveTime = 200
				
	def check_collisions(self):
		collidedict = sprite.groupcollide(self.bullets, self.enemyBullets, True, False)
		if collidedict:
			for value in collidedict.values():
				for currentSprite in value:
					self.enemyBullets.remove(currentSprite)
					self.allSprites.remove(currentSprite)

		enemiesdict = sprite.groupcollide(self.bullets, self.enemies, True, False)
		if enemiesdict:
			for value in enemiesdict.values():
				for currentSprite in value:
					self.sounds["invaderkilled"].play()
					self.killedRow = currentSprite.row
					self.killedColumn = currentSprite.column
					score = self.calculate_score(currentSprite.row)
					explosion = Explosion(currentSprite.rect.x, currentSprite.rect.y, currentSprite.row, False, False, score)
					self.explosionsGroup.add(explosion)
					self.allSprites.remove(currentSprite)
					self.enemies.remove(currentSprite)
					self.gameTimer = time.get_ticks()
					break
		
		mysterydict = sprite.groupcollide(self.bullets, self.mysteryGroup, True, True)
		if mysterydict:
			for value in mysterydict.values():
				for currentSprite in value:
					currentSprite.mysteryEntered.stop()
					self.sounds["mysterykilled"].play()
					score = self.calculate_score(currentSprite.row)
					explosion = Explosion(currentSprite.rect.x, currentSprite.rect.y, currentSprite.row, False, True, score)
					self.explosionsGroup.add(explosion)
					self.allSprites.remove(currentSprite)
					self.mysteryGroup.remove(currentSprite)
					newShip = Mystery()
					self.allSprites.add(newShip)
					self.mysteryGroup.add(newShip)
					break

		bulletsdict = sprite.groupcollide(self.enemyBullets, self.playerGroup, True, False)     
		if bulletsdict:
			for value in bulletsdict.values():
				for playerShip in value:
					if self.lives == 3:
						self.lives -= 1
						self.livesGroup.remove(self.life3)
						self.allSprites.remove(self.life3)
					elif self.lives == 2:
						self.lives -= 1
						self.livesGroup.remove(self.life2)
						self.allSprites.remove(self.life2)
					elif self.lives == 1:
						self.lives -= 1
						self.livesGroup.remove(self.life1)
						self.allSprites.remove(self.life1)
					elif self.lives == 0:
						self.gameOver = True
						self.startGame = False
					self.sounds["shipexplosion"].play()
					explosion = Explosion(playerShip.rect.x, playerShip.rect.y, 0, True, False, 0)
					self.explosionsGroup.add(explosion)
					self.allSprites.remove(playerShip)
					self.playerGroup.remove(playerShip)
					self.makeNewShip = True
					self.shipTimer = time.get_ticks()
					self.shipAlive = False

		if sprite.groupcollide(self.enemies, self.playerGroup, True, True):
			self.gameOver = True
			self.startGame = False
	
		sprite.groupcollide(self.bullets, self.allBlockers, True, False)
		sprite.groupcollide(self.enemyBullets, self.allBlockers, True, False)
		sprite.groupcollide(self.enemies, self.allBlockers, False, True)

	def create_new_ship(self, createShip, currentTime):
		if createShip and (currentTime - self.shipTimer > 900):
			self.player = Ship()
			self.allSprites.add(self.player)
			self.playerGroup.add(self.player)
			self.makeNewShip = False
			self.shipAlive = True

	def create_game_over(self, currentTime):
		self.screen.blit(self.background, (0,0))
		if currentTime - self.timer < 750:
			self.gameOverText.draw(self.screen)
		if currentTime - self.timer > 750 and currentTime - self.timer < 1500:
			self.screen.blit(self.background, (0,0))
		if currentTime - self.timer > 1500 and currentTime - self.timer < 2250:
			self.gameOverText.draw(self.screen)
		if currentTime - self.timer > 2250 and currentTime - self.timer < 2750:
			self.screen.blit(self.background, (0,0))
		if currentTime - self.timer > 2750 and currentTime - self.timer < 3500:
			self.gameOverText.draw(self.screen)
		if currentTime - self.timer > 3500 and currentTime - self.timer < 4250:
			self.screen.blit(self.background, (0,0))
		if currentTime - self.timer > 4500:
			self.mainScreen2 = True
		
		for e in event.get():
			if e.type == QUIT:
				sys.exit()

	def main(self):
		while True:
			if self.mainScreen1:
				self.reset(0, 3, True)
				self.screen.blit(self.background, (0,0))
				self.titleText.draw(self.screen)
				self.titleText2.draw(self.screen)
				self.titleText3.draw(self.screen)
				self.enemy1 = IMAGES["enemy3_1"]
				self.enemy1 = transform.scale(self.enemy1 , (100, 100))
				self.enemy2 = IMAGES["enemy2_2"]
				self.enemy2 = transform.scale(self.enemy2 , (100, 100))
				self.enemy3 = IMAGES["enemy1_2"]
				self.enemy3 = transform.scale(self.enemy3 , (100, 100))
				self.enemy4 = IMAGES["mystery"]
				self.enemy4 = transform.scale(self.enemy4 , (200, 100))
				self.screen.blit(self.enemy1, (370, 500))
				self.screen.blit(self.enemy2, (520, 500))
				self.screen.blit(self.enemy3, (670, 500))
				self.screen.blit(self.enemy4, (810, 500))
				self.com.event()
				if self.com.handOnPos:
					self.handsOff = True
					self.mainScreen1 = False

			elif self.handsOff:
				self.screen.blit(self.background, (0,0))
				self.handsOffText1.draw(self.screen)
				self.handsOffText2.draw(self.screen)

				self.com.event()
				if self.com.rightHand == False and self.com.leftHand == False:
					time.wait(500)
					self.handsOff = False
					self.startCalib = True

			elif self.startCalib:
				self.screen.blit(self.background, (0,0))
				self.CalibText1.draw(self.screen)
				self.CalibText2.draw(self.screen)
				self.handR = IMAGES["righthand"]
				self.handR = transform.scale(self.handR , (350, 350))
				self.handL = IMAGES["lefthand"]
				self.handL = transform.scale(self.handL , (350, 350))
				self.screen.blit(self.handL, (270, 350))
				self.screen.blit(self.handR, (730, 350))

				self.com.event()
				if self.com.rightHand == True:
					self.strongRight += 1
				else:
					self.strongRight = 0
				if self.com.leftHand == True:
					self.strongLeft += 1
				else:
					self.strongLeft = 0
				if self.strongRight >= 30 or self.strongLeft >= 30:
					if self.strongRight >= self.strongLeft:
						self.handText1 = Text(FONT, 70, "You've selected right", WHITE, 170, 250)
						self.handText2 = Text(FONT, 70, "as your strong hand", WHITE, 210, 420)

					else:
						self.handText1 = Text(FONT, 70, "You've selected left", WHITE, 170, 250)
						self.handText2 = Text(FONT, 70, "as your strong hand", WHITE, 200, 420)
					self.handsSelection = True
					self.startCalib = False
					self.timer = time.get_ticks()

			elif self.handsSelection:
				self.screen.blit(self.background, (0,0))
				self.handText1.draw(self.screen)
				self.handText2.draw(self.screen)
				currentTime = time.get_ticks()

				# if currentTime - self.timer < 750:
				# 	self.handText1.draw(self.screen)
				# 	self.handText2.draw(self.screen)
				# if currentTime - self.timer > 750 and currentTime - self.timer < 1500:
				# 	self.screen.blit(self.background, (0,0))
				# if currentTime - self.timer > 1500 and currentTime - self.timer < 2250:
				# 	self.handText1.draw(self.screen)
				# 	self.handText2.draw(self.screen)
				# if currentTime - self.timer > 2250 and currentTime - self.timer < 2750:
				# 	self.screen.blit(self.background, (0,0))
				# if currentTime - self.timer > 2750 and currentTime - self.timer < 3500:
				# 	self.handText1.draw(self.screen)
				# 	self.handText2.draw(self.screen)
				# if currentTime - self.timer > 3500 and currentTime - self.timer < 4250:
				# 	self.screen.blit(self.background, (0,0))
				# if currentTime - self.timer > 4500:
				# 	self.handsSelection = False
				# 	self.mainScreen2 = True
				if currentTime - self.timer > 1500:
					self.handsSelection = False
					self.mainScreen2 = True
		
			elif self.mainScreen2:
				self.screen.blit(self.background, (0,0))
				self.reset(0, 3, True)
				self.titleText.draw(self.screen)
				self.titleText4.draw(self.screen)
				self.enemy1Text.draw(self.screen)
				self.enemy2Text.draw(self.screen)
				self.enemy3Text.draw(self.screen)
				self.enemy4Text.draw(self.screen)
				self.create_main_menu()

			elif self.mainScreen3:
				self.screen.blit(self.background, (0,0))
				self.ReadyText.draw(self.screen)
				currentTime = time.get_ticks()

				# if currentTime - self.timer < 750:
				# 	self.handsOffText1.draw(self.screen)
				# 	self.handsOffText2.draw(self.screen)
				# if currentTime - self.timer > 750 and currentTime - self.timer < 1500:
				# 	self.screen.blit(self.background, (0,0))
				# if currentTime - self.timer > 1500 and currentTime - self.timer < 2250:
				# 	self.ReadyText.draw(self.screen)
				# if currentTime - self.timer > 2250 and currentTime - self.timer < 2750:
				# 	self.screen.blit(self.background, (0,0))
				# # if currentTime - self.timer > 2750 and currentTime - self.timer < 3500:
				# # 	self.SetGoText.draw(self.screen)
				# # if currentTime - self.timer > 3500 and currentTime - self.timer < 4250:
				# # 	self.screen.blit(self.background, (0,0))
				if currentTime - self.timer > 1500:
					self.mainScreen3 = False
					self.startGame = True


			elif self.startGame:
				if len(self.enemies) == 0:
					currentTime = time.get_ticks()
					if currentTime - self.gameTimer < 3000:          
						self.screen.blit(self.background, (0,0))
						self.scoreText2 = Text(FONT, 25, str(self.score), GREEN, 115, 5)
						self.scoreText.draw(self.screen)
						self.scoreText2.draw(self.screen)
						self.nextRoundText.draw(self.screen)
						self.livesText.draw(self.screen)
						self.livesGroup.update(self.keys)
						self.check_input()
					if currentTime - self.gameTimer > 3000:
						# Move enemies closer to bottom
						self.enemyPositionStart += 35
						self.reset(self.score, self.lives)
						self.make_enemies()
						self.gameTimer += 3000
				else:
					currentTime = time.get_ticks()
					self.play_main_music(currentTime)              
					self.screen.blit(self.background, (0,0))
					self.allBlockers.update(self.screen)
					self.scoreText2 = Text(FONT, 25, str(self.score), GREEN, 115, 5)
					self.scoreText.draw(self.screen)
					self.scoreText2.draw(self.screen)
					self.livesText.draw(self.screen)
					self.check_input()
					self.allSprites.update(self.keys, currentTime, self.killedRow, self.killedColumn, self.killedArray)
					self.explosionsGroup.update(self.keys, currentTime)
					self.check_collisions()
					self.create_new_ship(self.makeNewShip, currentTime)
					self.update_enemy_speed()

					if len(self.enemies) > 0:
						self.make_enemies_shoot()

					stress = 0	
					for bullet in self.enemyBullets:
						stress += 1/(0.01+100*(bullet.rect.x-self.player.rect.x)**2+(bullet.rect.y-self.player.rect.y)**2)
					
					if self.com.leftHand:
						left = 1
					else:
						left = 0

					if self.com.rightHand:
						right = 1
					else:
						right = 0
						
					self.clinical_data.update(time.get_ticks(), self.com.potar, left, right, self.score, self.lives, stress)
	
	
			elif self.gameOver:
				currentTime = time.get_ticks()
				# Reset enemy starting position
				self.enemyPositionStart = self.enemyPositionDefault
				self.create_game_over(currentTime)
				os.chdir(path2)
				self.clinical_data.report()
				os.chdir(path1)


			display.update()
			self.clock.tick(60)
				

if __name__ == '__main__':
	game = SpaceInvaders()
	game.main()