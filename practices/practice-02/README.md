# Практическая работа №2. Знакомство с Webots
## Примечание
**Практическая работа выполнена на macOS**
## Иструкция
**1. Запуск скрипта-сервера Webots в терминале на macOS**

``` bash 
export WEBOTS_HOME=/Applications/Webots.app
python3 local_simulation_server.py
```

**2. Перейти в репозиторий в Ubuntu**

``` bash 
cd 2026-Project-Seminar-Mobile-Wheeled-Robots
```

**3. Сделать сборку среды**

``` bash
HOST_XAUTHORITY="$XAUTHORITY" docker compose --env-file .env --env-file .env.local -f docker-compose.yaml -f docker-compose.gpu.yaml -f docker-compose.webots-mac.yaml build
```
**4. Запустить среду разработки** 

``` bash 
HOST_XAUTHORITY="$XAUTHORITY" docker compose --env-file .env --env-file .env.local -f docker-compose.yaml -f docker-compose.gpu.yaml -f docker-compose.webots-mac.yaml up -d
```

``` bash
HOST_XAUTHORITY="$XAUTHORITY" docker compose --env-file .env --env-file .env.local -f docker-compose.yaml -f docker-compose.gpu.yaml -f docker-compose.webots-mac.yaml exec -it ros2-base zsh
```

**5. Собрать рабочее пространство**
``` bash
colcon build
```

**6. Активировать окружение**

```bash
source install/setup.zsh
```
**7. Запустить launch-файл сцены**

```bash
ros2 launch practice-02 webot_digits.launch.py
```
**8. Открыть второй терминал и запустить команду**

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/TwistStamped "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: 'base_link'}, twist: {linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.08}}}"
```
