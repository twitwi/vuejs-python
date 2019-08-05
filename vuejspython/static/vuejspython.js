
var vuejspython = {}

vuejspython.defaultPort = 4259
vuejspython.wsurl = null

vuejspython.start = function(opt={}, wsurl=undefined) {
  if (wsurl === undefined || wsurl === null) {
    wsurl = 'localhost'
  }
  if (opt.data === undefined) opt.data = ()=>({})
  if (! wsurl.startsWith('ws')) {
    wsurl = 'ws://' + wsurl
  }
  if (wsurl.substr(4).indexOf(':') == -1) {
    wsurl = wsurl + ':' + vuejspython.defaultPort
  }
  vuejspython.wsurl = wsurl
  var ws = new WebSocket(wsurl)
  let calls = {}
  let atomic = false
  let toApply = {}
  let valuesWhere = {}
  let vm = null
  ws.addEventListener('open', function(a) {
    ws.send('INIT')
    ws.send('ROOT')
  })
  ws.addEventListener('message', function(a) {
    a = a.data
    if (Object.keys(calls).length > 5) {
      console.log('PROBABLY MISSING RETURN FOR METHOD CALLS', Object.keys(calls).length, 'PENDING')
    }
    if (a.startsWith('INIT ')) {
      a = JSON.parse(a.substr('INIT '.length))
      let computed = {...opt.computed}
      let methods = {...opt.methods}
      let watch = {...opt.watch}
      let optdata = opt.data
      let optel = opt.el || '#main'
      for (let k of ['el', 'data', 'watch', 'methods', 'computed']) delete opt[k]
      for (let k in a.state) {
        let watchk = function (v, old) {
          if (valuesWhere[k] == v) return
          delete valuesWhere[k]
          ws.send('UPDATE')
          ws.send('ROOT')
          ws.send(k)
          ws.send(JSON.stringify(v))
        }
        if (watch[k] === undefined) {
          watch[k] = watchk
        } else {
          let owk = watch[k]
          watch[k] = function (...args) { watchk(...args); owk.bind(this)(...args) }
        }
      }
      for (let k of a.methods) {
        methods[k] = async function(...args) {
          return new Promise(function (resolve, reject) {
            ws.send('CALL')
            ws.send('ROOT')
            let callId = (Math.random()*1000).toString().replace(/\./, '')
            calls[callId] = {resolve, reject}
            ws.send(callId)
            ws.send(k)
            ws.send(JSON.stringify(args))
          })
        }
      }
      vm = new Vue({
        el: optel,
        data: () => ({
          ...a.state,
          ...optdata()
        }),
        computed,
        methods,
        watch,
        ...opt,
      })
      window.vuejspython_vm = vm // for console-based introspection
    } else if (a.startsWith('RETURN ')) {
      let parts = a.split(' ', 2)
      let callId = parts[1]
      if (calls[callId] !== undefined) {
        let v = JSON.parse(a.substr(parts.join(' ').length))
        calls[callId].resolve(v)
        delete calls[callId]
      }
    } else if (a.startsWith('ATOMIC ')) {
      let parts = a.split(' ')
      let upid = parts[1]
      // let k = parts[2] '_v_ATOMIC'
      let setAtomic = JSON.parse(parts[3])
      if (upid === 'ROOT') {
        if (!atomic && setAtomic) {
          atomic = true
          toApply = {}
        } else if (atomic && !setAtomic) {
          atomic = false
          for (let k in toApply) {
            let v = toApply[k]
            valuesWhere[k] = v
            vm.$set(vm, k, v)
          }
          toApply = {}
        } else {
          console.log('INCOHERENT atomic STATE', atomic, setAtomic)
        }
      }
    } else if (a.startsWith('UPDATE ')) {
      let parts = a.split(' ', 3)
      let upid = parts[1]
      let k = parts[2]
      if (upid === 'ROOT') {
        let v = a.substr(parts.join(' ').length)
        v = JSON.parse(v)
        if (atomic) {
          toApply[k] = v
        } else {
          valuesWhere[k] = v
          vm.$set(vm, k, v)
        }
      }
    }
  })
}


