class LowPassFilter:
    def __init__(self, alpha=0.4, warm_start=False):
        # warm_start seeds the filter with the first sample after a reset
        # instead of blending it against 0, avoiding a startup transient.
        # Must stay behaviorally identical to gnoci-sim's EMAFilter.
        self.warm_start = warm_start
        self.reset()
        self.alpha = alpha

    def reset(self):
        self.value = None if self.warm_start else 0

    def update(self, value):
        if self.value is None:
            self.value = value
        else:
            self.value = self.alpha * value + (1 - self.alpha) * self.value
        return self.value
