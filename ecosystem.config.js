module.exports = {
  apps: [
    {
      name: 'bugtracer',
      script: './run.py',
      cwd: __dirname,
      interpreter: './.venv/bin/python',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 2000,
      watch: false,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'bugtracer-mcp',
      script: './run_mcp_sse.py',
      args: '--port 5003',
      cwd: __dirname,
      interpreter: './.venv/bin/python',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 2000,
      watch: false,
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
};