vuejspython.component = function(pyClass, name, opt={}) {

  // later, consider refactoring if the two are really similar
  if (opt.props === undefined) opt.props = []
  if (opt.data === undefined) opt.data = ()=>({})

  let created = opt.created || (()=>{})
  let props = opt.props
  let optdata = opt.data
  for (let k of ['created', 'data', 'props']) delete opt[k]

  let description = (pyState) => ({
    created: function() {
      let vm = this
      vm.__id = 'NOT-SET-YET'
      let wsurl = vuejspython.wsurl
      let ws = new WebSocket(wsurl)
      let calls = {}
      let atomic = false
      let toApply = {}
      let valuesWhere = {}
      ws.addEventListener('open', function(a) {
        ws.send('INIT')
        ws.send(pyClass)
        ws.send(JSON.stringify(vm.$props))
      })

      ws.addEventListener('message', function(a) {
        a = a.data
        vm.__ws = ws
        if (a.startsWith('INIT ')) {
          a = JSON.parse(a.substr('INIT '.length))
          vm.__id = a.id

          for (let k in a.state) {
            vm.$set(vm, k, a.state[k])
            vm.$watch(k, function (v, old) {
              if (this.__id === 'NOT-SET-YET') return
              if (valuesWhere[k] == v) return
              delete valuesWhere[k]
              ws.send('UPDATE')
              ws.send(vm.__id)
              ws.send(k)
              ws.send(JSON.stringify(v))
            })
          }
          for (let k of a.props) {
            vm.$watch(k, function (v, old) {
              if (this.__id === 'NOT-SET-YET') return
              if (valuesWhere[k] == v) return
              delete valuesWhere[k]
              ws.send('UPDATE')
              ws.send(vm.__id)
              ws.send(k)
              ws.send(JSON.stringify(v))
            }, {immediate: true})
          }
          for (let k of a.methods) {
            vm[k] = async function(...args) {
              return new Promise(function (resolve, reject) {
                ws.send('CALL')
                ws.send(vm.__id)
                let callId = (Math.random()*1000).toString().replace(/\./, '')
                calls[callId] = {resolve, reject}
                ws.send(callId)
                ws.send(k)
                ws.send(JSON.stringify(args))
              })
            }
          }
        } else if (a.startsWith('RETURN ')) {
          let parts = a.split(' ', 2)
          let callId = parts[1]
          if (calls[callId] !== undefined) {
            let v = JSON.parse(a.substr(parts.join(' ').length))
            calls[callId].resolve(v)
            delete calls[callId]
          }
        } else if (a.startsWith('ATOMIC ')) {
          let parts = a.split(' ')
          let upid = parts[1]
          // let k = parts[2] '_v_ATOMIC'
          let setAtomic = JSON.parse(parts[3])
          if (upid === vm.__id) {
            if (!atomic && setAtomic) {
              atomic = true
              toApply = {}
            } else if (atomic && !setAtomic) {
              atomic = false
              for (let k in toApply) {
                let v = toApply[k]
                valuesWhere[k] = v
                vm.$set(vm, k, v)
              }
              toApply = {}
            } else {
              console.log('INCOHERENT COMPONENT atomic STATE', atomic, setAtomic)
            }
          }
        } else if (a.startsWith('UPDATE ')) {
          let parts = a.split(' ', 3)
          let upid = parts[1]
          let k = parts[2]
          if (upid === vm.__id) {
            let v = a.substr(parts.join(' ').length)
            v = JSON.parse(v)
            valuesWhere[k] = v
            vm.$set(vm, k, v)
          }
        }
      })

      created.bind(this)() // not sure when it is best to call it, or whether we should accept it at all
    },
    data: () => ({
      ...pyState,
      ...optdata()
    }),
    props,
    ...opt
  })


  Vue.component(name, function (resolve, reject) {
    let wsurl = vuejspython.wsurl
    let wsMeta = new WebSocket(wsurl)
    wsMeta.addEventListener('open', function(a) {
      wsMeta.send('INFO')
      wsMeta.send(pyClass)
    })
    wsMeta.addEventListener('message', function(a) {
      a = a.data
      if (a.startsWith('INFO ')) {
        a = JSON.parse(a.substr('INFO '.length))
        props = [...props, ...a.props]
        let desc = description(a.state)
        resolve(desc)
        wsMeta.close()
      }
    })
  })
}
