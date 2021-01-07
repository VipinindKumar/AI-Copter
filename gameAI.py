import pygame
import neat
import time
import os
import random

WIDTH = 500
HEIGHT = 600
FPS = 30
ACCELERATION = 3
BACKGROUND = (0,0,0)
ROTATION = 15
THICKNESS = 5
OBSTCOLOR = (255,10,10)
SPEED = 5

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game AI")
fpsClock = pygame.time.Clock()

class copter:
	"""docstring for copter"""
	def __init__(self, x, y):
		''' initialize the copter object and
			sets positional param '''
		self.x, self.y = x, y
		self.velocity = 1
		self.tick_cnt = 0
		self.tilt = 0
		self.image = pygame.image.load("img/copter.png")

	def draw(self):
		''' draw the copter on window '''
		rotImage = pygame.transform.rotate(self.image, self.tilt)

		win.blit(rotImage, (self.x, self.y))

	def move(self):
		''' move the copter '''
		self.tick_cnt += 1

		# s = v*t + 1/2*a*t^2
		displ = (self.velocity * self.tick_cnt +
				(1/2) * (ACCELERATION) * (self.tick_cnt) ** 2)

		# stop accelerating after certain point, (kinda terminal velocity)
		if displ > 15:
			displ = 15

		# add tilt to the copter
		# tilt up if going up
		if displ < 0:
			self.tilt = ROTATION
		# else just point down
		else:
			self.tilt = -ROTATION

		# update the position of the copter
		self.y += displ

	def jump(self):
		''' make the bird jump'''
		self.velocity = -10
		self.tick_cnt = 0

class obstacle(object):
	"""docstring for obstacle"""
	def __init__(self,x, y):
		self.x, self.y = x, y
		self.width = random.randrange(100, 500)
		
	def draw(self):
		'''draws the obstacle rectangle
		at x,y with defined thickness and width'''
		self.image = pygame.Rect(self.x, self.y, self.x + self.width, self.y + THICKNESS)
		pygame.draw.rect(win, OBSTCOLOR, self.image)

	def move(self):
		'''move obstacle left by speed'''
		self.x -= SPEED

copter1 = copter(WIDTH / 4, HEIGHT / 2)
obst1 = obstacle(500, random.randrange(100, 500))

run = True
while run:
	# to stop execution press 'q' on keyboard
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				run = False
			elif event.key == pygame.K_j:
				copter1.jump()

	copter1.move()
	obst1.move()

	# clear screen
	win.fill(BACKGROUND)

	copter1.draw()
	obst1.draw()
	pygame.display.update()
	fpsClock.tick(FPS)

pygame.quit()
quit()