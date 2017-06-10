import simpy
import time

# class Car(object):

# 	def __init__(self,env, name):
# 		self.env = env
# 		self.name = name
# 		self.action = env.process(self.run())

# 	def run(self):
# 		while True:
# 			print 'Car %s parking and charging at %d' % (self.name, self.env.now)
# 			charge_duration = 5
# 			try:
# 				yield self.env.process(self.charge(charge_duration))
# 			except simpy.Interrupt:
# 				print 'Interrupted. Hope battery is full'
# 			print 'Start driving at %d' % env.now
# 			time.sleep(1)
# 			trip_duration = 2
# 			yield self.env.timeout(trip_duration)

# 	def charge(self, duration):
# 		yield self.env.timeout(duration)

# def driver(env,car):
# 	yield env.timeout(3)
# 	car.action.interrupt()

# env = simpy.Environment()
# A = Car(env, 'A')
# env.process(driver(env, A))
# env.run(until = 15)

def car(env, name, bcs, driving_time, charge_duration):
	#simulate driving to the BCS
	yield env.timeout(driving_time)

	#request one of its charging spots
	print '%s arriving at %d' % (name, env.now)
	with bcs.request() as req:
		yield req
		#charge battery
		print '%s starting to charge at %s' % (name, env.now)
		time.sleep(1)
		yield env.timeout(charge_duration)
		print '%s leaving the bcs at %s' % (name, env.now)



env = simpy.Environment()
bcs = simpy.Resource(env, capacity = 2)

for i in range(4):
	env.process(car(env, 'Car %d' % i, bcs, i*2, 5))

env.run()