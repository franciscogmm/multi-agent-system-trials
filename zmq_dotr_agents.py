import zmq
import time
import sys
import random
from  multiprocessing import Process
from zmq.eventloop import ioloop, zmqstream
import simplejson

ioloop.install()

class Basic(object):
	def __init__(self,name, myport):
		self.name = name
		self.agent_type = 'Basic'
		self.Timer_initialize = random.randint(5,20) #initial fitness
		self.vote_remaining = 1
		self.see_heartbeat = 0
		self.Timer = self.Timer_initialize
		# self.E = self.Timer_initialize
		self.my_port = myport
		#sockets
		self.socket_agent = zmq.Context().socket(zmq.REP)
		self.socket_agent.bind('tcp://*:%s' % self.my_port)
		self.heartbeat_socket = zmq.Context().socket(zmq.PULL)
		self.allagents = {}
		self.heartbeat_socket_out = ''
		self.push_socket_agent = ''
		self.connected_to_best = {}
		self.best_details = ''
		self.allagents = {'A':'7770', 'B':'7771', 'C':'7772'} #hard coded for demonstration

	### GENERAL FUNCTIONS ###

	def reset(self):
		self.Timer = self.Timer_initialize

	### Basic FUNCTIONS ###

	def countdown(self):
		time.sleep(1)
		self.Timer -= 1

	def be_better(self):
		prev_position = self.agent_type
		self.agent_type = 'Better'
		print "%s %s became a %s" % (prev_position, self.name, self.agent_type)
			#connect to other agents' sockets and request for vote

	def connect_to_best(self,message):
		self.best_details = simplejson.loads(message.strip())
		print self.agent_type, self.name, ': Connecting to best.'
		self.heartbeat_socket.connect('tcp://localhost:%s' % self.best_details.get('best_heartbeat_port'))
		print self.agent_type, self.name, ': Connected!'


	### Better FUNCTIONS ###

	def make_me_best(self):
		#vote for self
		total_his = 1
		for agent, sock in self.allagents.iteritems():
			if agent == self.name:
				pass
			else:
				context = zmq.Context()
				send_hi = context.socket(zmq.REQ)
				print self.agent_type, self.name, ': connect to Agent', agent
				send_hi.connect('tcp://localhost:%s' % sock)
				#print self.name, ': sending vote request RPC'
				while True:
					send_hi.send(b'Hi! from %s' % (self.name))
					hi_received = send_hi.recv()
					if hi_received:
						print self.agent_type, self.name, ': %s Hi received from Agent' % hi_received, agent
						break
				total_his += 1

				
		return total_his

	def be_best(self):
		#establish new settings
		self.agent_type = 'Best'
		self.heartbeat_socket_out = zmq.Context().socket(zmq.PUSH) #try
		best_heartbeat_port = '9998'
		self.heartbeat_socket_out.bind('tcp://*:%s' % best_heartbeat_port)
		best_details = {'best_name:':self.name,'best_heartbeat_port':best_heartbeat_port}
		#for sending
		serialized_best_details = simplejson.dumps(best_details)

		for agent, sock in self.allagents.iteritems():
			if agent == self.name:
				pass
			else:
				context = zmq.Context()
				change_bestship = context.socket(zmq.REQ)
				print self.agent_type, self.name, ': connect to Agent', agent
				change_bestship.connect('tcp://localhost:%s' % sock)
				print self.agent_type, self.name, ': confirming that I am the best'
				while True:
					#ping the Basics to adjust to new best
					change_bestship.send_string('%s' % serialized_best_details)
					confirmation = change_bestship.recv()
					if confirmation:
						print self.agent_type, self.name, ': bestship change accepted by %s' % agent
						break
		#send best details
				
	def ping_others(self):
		while True:

			heartbeat_send = self.name
			self.heartbeat_socket_out.send('%s' % heartbeat_send)
			print self.name, '.'
			time.sleep(1)

	### PROGRAM FUNCTIONS ###				

	def program(self):
		#while not Better/best, no request_vote RPC received, no heartbeat, 
		_ = raw_input('Press enter when other agents are ready')
		while True:
			
			print self.agent_type, self.name,': Listening...'
			if self.agent_type != 'Best':
				while True:
					#heartbeat
					try:
						heartbeat_rcv = self.heartbeat_socket.recv(zmq.DONTWAIT)
						self.reset()
						print self.agent_type, self.name, ': Heartbeat received from best'
						break
					except zmq.Again:
						#print self.agent_type, self.name, ': No heartbeat...'
						print self.agent_type, self.name, ': Timer -', self.Timer
						break

			while True:
				try:
					#if there is a message, proceed with reading it
					message = self.socket_agent.recv(zmq.DONTWAIT)
					
					if message.startswith('Hi!'):
						if self.agent_type == 'Basic':
							print self.agent_type, self.name, ':', message
							self.reset()
							time.sleep(1)
							self.socket_agent.send(b'Hi sir!')
							break
						else: 
							self.socket_agent.send(b'Hi!')
							break
					else: #message.startswith('New_best'): #if elected... adjust to new best
						if self.agent_type == 'Better':
							#convert Betters back to Basics
							self.agent_type = 'Basic'
						print self.agent_type, self.name, ':', message
						self.socket_agent.send(b'Yes!')
						self.connect_to_best(message)
					break
				except zmq.Again:
					#if there are no messages. break out
					print self.agent_type, self.name,': No one is talking...'
					break

			if self.agent_type != 'Best':
				if self.Timer == 0:
					print self.agent_type, self.name, ': be Better.'
					self.be_better()
					print self.agent_type, self.name, ': I want to talk now. Other agents... listen to me.'
					total = self.make_me_best()
					print self.agent_type, self.name, ': total replies received:', total
					self.reset()
					self.be_best()
				self.countdown()
			else: #if best
			
				print self.agent_type, self.name,": I'm the best!!"
				
				self.ping_others()

				

def main():

	name_to_use = sys.argv[1]
	port_to_use = sys.argv[2]

	basic = Basic(name_to_use, port_to_use)
	#Basic.to_connect(client_push_port, client_pub_port, client_recv_port)
	basic.program()

if __name__ == '__main__':
	main()


