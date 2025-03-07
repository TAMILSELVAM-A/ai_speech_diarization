import openai
from pyannote.audio import Pipeline
from typing import List, Dict
import logging
import os
import soundfile as sf
import librosa
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



load_dotenv()

hf_auth_token = os.getenv('HF_AUTH_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')

try:
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0", use_auth_token=hf_auth_token)
    logger.info("Speaker diarization pipeline loaded successfully!")


except Exception as e:
    logger.error(f"Failed to load diarization pipeline: {e}")
    pipeline = None

def convert_audio_to_wav(input_audio: str) -> str:
    output_wav = "converted_audio.wav"
    try:
        audio, sr = librosa.load(input_audio, sr=16000)
        sf.write(output_wav, audio, 16000, subtype='PCM_16')
        logger.info("Audio converted to WAV format successfully!")
        return output_wav
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise

def transcribe_audio_with_openai(audio_path: str) -> Dict:
    try:
        openai.api_key = openai_api_key
        with open(audio_path, "rb") as audio_file:
            whisper_response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="en",
                response_format="verbose_json"
            )
        logger.info("Transcription completed using OpenAI Whisper API!")
        return whisper_response
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return None

def diarize_audio(audio_path: str) -> List[Dict[str, str]]:
    if pipeline is None:
        raise ValueError("Diarization pipeline is not loaded. Check logs for errors.")

    processed_audio = convert_audio_to_wav(audio_path)
    transcript = transcribe_audio_with_openai(processed_audio)

    if transcript is None:
        raise ValueError("Transcription failed. Check OpenAI Whisper API response.")

    try:
        diarization = pipeline(processed_audio, max_speakers=4)
        diarized_segments = []
        seen_texts = set()  # To track unique text segments

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment_text = extract_text_for_segment(transcript["segments"], turn.start, turn.end)

            if segment_text not in seen_texts:  # Check for duplicates
                seen_texts.add(segment_text)  # Store unique text
                diarized_segments.append({
                    "start": str(round(turn.start, 2)),
                    "end": str(round(turn.end, 2)),
                    "speaker": speaker,
                    "text": segment_text
                })

        speaker_mapping = identify_speakers_with_openai(diarized_segments)
        for segment in diarized_segments:
            segment["speaker"] = speaker_mapping.get(segment["speaker"], segment["speaker"])

        return diarized_segments
    except Exception as e:
        logger.error(f"Error during diarization: {e}")
        raise

def extract_text_for_segment(segments, start_time, end_time):
    text = []    
    for seg in segments:
        if (seg["start"] <= end_time and seg["end"] >= start_time):
            text.append(seg["text"])

    return " ".join(text) if text else "..."


def identify_speakers_with_openai(diarized_segments: List[Dict[str, str]]) -> Dict[str, str]:
    openai.api_key = openai_api_key
    conversation_text = "\n".join([f"{seg['speaker']}: {seg['text']}" for seg in diarized_segments])

    prompt = f"""
    Below is a conversation with speaker labels. Identify the real names or roles of the speakers based on the content:
    
    {conversation_text}
    
    Provide a mapping of speaker labels (SPEAKER_XX) to real names or roles in JSON format. Example:
    {{
        "SPEAKER_00": "Alice",
        "SPEAKER_01": "Bob",
        "SPEAKER_02": "Doctor"
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI that identifies speaker names based on context."},
                      {"role": "user", "content": prompt}]
        )

        speaker_mapping = eval(response["choices"][0]["message"]["content"])
        return speaker_mapping
    except Exception as e:
        logger.error(f"Error identifying speakers: {e}")
        return {}
