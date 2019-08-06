__name__ = 'vuejspython'

import os
import asyncio
import websockets
import json
from vuejspython.observablecollections.observablelist import ObservableList
import traceback
from collections import defaultdict

g_components = {}
g_instances = {}

PREFIX = {
    'IN':   '🢀║   IN',
    'OUT':  ' ║🢂 OUT',
    'END':  '╚╩╝',
    'ENDx': '    ..',
    'ENDe': '    ⚠⚠',
    'ERR':  ' │ ⚠⚠⚠⚠⚠⚠',
    'def':  ' │ ►►►%s►►►',
}
# list of enabled logging
infos = ('DEPS ENDx ENDe'+' IN OUT END ERR').split()
def info(k, *args, **kwargs):
    if k in infos:
        if k in PREFIX.keys():
            pre = PREFIX[k]
        else:
            pre = PREFIX['def']%(k,)
        print('      ', pre, *args, **kwargs)

def info_exception(k, pre=''):
    for l in traceback.format_exc().split('\n'):
        info(k, pre + l)


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

def make_prop(k, no_broadcast):
    f = '_'+k
    def get(o):
        if hasattr(o, '_v_currently_computing') and o._v_currently_computing != []: # may be triggered before "start" (in __init__)
            o._v_deps[o._v_currently_computing[-1]].append(k)
            info('DEPS', o._v_deps)
        return getattr(o, f)
    def set(o, v):
        def trigger_on_change(*args):
            call_watcher(o, k)
            update_computed_depending_on(o, k)
            if not no_broadcast:
                broadcast(o, k)
        if type(v) == list:
            v = ObservableList(v)
            v.attach(trigger_on_change)
        if getattr(o, f) is v: return
        try:
            if type(getattr(o, f)) == type(v) and getattr(o, f) == v: return
        except:
            pass # e.g. exception with numpy compare
        setattr(o, f, v)
        trigger_on_change()
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

def recompute_scheduled_computed(o):
    # TODO use the deps to recompute in the proper order
    if not hasattr(o, '_v_schedule_recomputing') or len(o._v_schedule_recomputing) == 0: return
    tocomp = o._v_schedule_recomputing
    o._v_schedule_recomputing = []

    for k in tocomp:
        recompute_computed(o, k)
    recompute_scheduled_computed(o)

def recompute_computed(o, k):
    if o._v_just_schedule:
        o._v_schedule_recomputing += [k]
        return
    o._v_currently_computing += [k]
    v = o._v_computed[k](o)
    del o._v_currently_computing[-1]
    if cache_stale(o._v_cache, k, v):
        o._v_cache[k] = v
        update_computed_depending_on(o, k)
        broadcast(o, k)

def field_should_be_synced(cls):
    novue = cls._v_novue if hasattr(cls, '_v_novue') else []
    if hasattr(cls, 'props'):
        novue.append('props')
    return lambda k: k[0] != '_' and not k.startswith('computed_') and k not in novue

# class annotation
def model(cls):
    if not hasattr(cls, 'props'): setattr(cls, 'props', [])
    g_components[cls.__name__] = cls
    prefix = 'computed_'
    novue = cls._v_novue if hasattr(cls, '_v_novue') else []
    cls._v_nobroadcast = cls._v_nobroadcast if hasattr(cls, '_v_nobroadcast') else []
    computed = [k[len(prefix):] for k in dir(cls) if k.startswith(prefix)]
    cls._v_computed = {}
    cls._v_just_schedule = True
    for k in computed:
        cls._v_computed[k] = getattr(cls, prefix+k)
        setattr(cls, k, make_computed_prop(k))
    for k in filter(field_should_be_synced(cls), dir(cls)):
        if not callable(getattr(cls, k)):
            v = getattr(cls, k)
            setattr(cls, '_'+k, v)
            setattr(cls, k, make_prop(k, k in cls.props))
    return cls


def broadcast(self, k):
    if not hasattr(self, '__id'): return # no id yet, still building
    if k in self._v_nobroadcast: return
    asyncio.ensure_future(broadcast_update(self.__id, k, getattr(self, k)))

def broadcast_atomic(self, start):
    if not hasattr(self, '__id'): return # no id yet, still building
    asyncio.ensure_future(broadcast_update(self.__id, KEY_ATOMIC, start))

def call_watcher(o, k):
    watcher = 'watch_'+k
    if hasattr(o, watcher):
        watcher = getattr(o, watcher)
        if callable(watcher):
            watcher(getattr(o, k))

all = defaultdict(lambda: set())
KEY_ATOMIC = '_v_ATOMIC'
async def broadcast_update(id, k, v):
    a = all[id].copy()
    all[id].clear()
    if k == KEY_ATOMIC:
        comm = 'ATOMIC'
    else:
        comm = 'UPDATE'
    for ws in a:
        try:
            v = sanitize(v)
            await ws.send(comm+' '+str(id)+' '+str(k)+' '+json.dumps(v))
            info('OUT', comm, id, k, '{:.80} ...'.format(json.dumps(v)))
            all[id].add(ws)
        except:
            pass

