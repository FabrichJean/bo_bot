module.exports = {
  apps : [{
    name: "bo-bot",
    script: "main.py",
    interpreter: "/www/wwwroot/bo_bot/venv/bin/python",
    cwd: "/www/wwwroot/bo_bot",
    env: {
      PYTHONPATH: ".",
      DEBUG: "True"
    }
  }]
}
