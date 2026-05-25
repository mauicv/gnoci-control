class LowPassFilter:
    def __init__(self, alpha=0.4):
        self.reset()
        self.alpha = alpha

    def reset(self):
        self.value = 0

    def update(self, value):
        self.value = self.alpha * value + (1 - self.alpha) * self.value
        return self.value