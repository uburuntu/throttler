
class LoggerMock:

    def __init__(self):
        self.msg = []
        self.wait = []

    def __call__(self, msg: str, wait: float, **kwargs):
        self.msg.append(msg)
        self.wait.append(wait)
