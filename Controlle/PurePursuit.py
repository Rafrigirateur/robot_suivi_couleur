import math

# ---------- UTILS ----------

def clamp(val, vmin, vmax):
    return max(vmin, min(val, vmax))


# ---------- ROBOT MODEL (SIMULATION) ----------

class RobotModel:
    """Modèle cinématique unicycle (simulation uniquement)"""

    def __init__(self, x=0.0, y=0.0, yaw=0.0, dt=0.05, max_omega=2.0):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.dt = dt
        self.max_omega = max_omega

    def step(self, v, kappa):
        omega = clamp(v * kappa, -self.max_omega, self.max_omega)
        self.x += v * math.cos(self.yaw) * self.dt
        self.y += v * math.sin(self.yaw) * self.dt
        self.yaw += omega * self.dt


# ---------- SPLINE ----------

class SplineGenerator:
    def __init__(self, step=0.02, alpha=0.5):
        self.step = step
        self.alpha = alpha

    def generate(self, waypoints):
        path = []
        for i in range(len(waypoints) - 1):
            x0, y0 = waypoints[i]
            x1, y1 = waypoints[i + 1]
            t = 0.0
            while t <= 1.0:
                x = (1 - t) * x0 + t * x1
                y = (1 - t) * y0 + t * y1
                path.append((x, y))
                t += self.step
        return path


# ---------- PURE PURSUIT ----------

class PurePursuit:
    def __init__(self, path, Ld_min=0.3, Ld_gain=0.8):
        self.path = path
        self.Ld_min = Ld_min
        self.Ld_gain = Ld_gain
        self.target_index = 0

    def goal_reached(self, x, y, tol=0.2):
        gx, gy = self.path[-1]
        return math.hypot(gx - x, gy - y) < tol

    def compute(self, x, y, yaw, v):
        Ld = max(self.Ld_min, self.Ld_gain * v)

        while self.target_index < len(self.path) - 1:
            tx, ty = self.path[self.target_index]
            if math.hypot(tx - x, ty - y) > Ld:
                break
            self.target_index += 1

        tx, ty = self.path[self.target_index]
        dx = tx - x
        dy = ty - y

        angle = math.atan2(dy, dx)
        alpha = angle - yaw

        kappa = 2 * math.sin(alpha) / Ld
        return kappa, tx, ty, Ld
