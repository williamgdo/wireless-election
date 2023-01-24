import pickle, socket, threading, time, sys, random

def sendMsgForNeighbors(msg):
    for neighbor in process.neighbours:
        if neighbor[0] != process.parent:
            process.socket.sendto(pickle.dumps(msg),("localhost", neighbor[0]))

def parse_input(arg):
    file = open(arg + ".in", "r") 
    line = file.readline()
    line = line.split()
    node_id = line[0]
    node_port = int(line[1])
    line = file.readline()
    capacity = int(line)
    line = file.readline()
    line = line.split()
    neighbours = []
    for port in line:
        neighbours.append((int(port), -1))

    return (node_id, node_port, capacity, neighbours)  

class Process:
    parent = ""
    leader = ""
    socket = ""
    acks = 0
    election = -1
    bestCapacity = {"port": 0, "capacity": 0}

    def __init__(self, arg):
        self.id = arg[0]
        self.port = arg[1]
        self.capacity = arg[2]
        self.neighbours = arg[3]
    

def worker(message):
        while True:
            msgBytes, sender = process.socket.recvfrom(2048)
            #mensagem_resposta = msgBytes.decode().upper()         #aqui eh para retornar ao process:
            rcvMsg = pickle.loads(msgBytes)
            print(str(sender) + " type: " + str(rcvMsg["type"]))

            if rcvMsg["type"] == "election": 
              if rcvMsg["id"] > process.election: #mensagem recebida de eleicao
                print("nova eleicao")
                process.leader = ""
                process.election = rcvMsg["id"]
                process.parent = sender[1]
                process.acks = 1 #reduz a qtd de oks pq nao precisa receber do pai

                time.sleep(random.randint(1, 5)) 
                sendMsgForNeighbors(rcvMsg)
              elif rcvMsg["id"] == process.election:
                msgOK = {
                    "type": "ack",
                    "remetente": {"port": process.port, "capacity": 0}
                }
                process.socket.sendto(pickle.dumps(msgOK),("localhost", sender[1]))
            elif rcvMsg["type"] == "lider" and process.leader == "":
                print("novo lider: " + str(rcvMsg["remetente"]["port"]) + " capacity: " + str(rcvMsg["remetente"]["capacity"]) )

                time.sleep(random.randint(1, 5)) 
                sendMsgForNeighbors(rcvMsg)
                process.parent = ""
                process.leader = rcvMsg["remetente"]["port"]
            elif rcvMsg["type"] == "ack": #reconhecimento dos nós vizinhos
                process.acks += 1
                if rcvMsg["remetente"]["capacity"] > process.bestCapacity["capacity"]:
                    process.bestCapacity["capacity"] = rcvMsg["remetente"]["capacity"]
                    process.bestCapacity["port"] = rcvMsg["remetente"]["port"]
                elif rcvMsg["remetente"]["capacity"] == process.bestCapacity["capacity"] and rcvMsg["remetente"]["port"] > process.bestCapacity["port"]:
                    process.bestCapacity["capacity"] = rcvMsg["remetente"]["capacity"]
                    process.bestCapacity["port"] = rcvMsg["remetente"]["port"]

            if process.acks == (len(process.neighbours)) and process.election != -1: #recebeu todas confirmacoes
                
                if process.capacity > process.bestCapacity["capacity"]:
                    process.bestCapacity["port"] = process.port #salva port
                    process.bestCapacity["capacity"] = process.capacity #salvar capacity
                elif process.capacity == process.bestCapacity["capacity"] and process.port > process.bestCapacity["port"]:
                    process.bestCapacity["port"] = process.port
                    process.bestCapacity["capacity"] = process.capacity

                if process.parent == "": #if para identificar nó que iniciou a eleicao
                    msgLider = {
                        "type": "lider",
                        "remetente": process.bestCapacity
                    }
                    process.leader = process.bestCapacity["port"]

                    time.sleep(random.randint(1, 5)) 
                    sendMsgForNeighbors(msgLider)
                else: #retorna para o pai a melhor capacity
                    msgOK = {
                        "type": "ack",
                        "remetente": process.bestCapacity
                    }
                    process.socket.sendto(pickle.dumps(msgOK),("localhost", process.parent))
                    print("enviando para o pai " + str(process.parent) + ": " + str(process.bestCapacity))
                    
                process.acks = 0
                process.election = -1
                process.bestCapacity["capacity"]=0
                process.bestCapacity["port"]=0  
            

if __name__ == "__main__":
    process_arg = parse_input(sys.argv[1])
    process = Process(process_arg)

    process.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #process.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    process.socket.bind(('localhost', process.port))
    
    t = threading.Thread(target=worker,args=("thread sendo executada",))
    t.start()


    random.seed()
    print("Node_id: " + sys.argv[1])
    while True:
        #try:
            mensagem_envio = input("Iniciar eleicao:")
            msg = {
                "type": "election",
                "id": process.port,
            }
            process.election = process.port

            time.sleep(random.randint(1, 5)) 
            sendMsgForNeighbors(msg)