def handleClient():
    _previd = [0]
    def next_instance_id():
        _previd[0] += 1
        return str(_previd[0])

    async def handleClient(websocket, path):
        inited = None
        def cleanup():
            if inited is None: return
            if id != 'ROOT' and id in g_instances:
                del g_instances[id]
            if websocket in all[inited]:
                all[inited].remove(websocket)
                if len(all[inited]) == 0:
                    del all[inited]
        try:
            while True:
                comm = await websocket.recv()
                if comm == 'INIT' or comm == 'INFO':
                    clss_name = await websocket.recv()
                    if inited is not None:
                        info('ERR', 'Tentative double init/info', clss_name)
                    info('IN', comm, clss_name)
                    if clss_name == 'ROOT':
                        id = clss_name
                        all[id].add(websocket)
                        inited = id
                        o = g_instances[id]
                        clss = type(o)
                        o._v_just_schedule = False
                    elif clss_name not in g_components:
                        info('ERR', 'Component type ' + clss_name + ' not found (missing @model?).')
                    else:
                        clss = g_components[clss_name]
                        o = clss()
                        id = next_instance_id()
                        all[id].add(websocket)
                        inited = id
                        setattr(o, '__id', id)
                        setup_model_object_infra(o)
                        g_instances[id] = o
                        if comm == 'INIT':
                            prop_values = await websocket.recv()
                            prop_values = json.loads(prop_values)
                            info('IN', prop_values)
                            for k in prop_values.keys():
                                setattr(o, k, prop_values[k])
                            o._v_just_schedule = False
                            recompute_scheduled_computed(o)
                        else:
                            o._v_just_schedule = False
                            # we do it as for computed, we have no reasonable default...
                            # as they might depend on the properties (and thus their type is unknown)
                            # it would be called anyway on state[k] = getattr(o, k) below
                            # and for now we don't know what to put as a default value (that will be temporary present on the js side)
                            recompute_scheduled_computed(o)
                    state = {}
                    props = o.props if hasattr(o, 'props') else []
                    methods = []
                    for k in filter(field_should_be_synced(clss), dir(clss)):
                        if k in props: continue
                        if callable(getattr(clss, k)):
                            methods.append(k)
                        else:
                            state[k] = getattr(o, k)
                            state[k] = sanitize(state[k])
                    to_send = {
                        'id': id,
                        'props': props,
                        'state': state,
                        'methods': methods
                    }
                    to_send = json.dumps(to_send)
                    info('OUT', comm, '{:.80} ...'.format(to_send))
                    await websocket.send(comm + ' ' + to_send)
                elif comm == 'CALL':
                    id = await websocket.recv()
                    o = g_instances[id]
                    call_id = await websocket.recv()
                    info('IN', 'CALL_ID', call_id)
                    meth = await websocket.recv()
                    info('IN', 'METH', meth)
                    data = await websocket.recv()
                    info('IN', 'DATA', data)
                    try:
                        method_call = getattr(o, meth)(*json.loads(data))
                        # local block scope
                        async def local(method_call, call_id):
                            async def on_return(res):
                                info('OUT', '{:.80} ...'.format('RETURN %s %s'%(call_id, json.dumps(res))))
                                await websocket.send('RETURN %s %s'%(call_id, json.dumps(res)))

                            if type(method_call).__name__ == 'coroutine':
                                task = asyncio.ensure_future(method_call)
                                task.add_done_callback(lambda t: asyncio.ensure_future(on_return(t.result())))
                            else:
                                await on_return(method_call)
                        await local(method_call, call_id)
                    except Exception as inst:
                        info('ERR', 'Exception while calling method:', inst)
                        info_exception('ERR', '  ')
                elif comm == 'UPDATE':
                    id = await websocket.recv()
                    o = g_instances[id]
                    k = await websocket.recv()
                    v = await websocket.recv()
                    info('IN', 'UPDATE', k, v)
                    try:
                        setattr(o, k, json.loads(v))
                        call_watcher(o, k)
                    except Exception as e:
                        info('ERR', 'Not a JSON value (or watcher error) for key', k, '->', v, '//', e)
                        info_exception('ERR', '  ')
        except websockets.ConnectionClosed as e:
            cleanup()
            if e.code == 1001:
                info('END', 'disconnected')
            elif e.code == 1005:
                info('END', 'closed')
            else:
                info('END', e)
                info_exception('ENDx')
        except Exception as e:
            cleanup()
            info('END', e)
            info_exception('ENDe')
    return handleClient

# decorator
def atomic(f):
    def _decorator(self, *args, **kwargs):
        self._v_just_schedule = True # for the python to wait
        broadcast_atomic(self, True) # for the js to wait
        f(self, *args, **kwargs)
        self._v_just_schedule = False
        recompute_scheduled_computed(self)
        broadcast_atomic(self, False)
    return _decorator

def setup_model_object_infra(o):
    cls = o.__class__
    o._v_cache = {}
    o._v_currently_computing = []
    o._v_schedule_recomputing = []
    o._v_deps = {}
    # Set all attributes, so they get wrapped (e.g., observable) if necessary
    for k in filter(field_should_be_synced(cls), dir(cls)):
        if k not in o._v_computed.keys() and not callable(getattr(o, k)):
            setattr(o, k, getattr(o, '_'+k))
    for k in o._v_computed.keys():
        o._v_deps[k] = []
    for k in o._v_computed.keys():
        recompute_computed(o, k)


def start(o, http_port=4260, http_host='localhost', py_port=4259, py_host='localhost', serve=True):
    g_instances['ROOT'] = o
    setattr(o, '__id', 'ROOT')
    setup_model_object_infra(o)
    #inreader = asyncio.StreamReader(sys.stdin)
    ws_server = websockets.serve(handleClient(), py_host, py_port)
    asyncio.ensure_future(ws_server)
    if serve and os.environ.get('NOSERVE') is None:
        from .serve import run_http_server
        run_http_server(http_port, http_host)
    asyncio.get_event_loop().run_forever()
