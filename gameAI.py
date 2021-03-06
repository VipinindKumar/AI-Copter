import pygame
import neat
import random
import os
import pygame.freetype

from collections import deque

WIDTH = 500
HEIGHT = 600
FPS = 30
ACCELERATION = 1
BACKGROUND = (25,25,25)
OBSTCOLOR = (192,192,192)
TEXTCOLOR = (255,255,255)
ROTATION = 15
THICKNESS = 20
SPEED = 5
GAP = 100

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game AI")
generation = 0

class copter:
	"""docstring for copter"""
	def __init__(self, x, y):
		''' initialize the copter object and
			sets positional param '''
		self.x, self.y = x, y
		self.velocity = 0.5
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
		''' make the copter jump'''
		self.velocity = -4
		self.tick_cnt = 0

	def rect(self):
		'''returns the rect for the copter'''
		# return pygame.mask.from_surface(self.image)
		cRect = self.image.get_rect()
		cRect.topleft = (self.x, self.y)
		return cRect


class obstacle(object):
	"""docstring for obstacle"""
	def __init__(self,x, y):
		self.x, self.y = x, y
		self.width = random.randrange(100, 500)
		self.image = pygame.Rect(self.x, self.y, self.width, THICKNESS)
		self.varPassedEnd = False
		self.varPassedCopter = False
		self.varPassedScreen = False

	def draw(self):
		'''draws the obstacle rectangle
		at x,y with defined thickness and width'''
		self.image = pygame.Rect(self.x, self.y, self.width, THICKNESS)
		pygame.draw.rect(win, OBSTCOLOR, self.image)

	def move(self):
		'''move obstacle left by speed'''
		self.x -= SPEED

	def collision(self, copter):
		'''returns True if obstacle and 
		copter are overlapping'''
		return copter.rect().colliderect(self.image)

		# print(copterMask)
		# # obstacleMask = pygame.mask.from_surface(self.image)
		# pygame.sprite.collide_mask
		# # rect to surface
		# pygame.Surface((a.w, a.h))

	def passedEnd(self):
		'''fn to tell if end of the screen has been passed'''
		if self.varPassedEnd:
			return True

		if (self.x + self.width) < WIDTH:
			self.varPassedEnd = True
			return True
		return False

	def passedCopter(self):
		'''returns True if obstaces has passed copter or width/4
		'''
		if self.varPassedCopter:
			return True

		if (self.x + self.width) < (WIDTH / 4):
			self.varPassedCopter = True
			return True
		return False

	def passedScreen(self):
		'''if copter has passed the whole screen
		'''
		if self.varPassedScreen:
			return True

		if (self.x + self.width) < 0:
			self.varPassedScreen = True
			return True
		return False


def drawScreen(copters, obstacles, score):
	'''draws copters and obstacles and
		add labels for scroe and generation 
	'''
	global generation

	# clear screen
	win.fill(BACKGROUND)

	# draw all obstacles in the deque
	for obst in obstacles:
		obst.draw()

	# draw every copter
	for heli in copters:
		heli.draw()


	font = pygame.freetype.SysFont(None, 20)

	# label for score
	font.render_to(win, (10, 10), 'Score: ' + str(score), TEXTCOLOR)

    # label for generation
	font.render_to(win, (10, 40), 'Gen: ' + str(generation), TEXTCOLOR)

    #label for flying ccopters
	font.render_to(win, (10, 70), 'Flying: ' + str(len(copters)), TEXTCOLOR)

	pygame.display.update()


