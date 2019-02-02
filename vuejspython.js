
var vuejspython = {}

vuejspython.defaultPort =

vuejspython.start = function(wsurl, opt={}) {
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
    let methods = {}
    let watch = {}
    let valuesWhere = {}
    for (let k in a.state) {
      watch[k] = function (v, old) {
        if (valuesWhere[k] == v) return
        delete valuesWhere[k]
        ws.send('UPDATE')
        ws.send(k)
        ws.send(v)
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
      el: '#main',
      data: () => ({
        ...a.state
      }),
      computed,
      methods,
      watch
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
  });
}
