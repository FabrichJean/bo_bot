module.exports = {
  apps : [{
    name: "bo-bot",
    script: "main.py",
    interpreter: "/Users/md/Desktop/bobot/.venv/bin/python",
    cwd: "/Users/md/Desktop/bobot",
    env: {
      PYTHONPATH: ".",
      DEBUG: "True"
    }
  }]
}
