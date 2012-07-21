from fabric.api import local, lcd

def run_tests():
    with lcd('tests'):
        local('coverage run main.py')
        local('coverage html --include="../excatch.py"')

def run_bot():
    local("PYTHONPATH=. twistd -ny exbot/bot.tac")
