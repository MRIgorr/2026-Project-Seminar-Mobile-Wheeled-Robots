# Практическая работа №1
## Иструкция
**1. Перейти в репозиторий**

``` bash 
cd 2026-Project-Seminar-Mobile-Wheeled-Robots
```

**2. Сделать сборку среды**

``` bash
HOST_XAUTHORITY="$XAUTHORITY" docker compose --env-file .env --env-file .env.local -f docker-compose.yaml -f docker-compose.gpu.yaml build
```
**3. Запустить среду разработки** 

``` bash 
HOST_XAUTHORITY="$XAUTHORITY" docker compose --env-file .env --env-file .env.local -f docker-compose.yaml -f docker-compose.gpu.yaml up -d
```

``` bash
HOST_XAUTHORITY="$XAUTHORITY" docker compose --env-file .env --env-file .env.local -f docker-compose.yaml -f docker-compose.gpu.yaml exec -it ros2-base zsh
```

**4. Собрать рабочее пространство**
``` bash
colcon build
```

**5. Активировать окружение**

```bash
source install/setup.zsh
```
**6. Запустить launch-файл с переназначенными переменными**

```bash
ros2 launch practice01 numbers.launch.py turtle_name_1:=turtle01 digit_1:=0 turtle_name_2:=turtle02 digit_2:=5
```
