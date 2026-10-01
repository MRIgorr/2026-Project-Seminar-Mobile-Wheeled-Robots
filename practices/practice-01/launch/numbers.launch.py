from launch import LaunchDescription
from launch.actions import(
    ExecuteProcess, 
    LogInfo,
    RegisterEventHandler,
    TimerAction,
    DeclareLaunchArgument,
)
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.event_handlers import OnProcessStart

def generate_launch_description():

    turtlesim = Node(
        package="turtlesim", executable="turtlesim_node", name="turtlesim"
    )

    kill_turtle = ExecuteProcess(
        cmd=[
            "ros2",
            "service",
            "call",
            "/kill",
            "turtlesim/srv/Kill",
            "{name: turtle1}",
        ],
        output="screen",
    )

    get_turtle_name_1 = DeclareLaunchArgument("turtle_name_1", default_value="turtle01")

    spawn_turtle_1 = ExecuteProcess(
        cmd=[
            "ros2",
            "service",
            "call",
            "/spawn",
            "turtlesim/srv/Spawn",
            PythonExpression([
                "'{x: 4, y: 2, theta: 0, name: \"' + '",
                LaunchConfiguration('turtle_name_1'), 
                "' + '\"}'",
            ]),
        ],
        output="screen"
    )

    get_turtle_name_2 = DeclareLaunchArgument("turtle_name_2", default_value="turtle02")

    spawn_turtle_2 = ExecuteProcess(
        cmd=[
            "ros2",
            "service",
            "call",
            "/spawn",
            "turtlesim/srv/Spawn",
            PythonExpression([
                "'{x: 7, y: 2, theta: 0, name: \"' + '",
                LaunchConfiguration('turtle_name_2'), 
                "' + '\"}'",
            ]),
        ],
        output="screen"
    )

    digit_arg_1 = DeclareLaunchArgument("digit_1", default_value="0")

    num1 = Node(
        package="practice01",
        executable="turtle_node",
        name="turtle_node_1",
        parameters=[{
            "turtle": LaunchConfiguration("turtle_name_1"),
            "digit": LaunchConfiguration("digit_1"),
            "initial_x": 4,
            "initial_y": 2,
        }],
        output="screen",
    )

    digit_arg_2 = DeclareLaunchArgument("digit_2", default_value="0")

    num2 = Node(
        package="practice01",
        executable="turtle_node",
        name="turtle_node_2",
        parameters=[{
            "turtle": LaunchConfiguration("turtle_name_2"),
            "digit": LaunchConfiguration("digit_2"),
            "initial_x": 7,
            "initial_y": 2,
        }],
        output="screen",
    )

    return LaunchDescription(
        [
            get_turtle_name_1,
            digit_arg_1,
            get_turtle_name_2,
            digit_arg_2,
            turtlesim,
            RegisterEventHandler(
                OnProcessStart(
                    target_action=turtlesim,
                    on_start=[
                        LogInfo(msg="Turtlesim started, spawning two turtles"),
                        kill_turtle,
                        spawn_turtle_1,
                        spawn_turtle_2,
                        num1, 
                        num2,
                    ],
                )
            ),
            TimerAction(period=1.0, actions=[LogInfo(msg="Programm is ended")]),
        ]
    )
