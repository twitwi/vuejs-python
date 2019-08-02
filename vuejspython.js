
var vuejspython = {}

vuejspython.defaultPort = 4259
vuejspython.wsurl = null

vuejspython.start = function(wsurl, opt={}) {
  if (opt.data === undefined) opt.data = ()=>({})
  if (! wsurl.startsWith('ws')) {
    wsurl = 'ws://' + wsurl
  }
  if (wsurl.substr(4).indexOf(':') == -1) {
    wsurl = wsurl + ':' + vuejspython.defaultPort
  }
  vuejspython.wsurl = wsurl
  var ws = new WebSocket(wsurl)
  let valuesWhere = {}
  let vm = null
  ws.addEventListener('open', function(a) {
    ws.send('INIT')
    ws.send('ROOT')
  })
  ws.addEventListener('message', function(a) {
    a = a.data
    console.log("rcv root", a)
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
        methods[k] = function(...args) {
          ws.send('CALL')
          ws.send('ROOT')
          ws.send(k)
          ws.send(JSON.stringify(args))
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
    } else if (a.startsWith('UPDATE ')) {
      let parts = a.split(' ', 3)
      let upid = parts[1]
      let k = parts[2]
      if (upid === 'ROOT') {
        let v = a.substr(parts.join(' ').length)
        v = JSON.parse(v)
        valuesWhere[k] = v
        vm.$set(vm, k, v)
      }
    }
  })
}


let instanceId = 1

vuejspython.component = function(pyClass, name, opt={}) {

  // later, consider refactoring if the two are really similar
  if (opt.props === undefined) opt.props = []

  let created = opt.created || (()=>{})
  for (let k of ['created']) delete opt[k]

  // TODO make a first call to know what is in data (what is reactive)
  //      same for python-computed I guess
  // ... and this will make all this registration async, so async component
  // currently, we are forced to declare it also in js

  // TODO watch properties below to send notif
  Vue.component(name, {
    created: function() {
      let wsurl = vuejspython.wsurl
      let ws = new WebSocket(wsurl)
      let valuesWhere = {}
      ws.addEventListener('open', function(a) {
        ws.send('INIT')
        ws.send(pyClass)
        ws.send(JSON.stringify(opt.props))
      })

      let vm = this
      vm.__id = 'NOT-SET-YET'
      ws.addEventListener('message', function(a) {
        a = a.data
        vm.__ws = ws
        console.log("rcv", name, a)
        if (a.startsWith('INIT ')) {
          a = JSON.parse(a.substr('INIT '.length))
          vm.__id = a.id
          console.log("RECEIVED INIT ID", pyClass, a.id, Object.keys(a.state))

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
          for (let k of a.methods) {
            vm[k] = function(...args) {
              ws.send('CALL')
              ws.send(vm.__id)
              ws.send(k)
              ws.send(JSON.stringify(args))
            }
          }
        } else if (a.startsWith('UPDATE ')) {
          let parts = a.split(' ', 3)
          let upid = parts[1]
          let k = parts[2]
          if (upid === vm.__id) {
            let v = a.substr(parts.join(' ').length)
            console.log(v)
            v = JSON.parse(v)
            valuesWhere[k] = v
            vm.$set(vm, k, v)
          }
        }
      })

      created.bind(this)() // not sure when it is best to call it, or whether we should accept it at all
    },
    ...opt
  })
}
