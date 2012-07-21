from fabric.api import local, lcd

def run_tests():
    with lcd('tests'):
        local('coverage run main.py')
        local('coverage html --include="../excatch.py"')

def run_bot():
    local("PYTHONPATH=. twistd -ny exbot/bot.tac")

def test_exception():
    import sys
    sys.path.insert(0, '.')
    import excatch
    excatch.bind()

    def test():
        def cb():
            1 / 0
        cb()
    test()

