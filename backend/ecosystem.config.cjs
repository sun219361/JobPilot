module.exports = {
  apps: [
    {
      name: 'jobpilot-api',
      script: 'python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload',
      cwd: '/home/user/webapp/backend',
      env: {
        PYTHONPATH: '/home/user/webapp/backend',
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
    },
  ],
}
