# hongbo

智能移动机器人 ROS 工作空间，集成底盘启动、激光 SLAM、导航巡航、AR 标签识别、视觉目标检测、语音交互、视觉语言模型识别和任务执行等功能。项目采用 ROS1 + catkin 组织，主要面向 ABOT/移动机器人实车调试和比赛任务流程。

## 项目功能

- 底盘与传感器启动：串口底盘驱动、IMU、RPLIDAR、机器人模型与 TF。
- 建图与导航：GMapping 建图、地图保存、AMCL 定位、move_base 路径规划、多目标点巡航。
- 视觉识别：USB 摄像头、AR 标签识别、find_object_2d 目标识别、OpenCV 示例、人脸/行人检测、颜色检测、OCR。
- 多模态大模型：通过火山方舟 Ark SDK 调用视觉语言模型，支持图片计算题识别、水果识别和 LLM 查询服务。
- 语音交互：语音识别、TTS 语音合成、比赛任务音频播报。
- 上层任务：结合导航、AR 标签、视觉识别、语音和执行机构控制完成综合任务。

## 目录结构

```text
.
├── src/
│   ├── abot_base/          # 底盘启动、IMU、机器人模型、雷达滤波
│   ├── robot_slam/         # 建图、定位、导航、多目标点任务
│   ├── track_tag/          # USB 摄像头标定与 AR 标签识别
│   ├── abot_find/          # find_object_2d 目标识别
│   ├── abot_vlm/           # 视觉语言模型与 LLM 服务
│   ├── TTS_audio/          # 文本转语音服务
│   ├── robot_voice/        # 语音识别与语音助手
│   ├── user_demo/          # 综合任务节点
│   ├── shoot_cmd/          # 执行机构/射击控制
│   ├── face_pkg/           # 人脸与行人检测
│   ├── tracker_pkg/        # KCF/LK 视觉跟踪
│   ├── cam_track/          # 摄像头跟踪节点
│   ├── color_pkg/          # 颜色识别、巡线、火焰检测
│   ├── ocr_detect/         # OCR 检测
│   └── opencv_demo/        # OpenCV 功能示例
├── 1-gmapping.sh           # 一键启动建图流程
├── 1-mission.sh            # 一键启动综合任务流程
├── build/                  # catkin 编译产物
└── devel/                  # catkin 开发环境产物
```

## 环境依赖

推荐运行环境：

- Ubuntu 18.04/20.04
- ROS1 Melodic 或 Noetic
- catkin
- Python 2/3，根据 ROS 发行版和脚本 shebang 调整
- OpenCV、cv_bridge、image_transport
- move_base、amcl、map_server、gmapping
- rplidar_ros
- usb_cam
- ar_track_alvar
- find_object_2d
- teleop_twist_keyboard
- 火山方舟 Ark SDK：`volcenginesdkarkruntime`

常用 ROS 依赖可按需安装：

```bash
sudo apt update
sudo apt install ros-${ROS_DISTRO}-gmapping \
                 ros-${ROS_DISTRO}-navigation \
                 ros-${ROS_DISTRO}-map-server \
                 ros-${ROS_DISTRO}-amcl \
                 ros-${ROS_DISTRO}-move-base \
                 ros-${ROS_DISTRO}-usb-cam \
                 ros-${ROS_DISTRO}-ar-track-alvar \
                 ros-${ROS_DISTRO}-find-object-2d \
                 ros-${ROS_DISTRO}-teleop-twist-keyboard
```

Python 依赖示例：

```bash
pip install opencv-python pillow numpy volcenginesdkarkruntime
```

## 编译

克隆仓库后进入工作空间根目录：

```bash
git clone https://github.com/hbo0921/hongbo.git
cd hongbo
```

编译并加载环境：

```bash
catkin_make
source devel/setup.bash
```

如果部分 Python 脚本没有执行权限，可执行：

```bash
chmod +x src/*/scripts/*.py
chmod +x 1-gmapping.sh 1-mission.sh
```

## 快速开始

### 1. 启动底盘、IMU、模型和雷达

```bash
roslaunch abot_bringup robot_with_imu.launch
```

该启动文件会加载：

- `bringup_with_imu.launch`
- `model.launch`
- `rplidar.launch`

### 2. GMapping 建图

方式一：使用脚本一键启动多个终端：

```bash
bash 1-gmapping.sh
```

方式二：手动分终端启动：

