const
  express = require('express'),
  path = require('path'),
  serveStatic = require('serve-static'),
  history = require('connect-history-api-fallback'),
  compression = require('compression'),
  expressStaticGzip = require("express-static-gzip"),
  port = process.env.PORT || 5000;

const app = express();

app.use(history())
app.use(compression({
  level: 8,
  threshold: 0
}))

app.use("/", expressStaticGzip(path.join(__dirname, '/dist/spa/')));
app.use(serveStatic(__dirname + '/dist/spa/', {
  index: true
}))

app.listen(port, () => {
  console.log("server running ", port)
});
