import pyaudio
import wave
import threading
from pynput import keyboard
import os


class AudioRecorder:
    def __init__(self, key_turn_on='[', key_turn_off=']', key_quit='\\'):
        """
        Initialize the AudioRecorder object.
        :param key_turn_on: The key to start recording. Default is '['.
        :param key_turn_off: The key to stop recording. Default is ']'.
        :param key_quit: The key to quit the program. Default is '\\'.
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
        self.key_turn_on = key_turn_on
        self.key_turn_off = key_turn_off
        self.key_quit = key_quit
        print(f"Recording on standby. Press {key_turn_on} to start, {key_turn_off} to stop, {key_quit} to quit ------")

    def start_keyboard_listener(self):
        """
        Start the keyboard listener to detect key presses for starting, stopping recording and quitting the program.
        """
        def on_press(key):
            try:
                if key.char == self.key_turn_on and not self.is_recording:
                    self.start_recording()
                elif key.char == self.key_turn_off and self.is_recording:
                    self.stop_recording()
                elif key.char == self.key_quit:  # Detect the '\' key press
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
        Stop the audio recording process, save the recorded audio to a file and set the recording complete event.
        """
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.save_to_file()
            print("Recording has ended.")
            self.recording_complete_event.set()

    def callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for the audio stream. Append the incoming audio data to the frames list.
        :param in_data: The incoming audio data.
        :param frame_count: The number of frames.
        :param time_info: Time information.
        :param status: The status of the audio stream.
        :return: The incoming audio data and the continue flag.
        """
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def save_to_file(self):
        """
        Save the recorded audio frames to a WAV file.
        """
        with wave.open(self.file_name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))


if __name__ == "__main__":
    # Create an instance of AudioRecorder
    recorder = AudioRecorder()

    try:
        # Wait for the recording completion event
        recorder.recording_complete_event.wait()

        # Check if the recording file exists
        if os.path.exists(recorder.file_name):
            print(f"The recording file {recorder.file_name} has been saved.")
        else:
            print("The recording file was not saved successfully.")

    except KeyboardInterrupt:
        print("The program was manually interrupted.")
    finally:
        # Terminate the PyAudio session
        recorder.audio.terminate()