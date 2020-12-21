import pygame
import neat
import time
import os
import random

WIDTH = 500
HEIGHT = 600

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game AI")


class copter:
	"""docstring for copter"""
	def __init__(self, x, y):
		''' initialize the copter object and
			sets positional param '''
		self.x, self.y = x, y
		self.velocity = 0
		self.height = self.y
		# self.img = pygame.draw.circle(screen, BLUE, pos, 20)

	def draw(self):
		''' draw the copter on window '''

		myimage = pygame.image.load("img/copter.png")
		imagerect = myimage.get_rect()


		win.blit(myimage, imagerect)
		# while 1:
		#     your_code_here

		#     screen.fill(black)
		#     pygame.display.flip()

	def move(self):
		''' move the copter '''


run = True
while run:
	# to stop execution press 'q' on keyboard
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				run = False

	pygame.draw.circle(win, (255,0,0), (250, 300), 20)
	pygame.display.update()

pygame.quit()
quit()