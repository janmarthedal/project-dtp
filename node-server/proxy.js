var http = require('http'),
    httpProxy = require('http-proxy');

//
// Create a new instance of HttProxy to use in your server
//
var proxy = new httpProxy.RoutingProxy();

//
// Create a regular http server and proxy its handler
//
http.createServer(function (req, res) {

  var url = req.url;

  if (url == '/foo') {
    res.writeHead(200, {"Content-Type": "text/plain"});
    res.end("Hello foo\n");
  } else {
    proxy.proxyRequest(req, res, {
      host: 'localhost',
      port: 8000
    });
  }
}).listen(8001);

