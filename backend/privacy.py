import numpy as np

class DifferentialPrivacy:
    def __init__(self, epsilon=1.0):
        self.epsilon = epsilon

    def apply_laplace(self, value):
        noise = np.random.laplace(0, 1/self.epsilon)
        return value + noise

    def privatize_result(self, result):
        if result is None:
            return result

        privatized = []
        for row in result:
            new_row = []
            for item in row:
                if isinstance(item, (int, float)):
                    new_row.append(self.apply_laplace(item))
                else:
                    new_row.append(item)
            privatized.append(tuple(new_row))

        return privatized