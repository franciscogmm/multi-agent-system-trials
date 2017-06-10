from random import randint
from threading import Thread, Semaphore
import threading
from multiprocessing import Process
import time
import curses

screenlock = Semaphore(value = 1)
#use daemonic thread for global countdown
class Agent(Thread):
	'''Represents a physical object that can appear in an environment. Subclass object to get the objects needed. Each object can have a .__name__ slot.'''
	def __init__(self,E_init):
		Thread.__init__(self)
		percepts = []
		self.E_init = E_init #initial fitness
		#self.vote_remaining = 1
		self.see_heartbeat = 0
		self.ETO = E_init
		self.E = E_init
		#self.signature = signature
		
class Basic(Agent):
	def __init__(self, E_init):
		Agent.__init__(self,E_init)

	def run(self):
		for i in range(self.ETO, 0, -1):
			screenlock.acquire()
			print self.__class__.__name__, self.getName(),'| Time to upgrade:', i
			screenlock.release()
			secondsToSleep = 1 #randint(1,5)
			#print self.getName(), 'sleeping for', secondsToSleep, 'seconds'
			time.sleep(secondsToSleep)
		screenlock.acquire()
		print self.__class__.__name__, self.getName(), 'changed to Better Agent.'
		screenlock.release()
		self.__class__ = Better
		newcand = Better(100)
		newcand.start()
		newcand.join()
		# screenlock.acquire()
		# print self.__class__.__name__
		# screenlock.release()

class Better(Agent):
	def __init__(self, E_init):
		Agent.__init__(self, E_init)

	def run(self):
		main_thread = threading.current_thread()
		for t in threading.enumerate():
			if t is main_thread:
				print 'Better!'
				continue
			else: 
				print t
 
if __name__ == '__main__':

	t1 = Basic(10)
	t1.setName('A')

	t2 = Basic(7)
	t2.setName('B')

	t3 = Basic(5)
	t3.setName('C')

	t1.start()
	t2.start()
	t3.start()

	t1.join()
	t2.join()
	t3.join()

	print 'done'