def eval_genomes(genomes, config):
	''' runs for every generation of copters,
		run the copter game for every copter 
		from the population simultaneously, 
		taking their actions from neural network
		and updating their fitness according to thier
		performance
	'''
	# vriable definations to be used in fn
	global generation
	generation += 1
	score = 0
	run = True
	fpsClock = pygame.time.Clock()
	obstacles = deque()
	obstacles.append(obstacle(500, 250))
	nnets = []
	copters = []
	gl = []

	# create copter, neuralnet for every genome in generation
	for genomeId, genome in genomes:
		# set initial fitness for copters to 0
		genome.fitness = 0
		nnet = neat.nn.FeedForwardNetwork.create(genome, config)
		nnets.append(nnet)
		copters.append(copter(WIDTH / 4, HEIGHT / 2))
		gl.append(genome)

	# run till no copter is left flying
	while len(copters) > 0 and run:
		fpsClock.tick(FPS)

		# to stop execution
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break

		# which obstacle the copter need to make decision on
		obstIndex = 0
		for obstIndex, obst in enumerate(obstacles):
			if not obst.passedCopter():
				break

		# move copter and predict if copter need to jump or not
		for i, heli in enumerate(copters):
			# increase fitness for copter for every frame survived
			gl[i].fitness += 0.1
			heli.move()

			# inputs y position of copter and vertical distance b/w copter and obstacle
			predict = nnets[i].activate((heli.y, (heli.y - obstacles[obstIndex].y)))
			if predict[0] > 0.5:
				heli.jump()

		# advance the game
		addObst = False
		removeObst = False
		for obst in obstacles:
			obst.move()
			
			# remove copter if collidede with obstacle
			for i, heli in enumerate(copters):
				if obst.collision(heli):
					gl[i].fitness -= 1
					gl.pop(i)
					nnets.pop(i)
					copters.pop(i)

			# add obstacle if needed
			if not obst.varPassedEnd and obst.passedEnd():
				addObst = True
				# ineffiecient implementation for getting gap
				cordY = obst.y
				rdm = cordY
				while rdm > (cordY-GAP) and rdm < (cordY+GAP):
					rdm = random.randrange(100, 500)

			# if copter passed this obstacle
			if not obst.varPassedCopter and obst.passedCopter():
				score += 1
				for genome in gl:
					genome.fitness += 10

			# remove obstacle that passed the screen
			if not obst.varPassedScreen and obst.passedScreen():
				removeObst = True

		# add obstacle
		if addObst:
			obstacles.append(obstacle(500, rdm))
		# remove obstacle
		if removeObst:
			obstacles.popleft()

		# remove copters that fallen down
		# or gone to space
		for i, heli in enumerate(copters):
			if heli.y >= HEIGHT:
				nnets.pop(i)
				copters.pop(i)
				gl.pop(i)
			elif heli.y < 0:
				nnets.pop(i)
				copters.pop(i)
				gl.pop(i)


		# draws copters, obstacles and add score on screen
		drawScreen(copters, obstacles, score)


def run(config_file):
	# Load configuration.
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
	                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
	                     config_file)

	# Create the population, which is the top-level object for a NEAT run.
	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))

	# Run for up to 50 generations.
	winner = p.run(eval_genomes, 50)


if __name__ == '__main__':
	# load the config file fot neat
	run(os.path.join(os.path.dirname(__file__),	'neatConfig.txt'))


################################################
'''
# code used for testing the copter game
copter1 = copter(WIDTH / 4, HEIGHT / 2)
obstrn = deque()
obstrn.append(obstacle(500, 250))

run = True
while run:
	# to stop execution press 'q' on keyboard
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				run = False
			elif event.key == pygame.K_j:
				copter1.jump()

	# clear screen
	win.fill(BACKGROUND)

	copter1.move()
	# if copter hit ground
	if copter1.y >= HEIGHT:
		run = False

	for obst in obstrn:
		obst.move()
		obst.draw()
		# stop the game if copter collided with obstacle
		if obst.collision(copter1):
			run = False

	# create new obstacle, to keep them adjacent
	if obstrn[-1].passedEnd():
		# code to get obstcles with a certain gap b/w them
		# cordY = obstrn[-1].y
		# rdm = random.randrange(100, cordY)
		# if rdm > (cordY - GAP):
		# 	rdm += (2 * GAP)

		# ineffiecient implementation for getting gap
		cordY = obstrn[-1].y
		rdm = cordY
		while rdm > (cordY-GAP) and rdm < (cordY+GAP):
			rdm = random.randrange(100, 500)

		obstrn.append(obstacle(500, rdm))

	copter1.draw()
	pygame.display.update()
	fpsClock.tick(FPS)

pygame.quit()
quit()
'''
################################################