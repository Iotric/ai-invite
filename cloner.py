import random
import sys
from pydub import AudioSegment
import tqdm
from pathlib import Path
import soundfile as sf
import torch
from cached_path import cached_path

from model import DiT, UNetT
from model.utils import seed_everything
from model.utils_infer import (
    load_vocoder,
    load_model,
    infer_process,
    remove_silence_for_generated_wav,
    save_spectrogram,
)


class Cloner:
    def __init__(
        self,
        model_type="F5-TTS",
        ckpt_file="",
        vocab_file="",
        ode_method="euler",
        use_ema=True,
        local_path=None,
        device=None,
    ):
        """
        Initialize the Cloner with specified parameters and load the required models.

        Args:
        - model_type (str): Type of TTS model to use ("F5-TTS" or "E2-TTS").
        - ckpt_file (str): Path to the model checkpoint file.
        - vocab_file (str): Path to the vocabulary file.
        - ode_method (str): ODE solver method for the inference process.
        - use_ema (bool): Whether to use Exponential Moving Average (EMA) weights.
        - local_path (str): Path to local vocoder resources (optional).
        - device (str): Device to run the model on ("cuda", "mps", or "cpu").
        """
        self.final_wave = None
        self.target_sample_rate = 24000  # Target audio sample rate in Hz
        self.n_mel_channels = 100  # Number of mel channels for spectrograms
        self.hop_length = 256  # Hop length for audio processing
        self.target_rms = 0.1  # Target Root Mean Square for audio normalization
        self.seed = -1  # Random seed for reproducibility

        # Determine the compute device
        self.device = device or (
            "cuda"
            if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available() else "cpu"
        )

        # Load vocoder and TTS models
        self.load_vocoder_model(local_path)
        self.load_ema_model(model_type, ckpt_file, vocab_file, ode_method, use_ema)

    def load_vocoder_model(self, local_path):
        """
        Load the vocoder model to convert spectrograms to audio.

        Args:
        - local_path (str): Path to local resources, if available.
        """
        self.vocos = load_vocoder(local_path is not None, local_path, self.device)

    def load_ema_model(self, model_type, ckpt_file, vocab_file, ode_method, use_ema):
        """
        Load the main TTS model based on the specified parameters.

        Args:
        - model_type (str): Model type ("F5-TTS" or "E2-TTS").
        - ckpt_file (str): Path to the checkpoint file.
        - vocab_file (str): Path to the vocabulary file.
        - ode_method (str): ODE solver method.
        - use_ema (bool): Whether to use EMA weights.
        """
        if model_type == "F5-TTS":
            if not ckpt_file:
                ckpt_file = str(
                    cached_path(
                        "hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors"
                    )
                )
            model_cfg = dict(
                dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4
            )
            model_cls = DiT
        elif model_type == "E2-TTS":
            if not ckpt_file:
                ckpt_file = str(
                    cached_path(
                        "hf://SWivid/E2-TTS/E2TTS_Base/model_1200000.safetensors"
                    )
                )
            model_cfg = dict(dim=1024, depth=24, heads=16, ff_mult=4)
            model_cls = UNetT
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        self.ema_model = load_model(
            model_cls,
            model_cfg,
            ckpt_file,
            vocab_file,
            ode_method,
            use_ema,
            self.device,
        )

    def export_wav(self, wav, file_wave, remove_silence=False):
        """
        Export the generated waveform to a WAV file.

        Args:
        - wav (np.ndarray): Audio waveform.
        - file_wave (str): Path to save the WAV file.
        - remove_silence (bool): Whether to remove silence from the audio.
        """
        sf.write(file_wave, wav, self.target_sample_rate)

        if remove_silence:
            remove_silence_for_generated_wav(file_wave)

    def export_spectrogram(self, spect, file_spect):
        """
        Save the spectrogram to a file.

        Args:
        - spect (np.ndarray): Spectrogram data.
        - file_spect (str): Path to save the spectrogram.
        """
        save_spectrogram(spect, file_spect)

    def infer(
        self,
        ref_file,
        ref_text,
        gen_text,
        show_info=print,
        progress=tqdm,
        target_rms=0.1,
        cross_fade_duration=0.15,
        sway_sampling_coef=-1,
        cfg_strength=2,
        nfe_step=32,
        speed=1.0,
        fix_duration=None,
        remove_silence=False,
        file_wave=None,
        file_spect=None,
        seed=-1,
    ):
        """
        Perform inference to generate audio based on input text and reference.

        Args:
        - ref_file (str): Path to the reference audio file.
        - ref_text (str): Text content of the reference file.
        - gen_text (str): Text to generate new audio for.
        - show_info (callable): Callback to display process information.
        - progress (callable): Progress bar display (e.g., tqdm).
        - target_rms (float): RMS target for audio normalization.
        - cross_fade_duration (float): Duration for cross-fading segments.
        - sway_sampling_coef (float): Coefficient for sway sampling.
        - cfg_strength (int): Classifier-free guidance strength.
        - nfe_step (int): Number of function evaluations per step.
        - speed (float): Speed multiplier for generated audio.
        - fix_duration (float): Override duration for the generated audio.
        - remove_silence (bool): Whether to remove silence from the output.
        - file_wave (str): Path to save the generated WAV file.
        - file_spect (str): Path to save the generated spectrogram.
        - seed (int): Random seed for reproducibility.
        """
        # Convert the reference file to WAV format
        audio = AudioSegment.from_file(ref_file)
        ref_file = Path(ref_file).with_suffix(".wav")
        # Export to WAV format
        audio.export(ref_file, format="wav")

        # Set random seed if not specified
        if seed == -1:
            seed = random.randint(0, sys.maxsize)
        seed_everything(seed)
        self.seed = seed

        # Generate audio and spectrogram using inference process
        wav, sr, spect = infer_process(
            ref_file,
            ref_text,
            gen_text,
            self.ema_model,
            show_info=show_info,
            progress=progress,
            target_rms=target_rms,
            cross_fade_duration=cross_fade_duration,
            nfe_step=nfe_step,
            cfg_strength=cfg_strength,
            sway_sampling_coef=sway_sampling_coef,
            speed=speed,
            fix_duration=fix_duration,
            device=self.device,
        )

        # Export results if file paths are specified
        if file_wave is not None:
            self.export_wav(wav, file_wave, remove_silence)

        if file_spect is not None:
            self.export_spectrogram(spect, file_spect)

        return wav, sr, spect
