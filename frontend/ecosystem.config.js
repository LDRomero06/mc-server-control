module.exports = {
  apps: [{
    name: 'my-app',
    script: './app.js',
    instances: 1,
    execUser: 'unknown',
    env: { 
      NODE_ENV: 'development',
      IP: '127.0.0.1'
    }
  }] 
};