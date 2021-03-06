'''
Please add your name:
Please add your matric number: 
'''

import os
import sys
import atexit
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import Link
from mininet.node import RemoteController

net = None

class TreeTopo(Topo):
			
	def __init__(self):
		# Initialize topology
		Topo.__init__(self) 
		f = open('topology.in')
		firstline = f.readline().split(' ')

		numHosts = int(firstline[0])
		numSwitches = int(firstline[1])
		numLinks = int(firstline[2])

		hosts = []
		for i in xrange(numHosts):
		    hosts.append(self.addHost('h%d' % (i+1)))

		print hosts

		switches = []
		for i in xrange(numSwitches):
		    sconfig = {'dpid': "%016x" % (i+1)}
		    switch = self.addSwitch('s%d' % (i+1), **sconfig)
		    switches.append(switch)

		print switches
		print self.switches()

		self.linkConfigs = []
		for i in xrange(numLinks):
		    line = f.readline().strip().split(', ')
		    print line
		    self.linkConfigs.append(line)
		    firstNode = line[0]
		    secondNode = line[1]
		    # add link without bandwidth since the bandwidth will be added later in queue
		    self.addLink(firstNode, secondNode)

		print self.links(True, False, True)       


def startNetwork():
    info('** Creating the tree network\n')
    topo = TreeTopo()

    global net
    net = Mininet(topo=topo, link = Link,
                  controller=lambda name: RemoteController(name, ip='SERVER IP'),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
    net.start()

    # Create QoS Queues
    # > os.system('sudo ovs-vsctl -- set Port [INTERFACE] qos=@newqos \
    #            -- --id=@newqos create QoS type=linux-htb other-config:max-rate=[LINK SPEED] queues=0=@q0,1=@q1,2=@q2 \
    #            -- --id=@q0 create queue other-config:max-rate=[LINK SPEED] other-config:min-rate=[LINK SPEED] \
    #            -- --id=@q1 create queue other-config:min-rate=[X] \
    #            -- --id=@q2 create queue other-config:max-rate=[Y]')

    info('** Running CLI\n')
    CLI(net)

def stopNetwork():
    if net is not None:
        net.stop()
        # Remove QoS and Queues
        os.system('sudo ovs-vsctl --all destroy Qos')
        os.system('sudo ovs-vsctl --all destroy Queue')


if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
