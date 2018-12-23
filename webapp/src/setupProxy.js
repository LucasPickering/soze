const proxy = require('http-proxy-middleware');

module.exports = app => {
  app.use(
    proxy('/api', {
      target: process.env.SOZE_SERVER || 'http://localhost:5000/',
      pathRewrite: { '^/api': '/' },
    })
  );
};
