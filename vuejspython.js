
var vuejspython = {}

vuejspython.defaultPort =

vuejspython.start = function(wsurl, opt={}) {
  if (opt.data === undefined) opt.data = ()=>({})
  if (! wsurl.startsWith('ws')) {
    wsurl = 'ws://'+wsurl
  }
  if (wsurl.substr(4).indexOf(':') == -1) {
    wsurl = wsurl+':4259'
  }
  var wsInit = new WebSocket(wsurl+'/init');
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
    });
    ws.addEventListener('message', function(a) {
      a = a.data
      if (a.startsWith('UPDATE ')) {
        let parts = a.split(' ', 2)
        let k = parts[1]
        let v = a.substr(parts.join(" ").length)
        v = JSON.parse(v)
        valuesWhere[k] = v
        vm.$set(vm, k, v)
      }
    })
    window.vuejspython_vm = vm // for console-based introspection
  });
}
