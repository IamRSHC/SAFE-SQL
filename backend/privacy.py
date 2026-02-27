import numpy as np

class DifferentialPrivacy:
    def __init__(self, epsilon=1.0, total_budget=10.0):
        self.epsilon = float(epsilon)
        self.total_budget = float(total_budget)
        self.remaining_budget = float(total_budget)
        self.mode = "private"  # private | raw | audit
        self.last_noise = []

    # --------------------------
    # Runtime Epsilon Control
    # --------------------------
    def set_epsilon(self, new_epsilon):
        new_epsilon = float(new_epsilon)
        if new_epsilon <= 0:
            raise ValueError("Epsilon must be greater than 0.")
        self.epsilon = new_epsilon

    # --------------------------
    # Mode Control
    # --------------------------
    def set_mode(self, mode):
        if mode not in ["private", "raw", "audit"]:
            raise ValueError("Mode must be 'private', 'raw', or 'audit'")
        self.mode = mode

    # --------------------------
    # Budget Check
    # --------------------------
    def check_budget(self):
        if self.remaining_budget < self.epsilon:
            raise Exception("Privacy budget exhausted.")

    # --------------------------
    # Laplace Mechanism
    # --------------------------
    def apply_laplace(self, value):
        noise = np.random.laplace(0, 1/self.epsilon)
        self.last_noise.append(noise)
        return value + noise

    # --------------------------
    # Main Privacy Handler
    # --------------------------
    def process_result(self, result):

        if result is None:
            return None

        # RAW MODE
        if self.mode == "raw":
            return {
                "raw": result,
                "private": result,
                "noise": None
            }

        # Budget Enforcement
        self.check_budget()
        self.last_noise = []

        privatized = []

        for row in result:
            new_row = []
            for item in row:
                if isinstance(item, (int, float)):
                    new_row.append(self.apply_laplace(item))
                else:
                    new_row.append(item)
            privatized.append(tuple(new_row))

        # Deduct privacy budget
        self.remaining_budget -= self.epsilon

        # PRIVATE MODE
        if self.mode == "private":
            return {
                "raw": None,
                "private": privatized,
                "noise": None
            }

        # AUDIT MODE
        if self.mode == "audit":
            return {
                "raw": result,
                "private": privatized,
                "noise": self.last_noise
            }

    # --------------------------
    # Metrics
    # --------------------------
    def get_metrics(self):
        return {
            "epsilon": self.epsilon,
            "total_budget": self.total_budget,
            "remaining_budget": self.remaining_budget,
            "mode": self.mode
        }