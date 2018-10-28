import random
import asyncio

#globalni promenne
n=65537
g=111
maleC=123123
def diffehel(velkeS):
   
    global n,g,maleC
    velkeS=int(velkeS)
    klic=velkeS**maleC%n
    return klic


async def posliVecDostanOdpoved(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888,loop=loop)
    writer.write(message.encode())
    data=await reader.read(4096)
    writer.close()
    return data.decode()
    # print('Send: %r' % message)
    # writer.write(message.encode())

    # DHvelkeC=g**maleC%n
    # DHvelkeC="001"+str(DHvelkeC)
    # writer.write(DHvelkeC.encode())
    
    # #prijmeme data
    # data = await reader.read(100)
    # print('Received: %r' % data.decode())
    # message=data.decode()
    # if(message[:3]=="001"):
    #     klic=diffehel(message[3:])
    #     print("klic je ",klic)
    # else:
    #     pass
    # print('Close the socket')
    

def obal(msg,loop):
    return loop.run_until_complete(posliVecDostanOdpoved(msg, loop))



loop = asyncio.get_event_loop()
#for x in range(20):
#loop.run_until_complete(tcp_echo_client(msg, loop))
#    if x==15:
#        loop.run_until_complete(tcp_echo_client("001123123?", loop))
# loop.run_until_complete(tcp_echo_client("001123123", loop))
odpoved=obal("002ahoj",loop)
print(odpoved)
input("AAAAAAAAAAAAAAAAAAAa")


    
loop.close()
input("konec?")