import pyaudio
import wave
import threading
from pynput import keyboard
import shutil
import tempfile
import os
from SpeechRecognizer import SpeechRecognizer
from LLMControlApi import LLMControlApi


# AudioRecorder class is used to record audio from the microphone
class AudioRecorder:
    def __init__(self):
        """
        Initialize the AudioRecorder instance.
        Set up the audio stream, variables for recording, and start the keyboard listener.
        """
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.file_name = 'temp.wav'
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.recording_complete_event = threading.Event()
        self.listener = None
        self.start_keyboard_listener()
        print("Recording on standby ------")

    def start_keyboard_listener(self):
        """
        Start the keyboard listener to detect key presses for starting and stopping recording.
        Also, handle the key press to exit the program.
        """
        def on_press(key):
            try:
                if key.char == '[' and not self.is_recording:
                    self.start_recording()
                elif key.char == ']' and self.is_recording:
                    self.stop_recording()
                elif key.char == '\\':  # Detect the '\' key press
                    if self.is_recording:
                        self.stop_recording()
                    self.listener.stop()  # Stop the keyboard listener
                    os._exit(0)  # Exit the program
            except AttributeError:
                pass

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def start_recording(self):
        """
        Start the audio recording process.
        Open the audio stream and set the recording flag to True.
        """
        self.frames = []
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self.callback
        )
        self.is_recording = True
        print("Recording in progress...")

    def stop_recording(self):
        """
        Stop the audio recording process.
        Stop and close the audio stream, save the recorded audio to a file, and set the recording complete event.
        """
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.save_to_file()
            print("Recording has ended")
            self.recording_complete_event.set()

    def callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for the audio stream.
        Append the incoming audio data to the frames list.
        """
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def save_to_file(self):
        """
        Save the recorded audio frames to a WAV file.
        Set the audio parameters and write the frames to the file.
        """
        with wave.open(self.file_name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))


# Process the recorded audio file, recognize the speech, and get feedback from the LLM
def process_recording(recognizer, llm_api):
    """
    Process the recorded audio file.
    Copy the temporary audio file, recognize the speech in it, and get feedback from the LLM.
    Finally, delete the temporary file.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_name = temp_file.name
        shutil.copyfile('temp.wav', temp_name)
        recognized_text = recognizer.recognize_file(temp_name)
        if recognized_text:
            model_feedback = llm_api.get_model_feedback(recognized_text)
            print(f"Large model feedback result: {model_feedback}")
    except Exception as e:
        print(f"Error processing recording: {e}")
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


if __name__ == "__main__":
    voice_appid = "xxx"
    voice_token = "xxx"
    recognizer = SpeechRecognizer(voice_appid, voice_token)

    LLM_api_key = "xxx"
    LLM_base_url = "https://ark.cn-beijing.volces.com/api/v3"
    llm_api = LLMControlApi(LLM_api_key, LLM_base_url)

    recorder = AudioRecorder()

    while True:
        recorder.recording_complete_event.wait()
        threading.Thread(
            target=process_recording,
            args=(recognizer, llm_api)
        ).start()
        recorder.recording_complete_event.clear()
        print("Recording on standby ------")