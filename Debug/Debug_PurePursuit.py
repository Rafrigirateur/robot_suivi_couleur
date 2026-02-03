import math
import random
import matplotlib.pyplot as plt
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from Controlle.PurePursuit import (
    RobotModel,
    PurePursuit,
    SplineGenerator,
    clamp
)

# ---------- WAYPOINTS ----------

def generate_fake_waypoints(n=8):
    pts = [(0.0, 0.0)]
    x, y = 0.0, 0.0
    for _ in range(n - 1):
        x += random.uniform(0.5, 1.0)
        y += random.uniform(-1.2, 1.2)
        pts.append((x, y))
    return pts


# ---------- VISU ----------

class DebugVisualizer:
    def __init__(self):
        plt.ion()
        self.fig = plt.figure(figsize=(10, 6))

    def update(self, path, traj, target=None, Ld=None):
        self.fig.clear()
        px, py = zip(*path)
        tx, ty = zip(*traj)

        plt.plot(px, py, "k--", label="Spline")
        plt.plot(tx, ty, "r-", label="Robot")
        plt.plot(tx[-1], ty[-1], "ro")

        if target:
            plt.scatter(*target, c="g", marker="*")

        plt.axis("equal")
        plt.grid()
        plt.legend()
        plt.pause(0.001)


# ---------- MAIN ----------

def main():
    waypoints = generate_fake_waypoints(10)
    path = SplineGenerator(step=0.01).generate(waypoints)

    controller = PurePursuit(path)
    robot = RobotModel(x=-0.3, y=-0.4, dt=0.025)

    traj = [(robot.x, robot.y)]
    debug = DebugVisualizer()

    for _ in range(3000):
        if controller.goal_reached(robot.x, robot.y):
            break

        dist = math.hypot(path[-1][0] - robot.x, path[-1][1] - robot.y)
        v = 0.4 * clamp(dist / 3.0, 0.1, 1.0)

        kappa, tx, ty, Ld = controller.compute(robot.x, robot.y, robot.yaw, v)
        robot.step(v, kappa)
        traj.append((robot.x, robot.y))

        debug.update(path, traj, (tx, ty), Ld)

    plt.show()


if __name__ == "__main__":
    main()
