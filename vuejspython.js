
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
  var wsInit = new WebSocket(wsurl+'/init')
  wsInit.addEventListener('message', function(a) {
    a = JSON.parse(a.data)
    var ws = new WebSocket(wsurl+'/');
    let computed = {...opt.computed}
    let methods = {...opt.methods}
    let watch = {...opt.watch}
    let optdata = opt.data
    let optel = opt.el || '#main'
    for (let k of ['el', 'data', 'watch', 'methods', 'computed']) delete opt[k]
    let valuesWhere = {}
    for (let k in a.state) {
      let watchk = function (v, old) {
        if (valuesWhere[k] == v) return
        delete valuesWhere[k]
        ws.send('UPDATE')
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
        ws.send(k)
        ws.send(JSON.stringify(args))
      }
    }
    let vm = new Vue({
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
    ws.addEventListener('message', function(a) {
      a = a.data
      if (a.startsWith('UPDATE ')) {
        let parts = a.split(' ', 2)
        let k = parts[1]
        let v = a.substr(parts.join(' ').length)
        v = JSON.parse(v)
        valuesWhere[k] = v
        vm.$set(vm, k, v)
      }
    })
    window.vuejspython_vm = vm // for console-based introspection
  })
}

let instanceId = 1

vuejspython.component = function(pyClass, name, opt={}) {
  // later, consider refactoring if the two are really similar
  if (opt.data === undefined) opt.data = ()=>({})
  if (opt.props === undefined) opt.props = []
  // async component
  Vue.component(name, function (resolve, reject) {
    let id = instanceId
    instanceId++
    let wsurl = vuejspython.wsurl
    // TODO watch properties below to send notif
    var wsInit = new WebSocket(wsurl+'/init:'+pyClass+':'+id)







    /// TODO WIP, it seems the promise is called only once
    /// the async is more for loading the component, not the instance
    /// should consider how to do the creation of instances
    /// maybe everything is too single-instance in the code...
    /// so above we cannot just connect to init:Truc:1
    /// it might well be easy still, as below we don't really access the js object
    /// maybe beforeCreate .... .__id = instanceId++ .... etc
    wsInit.addEventListener('message', function(a) {
      a = JSON.parse(a.data)
      var ws = new WebSocket(wsurl+'/');
      let props = {...opt.props}
      let computed = {...opt.computed}
      let methods = {...opt.methods}
      let watch = {...opt.watch}
      let optdata = opt.data
      for (let k of ['props', 'data', 'watch', 'methods', 'computed']) delete opt[k]
      let valuesWhere = {}

      for (let k in a.state) {
        let watchk = function (v, old) {
          if (valuesWhere[k] == v) return
          delete valuesWhere[k]
          ws.send('UPDATE:'+id)
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
          console.log('CALL:'+id, ...args)
          ws.send('CALL:'+id)
          ws.send(k)
          ws.send(JSON.stringify(args))
        }
      }
      resolve({
        data: () => ({
          ...a.state,
          ...optdata()
        }),
        props,
        computed,
        methods,
        watch,
        ...opt,
      })
      ws.addEventListener('message', function(a) {
        a = a.data
        if (a.startsWith('UPDATE:'+id+' ')) {
          let parts = a.split(' ', 2)
          let k = parts[1]
          let v = a.substr(parts.join(' ').length)
          v = JSON.parse(v)
          valuesWhere[k] = v
          vm.$set(vm, k, v)
        }
      })
    })
    wsInit.addEventListener('open', function(a) {
      wsInit.send(JSON.stringify(opt.props))
    })
  })
}
