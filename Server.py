import asyncio

#globalni promenne
n=65537
g=111
maleS=15

#definice funkci ke zpracovavani paketů
def diffehel(velkeC):
    global n,g,maleS
    velkeC=int(velkeC)
    klic=velkeC**maleS%n
    return klic
    
async def nahodnyjunk(a,b,c):
    print("nahodny junk")

#seznam operaci podle prvnich tri cisel v kazdem packetu, vybere prislusnou funkci a zavola ji-zatim bez dat ale v budoucnu s nima
handlers={
    1: diffehel,
    2: nahodnyjunk
}

async def handle_echo(reader, writer):
    #prijem dat
    data = await reader.read(100)
    
    print("data= ",data)
    #zpracovavani do citelne podoby(string)
    message = data.decode()
    DHvelkeS=g**maleS%n
    DHvelkeS="001"+str(DHvelkeS)
    writer.write(DHvelkeS.encode())
    
    print("message= ",message)
    #prvni tri cisla paketu- definuji obsah zpravy
    packet_id=int(data[0:3].decode())
 
    print("Packet_id je ",str(packet_id))
    
    #vola prislusnou funkci podle ID paketu
    if packet_id==1:
        klic= diffehel(message[3:])
        print("klic je ",klic)
    else:
        #dela nejake veci, nejspis nezajimave
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (message, addr))

        #jen echo toho co dostal
        writer.write(data)

        #nejspis to musi z nejakeho duvodu tady byt
        await writer.drain()
    

    #konec relace
    print("Close the client socket")
    writer.close()


#inicializace serveru+smycky
loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()