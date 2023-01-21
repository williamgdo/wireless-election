# node A 
# neighbors: B, J

import pickle, socket, threading, time

def sendMsgForNeighbors(msg):
    for neighbor in process.neighbors:
        if neighbor[0] != process.parent:
            process.socket.sendto(pickle.dumps(msg),("localhost", neighbor[0]))

class Process:
    port = 22009
    capacity = 5
    neighbors = [(22006, -1), (22008, -1)] # ([port, capacity])
    parent = ""
    leader = ""
    socket = ""
    acks = 0
    election = -1
    bestCapacity = {"port": 0, "capacity": 0}

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
                sendMsgForNeighbors(rcvMsg)
              elif rcvMsg["id"] == process.election:
                msgOK = {
                    "type": "ack",
                    "remetente": {"port": process.port, "capacity": 0}
                }
                process.socket.sendto(pickle.dumps(msgOK),("localhost", sender[1]))
            elif rcvMsg["type"] == "lider" and process.leader == "":
                print("novo lider: " + str(rcvMsg["remetente"]["porta"]) + " capacity: " + str(rcvMsg["remetente"]["capacity"]) )
                sendMsgForNeighbors(rcvMsg)
                process.parent = ""
                process.leader = rcvMsg["remetente"]["porta"]
            elif rcvMsg["type"] == "ack": #reconhecimento dos nós vizinhos
                process.acks += 1
                if rcvMsg["remetente"]["capacity"] > process.bestCapacity["capacity"]:
                    process.bestCapacity["capacity"] = rcvMsg["remetente"]["capacity"]
                    process.bestCapacity["porta"] = rcvMsg["remetente"]["porta"]
                elif rcvMsg["remetente"]["capacity"] == process.bestCapacity["capacity"] and rcvMsg["remetente"]["porta"] > process.bestCapacity["porta"]:
                    process.bestCapacity["capacity"] = rcvMsg["remetente"]["capacity"]
                    process.bestCapacity["porta"] = rcvMsg["remetente"]["porta"]

            if process.acks == (len(process.neighbors)) and process.election != -1: #recebeu todas confirmacoes
                
                if process.capacity > process.bestCapacity["capacity"]:
                    process.bestCapacity["porta"] = process.port #salva porta
                    process.bestCapacity["capacity"] = process.capacity #salvar capacity
                elif process.capacity == process.bestCapacity["capacity"] and process.port > process.bestCapacity["porta"]:
                    process.bestCapacity["porta"] = process.port
                    process.bestCapacity["capacity"] = process.capacity

                if process.parent == "": #if para identificar nó que iniciou a eleicao
                    msgLider = {
                        "type": "lider",
                        "remetente": process.bestCapacity
                    }
                    process.leader = process.bestCapacity["porta"]
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
                process.bestCapacity["porta"]=0  
            

if __name__ == "__main__":
    process = Process()

    process.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #process.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    process.socket.bind(('localhost', process.port))
    
    t = threading.Thread(target=worker,args=("thread sendo executada",))
    t.start()

    while True:
        #try:
            mensagem_envio = input("Iniciar eleicao:")
            msg = {
                "type": "election",
                "id": process.port,
            }
            process.election = process.port
            sendMsgForNeighbors(msg)