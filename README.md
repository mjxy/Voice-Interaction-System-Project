# 语音交互系统项目

## 一、项目概述

本项目是一个语音交互系统，它允许用户通过键盘控制录音，将录制的语音文件进行语音识别，再将识别结果发送给大语言模型（LLM）以获取反馈。系统主要包含音频录制、语音识别和大语言模型交互三个核心模块。

## 二、作者信息

- **作者**：陈俊友
- **所属院校**：山东大学
- **制作时间**：3 月 7 日

## 三、环境要求

### 操作系统

支持 Windows、Mac OS 和 Linux 操作系统。

### Python 版本

Python 3.6 及以上版本。

### 依赖库

项目依赖的 Python 库如下，可通过 `pip install -r requirements.txt` 进行安装：

```plaintext
pyaudio
pynput
openai
websockets
```

## 四、项目结构

```plaintext
project_root/
│
├── LLMControlApi.py        # 大语言模型交互模块
├── AudioRecorder.py        # 音频录制模块
├── SpeechRecognizer.py     # 语音识别模块
├── main.py                 # 主程序入口
├── Prompt.txt              # 大语言模型交互的提示信息文件
├── requirements.txt        # 项目依赖库文件
└── README.md               # 项目说明文档
```

## 五、使用方法

### 1. 配置参数

在 `main.py` 文件中，需要替换以下参数为实际的值：

```python
voice_appid = "xxx"  # 语音识别服务的 appid
voice_token = "xxx"  # 语音识别服务的 token
LLM_api_key = "xxx"  # 大语言模型的 API 密钥
LLM_base_url = "https://ark.cn-beijing.volces.com/api/v3"  # 大语言模型的基础 URL
```

### 2. 启动程序

在项目根目录下，执行以下命令启动程序：

```bash
python main.py
```

### 3. 录音操作

程序启动后，会提示录音处于待机状态，并告知开始、停止和退出的按键（默认分别为 `[`、`]` 和 `\`）。

- 按下开始录音键，开始录制音频。
- 按下停止录音键，停止录音，系统会将录制的音频保存为 `temp.wav` 文件，并进行语音识别和大语言模型交互。
- 按下退出程序键，若正在录音则先停止录音，然后退出程序。

## 六、模块说明

### 1. 音频录制模块（`AudioRecorder.py`）

负责从麦克风录制音频，并将录制的音频保存为 WAV 文件。支持自定义开始、停止和退出录音的按键。

### 2. 语音识别模块（`SpeechRecognizer.py`）

接收音频文件路径，调用语音识别 API 对音频文件进行识别，返回识别出的文本内容。支持 `.wav` 和 `.mp3` 格式的音频文件。

### 3. 大语言模型交互模块（`LLMControlApi.py`）

接收用户输入和系统提示信息，将其组合成消息列表发送给大语言模型，获取模型的反馈结果并返回。

### 4. 主程序（`main.py`）

初始化各个组件，循环等待录音完成事件。当录音完成后，创建新线程处理录制的音频文件，处理完成后继续等待下一次录音。

## 七、注意事项

- 请确保语音识别服务和大语言模型的 API 密钥和令牌正确配置，避免因身份验证失败导致程序异常。
- 录音过程中，请确保麦克风正常工作，避免因音频输入问题导致语音识别失败。
- 在与语音识别服务和大语言模型进行通信时，应使用安全的传输协议（如 HTTPS），确保数据传输安全。

## 八、贡献与反馈

如果你在使用过程中遇到问题或有任何建议，欢迎通过以下方式反馈：

- 提交 issue 到项目的 GitHub 仓库。
- 联系作者：2405842327@qq.com

希望本项目能为你带来良好的使用体验！

################################################################

# Voice Interaction System Project

## I. Project Overview

This project is a voice interaction system that allows users to control audio recording via the keyboard. The recorded voice files are then subjected to speech recognition, and the recognition results are sent to a large language model (LLM) to obtain feedback. The system mainly consists of three core modules: audio recording, speech recognition, and interaction with the large language model.

## II. Author Information

- **Author**: Junyou Chen 
- **Affiliation**: Shandong University
- **Creation Date**: March 7th

## III. Environment Requirements

### Operating System

Supported operating systems include Windows, Mac OS, and Linux.

### Python Version

Python 3.6 or higher is required.

### Dependencies

The Python libraries required for this project are as follows. You can install them using the command `pip install -r requirements.txt`:

```plaintext
pyaudio
pynput
openai
websockets
```

## IV. Project Structure

```plaintext
project_root/
│
├── LLMControlApi.py        # Module for interacting with the large language model
├── AudioRecorder.py        # Module for audio recording
├── SpeechRecognizer.py     # Module for speech recognition
├── main.py                 # Main program entry point
├── Prompt.txt              # File containing prompt information for interaction with the large language model
├── requirements.txt        # File listing project dependencies
└── README.md               # Project documentation
```

## V. Usage Instructions

### 1. Parameter Configuration

In the `main.py` file, replace the following parameters with your actual values:

```python
voice_appid = "xxx"  # App ID for the speech recognition service
voice_token = "xxx"  # Token for the speech recognition service
LLM_api_key = "xxx"  # API key for the large language model
LLM_base_url = "https://ark.cn-beijing.volces.com/api/v3"  # Base URL for the large language model
```

### 2. Starting the Program

In the project root directory, execute the following command to start the program:

```bash
python main.py
```

### 3. Recording Operations

After the program starts, it will prompt that the recording is on standby and inform you of the keys for starting, stopping, and exiting the recording (by default, `[`, `]`, and `\` respectively).

- Press the start recording key to begin recording audio.
- Press the stop recording key to end the recording. The system will save the recorded audio as a `temp.wav` file and proceed with speech recognition and interaction with the large language model.
- Press the exit program key. If recording is in progress, it will stop first, and then the program will exit.

## VI. Module Descriptions

### 1. Audio Recording Module (`AudioRecorder.py`)

This module is responsible for recording audio from the microphone and saving the recorded audio as a WAV file. It supports customizing the keys for starting, stopping, and exiting the recording.

### 2. Speech Recognition Module (`SpeechRecognizer.py`)

This module takes the path of an audio file as input, calls the speech recognition API to recognize the audio file, and returns the recognized text content. It supports audio files in `.wav` and `.mp3` formats.

### 3. Large Language Model Interaction Module (`LLMControlApi.py`)

This module receives user input and system prompt information, combines them into a message list, sends it to the large language model, and returns the feedback result from the model.

### 4. Main Program (`main.py`)

The main program initializes each component and waits in a loop for the recording completion event. When the recording is completed, it creates a new thread to process the recorded audio file. After processing, it continues to wait for the next recording.

## VII. Notes

- Ensure that the API keys and tokens for the speech recognition service and the large language model are correctly configured to avoid program exceptions caused by authentication failures.
- During the recording process, make sure the microphone is working properly to avoid speech recognition failures due to audio input issues.
- When communicating with the speech recognition service and the large language model, use a secure transmission protocol (such as HTTPS) to ensure data transmission security.

## VIII. Contribution and Feedback

If you encounter any problems or have suggestions during use, you can provide feedback in the following ways:

- Submit an issue to the project's GitHub repository.
- Contact the author: [Specific contact information can be added here]

We hope this project will provide you with a great user experience!