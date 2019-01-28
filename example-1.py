
import asyncio
import websockets
import json
from reactive.ObservableDict import ObservableDict


class Comp:

    def __init__(self):
        self.suggestions = ['salut', 'ToTo']
        self.title = 'Test1'
        self.i = 42

    async def _up(self, k):
        await broadcast_update(k, getattr(self, k))

    async def meth1(self, v):
        print("Com", v)
        if v == 'salut':
            self.i += 1
            await self._up('i')

    async def clone(self, v):
        self.suggestions.append(v)
        await self._up('suggestions')

#state = ObservableDict()
#state = {}
#state['suggestions'] = ['salut', 'TOto']
#state['title'] = 'Test1'

#methods = {}
#methods['meth1'] = "yes"

o = Comp()

all = []
async def broadcast_update(k, v):
    a = all.copy()
    all[:] = []
    for ws in a:
        try:
            await ws.send("UPDATE "+str(k)+" "+json.dumps(v))
            all.append(ws)
        except:
            pass

async def demo_incr():
    while True:
        await asyncio.sleep(3)
        o.i += 3
        await o._up('i')

async def handleClient(websocket, path):
    if path == '/init':
        state = {}
        methods = []
        for k in filter(lambda k: k[0] != '_', o.__dir__()):
            if callable(getattr(o, k)):
                methods.append(k)
            else:
                state[k] = getattr(o, k)
        to_send = {
            'state': state,
            'methods': methods
        }
        await websocket.send(json.dumps(to_send))
    else:
        all.append(websocket)
        while True:
            comm = await websocket.recv()
            if comm == 'CALL':
                meth = await websocket.recv()
                print('METH', meth)
                data = await websocket.recv()
                print('DATA', data)
                res = await getattr(o, meth)(*json.loads(data))
            elif comm == 'UPDATE':
                k = await websocket.recv()
                v = await websocket.recv()
                try:
                    setattr(o, k, json.loads(v))
                except:
                    print("Not a JSON value for key", k, "->", v)


#inreader = asyncio.StreamReader(sys.stdin)
ws_server = websockets.serve(handleClient, 'localhost', 4259)
asyncio.ensure_future(ws_server)
asyncio.ensure_future(demo_incr())
asyncio.get_event_loop().run_forever()
