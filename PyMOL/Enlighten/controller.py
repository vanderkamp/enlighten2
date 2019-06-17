class Controller:

    def __init__(self):
        self.state = {}
        self.listeners = {}

    def update(self, key, value):
        if self.state.get(key) == value:
            return
        self.state[key] = value
        print(self.state)
        for listener in self._get_listeners(key):
            listener(value)

    def updater(self, key):
        return lambda value: self.update(key, value)

    def listen(self, key, listener):
        self.listeners[key] = self._get_listeners(key) + [listener]

    def _get_listeners(self, key):
        return self.listeners.get(key, [])


class EnlightenController(Controller):

    @staticmethod
    def open_enlighten_website():
        import webbrowser
        webbrowser.open_new("https://github.com/vanderkamp/enlighten2/")
