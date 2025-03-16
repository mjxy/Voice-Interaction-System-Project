# coding=utf-8

"""
Requires Python 3.6 or later

pip install asyncio
pip install websockets
"""

import asyncio
import base64
import gzip
import hmac
import json
import logging
import os
import uuid
import wave
from enum import Enum
from hashlib import sha256
from io import BytesIO
from typing import List, Optional
from urllib.parse import urlparse
import time
import websockets


class AudioType(Enum):
    LOCAL = 1  # Use local audio files


class SpeechRecognizer:
    def __init__(self, appid, token, cluster="volcengine_input_common"):
        """
        Initialize the speech recognizer.

        :param appid: The appid of the project.
        :param token: The token of the project.
        :param cluster: The cluster to request.
        """
        self.appid = appid
        self.token = token
        self.cluster = cluster
        self.ws_url = "wss://openspeech.bytedance.com/api/v2/asr"
        self.auth_method = "token"

        # Default parameter settings
        self.success_code = 1000
        self.seg_duration = 15000
        self.nbest = 1
        self.uid = "streaming_asr_demo"
        self.workflow = "audio_in,resample,partition,vad,fe,decode,itn,nlu_punctuate"
        self.show_language = False
        self.show_utterances = False
        self.result_type = "full"
        self.rate = 16000
        self.language = "zh-CN"
        self.bits = 16
        self.channel = 1
        self.codec = "raw"
        self.mp3_seg_size = 10000

    async def _recognize_audio(self, audio_path):
        """
        Internal method: Call the speech recognition API to process the audio file.
        """
        # Set the audio format (based on the file extension)
        self.format = os.path.splitext(audio_path)[1][1:].lower()
        if self.format not in ["wav", "mp3"]:
            raise ValueError("Only .wav and .mp3 formats are supported")

        client = AsrWsClient(
            audio_path=audio_path,
            cluster=self.cluster,
            appid=self.appid,
            token=self.token,
            format=self.format,
            audio_type=AudioType.LOCAL,
            auth_method=self.auth_method,
            ws_url=self.ws_url,
            seg_duration=self.seg_duration,
            nbest=self.nbest,
            uid=self.uid,
            workflow=self.workflow,
            show_language=self.show_language,
            show_utterances=self.show_utterances,
            result_type=self.result_type,
            sample_rate=self.rate,
            language=self.language,
            bits=self.bits,
            channel=self.channel,
            codec=self.codec,
            mp3_seg_size=self.mp3_seg_size
        )

        return await client.execute()

    def recognize_file(self, audio_path):
        """
        Recognize the content of an audio file.

        :param audio_path: The path of the audio file (.wav or .mp3 format).
        :return: The recognized text content.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = asyncio.run(self._recognize_audio(audio_path))

        # Extract text from the result
        if (
                'payload_msg' in result and
                'result' in result['payload_msg'] and
                result['payload_msg']['result'] and
                'text' in result['payload_msg']['result'][0]
        ):
            return result['payload_msg']['result'][0]['text']
        else:
            if 'payload_msg' in result and 'message' in result['payload_msg']:
                error_message = result['payload_msg']['message']
                raise Exception(f"Recognition failed: {error_message}")
            else:
                raise Exception("Recognition failed for unknown reason")


# The following are support classes, keeping the functions in the original code unchanged
class AsrWsClient:
    def __init__(self, audio_path, cluster, **kwargs):
        """
        :param config: Configuration.
        """
        self.audio_path = audio_path
        self.cluster = cluster
        self.success_code = int(kwargs.get("success_code", 1000))  # Success code, default is 1000
        self.seg_duration = int(kwargs.get("seg_duration", 15000))
        self.nbest = int(kwargs.get("nbest", 1))
        self.appid = kwargs.get("appid", "")
        self.token = kwargs.get("token", "")
        self.ws_url = kwargs.get("ws_url", "wss://openspeech.bytedance.com/api/v2/asr")
        self.uid = kwargs.get("uid", "streaming_asr_demo")
        self.workflow = kwargs.get("workflow", "audio_in,resample,partition,vad,fe,decode,itn,nlu_punctuate")
        self.show_language = kwargs.get("show_language", False)
        self.show_utterances = kwargs.get("show_utterances", False)
        self.result_type = kwargs.get("result_type", "full")
        self.format = kwargs.get("format", "wav")
        self.rate = kwargs.get("sample_rate", 16000)
        self.language = kwargs.get("language", "zh-CN")
        self.bits = kwargs.get("bits", 16)
        self.channel = kwargs.get("channel", 1)
        self.codec = kwargs.get("codec", "raw")
        self.audio_type = kwargs.get("audio_type", AudioType.LOCAL)
        self.secret = kwargs.get("secret", "access_secret")
        self.auth_method = kwargs.get("auth_method", "token")
        self.mp3_seg_size = int(kwargs.get("mp3_seg_size", 10000))

    def construct_request(self, reqid):
        """
        Construct the request data.
        :param reqid: The request ID.
        :return: The constructed request dictionary.
        """
        req = {
            'app': {
                'appid': self.appid,
                'cluster': self.cluster,
                'token': self.token,
            },
            'user': {
                'uid': self.uid
            },
            'request': {
                'reqid': reqid,
                'nbest': self.nbest,
                'workflow': self.workflow,
                'show_language': self.show_language,
                'show_utterances': self.show_utterances,
                'result_type': self.result_type,
                "sequence": 1
            },
            'audio': {
                'format': self.format,
                'rate': self.rate,
                'language': self.language,
                'bits': self.bits,
                'channel': self.channel,
                'codec': self.codec
            }
        }
        return req

    @staticmethod
    def slice_data(data: bytes, chunk_size: int):
        """
        Slice the data.
        :param data: The wav data.
        :param chunk_size: The segment size in one request.
        :return: The segment data and the last flag.
        """
        data_len = len(data)
        offset = 0
        while offset + chunk_size < data_len:
            yield data[offset: offset + chunk_size], False
            offset += chunk_size
        else:
            yield data[offset: data_len], True

    def token_auth(self):
        """
        Perform token authentication.
        :return: The authentication header.
        """
        return {'Authorization': 'Bearer; {}'.format(self.token)}

    def signature_auth(self, data):
        """
        Perform signature authentication.
        :param data: The data for authentication.
        :return: The authentication header.
        """
        header_dicts = {
            'Custom': 'auth_custom',
        }

        url_parse = urlparse(self.ws_url)
        input_str = 'GET {} HTTP/1.1\n'.format(url_parse.path)
        auth_headers = 'Custom'
        for header in auth_headers.split(','):
            input_str += '{}\n'.format(header_dicts[header])
        input_data = bytearray(input_str, 'utf-8')
        input_data += data
        mac = base64.urlsafe_b64encode(
            hmac.new(self.secret.encode('utf-8'), input_data, digestmod=sha256).digest())
        header_dicts['Authorization'] = 'HMAC256; access_token="{}"; mac="{}"; h="{}"'.format(self.token,
                                                                                              str(mac, 'utf-8'),
                                                                                              auth_headers)
        return header_dicts

    async def segment_data_processor(self, wav_data: bytes, segment_size: int):
        """
        Process the segmented audio data.
        :param wav_data: The wav audio data.
        :param segment_size: The segment size.
        :return: The processing result.
        """
        reqid = str(uuid.uuid4())
        # Construct the full client request and serialize and compress it
        request_params = self.construct_request(reqid)
        payload_bytes = str.encode(json.dumps(request_params))
        payload_bytes = gzip.compress(payload_bytes)
        full_client_request = bytearray(generate_full_default_header())
        full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
        full_client_request.extend(payload_bytes)  # payload
        header = None
        if self.auth_method == "token":
            header = self.token_auth()
        elif self.auth_method == "signature":
            header = self.signature_auth(full_client_request)
        async with websockets.connect(self.ws_url, extra_headers=header, max_size=1000000000) as ws:
            # Send the full client request
            await ws.send(full_client_request)
            res = await ws.recv()
            result = parse_response(res)
            if 'payload_msg' in result and result['payload_msg']['code'] != self.success_code:
                return result
            for seq, (chunk, last) in enumerate(AsrWsClient.slice_data(wav_data, segment_size), 1):
                # If no compression, comment this line
                payload_bytes = gzip.compress(chunk)
                audio_only_request = bytearray(generate_audio_default_header())
                if last:
                    audio_only_request = bytearray(generate_last_audio_default_header())
                audio_only_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
                audio_only_request.extend(payload_bytes)  # payload
                # Send the audio-only client request
                await ws.send(audio_only_request)
                res = await ws.recv()
                result = parse_response(res)
                if 'payload_msg' in result and result['payload_msg']['code'] != self.success_code:
                    return result
        return result

    async def execute(self):
        """
        Execute the audio recognition process.
        :return: The recognition result.
        """
        with open(self.audio_path, mode="rb") as _f:
            data = _f.read()
        audio_data = bytes(data)
        if self.format == "mp3":
            segment_size = self.mp3_seg_size
            return await self.segment_data_processor(audio_data, segment_size)
        if self.format != "wav":
            raise Exception("Format should be either wav or mp3")
        nchannels, sampwidth, framerate, nframes, wav_len = read_wav_info(
            audio_data)
        size_per_sec = nchannels * sampwidth * framerate
        segment_size = int(size_per_sec * self.seg_duration / 1000)
        return await self.segment_data_processor(audio_data, segment_size)


# Auxiliary functions, keeping the same as the original code
def read_wav_info(data: bytes = None):
    """
    Read the information of a wav file.
    :param data: The wav file data.
    :return: The number of channels, sample width, frame rate, number of frames, and the length of the wav data.
    """
    with BytesIO(data) as _f:
        wave_fp = wave.open(_f, 'rb')
        nchannels, sampwidth, framerate, nframes = wave_fp.getparams()[:4]
        wave_bytes = wave_fp.readframes(nframes)
    return nchannels, sampwidth, framerate, nframes, len(wave_bytes)


def generate_header(
        version=0b0001,
        message_type=0b0001,
        message_type_specific_flags=0b0000,
        serial_method=0b0001,
        compression_type=0b0001,
        reserved_data=0x00,
        extension_header=bytes()
):
    """
    Generate the header of the protocol.
    protocol_version(4 bits), header_size(4 bits),
    message_type(4 bits), message_type_specific_flags(4 bits)
    serialization_method(4 bits) message_compression(4 bits)
    reserved （8bits) Reserved field
    header_extensions Extended header (size equals 8 * 4 * (header_size - 1) )
    """
    header = bytearray()
    header_size = int(len(extension_header) / 4) + 1
    header.append((version << 4) | header_size)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(reserved_data)
    header.extend(extension_header)
    return header


def generate_full_default_header():
    """
    Generate the default full header.
    :return: The generated header.
    """
    return generate_header()


def generate_audio_default_header():
    """
    Generate the default audio header.
    :return: The generated header.
    """
    return generate_header(
        message_type=0b0010
    )


def generate_last_audio_default_header():
    """
    Generate the last audio header.
    :return: The generated header.
    """
    return generate_header(
        message_type=0b0010,
        message_type_specific_flags=0b0010
    )


def parse_response(res):
    """
    Parse the response data.
    protocol_version(4 bits), header_size(4 bits),
    message_type(4 bits), message_type_specific_flags(4 bits)
    serialization_method(4 bits) message_compression(4 bits)
    reserved （8bits) Reserved field
    header_extensions Extended header (size equals 8 * 4 * (header_size - 1) )
    payload Similar to the HTTP request body
    """
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    reserved = res[3]
    header_extensions = res[4:header_size * 4]
    payload = res[header_size * 4:]
    result = {}
    payload_msg = None
    payload_size = 0
    if message_type == 0b1001:  # SERVER_FULL_RESPONSE
        payload_size = int.from_bytes(payload[:4], "big", signed=True)
        payload_msg = payload[4:]
    elif message_type == 0b1011:  # SERVER_ACK
        seq = int.from_bytes(payload[:4], "big", signed=True)
        result['seq'] = seq
        if len(payload) >= 8:
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]
    elif message_type == 0b1111:  # SERVER_ERROR_RESPONSE
        code = int.from_bytes(payload[:4], "big", signed=False)
        result['code'] = code
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8:]
    if payload_msg is None:
        return result
    if message_compression == 0b0001:  # GZIP
        payload_msg = gzip.decompress(payload_msg)
    if serialization_method == 0b0001:  # JSON
        payload_msg = json.loads(str(payload_msg, "utf-8"))
    elif serialization_method != 0b0000:  # NO_SERIALIZATION
        payload_msg = str(payload_msg, "utf-8")
    result['payload_msg'] = payload_msg
    result['payload_size'] = payload_size
    return result


if __name__ == '__main__':
    voice_appid = "xxx"  # The appid of the project
    voice_token = "xxx"  # The token of the project
    audio_path = "客服.wav"  # The path of the audio file

    # Create an instance of the speech recognizer
    recognizer = SpeechRecognizer(appid=voice_appid, token=voice_token)

    # Recognize the audio file
    try:
        text = recognizer.recognize_file(audio_path)
        print(f"Recognition result: {text}")
    except Exception as e:
        print(f"Recognition failed: {str(e)}")
