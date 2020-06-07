class BusinessException(Exception):
    def __init__(self, response_code, error):
        self.response_code = response_code
        self.exception = error

    def responseCode(self):
        return self.response_code

    def __str__(self):
        return self.exception