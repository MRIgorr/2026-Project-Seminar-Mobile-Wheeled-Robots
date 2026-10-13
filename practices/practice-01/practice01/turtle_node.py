import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose as TurtlePose

def wrap_to_pi(a: float) -> float:
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

point = {
    0: [(0.0, 2.0), (-1.0, 2.0), (-1.0, 0.0), (0.0, 0.0)],
    1: [(0.0, 2.0)],
    2: [(-1.0, 0.0), (-1.0, 1.0), (0.0, 1.0), (0.0, 2.0), (-1.0, 2.0)],
    3: [(-1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (-1.0, 1.0), (0.0, 1.0), (0.0, 2.0), (-1.0, 2.0)],
    4: [(0.0, 2.0), (0.0, 1.0), (-1.0, 1.0), (-1.0, 2.0)],
    5: [(-1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (-1.0, 1.0), (-1.0, 2.0), (0.0, 2.0)],
    6: [(-1.0, 0.0), (-1.0, 1.0), (0.0, 1.0), (0.0, 0.0), (-1.0, 0.0), (-1.0, 2.0), (0.0, 2.0)],
    8: [(-1.0, 0.0), (-1.0, 2.0), (0.0, 2.0), (0.0, 0.0), (-1.0, 0.0), (-1.0, 1.0), (0.0, 1.0)],
    7: [(0.0, 2.0), (-1.0, 2.0)],
    9: [(-1.0, 0.0), (0.0, 0.0), (0.0, 2.0), (-1.0, 2.0), (-1.0, 1.0), (0.0, 1.0)],
}

size = 2.0

class NumberDrawer(Node):
    def __init__(self):
        super().__init__("turtle_node")

        self.declare_parameter("turtle", "turtle1")
        self.declare_parameter("digit", 0)
        self.declare_parameter("initial_x", 0)
        self.declare_parameter("initial_y", 0)
        self.declare_parameter("control_hz", 20.0)
        self.declare_parameter("point_tolerance", 0.05)

        self.declare_parameter("k_lin", 1.0)
        self.declare_parameter("k_ang", 5.0)
        self.declare_parameter("max_lin", 0.5)
        self.declare_parameter("max_ang", 1.5)
        self.declare_parameter("normal_angle", 0.05)

        turtle = self.get_parameter("turtle").value

        self.digit = int(self.get_parameter("digit").value)
        self.initial_x = int(self.get_parameter("initial_x").value)
        self.initial_y = int(self.get_parameter("initial_y").value)
        self.pose_topic = f"/{turtle}/pose"
        self.cmd_topic = f"/{turtle}/cmd_vel"

        self.control_hz = float(self.get_parameter("control_hz").value)
        self.dt = 1.0 / self.control_hz
        self.tol = float(self.get_parameter("point_tolerance").value)

        self.k_lin = float(self.get_parameter("k_lin").value)
        self.k_ang = float(self.get_parameter("k_ang").value)
        self.max_lin = float(self.get_parameter("max_lin").value)
        self.max_ang = float(self.get_parameter("max_ang").value)
        self.normal_angle = float(self.get_parameter("normal_angle").value)

        self.points = point[self.digit]
        self.point_index = 0

        self.pose_ready = False
        self.pose = TurtlePose()

        self.pose_sub = self.create_subscription(TurtlePose, self.pose_topic, self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, self.cmd_topic, 10)

        self.timer = self.create_timer(self.dt, self.on_timer)
    
    def on_pose(self, msg: TurtlePose):
        self.pose = msg
        self.pose_ready = True
    
    def publish_stop(self):
        self.cmd_pub.publish(Twist())
    
    def on_timer(self):
        if not self.pose_ready or self.point_index >= len(self.points):
            self.publish_stop()
            return

        x, y, theta = float(self.pose.x), float(self.pose.y), float(self.pose.theta)
        tx, ty = self.points[self.point_index]

        tx, ty = size * tx, size * ty

        dx, dy = tx - x + self.initial_x, ty - y + self.initial_y
        dist = math.hypot(dx, dy)

        if dist < self.tol:
            self.point_index += 1
            self.publish_stop()
            return
        
        angle_to_point = math.atan2(dy, dx)
        ang_err = wrap_to_pi(angle_to_point - theta)

        w = clamp(self.k_ang * ang_err, -self.max_ang, self.max_ang)
        v = min(self.k_lin * dist, self.max_lin)

        cmd = Twist()

        if abs(ang_err) > self.normal_angle:
            cmd.linear.x = 0.0
            cmd.angular.z = float(w)
        else:
            cmd.linear.x = float(v)
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)

def main():
    rclpy.init()
    node = NumberDrawer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
