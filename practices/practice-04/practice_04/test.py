import math
import csv
import json
from pathlib import Path
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.executors import ExternalShutdownException
from tf2_ros import Buffer, TransformListener, TransformException
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def yaw(q):
    return math.atan2(
        2 * (q.w * q.z + q.x * q.y),
        1 - 2 * (q.y * q.y + q.z * q.z)
    )

class Test(Node):
    def __init__(self):
        super().__init__('test')

        self.declare_parameter('duration', 240.0)
        self.declare_parameter('pos_threshold', 0.2)
        self.declare_parameter('yaw_threshold', 0.15)
        self.declare_parameter('confirm_duration', 10.0)
        self.declare_parameter('run_name', 'test')
        self.declare_parameter('results_dir', 'results')

        self.duration = self.get_parameter('duration').value
        self.pos_limit = self.get_parameter('pos_threshold').value
        self.yaw_limit = self.get_parameter('yaw_threshold').value
        self.confirm = self.get_parameter('confirm_duration').value
        self.name = self.get_parameter('run_name').value
        self.folder = Path(self.get_parameter('results_dir').value)

        self.buf = Buffer()
        self.listener = TransformListener(self.buf, self)

        self.start = None
        self.prev = None
        self.good =None
        self.conv = None
        self.rows = []
        self.done = False

        self.timer = self.create_timer(0.1, self.measure)
        self.get_logger().info('Waiting for transforms')

    def measure(self):
        now = self.get_clock().now().nanoseconds / 1e9
        if now <= 0:
            return

        if self.start is not None and now - self.start >= self.duration:
            self.save()
            return

        try:
            amcl = self.buf.lookup_transform('map', 'base_link', Time())
            stamp = Time.from_msg(amcl.header.stamp)
            gt = self.buf.lookup_transform('map', 'base_link_gt', stamp)
        except TransformException:
            return

        current = stamp.nanoseconds / 1e9

        if self.start is None:
            self.start = current
            self.get_logger().info('Started')

        t = current - self.start

        if self.prev is not None and t <= self.prev:
            return
        
        a = amcl.transform.translation
        g = gt.transform.translation

        pos = math.hypot(a.x - g.x, a.y - g.y)

        angle = yaw(amcl.transform.rotation) - yaw(gt.transform.rotation)
        err = abs(math.atan2(math.sin(angle), math.cos(angle)))

        self.rows.append([
            t, g.x, g.y, yaw(gt.transform.rotation),
            a.x, a.y, yaw(amcl.transform.rotation), pos, err
        ])

        if self.prev is not None and t - self.prev > 0.5:
            self.good = None
        if pos <= self.pos_limit and err <= self.yaw_limit:
            if self.good is None:
                self.good = t
            if self.conv is None and t - self.good >= self.confirm:
                self.conv = self.good
                self.get_logger().info(f'Convergence: {self.conv:.2f}')
        else:
            self.good = None

        self.prev = t

        if len(self.rows) % 20 == 0:
            self.get_logger().info(f't={t:.1f} pos={pos:.3f} yaw={err:.3f}')

    def save(self):
        if self.done:
            return
        self.done = True
        self.timer.cancel()
        self.folder.mkdir(parents=True, exist_ok=True)

        with open(self.folder / f'{self.name}.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow([
                'time', 'gt_x', 'gt_y', 'gt_yaw',
                'amcl_x', 'amcl_y', 'amcl_yaw',
                'pos_error', 'yaw_error'
            ])
            w.writerows(self.rows)

        info = {
            'run_name': self.name,
            'duration': self.duration,
            'pos_threshold': self.pos_limit,
            'yaw_threshold': self.yaw_limit,
            'confirm_duration': self.confirm,
            'convergence_time': self.conv,
            'samples': len(self.rows)
        }

        with open(self.folder / f'{self.name}.json', 'w') as f:
            json.dump(info, f, indent=2)

        if self.rows:
            self.plot()

        self.get_logger().info(f'Convergence time: {self.conv}')
        self.get_logger().info('Results saved')

    def plot(self):
        t, gx, gy, ga, ax, ay, aa, ep, ey = zip(*self.rows)

        fig, p = plt.subplots(3, 1, figsize=(9, 12))

        p[0].plot(gx, gy, label='Истинная траектория')
        p[0].plot(ax, ay, label='Оценка AMCL')
        p[0].set_title('Траектория робота')
        p[0].set_xlabel('X (м)')
        p[0].set_ylabel('Y (м)')
        p[0].set_aspect('equal')
        p[0].legend()
        p[0].grid()

        for i, values, limit, title, unit in [(1, ep, self.pos_limit, 'Ошибка положения', 'м'), (2, ey, self.yaw_limit, 'Ошибка угла', 'рад')]:
            p[i].plot(t, values, label=title)
            p[i].axhline(limit, color='red', linestyle='--', label='Порог')

            if self.conv is not None:
                p[i].axvline(self.conv, color='green', linestyle=':', label='Сходимость')

            p[i].set_xlabel('Время от начала эксперимента (с)')
            p[i].set_ylabel(f'{title} ({unit})')
            p[i].legend()
            p[i].grid()

        plt.tight_layout()
        plt.savefig(self.folder / f'{self.name}.png', dpi=150)
        plt.close()

def main(args=None):
    rclpy.init(args=args)
    node = Test()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.5)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