```bash
roscore
source devel/setup.bash
roslaunch abot_bringup robot_with_imu.launch
roslaunch robot_slam gmapping.launch
roslaunch robot_slam view_mapping.launch
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

保存地图：

```bash
roslaunch robot_slam save_map.launch
```

默认地图文件位于：

```text
src/robot_slam/maps/
```

### 3. 定位与导航

默认导航启动：

```bash
roslaunch robot_slam navigation.launch
```

该流程会加载 `map_server`、`move_base` 和 `amcl`，默认地图参数为 `test.yaml`。

如果需要指定地图：

```bash
roslaunch robot_slam navigation.launch map_name:=test.yaml
```

启动 RViz 导航视图：

```bash
roslaunch robot_slam view_nav.launch
```

### 4. AR 标签识别

启动 USB 摄像头及标定：

```bash
roslaunch track_tag usb_cam_with_calibration.launch
```

启动 AR 标签识别：

```bash
roslaunch track_tag ar_track_camera.launch
```

### 5. 视觉目标识别

启动 find_object_2d：

```bash
roslaunch find_object_2d find_object_2d.launch
```

或使用项目内封装：

```bash
roslaunch abot_find find_object_2d.launch
```

### 6. 视觉语言模型服务

启动 VLM/LLM 节点：

```bash
roslaunch abot_vlm vlm_node.launch
```

该启动文件包含：

- `top_view_shot_node`：订阅 `/usb_cam/image_raw`，保存当前图像并进行计算题识别。
- `identify_node`：提供水果识别服务。
- `llm_server`：提供 `llm_query` 服务。

相关接口：

```text
abot_vlm/srv/LLMQuery.srv
request:  string query
response: string result

abot_vlm/srv/VisionResult.srv
request:  string result
response: bool success
```

使用前需要配置火山方舟 Ark API Key 和模型接入点。建议通过环境变量或本地私有配置文件管理密钥，不要将真实 Key 提交到公开仓库。

### 7. 综合任务流程

一键启动比赛/任务流程：

```bash
bash 1-mission.sh
```

脚本会依次启动：

- `roscore`
- `abot_bringup robot_with_imu.launch`
- `robot_slam view_nav.launch`
- `robot_slam navigation.launch`
- `track_tag usb_cam_with_calibration.launch`
- `track_tag ar_track_camera.launch`
- `find_object_2d find_object_2d.launch`
- `robot_slam multi_goal.launch`
- `abot_vlm vlm_node.launch`

多目标点参数在以下文件中配置：

```text
src/robot_slam/launch/multi_goal.launch
src/user_demo/param/mission.yaml
```

## 常用模块命令

```bash
# 人脸检测
roslaunch face_pkg face_detector.launch

# 人脸识别
roslaunch face_pkg face_rec.launch

# 行人检测
roslaunch face_pkg detect_people.launch

# KCF 目标跟踪
roslaunch tracker_pkg kcf_tracker.launch

# LK 光流跟踪
roslaunch tracker_pkg lk_tracker.launch

# 颜色巡线
roslaunch color_pkg line_follower.launch

# 火焰/颜色检测
roslaunch color_pkg fire_detector.launch

# OCR 检测
roslaunch ocr_detect ocr.launch

# 摄像头跟踪
roslaunch cam_track cam_track.launch

# 射击/执行机构控制
rosrun shoot_cmd shoot_control
```

## 参数配置

- 导航地图：`src/robot_slam/maps/test.yaml`
- 导航参数：`src/robot_slam/params/`
- 多目标点：`src/robot_slam/launch/multi_goal.launch`
- 任务点位：`src/user_demo/param/mission.yaml`
- AR 相机标定：`src/track_tag/camera_calibration.yaml`
- 目标控制参数：`src/shoot_cmd/params/target.yaml`
- 跟踪 PID：`src/tracker_pkg/parameters/PID_param.yaml`

## 注意事项

1. `build/` 和 `devel/` 是 catkin 生成目录，重新编译时可由 `catkin_make` 生成。
2. 实车运行前请确认串口权限、雷达端口、摄像头设备号和底盘电源状态。
3. 不同 ROS 发行版对 Python 版本要求不同，若脚本启动失败，请检查 shebang、执行权限和依赖安装位置。
4. 部分脚本中存在绝对路径，例如 `/home/abot/310117`、`/home/abot/new_vision`，换机器部署时需要按实际工作空间路径修改。
5. 大模型相关功能需要网络连接和有效 API Key。公开仓库中不要提交真实密钥、音频素材版权文件或个人隐私数据。

## License

当前仓库内多个 `package.xml` 仍标记为 `TODO`。正式开源前建议补充明确许可证，例如 MIT、Apache-2.0 或 GPL-3.0。
