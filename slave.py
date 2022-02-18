import socket
import struct
import time
import datetime
import base64
import cracker
import argparse
import pickle
import logging
import time
import sys
import random
import threading
from utils import dht_hash


MCAST_GRP = '224.3.29.71'
MCAST_PORT = 5007
IS_ALL_GROUPS = False
ServerLocal = '127.0.1.1'
Port = 8000
User = 'root'
#Send
class Slave:
    def __init__(self, timeout = 10, secret = "5" ,MSize = 1 ):
        #fazer dic user, pass
        #Parte do servidor
        """
            Secalhar nao criavamos logo a socket TCP
            Primeiro trocavamos mensagens para decidir quem tinha o maior ID (Por floding no inicio que é mais fácil depois tentar por bullying?)
            Depois esse ID determinava quem se iria ligar ao HTTPServer (tipo os 3 mais pequenos que responderem)
            Os que respondiam com um Ack comecavam a trabalhar
            Se algum deles nao respondesse ou nao envia se uma mensagem de Acknowledge
            o Coordenador(Maior ID) Escolhia outro(1 ou mais) gajo para ser outro slave
            so one and so forth
            Esses 3 escolhido periodicamente informavam o coordenador do seu 'estado'
            Tipo uma lista de passes testadas ou a pedir mais ou a dizer ei descobri a pass

        """
        self.controllingSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criar socket
        self.controllingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.controllingSocket.bind(("localhost", 5008))
        self.controllingSocket.listen(100)

        #MULTICAST
        global MCAST_GRP
        global MCAST_PORT
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket UDP
        self.sockUDP.settimeout(timeout)
        self.timeout = timeout/2
        self.timestamp = time.time()

        self.sockUDP.bind(('', MCAST_PORT))
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack('4sl', group, socket.INADDR_ANY)
        self.sockUDP.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sockUDP.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_LOOP,0)
        self.done_UDP = False
        self.role = None
        self.election = True

        #self.sock.bind(( MCAST_GRP, MCAST_PORT))

        #self.generatePassword(MSize)

        hostname = socket.gethostname()

        self.address = socket.gethostbyname(hostname)

        self.port = int(socket.getnameinfo(self.sockUDP.getsockname(), socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)[1])
        self.peers = {}

        self.identification = dht_hash(self.address.__str__())
        self.logger = logging.getLogger(f"Slave {self.identification}")

        self.coordenador = -1000
        self.keep_alive = time.time()
        self.workers = {} #dict para associar IDs a workloads
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(("192.168.1.162", 8000))

        self.workInProgress = dict()
        print(secret)
        self.sendPass(secret)


    #Receive
    """
    def receive(self):
        global IS_ALL_GROUPS
        global MCAST_PORT
        global MCAST_GRP

        #token pass
        #ideia: pode ser um boolean com vdd encontrou pass ou não.
        if  IS_ALL_GROUPS:
            # on this port, receives ALL multicast groups
            self.sock.bind(('', MCAST_PORT))
        else:
            # on this port, listen ONLY to MCAST_GRP

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)

        while True:
        # For Python 3, change next line to "print(sock.recv(10240))"
            print(self.sock.recv(10240))
            """

    def sendPass(self, password):
        global User
        global ServerLocal
        token = base64.encodebytes((f"{User}:{password}").encode()).strip()
        lines = f"GET / HTTP/1.1\nHost: {ServerLocal}\nAuthorization: Basic {token.decode()}\n\n" #linha q precisa enviar na mensagem
        self.server_sock.send(lines.encode('utf-8'))
        print(password)
        self.server_sock.recv(4096)



    def generatePassword(self, current, MaxSize = 1):
        self.threads_launched = []
        for i in range(0,MaxSize):
            t = cracker.passGening( 1, i, i, current)
            t.start()
            self.threads_launched.append(t)

    def sendMessage(self, msg, line ,addr = ('224.3.29.71',5007)):
        print(f"ID {self.identification} S: {msg} line : {line}")
        self.sockUDP.sendto(pickle.dumps(msg),addr)

    def getHigherPriorityPeers(self, limit=None):
        print(f"LIST PRIORITY ID  {self.peers}")
        if limit != None:
            return [self.peers[x] for x in self.peers.keys() if x > self.identification ][0:limit]
        return [self.peers[x] for x in self.peers.keys() if x > self.identification ]


    def getLowerPriorityPeers(self):
        print(f"LIST PRIORITY ID  {self.peers}")
        return [self.peers[x] for x in self.peers.keys() if x < self.identification ]

    def getNextPass(self):
        return

    def async work(self, initPass, rangeToTest):
        print("hello world")

    # RUN UPD stuff


    def run(self):
        global MCAST_GRP
        global MCAST_PORT

        connectionMessage = {
                "command":"DISCOVER",
                "ID":self.identification,
                "IP":(self.address,self.port)
                }

        self.sendMessage(connectionMessage, 136)

        while not self.done_UDP:
            nn = datetime.datetime.now()
            try:
                payload, addr = self.sockUDP.recvfrom(1024)
                output = pickle.loads(payload)
                print(f"{nn =: %H:%M:%S}O: {output} ADDR: {addr}" )
            except socket.timeout:
                payload, addr = None, None
            # 875 != 1000 and 875 != 221
            if self.coordenador != -1000 and self.coordenador != self.identification:
                try:
                    if addr is not None and addr == self.peers[self.coordenador] or self.election :# received from coord reset timestamp
                        self.timestamp = time.time()
                except KeyError:
                    pass

            if self.election == True:
                if payload is not None:
                    output = pickle.loads(payload)

                    if output["command"] != "HI" and output["command"] != "ola":
                        self.peers[output["ID"]] = output["IP"] # Add peers to dict

                    nn = datetime.datetime.now()
                    print(f"{nn =: %H:%M:%S}O: {output}" )

                    if output["command"] == "ELECTION":
                             #3               #4, 4 terá de ser o coordenador
                             #identification do nó, e o output é a msg q recebi

                        if output["ID"] < self.identification:
                            # Send a message to all higher priority ID's
                            #temos q verificar sempre se o id maior está vivo atraves da eleicao
                            self.election = True
                            connectionMessage = {
                                    "command":"ELECTION",
                                    "ID":self.identification,
                                    "IP":(self.address,self.port)
                                    }
                            list_ids = self.getHigherPriorityPeers()
                            for addr_tuple in list_ids:
                                self.sendMessage(connectionMessage, 182 , addr_tuple)

                            list_ids = self.getLowerPriorityPeers()
                            for addr_tuple in list_ids:
                                self.sendMessage({"command" : "ola"}, 186 , addr_tuple)

                        else:# eu sou o mais peque
                            #caso i id for inferior, saimos da eleicao e eles msm n podem ser coordenadores
                            self.election = False

                    if output["command"] == "HI":
                        if self.coordenador != int(output["COORD_ID"]):
                            # Shit dis is bad
                            connectionMessage = {
                                    "command":"ELECTION",
                                    "ID":self.identification,
                                    "IP":(self.address,self.port)
                                    }
                            list_ids = self.getHigherPriorityPeers()
                            for addr_tuple in list_ids:
                                self.sendMessage(connectionMessage, 202, addr_tuple)
                        else:
                            self.coordenador = int(output["COORD_ID"])
                            print(f"entrei coordenador: {self.coordenador}, output coordenador: {int(output['COORD_ID'])}")
                            self.election = False


                    if output["command"] == "DISCOVER":

                        # Send requested information
                        connectionMessage = {
                                "command":"RESP",
                                "ID":self.identification,
                                "IP":(self.address,self.port),
                                "COORD" : self.coordenador,
                                }
                        self.sendMessage(connectionMessage, 218, output["IP"])

                    if output["command"] == "RESP":
                        if output["COORD"] :
                            if output["COORD"] > self.identification:
                                self.coordenador = int(output["COORD"])
                                self.election = False
                            else:
                                #Start an election
                                connectionMessage = {
                                        "command":"ELECTION",
                                        "ID":self.identification,
                                        "IP":(self.address,self.port)
                                        }
                                print(output["IP"])
                                list_ids = self.getHigherPriorityPeers()
                                for addr_tuple in list_ids:
                                    self.sendMessage(connectionMessage, 235 , addr_tuple)

                    if output["command"] == "COORDINATOR":
                        #5                      6
                        if  self.identification < int(output["ID"]) :
                            # start election
                            """connectionMessage = {
                                    "command":"ELECTION",
                                    "ID":self.identification,
                                    "IP":(self.address,self.port)
                                    }
                            print(output["IP"])
                            list_ids = self.getHigherPriorityPeers()
                            for addr_tuple in list_ids:
                                self.sendMessage(connectionMessage, 195 , addr_tuple)
                        else:"""
                            if self.coordenador < int(output["ID"]):
                                self.coordenador = int(output["ID"])
                                self.election = False
                                print(f"This is the coordinator {self.coordenador}  ")

                if payload is None: # Socket Timeout
                    print("I am the elected-----------------------------------------------------------------------")
                    self.coordenador = self.identification
                    connectionMessage = {
                            "command":"COORDINATOR",
                            "ID":self.coordenador,
                            "IP":(self.address,self.port)
                            }
                    self.election = False
                    self.timestamp = time.time()
                    self.sendMessage(connectionMessage, 265)# sent over BROADCAST

            if self.election == False:
                #temos de receber msg do coordenador, começar a trabalhar. eleição acaba e recebmos msg do coordenador.
                #quando a eleicao fica a false, o coordenador apresenta-se e começam a trabalhar. Slaves só trabalham c um mestre

                if payload is not None:
                    output = pickle.loads(payload)
                    if output["command"] != "HI" and output["command"] != "ola":
                        self.peers[output["ID"]] = output["IP"]

                    if output["command"] == "ELECTION":
                        self.election = True
                        self.coordenador = -1000
                        connectionMessage = {
                                "command":"ELECTION",
                                "ID":self.identification,
                                "IP":(self.address,self.port)
                                }
                        list_ids = self.getHigherPriorityPeers()
                        for addr_tuple in list_ids:
                            self.sendMessage(connectionMessage, 292, addr_tuple)

                    if output["command"] == "DISCOVER":
                        # Send requested information
                        connectionMessage = {
                                "command":"RESP",
                                "ID":self.identification,
                                "IP":(self.address,self.port),
                                "COORD" : self.coordenador,
                                }
                        self.sendMessage(connectionMessage,297, output["IP"])

                    if output["command"] == "HI":
                        if self.coordenador != output["COORD_ID"]:
                            # Shit dis is bad
                            connectionMessage = {
                                    "command":"ELECTION",
                                    "ID":self.identification,
                                    "IP":(self.address,self.port)
                                    }
                            list_ids = self.getHigherPriorityPeers()
                            for addr_tuple in list_ids:
                                self.sendMessage(connectionMessage, 309, addr_tuple)

                    if output["command"] == "COORDINATOR":
                        if  self.identification < int(output["ID"]) :
                            # start election
                            """
                            connectionMessage = {
                                    "command":"ELECTION",
                                    "ID":self.identification,
                                    "IP":(self.address,self.port)
                                    }
                            print(output["IP"])
                            list_ids = self.getHigherPriorityPeers()
                            for addr_tuple in list_ids:
                                self.sendMessage(connectionMessage, 195 , addr_tuple)
                        else:"""
                            self.coordenador = int(output["ID"])
                            self.election = False
                            print(f"This is the coordinator {output['ID']}")
                        if self.coordenador > int(output["ID"]):
                            message = {
                                    "command" : "COORDINATOR",
                                    "ID"      : self.coordenador,
                                    "IP"      : (self.address,self.port)
                                    }
                            self.sendMessage(message, 350)

                    if output["command"] == "WORK":
                        if self.identification == int(output["ID"]):
                            await work(initPass = output["initPass"], rangeToTest=int(output["rangeToTest"])
                """else:
                    connectionmessage = {
                            "command":"HI",
                            "COORD_ID":self.coordenador,
                            "COORD_IP":(self.address,self.port)
                            }
                    self.sendMessage(connectionmessage, 334)
                """
            if self.coordenador == self.identification:
                initPass = self.getNextPass()
                connectionmessage = {
                        "command":"WORK",
                        "COORD_ID":self.identification,
                        "COORD_IP":(self.address,self.port),
                        "initPass": initPass,
                        "rangeToTest" : 10
                        }
                self.workInProgress.pop(initPass)

                self.sendMessage(connectionmessage, 334)



            # a quanto tempo o coordenador nao manda uma mensagem
            if ( (time.time() - self.timestamp) > self.timeout - 2 ) and
                self.identification == self.coordenador and not self.election:

                self.sendMessage({"command":"ola"},337)
                self.timestamp = time.time()

            # A quanto tempo nao recebes uma mensagem do coordenador
            if (time.time() - self.timestamp) > ((2 * self.timeout) + 1)
                and self.identification != self.coordenador and not self.election:

                connectionMessage = {
                                    "command":"ELECTION",
                                    "ID":self.identification,
                                    "IP":(self.address,self.port)
                                    }
                list_ids = self.getHigherPriorityPeers()
                for addr_tuple in list_ids:
                    self.sendMessage(connectionMessage, 348, addr_tuple)
                self.election = True
                self.coordenador = -1000

            print(f"ID {self.identification} Coordenador:{self.coordenador} ")
            print(f"ID {self.identification} lista: {self.peers}")

class SlaveController(threading.Thread):
    def __init__ (self, sockUDP, SlaveAddr):
        self.sUDP = sockUDP
        self.serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criar socket
        self.serverSocket.connect(SlaveAddr)

    def run(self):
        pass


def main (secret, MSize, identification):
    s = Slave()
    s.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Basic HTTP Authentication Server Cracker')
    parser.add_argument('-l', dest='MaxSize', type=int, help="Max string length for passwords", default=1)
    parser.add_argument('-s', dest='secret',type=str, help="Secret To use", default=None)
    parser.add_argument('-i', dest='id',type=str, help="Id fo worker", default=1)
    #parser.add_arguments('-s', dest='secret',type=str, help="Secret To use", default=None)
    args = parser.parse_args()
    main(args.secret,args.MaxSize,args.id)
