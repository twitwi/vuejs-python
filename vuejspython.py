
import asyncio
import websockets
import json

def is_ndarray(a):
    try:
        import numpy
        return type(a) == numpy.ndarray
    except:
        return False

def sanitize(v): # for sending as JSON
    if is_ndarray(v):
        return v.tolist()
    return v

def cache_stale(cache, k, v):
    if k not in cache: return True
    if cache[k] is v: return False
    if is_ndarray(v):
        return (v != cache[k]).any()
    return cache[k] != v

def make_prop(k):
    f = '_'+k
    def get(o):
        if hasattr(o, '_v_currently_computing') and o._v_currently_computing != []: # may be triggered before "start" (in __init__)
            o._v_deps[o._v_currently_computing[-1]].append(k)
            print("DEPS", o._v_deps)
        return getattr(o, f)
    def set(o, v):
        if getattr(o, f) is v: return
        try:
            if getattr(o, f) == v: return
        except:
            pass # e.g. exception with numpy compare
        setattr(o, f, v)
        call_watcher(o, k)
        update_computed_depending_on(o, k)
        broadcast(o, k)
    return property(get, set)

def make_computed_prop(k):
    def get(o):
        if k not in o._v_cache:
            recompute_computed(o, k)
        return o._v_cache[k]
    return property(get, None)
    # TODO: might want to allow set() in some way (see vue)

def update_computed_depending_on(o, k):
    if not hasattr(o, '_v_deps'): return
    for f, deps in o._v_deps.items():
        if k in deps:
            deps[:] = []
            recompute_computed(o, f)

def recompute_computed(o, k):
    o._v_currently_computing += [k]
    v = o._v_computed[k](o)
    del o._v_currently_computing[-1]
    if cache_stale(o._v_cache, k, v):
        o._v_cache[k] = v
        update_computed_depending_on(o, k)
        broadcast(o, k)

def field_should_be_synced(cls):
    novue = cls._v_novue if hasattr(cls, '_v_novue') else []
    return lambda k: k[0] != '_' and k not in novue

# class annotation
def model(cls):
    prefix = 'computed_'
    novue = cls._v_novue if hasattr(cls, '_v_novue') else []
    cls._v_nobroadcast = cls._v_nobroadcast if hasattr(cls, '_v_nobroadcast') else []
    computed = [k[len(prefix):] for k in dir(cls) if k.startswith(prefix)]
    cls._v_computed = {}
    for k in computed:
        cls._v_computed[k] = getattr(cls, prefix+k)
        setattr(cls, k, make_computed_prop(k))
    for k in filter(field_should_be_synced(cls), dir(cls)):
        if not callable(getattr(cls, k)):
            setattr(cls, '_'+k, getattr(cls, k))
            setattr(cls, k, make_prop(k))
    return cls


def broadcast(self, k):
    if k in self._v_nobroadcast: return
    asyncio.ensure_future(broadcast_update(k, getattr(self, k)))

def call_watcher(o, k):
    watcher = 'watch_'+k
    if hasattr(o, watcher):
        watcher = getattr(o, watcher)
        if callable(watcher):
            watcher(getattr(o, k))

all = []
async def broadcast_update(k, v):
    a = all.copy()
    all[:] = []
    for ws in a:
        try:
            v = sanitize(v)
            await ws.send("UPDATE "+str(k)+" "+json.dumps(v))
            print('⇒ UPDATE', k, json.dumps(v))
            all.append(ws)
        except:
            pass

def handleClient(o):
    async def handleClient(websocket, path):
        if path == '/init':
            clss = type(o)
            state = {}
            methods = []
            for k in filter(field_should_be_synced(clss), dir(clss)):
                if callable(getattr(o, k)):
                    methods.append(k)
                else:
                    state[k] = getattr(o, k)
                    state[k] = sanitize(state[k])
            to_send = {
                'state': state,
                'methods': methods
            }
            print('⇒ INIT', list(state.keys()))
            await websocket.send(json.dumps(to_send))
        else:
            all.append(websocket)
            try:
                while True:
                    comm = await websocket.recv()
                    if comm == 'CALL':
                        meth = await websocket.recv()
                        print('⇐ METH', meth)
                        data = await websocket.recv()
                        print('⇐ DATA', data)
                        try:
                            res = await getattr(o, meth)(*json.loads(data))
                        except Exception as inst:
                            print('... exception while calling method:', inst)
                    elif comm == 'UPDATE':
                        k = await websocket.recv()
                        v = await websocket.recv()
                        print('⇐ UPDATE', k, v)
                        try:
                            setattr(o, k, json.loads(v))
                            call_watcher(o, k)
                        except Exception as e:
                            print("Not a JSON value (or watcher error) for key", k, "->", v, "//", e)
                            import traceback
                            traceback.print_exc()
            except:
                print('X websocket disconnected')
                pass # disconnected
    return handleClient

def start(o, port=4259, host='localhost'):
    o._v_cache = {}
    o._v_currently_computing = []
    o._v_deps = {}
    for k in o._v_computed.keys():
        o._v_deps[k] = []
    for k in o._v_computed.keys():
        recompute_computed(o, k)
    #inreader = asyncio.StreamReader(sys.stdin)
    ws_server = websockets.serve(handleClient(o), host, port)
    asyncio.ensure_future(ws_server)
    asyncio.get_event_loop().run_forever()
