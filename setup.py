import os, signal

if __name__ == "__main__":

    pid_list = []
    num_proc = 1
    letter = ord('A')
    
    while num_proc <= 10:
        pid = os.fork()
        if pid == 0:
            os.execlp('xterm', 'bash', '-e', 'python', 'node.py', chr(letter))
            break
        else:
            pid_list.append(pid)

        num += 1
        letter += 1


    if pid != 0:
        print("Pressione enter para terminar processos")
        input()
        for p in pid_list:
            os.kill(p, signal.SIGTERM)
