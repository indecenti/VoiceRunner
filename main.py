#!/usr/bin/env python3
"""
VOICE RUNNER PRO - ULTIMATE STANDALONE EDITION
Versione autoinstallante completamente autonoma
Richiede solo Python 3.7+
"""

import sys
import subprocess
import importlib.util

def check_and_install():
    """Controllo e installazione automatica delle dipendenze"""
    dependencies = [
        ('pygame', 'pygame'),
        ('numpy', 'numpy'),
        ('sounddevice', 'sounddevice')
    ]

    print("=" * 60)
    print("🎤 VOICE RUNNER PRO - Controllo dipendenze...")
    print("=" * 60)

    missing = []
    for module_name, package_name in dependencies:
        if importlib.util.find_spec(module_name) is None:
            missing.append((module_name, package_name))
            print(f"⚠  {module_name} non trovato")
        else:
            print(f"✓  {module_name} già installato")

    if missing:
        print(f"\n📦 Installazione di {len(missing)} pacchetti mancanti...")
        for module_name, package_name in missing:
            try:
                print(f"   Installazione {package_name}...", end=" ")
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', package_name, '-q'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("✓")
            except subprocess.CalledProcessError as e:
                print(f"✗\n⚠ Errore installazione {package_name}: {e}")
                print(f"   Prova manualmente: pip install {package_name}")
                sys.exit(1)
        print("\n✓ Tutte le dipendenze installate con successo!\n")
    else:
        print("\n✓ Tutte le dipendenze già presenti!\n")

# Esegui check dipendenze PRIMA di qualsiasi altro import
check_and_install()

# Import di tutte le librerie necessarie
import json
import os
import math
import random
import time
from dataclasses import dataclass, field

import pygame
import numpy as np
import sounddevice as sd

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(16)
pygame.joystick.init()

# Screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("🎤 VOICE RUNNER PRO - SYNTH EDITION 🎮")
clock = pygame.time.Clock()

CONFIG_FILE = "vr_config.json"

# COLLISION IMPROVEMENTS
COLLISION_MULTIPLIER = 0.75  # Hitbox ridotta al 75% per gameplay più faire
WARNING_DISTANCE_MULTIPLIER = 1.5  # Distanza per warning visivo
INVINCIBILITY_FRAMES = 60  # 1 secondo di invincibilità dopo spawn

# Colors
DARK_BG = (8, 12, 30)
DARKER_BG = (4, 6, 15)
NEON_CYAN = (0, 255, 200)
NEON_MAGENTA = (255, 0, 127)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (180, 100, 255)
NEON_BLUE = (0, 150, 255)
NEON_ORANGE = (255, 140, 0)
NEON_YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 170)
DARK_GRAY = (80, 80, 100)

CYBERPUNK_PALETTES = [
    {
        'name': 'Neon Teal',
        'sky_top': (5, 20, 30),
        'sky_bottom': (20, 60, 85),
        'ground_top': (25, 80, 95),
        'ground_mid': (15, 50, 60),
        'ground_bottom': (5, 15, 20),
        'clouds': [(18, 35, 45), (22, 45, 60), (28, 55, 75)],
        'nebula': (30, 80, 100),
        'nebula_accent': (50, 120, 140),
        'horizon_glow': (100, 255, 240),
        'particles': (120, 200, 220),
        'particles_accent': (150, 255, 240),
        'objects': (0, 255, 200),
        'lights': (0, 255, 220),
        'grid': (0, 180, 160),
        'scanlines': (0, 150, 130),
    },
    {
        'name': 'Purple Dreams',
        'sky_top': (15, 5, 35),
        'sky_bottom': (70, 25, 90),
        'ground_top': (85, 25, 105),
        'ground_mid': (50, 15, 65),
        'ground_bottom': (15, 5, 20),
        'clouds': [(25, 18, 45), (40, 20, 55), (55, 20, 70)],
        'nebula': (90, 40, 130),
        'nebula_accent': (140, 70, 180),
        'horizon_glow': (220, 120, 255),
        'particles': (180, 120, 220),
        'particles_accent': (220, 150, 255),
        'objects': (180, 100, 255),
        'lights': (200, 120, 255),
        'grid': (140, 80, 190),
        'scanlines': (120, 60, 170),
    },
    {
        'name': 'Sakura Night',
        'sky_top': (25, 5, 20),
        'sky_bottom': (80, 30, 60),
        'ground_top': (95, 35, 70),
        'ground_mid': (60, 20, 45),
        'ground_bottom': (20, 5, 15),
        'clouds': [(45, 18, 35), (60, 25, 45), (75, 30, 55)],
        'nebula': (100, 40, 80),
        'nebula_accent': (140, 60, 110),
        'horizon_glow': (255, 140, 200),
        'particles': (220, 120, 180),
        'particles_accent': (255, 160, 210),
        'objects': (255, 100, 180),
        'lights': (255, 120, 200),
        'grid': (180, 80, 150),
        'scanlines': (160, 70, 130),
    },
    {
        'name': 'Cyber Orange',
        'sky_top': (30, 15, 5),
        'sky_bottom': (85, 50, 20),
        'ground_top': (105, 60, 25),
        'ground_mid': (65, 35, 15),
        'ground_bottom': (20, 10, 5),
        'clouds': [(45, 28, 18), (60, 40, 22), (75, 50, 28)],
        'nebula': (130, 80, 40),
        'nebula_accent': (180, 120, 70),
        'horizon_glow': (255, 180, 100),
        'particles': (220, 150, 120),
        'particles_accent': (255, 200, 150),
        'objects': (255, 140, 0),
        'lights': (255, 160, 40),
        'grid': (190, 120, 0),
        'scanlines': (170, 100, 0),
    },
    {
        'name': 'Matrix Green',
        'sky_top': (5, 15, 5),
        'sky_bottom': (20, 60, 20),
        'ground_top': (25, 85, 25),
        'ground_mid': (15, 50, 15),
        'ground_bottom': (5, 20, 5),
        'clouds': [(18, 35, 18), (22, 45, 22), (28, 55, 28)],
        'nebula': (40, 100, 40),
        'nebula_accent': (70, 140, 70),
        'horizon_glow': (120, 255, 120),
        'particles': (150, 220, 150),
        'particles_accent': (180, 255, 180),
        'objects': (0, 255, 0),
        'lights': (40, 255, 40),
        'grid': (0, 180, 0),
        'scanlines': (0, 150, 0),
    },
    {
        'name': 'Arctic Blue',
        'sky_top': (10, 20, 40),
        'sky_bottom': (40, 80, 120),
        'ground_top': (50, 100, 140),
        'ground_mid': (30, 60, 90),
        'ground_bottom': (10, 20, 30),
        'clouds': [(25, 40, 60), (35, 60, 85), (45, 80, 110)],
        'nebula': (60, 120, 160),
        'nebula_accent': (90, 160, 200),
        'horizon_glow': (140, 220, 255),
        'particles': (160, 200, 230),
        'particles_accent': (190, 230, 255),
        'objects': (100, 200, 255),
        'lights': (120, 220, 255),
        'grid': (80, 160, 200),
        'scanlines': (70, 140, 180),
    },
    {
        'name': 'Neon Pink',
        'sky_top': (35, 5, 25),
        'sky_bottom': (90, 20, 70),
        'ground_top': (105, 25, 85),
        'ground_mid': (65, 15, 50),
        'ground_bottom': (20, 5, 15),
        'clouds': [(45, 18, 35), (55, 22, 45), (70, 28, 55)],
        'nebula': (130, 40, 100),
        'nebula_accent': (180, 70, 140),
        'horizon_glow': (255, 100, 220),
        'particles': (220, 120, 200),
        'particles_accent': (255, 150, 230),
        'objects': (255, 0, 200),
        'lights': (255, 40, 220),
        'grid': (190, 0, 150),
        'scanlines': (170, 0, 130),
    },
    {
        'name': 'Toxic Yellow',
        'sky_top': (30, 30, 5),
        'sky_bottom': (85, 85, 20),
        'ground_top': (105, 105, 25),
        'ground_mid': (65, 65, 15),
        'ground_bottom': (20, 20, 5),
        'clouds': [(45, 45, 18), (55, 55, 22), (75, 75, 28)],
        'nebula': (130, 130, 40),
        'nebula_accent': (180, 180, 70),
        'horizon_glow': (255, 255, 100),
        'particles': (220, 220, 150),
        'particles_accent': (255, 255, 180),
        'objects': (200, 255, 0),
        'lights': (220, 255, 40),
        'grid': (150, 180, 0),
        'scanlines': (130, 150, 0),
    },
    {
        'name': 'Cyber Red',
        'sky_top': (35, 5, 5),
        'sky_bottom': (90, 20, 20),
        'ground_top': (105, 25, 25),
        'ground_mid': (65, 15, 15),
        'ground_bottom': (20, 5, 5),
        'clouds': [(45, 18, 18), (55, 22, 22), (70, 28, 28)],
        'nebula': (130, 40, 40),
        'nebula_accent': (180, 70, 70),
        'horizon_glow': (255, 100, 100),
        'particles': (220, 120, 120),
        'particles_accent': (255, 150, 150),
        'objects': (255, 40, 40),
        'lights': (255, 80, 80),
        'grid': (190, 30, 30),
        'scanlines': (170, 20, 20),
    },
    {
        'name': 'Synthwave Sunset',
        'sky_top': (25, 5, 30),
        'sky_bottom': (70, 20, 85),
        'ground_top': (85, 25, 105),
        'ground_mid': (50, 15, 65),
        'ground_bottom': (15, 5, 20),
        'clouds': [(35, 18, 45), (45, 22, 55), (55, 28, 70)],
        'nebula': (80, 40, 130),
        'nebula_accent': (110, 70, 180),
        'horizon_glow': (200, 100, 255),
        'particles': (180, 120, 220),
        'particles_accent': (210, 150, 255),
        'objects': (255, 100, 255),
        'lights': (255, 140, 255),
        'grid': (180, 80, 180),
        'scanlines': (160, 70, 160),
    },
    {
        'name': 'Ocean Deep',
        'sky_top': (5, 10, 25),
        'sky_bottom': (20, 40, 70),
        'ground_top': (25, 50, 85),
        'ground_mid': (15, 30, 50),
        'ground_bottom': (5, 10, 20),
        'clouds': [(18, 25, 45), (22, 35, 55), (28, 45, 75)],
        'nebula': (40, 80, 130),
        'nebula_accent': (70, 120, 180),
        'horizon_glow': (100, 180, 255),
        'particles': (120, 160, 220),
        'particles_accent': (150, 190, 255),
        'objects': (0, 150, 255),
        'lights': (40, 170, 255),
        'grid': (0, 120, 190),
        'scanlines': (0, 100, 170),
    },
    {
        'name': 'Cyber Gold',
        'sky_top': (35, 25, 5),
        'sky_bottom': (90, 70, 20),
        'ground_top': (105, 85, 25),
        'ground_mid': (65, 50, 15),
        'ground_bottom': (20, 15, 5),
        'clouds': [(45, 35, 18), (55, 45, 22), (70, 55, 28)],
        'nebula': (130, 100, 40),
        'nebula_accent': (180, 140, 70),
        'horizon_glow': (255, 200, 100),
        'particles': (220, 180, 120),
        'particles_accent': (255, 210, 150),
        'objects': (255, 180, 0),
        'lights': (255, 200, 40),
        'grid': (190, 140, 0),
        'scanlines': (170, 120, 0),
    },
    {
        'name': 'Neon Violet',
        'sky_top': (25, 5, 40),
        'sky_bottom': (70, 20, 95),
        'ground_top': (85, 25, 115),
        'ground_mid': (50, 15, 70),
        'ground_bottom': (15, 5, 25),
        'clouds': [(35, 18, 50), (45, 22, 65), (55, 28, 80)],
        'nebula': (80, 40, 140),
        'nebula_accent': (110, 70, 190),
        'horizon_glow': (180, 100, 255),
        'particles': (160, 120, 230),
        'particles_accent': (190, 150, 255),
        'objects': (150, 0, 255),
        'lights': (170, 40, 255),
        'grid': (120, 0, 190),
        'scanlines': (100, 0, 170),
    },
    {
        'name': 'Electric Lime',
        'sky_top': (20, 30, 5),
        'sky_bottom': (60, 85, 20),
        'ground_top': (70, 105, 25),
        'ground_mid': (45, 65, 15),
        'ground_bottom': (15, 20, 5),
        'clouds': [(35, 45, 18), (45, 55, 22), (55, 75, 28)],
        'nebula': (80, 130, 40),
        'nebula_accent': (110, 180, 70),
        'horizon_glow': (180, 255, 100),
        'particles': (160, 220, 120),
        'particles_accent': (190, 255, 150),
        'objects': (140, 255, 0),
        'lights': (160, 255, 40),
        'grid': (110, 190, 0),
        'scanlines': (90, 170, 0),
    },
    {
        'name': 'Holo Silver',
        'sky_top': (25, 25, 30),
        'sky_bottom': (70, 70, 85),
        'ground_top': (85, 85, 105),
        'ground_mid': (50, 50, 65),
        'ground_bottom': (15, 15, 20),
        'clouds': [(35, 35, 45), (45, 45, 55), (55, 55, 70)],
        'nebula': (80, 80, 130),
        'nebula_accent': (110, 110, 180),
        'horizon_glow': (180, 180, 255),
        'particles': (160, 160, 220),
        'particles_accent': (190, 190, 255),
        'objects': (200, 200, 255),
        'lights': (220, 220, 255),
        'grid': (150, 150, 190),
        'scanlines': (130, 130, 170),
    },
        {
        'name': 'Midnight Run',
        'sky_top': (2, 5, 10),           # Quasi nero
        'sky_bottom': (10, 20, 40),      # Blu notte profondo
        'ground_top': (20, 30, 50),      # Asfalto bagnato scuro
        'ground_mid': (10, 15, 25),      # Ombre urbane
        'ground_bottom': (0, 0, 0),      # Nero assoluto
        'clouds': [(15, 25, 35), (20, 30, 45), (25, 35, 55)], # Nuvole temporalesche
        'nebula': (30, 0, 60),           # Viola scuro minaccioso
        'nebula_accent': (60, 20, 100),  # Bagliore distante
        'horizon_glow': (100, 120, 150), # Inquinamento luminoso freddo
        'particles': (200, 220, 255),    # Pioggia/scintille bianche
        'particles_accent': (100, 150, 255), # Blu elettrico scarica
        'objects': (0, 180, 255),        # Ciano puro per visibilità
        'lights': (0, 200, 255),         # Luci auto/neon blu
        'grid': (40, 60, 90),            # Griglia sottile, non intrusiva
        'scanlines': (20, 40, 60),       # Scanlines appena visibili
    },
    {
        'name': 'Retro Vibe',
        'sky_top': (45, 15, 55),         # Prugna retrò
        'sky_bottom': (255, 140, 0),     # Arancione tramonto 80s
        'ground_top': (20, 0, 40),       # Viola scuro griglia base
        'ground_mid': (15, 0, 30),       # Viola più scuro
        'ground_bottom': (10, 0, 20),    # Viola nero
        'clouds': [(255, 100, 150), (255, 150, 100), (255, 200, 50)], # Nuvole pastello
        'nebula': (255, 0, 128),         # Magenta vaporwave
        'nebula_accent': (0, 255, 255),  # Ciano contrasto
        'horizon_glow': (255, 200, 0),   # Sole all'orizzonte
        'particles': (255, 255, 0),      # Scintille dorate
        'particles_accent': (255, 0, 255), # Scintille magenta
        'objects': (0, 255, 255),        # Oggetti Ciano puro
        'lights': (255, 0, 255),         # Luci Magenta neon
        'grid': (255, 0, 128),           # Griglia Laser Rosa
        'scanlines': (50, 0, 50),        # Scanlines viola
    },
    {
        'name': 'Acid Trip',  # PENULTIMA (Mantenuta)
        'sky_top': (25, 0, 50),
        'sky_bottom': (255, 0, 128),
        'ground_top': (50, 255, 0),
        'ground_mid': (255, 255, 0),
        'ground_bottom': (0, 50, 255),
        'clouds': [(255, 100, 0), (0, 255, 255), (255, 0, 255)],
        'nebula': (128, 0, 255),
        'nebula_accent': (50, 255, 50),
        'horizon_glow': (255, 255, 255),
        'particles': (255, 50, 150),
        'particles_accent': (50, 255, 255),
        'objects': (255, 255, 0),
        'lights': (0, 255, 100),
        'grid': (255, 0, 128),
        'scanlines': (0, 255, 255),
    },

    {
        'name': 'Acid Trip',
        'sky_top': (25, 0, 50),          # Viola scuro acido
        'sky_bottom': (255, 0, 128),     # Fucsia shocking
        'ground_top': (50, 255, 0),      # Verde neon puro
        'ground_mid': (255, 255, 0),     # Giallo evidenziatore
        'ground_bottom': (0, 50, 255),   # Blu elettrico saturo
        'clouds': [
            (255, 100, 0),               # Arancione
            (0, 255, 255),               # Ciano
            (255, 0, 255)                # Magenta
        ],
        'nebula': (128, 0, 255),         # Indaco
        'nebula_accent': (50, 255, 50),  # Verde Matrix
        'horizon_glow': (255, 255, 255), # Bianco accecante
        'particles': (255, 50, 150),     # Rosa bubblegum
        'particles_accent': (50, 255, 255), # Turchese laser
        'objects': (255, 255, 0),        # Giallo puro
        'lights': (0, 255, 100),         # Verde smeraldo neon
        'grid': (255, 0, 128),           # Griglia Fucsia
        'scanlines': (0, 255, 255),      # Scanlines Ciano
    },


]



def lerp_color(color1, color2, t):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))

font_xl = pygame.font.Font(None, 82)
font_lg = pygame.font.Font(None, 58)
font_md = pygame.font.Font(None, 40)
font_sm = pygame.font.Font(None, 30)
font_xs = pygame.font.Font(None, 24)

current_rms = 0.0

# Joypad support
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    print(f"✓ Joypad {i} connesso: {joystick.get_name()}")

# ============================================
# PROFESSIONAL SYNTHESIZER ENGINE - IMPROVED
# ============================================

class Synthesizer:
    """Professional Software Synthesizer with ADSR, Multiple Oscillators, Filters"""
    
    SAMPLE_RATE = 44100
    
    @staticmethod
    def generate_oscillator(waveform, frequency, duration, sample_rate=44100):
        """Generate oscillator waveforms"""
        frames = int(sample_rate * duration)
        t = np.linspace(0, duration, frames, endpoint=False)
        
        if waveform == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        
        elif waveform == 'saw':
            phase = (frequency * t) % 1.0
            wave = 2 * phase - 1
        
        elif waveform == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        
        elif waveform == 'triangle':
            phase = (frequency * t) % 1.0
            wave = 2 * np.abs(2 * phase - 1) - 1
        
        elif waveform == 'pulse':
            phase = (frequency * t) % 1.0
            wave = np.where(phase < 0.3, 1.0, -1.0)
        
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        
        return wave, t
    
    @staticmethod
    def apply_adsr_envelope(wave, attack, decay, sustain_level, release, sample_rate=44100):
        """Apply ADSR envelope"""
        total_frames = len(wave)
        
        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        release_samples = int(release * sample_rate)
        sustain_samples = max(0, total_frames - attack_samples - decay_samples - release_samples)
        
        envelope = np.zeros(total_frames)
        
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        if decay_samples > 0:
            envelope[decay_start:decay_end] = np.linspace(1, sustain_level, decay_samples)
        
        sustain_start = decay_end
        sustain_end = sustain_start + sustain_samples
        envelope[sustain_start:sustain_end] = sustain_level
        
        release_start = sustain_end
        if release_samples > 0 and release_start < total_frames:
            actual_release = min(release_samples, total_frames - release_start)
            envelope[release_start:release_start + actual_release] = np.linspace(sustain_level, 0, actual_release)
        
        return wave * envelope
    
    @staticmethod
    def apply_lowpass_filter(wave, cutoff_freq, sample_rate=44100):
        """Lowpass filter"""
        if cutoff_freq >= sample_rate / 2:
            return wave
        
        window_size = int(sample_rate / (cutoff_freq * 2))
        window_size = max(2, window_size)
        
        kernel = np.ones(window_size) / window_size
        filtered = np.convolve(wave, kernel, mode='same')
        
        return filtered
    
    @staticmethod
    def synthesize_beep():
        """Improved Beep: Bright and crisp"""
        duration = 0.12
        
        # Bell-like tone
        sine1, t = Synthesizer.generate_oscillator('sine', 1320, duration)
        sine2, _ = Synthesizer.generate_oscillator('sine', 1980, duration)
        triangle, _ = Synthesizer.generate_oscillator('triangle', 660, duration)
        
        mixed = sine1 * 0.5 + sine2 * 0.3 + triangle * 0.2
        
        enveloped = Synthesizer.apply_adsr_envelope(
            mixed, 
            attack=0.005, 
            decay=0.04, 
            sustain_level=0.4, 
            release=0.075
        )
        
        audio = (enveloped * 32767 * 0.85).astype(np.int16)
        stereo = np.array([audio, audio]).T.copy(order='C')
        
        sound = pygame.sndarray.make_sound(stereo)
        sound.set_volume(1.0)
        return sound
    
    @staticmethod
    def synthesize_whoosh():
        """Improved Whoosh: Smoother sweep"""
        duration = 0.25
        sample_rate = Synthesizer.SAMPLE_RATE
        frames = int(sample_rate * duration)
        t = np.linspace(0, duration, frames)
        
        freq_start, freq_end = 300, 2800
        frequency = np.linspace(freq_start, freq_end, frames)
        
        # FM modulation
        modulator_freq = 10
        modulation_index = 400
        modulator = np.sin(2 * np.pi * modulator_freq * t) * modulation_index
        
        phase = np.cumsum(2 * np.pi * (frequency + modulator) / sample_rate)
        carrier = np.sin(phase)
        
        # Add harmonics
        harmonic = np.sin(phase * 1.5) * 0.3
        mixed = carrier * 0.7 + harmonic
        
        enveloped = Synthesizer.apply_adsr_envelope(
            mixed,
            attack=0.015,
            decay=0.06,
            sustain_level=0.45,
            release=0.175
        )
        
        filtered = Synthesizer.apply_lowpass_filter(enveloped, 4000)
        
        audio = (filtered * 32767 * 0.85).astype(np.int16)
        stereo = np.array([audio, audio]).T.copy(order='C')
        
        sound = pygame.sndarray.make_sound(stereo)
        sound.set_volume(1.0)
        return sound
    
    @staticmethod
    def synthesize_explosion():
        """Improved Explosion: More punch"""
        duration = 0.40
        sample_rate = Synthesizer.SAMPLE_RATE
        frames = int(sample_rate * duration)
        t = np.linspace(0, duration, frames)
        
        # Deep sub bass sweep
        bass_start, bass_end = 80, 30
        bass_freq = np.linspace(bass_start, bass_end, frames)
        phase_bass = np.cumsum(2 * np.pi * bass_freq / sample_rate)
        bass = np.sin(phase_bass) * 0.8
        
        # Mid punch
        mid_freq = 120
        mid = np.sin(2 * np.pi * mid_freq * t) * 0.4 * np.exp(-t * 5)
        
        # Noise burst
        noise = np.random.uniform(-0.5, 0.5, frames)
        
        mixed = bass + mid + noise
        mixed = np.clip(mixed, -1.0, 1.0)
        
        enveloped = Synthesizer.apply_adsr_envelope(
            mixed,
            attack=0.002,
            decay=0.12,
            sustain_level=0.18,
            release=0.278
        )
        
        filtered = Synthesizer.apply_lowpass_filter(enveloped, 1000)
        
        audio = (filtered * 32767 * 0.95).astype(np.int16)
        stereo = np.array([audio, audio]).T.copy(order='C')
        
        sound = pygame.sndarray.make_sound(stereo)
        sound.set_volume(1.0)
        return sound
    
    @staticmethod
    def synthesize_levelup():
        """Improved Level Up: More triumphant"""
        duration = 0.50
        sample_rate = Synthesizer.SAMPLE_RATE
        
        # Bright arpeggio
        notes = [659.25, 830.61, 987.77, 1318.51]  # E5, G#5, B5, E6
        note_duration = duration / len(notes)
        
        full_wave = []
        
        for i, freq in enumerate(notes):
            saw, _ = Synthesizer.generate_oscillator('saw', freq, note_duration, sample_rate)
            pulse, _ = Synthesizer.generate_oscillator('pulse', freq * 2, note_duration, sample_rate)
            
            mixed = saw * 0.6 + pulse * 0.4
            
            # Cada nota más fuerte
            amp = 0.6 + (i * 0.1)
            
            enveloped = Synthesizer.apply_adsr_envelope(
                mixed,
                attack=0.008,
                decay=0.04,
                sustain_level=0.75,
                release=0.06,
                sample_rate=sample_rate
            ) * amp
            
            full_wave.append(enveloped)
        
        final_wave = np.concatenate(full_wave)
        
        audio = (final_wave * 32767 * 0.80).astype(np.int16)
        stereo = np.array([audio, audio]).T.copy(order='C')
        
        sound = pygame.sndarray.make_sound(stereo)
        sound.set_volume(1.0)
        return sound
    
    @staticmethod
    def synthesize_collision():
        """Improved Collision: Massive impact"""
        duration = 0.55
        sample_rate = Synthesizer.SAMPLE_RATE
        frames = int(sample_rate * duration)
        t = np.linspace(0, duration, frames)
        
        # Super low bass drop
        bass_start, bass_end = 70, 20
        bass_freq = np.linspace(bass_start, bass_end, frames)
        phase_bass = np.cumsum(2 * np.pi * bass_freq / sample_rate)
        bass = np.sin(phase_bass) * 0.9
        
        # Secondary bass layer
        bass2 = np.sin(phase_bass * 1.5) * 0.5
        
        # Harsh metallic crash
        noise = np.random.uniform(-0.7, 0.7, frames)
        
        # Impact pulse
        pulse, _ = Synthesizer.generate_oscillator('pulse', 60, duration, sample_rate)
        pulse *= 0.5 * np.exp(-t * 3)
        
        mixed = bass + bass2 + noise + pulse
        mixed = np.clip(mixed, -1.0, 1.0)
        
        # Hard distortion
        mixed = np.tanh(mixed * 1.5)
        
        enveloped = Synthesizer.apply_adsr_envelope(
            mixed,
            attack=0.001,
            decay=0.15,
            sustain_level=0.12,
            release=0.399
        )
        
        filtered = Synthesizer.apply_lowpass_filter(enveloped, 800)
        
        audio = (filtered * 32767 * 0.98).astype(np.int16)
        stereo = np.array([audio, audio]).T.copy(order='C')
        
        sound = pygame.sndarray.make_sound(stereo)
        sound.set_volume(1.0)
        return sound

# ============================================
# INITIALIZE SYNTH SOUNDS
# ============================================

try:
    print("🎹 Inizializzazione sintetizzatore professionale...")
    SOUND_BEEP = Synthesizer.synthesize_beep()
    print("  ✓ Beep sintetizzato")
    
    SOUND_WHOOSH = Synthesizer.synthesize_whoosh()
    print("  ✓ Whoosh sintetizzato")
    
    SOUND_BOOM = Synthesizer.synthesize_explosion()
    print("  ✓ Boom sintetizzato")
    
    SOUND_LEVELUP = Synthesizer.synthesize_levelup()
    print("  ✓ Level Up sintetizzato")
    
    SOUND_COLLISION = Synthesizer.synthesize_collision()
    print("  ✓ Collision sintetizzato")
    
    print("✓ Sintetizzatore ready")
    
except Exception as e:
    print(f"⚠ Errore sintesi: {e}")
    SOUND_BEEP = SOUND_WHOOSH = SOUND_BOOM = SOUND_LEVELUP = SOUND_COLLISION = None

def play_sound(sound, force=False):
    """Play synthesized sound"""
    if sound is None:
        return
    try:
        if force:
            pygame.mixer.stop()
            sound.play()
        else:
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)
            else:
                sound.play()
    except Exception as e:
        pass

def audio_callback(indata, frames, time_info, status):
    global current_rms
    try:
        audio = np.abs(indata[:, 0]).astype(np.float32)
        current_rms = float(np.sqrt(np.mean(audio ** 2)))
    except:
        pass

try:
    stream = sd.InputStream(channels=1, samplerate=44100, blocksize=2048, callback=audio_callback)
    stream.start()
    print("✓ Microfono attivo")
except Exception as e:
    print(f"⚠ Errore microfono: {e}")
    sys.exit(1)

class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'color', 'lifetime', 'age', 'size']
    
    def __init__(self, x, y, vx, vy, color, lifetime=60, size=6):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.size = size
    
    def update(self):
        self.age += 1
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.vx *= 0.97
        return self.age < self.lifetime
    
    def draw(self, surf):
        alpha = 1 - self.age / self.lifetime
        size = max(1, int(self.size * alpha))
        if size > 0:
            # Glow effect
            for i in range(3):
                glow_size = size + i * 2
                glow_alpha = alpha * (1 - i * 0.3)
                if glow_alpha > 0:
                    glow_color = tuple(int(c * glow_alpha) for c in self.color)
                    pygame.draw.circle(surf, glow_color, (int(self.x), int(self.y)), glow_size)





# IMPROVED SCORE POPUP - Comic/Explosive style
class ScorePopup:
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.score = int(score)  # Assicura che sia un intero
        self.lifetime = 70
        self.age = 0
        self.particles = []
        
        # Spawn particles around popup
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, 5),
                'color': random.choice([NEON_GREEN, NEON_YELLOW, WHITE])
            })
        
    def update(self):
        self.age += 1
        self.y -= 1.8
        
        # Update particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.3
            p['vx'] *= 0.95
        
        return self.age < self.lifetime
    
    def draw(self, surf):
        if self.age >= self.lifetime:
            return
            
        # Draw particles first
        particle_alpha = 1 - (self.age / self.lifetime)
        for p in self.particles:
            if particle_alpha > 0:
                size = max(1, int(p['size'] * particle_alpha))
                color = tuple(int(c * particle_alpha) for c in p['color'])
                pygame.draw.circle(surf, color, (int(p['x']), int(p['y'])), size)
        
        # Explosive scale animation
        if self.age < 15:
            scale_factor = 0.5 + (self.age / 15) * 1.5  # 0.5 -> 2.0
        elif self.age < 30:
            scale_factor = 2.0 - ((self.age - 15) / 15) * 0.3  # 2.0 -> 1.7
        else:
            scale_factor = 1.7 - ((self.age - 30) / (self.lifetime - 30)) * 0.7  # 1.7 -> 1.0
        
        alpha_factor = 1 - (self.age / self.lifetime) ** 0.5
        
        # Wobble effect
        wobble = math.sin(self.age * 0.5) * 5
        
        # 🟢 MODIFICA QUI: Usa self.score invece di "+1" fisso
        score_str = f"+{self.score}"
        
        # Main text with outline (comic style)
        text = font_xl.render(score_str, True, WHITE)
        scaled_w = int(text.get_width() * scale_factor)
        scaled_h = int(text.get_height() * scale_factor)
        
        if scaled_w > 0 and scaled_h > 0:
            scaled_text = pygame.transform.scale(text, (scaled_w, scaled_h))
            
            # Multiple colored glows (comic explosion)
            glow_colors = [NEON_YELLOW, NEON_ORANGE, NEON_GREEN]
            for i, glow_col in enumerate(glow_colors):
                glow_offset = (i + 1) * 8
                for angle in range(0, 360, 45):
                    offset_x = int(math.cos(math.radians(angle)) * glow_offset)
                    offset_y = int(math.sin(math.radians(angle)) * glow_offset)
                    
                    glow_surf = pygame.Surface((scaled_w + 20, scaled_h + 20), pygame.SRCALPHA)
                    # 🟢 MODIFICA QUI: Usa score_str
                    glow_text = font_xl.render(score_str, True, glow_col)
                    glow_scaled = pygame.transform.scale(glow_text, (scaled_w, scaled_h))
                    glow_scaled.set_alpha(int(120 * alpha_factor * (1 - i * 0.3)))
                    glow_surf.blit(glow_scaled, (10, 10))
                    
                    surf.blit(glow_surf, 
                             (int(self.x + wobble) - scaled_w // 2 + offset_x - 10, 
                              int(self.y) - scaled_h // 2 + offset_y - 10))
            
            # Black outline (comic style)
            # 🟢 MODIFICA QUI: Usa score_str
            outline_text = font_xl.render(score_str, True, (0, 0, 0))
            outline_scaled = pygame.transform.scale(outline_text, (scaled_w + 4, scaled_h + 4))
            surf.blit(outline_scaled, 
                     (int(self.x + wobble) - (scaled_w + 4) // 2, 
                      int(self.y) - (scaled_h + 4) // 2))
            
            # Main text
            surf.blit(scaled_text, 
                     (int(self.x + wobble) - scaled_w // 2, 
                      int(self.y) - scaled_h // 2))



class LevelNotification:
    def __init__(self, level_num):
        self.level_num = level_num
        self.lifetime = 90  # Più breve per impatto maggiore
        self.age = 0
        
    def update(self):
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, surf):
        scr_w = surf.get_width()
        scr_h = surf.get_height()
        
        # FASE 1: FLASH BIANCO ULTRA BREVE (primi 8 frame)
        if self.age <= 8:
            flash_scale = 1.0 + (self.age * 0.3)  # Espansione flash
            flash_alpha = int(255 * (1.0 - self.age / 8.0))  # Fade out rapido
            
            flash_size = int(400 * flash_scale)
            flash_surf = pygame.Surface((flash_size, flash_size), pygame.SRCALPHA)
            
            # FLASH BIANCO PERFETTO
            pygame.draw.circle(flash_surf, (*WHITE, flash_alpha), 
                             (flash_size//2, flash_size//2), flash_size//2)
            
            surf.blit(flash_surf, (scr_w//2 - flash_size//2, scr_h//2 - flash_size//2))
            return  # Solo flash nei primi frame
        
        # FASE 2: BANNER CYBERPUNK (frame 9-90)
        progress = (self.age - 8) / 82.0  # Progressione normale
        pulse = math.sin(progress * math.pi * 3) * 0.2  # Pulsazione cyber
        scale = 1.1 + pulse
        
        # Testo principale LIVEL
        main_text = font_xl.render(f"LEVEL {self.level_num}", True, NEON_CYAN)
        scaled_w = int(main_text.get_width() * scale)
        scaled_h = int(main_text.get_height() * scale)
        
        if scaled_w > 0 and scaled_h > 0:
            scaled_text = pygame.transform.scale(main_text, (scaled_w, scaled_h))
            
            # 1. SFONDO PANEL CYBERPUNK
            panel_w = scaled_w + 60
            panel_h = scaled_h + 40
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            
            # Gradiente sfondo scuro cyber
            for i in range(panel_h):
                t = i / panel_h
                bg_color = tuple(int(DARK_GRAY[j] * (0.3 + t * 0.4)) for j in range(3))
                pygame.draw.line(panel_surf, (*bg_color, 180), (0, i), (panel_w, i))
            
            # Bordo neon pulsante
            border_glow = int(120 + 80 * abs(math.sin(progress * 8)))
            pygame.draw.rect(panel_surf, (*NEON_CYAN, border_glow), 
                           (0, 0, panel_w, panel_h), width=4, border_radius=20)
            
            # 2. GLOW MULTI-LAYER
            for r in range(40, 0, -6):
                glow_alpha = int(100 * (1 - r/40) * (1 - progress * 0.5))
                if glow_alpha > 0:
                    glow_surf = pygame.Surface((scaled_w + r*2, scaled_h + r*2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*NEON_CYAN, glow_alpha), 
                                   (0, 0, glow_surf.get_width(), glow_surf.get_height()),
                                   border_radius=25)
                    surf.blit(glow_surf, 
                            (scr_w//2 - glow_surf.get_width()//2 + 30, 
                             scr_h//2 - glow_surf.get_height()//2 + 20))
            
            # 3. OUTLINE NERO (stile fumetto)
            outline_surf = scaled_text.copy()
            outline_surf.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
            outline_surf.set_alpha(200)
            
            for dx, dy in [(2,2), (2,-2), (-2,2), (-2,-2), (1,0), (-1,0), (0,1), (0,-1)]:
                surf.blit(outline_surf, 
                         (scr_w//2 - scaled_w//2 + dx + 30, 
                          scr_h//2 - scaled_h//2 + dy + 20))
            
            # 4. TESTO PRINCIPALE
            surf.blit(scaled_text, 
                     (scr_w//2 - scaled_w//2 + 30, scr_h//2 - scaled_h//2 + 20))
            
            # 5. EFFETTO GLITCH (ogni 7 frame)
            if self.age % 7 == 0:
                glitch_offset = random.randint(-3, 3)
                glitch_surf = pygame.transform.scale(scaled_text, (scaled_w, scaled_h))
                surf.blit(glitch_surf, 
                         (scr_w//2 - scaled_w//2 + 30 + glitch_offset, 
                          scr_h//2 - scaled_h//2 + 20))
            
            # 6. BOLLE NEON ai lati (cyberpunk)
            for side, offset_x in enumerate([-panel_w//2 - 15, panel_w//2 + 15]):
                bubble_alpha = int(100 * (1 - progress))
                bubble_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                color = NEON_CYAN if side == 0 else NEON_MAGENTA
                pygame.draw.circle(bubble_surf, (*color, bubble_alpha), (15, 15), 15)
                pygame.draw.circle(bubble_surf, (*WHITE, bubble_alpha//2), (15, 15), 8)
                surf.blit(bubble_surf, 
                         (scr_w//2 + offset_x, scr_h//2 - scaled_h//2 + 10))











class ComicExplosion:
    """
    Esplosione CYBERPUNK v8 - PERFECT SILHOUETTE + SHOCKWAVE + GLITCH
    Migliorie: 1)Shockwave radiale 2)Debris trails rotanti 3)Testo glitch cyberpunk
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 60
        self.age = 0
        self.shockwave_phase = 0  # Nuova: per shockwave

        # Palette (compatibile con CYBERPUNK_PALETTES)
        self.palette = random.choice(CYBERPUNK_PALETTES)
        self.primary_color = self.palette.get('objects', (255, 60, 0))
        
        # Colori Nuvola (invariati)
        base_cloud = self.palette.get('clouds', [(245, 245, 255)])[0]
        self.smoke_light = base_cloud
        self.smoke_shadow = tuple(max(0, c - 50) for c in base_cloud)
        self.deep_black = (10, 10, 15)
        
        # M1: Colori Shockwave (neon radiale)
        self.shock_color = self.palette.get('neon_glow', (0, 255, 255))
        self.shock_trail = tuple(max(0, c - 80) for c in self.shock_color)
        
        random.seed(int(x * 100 + y + pygame.time.get_ticks()))

        # --- STRUTTURA NUVOLA --- (invariata)
        self.puffs = []
        self.puffs.append({'ang': 0, 'dist': 0, 'r': 70})
        num_puffs = 8
        for i in range(num_puffs):
            ang = (i / num_puffs) * 6.28
            dist = 40
            self.puffs.append({'ang': ang, 'dist': dist, 'r': random.uniform(50, 60)})

        # M2: Debris MIGLIORATI con rotazione e trail colors
        self.debris = []
        for _ in range(15):  # +3 per densità
            ang = random.uniform(0, 6.28)
            speed = random.uniform(8, 18)
            rot_speed = random.uniform(-0.3, 0.3)
            trail_cols = [self.primary_color, self.palette.get('neon_glow', (0,255,255)), (255,255,200)]
            self.debris.append({
                'vx': math.cos(ang) * speed, 'vy': math.sin(ang) * speed,
                'x': 0, 'y': 0, 'rot': 0, 'rot_speed': rot_speed,
                'trail_cols': random.sample(trail_cols, 3), 'life': 1.0
            })

    def ease_out_back(self, t):
        c1 = 1.70158; c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    def update(self):
        self.age += 1
        self.shockwave_phase = min(15, self.age)  # M1: Controlla shockwave
        
        # M2: Update debris migliorato
        for d in self.debris:
            d['x'] += d['vx']; d['y'] += d['vy']
            d['vx'] *= 0.92; d['vy'] *= 0.92; d['vy'] += 0.4
            d['rot'] += d['rot_speed']
            d['life'] *= 0.96  # Fade naturale
            
        return self.age < self.lifetime

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        
        # M1: SHOCKWAVE RADIALE (nuovo layer 0)
        if self.age <= 15:
            t = self.age / 15.0
            shock_r = 20 + 200 * t * t  # Accelerazione cubica
            shock_a = int(200 * (1 - t)**2)
            
            if shock_a > 10:
                # Anello principale neon
                pygame.draw.circle(surf, self.shock_color, (cx, cy), int(shock_r), 3)
                # Trail interno sfumato
                pygame.draw.circle(surf, self.shock_trail, (cx, cy), int(shock_r * 0.85), 2)
                # Distorsione: righe radiali (simulazione warp)
                for i in range(12):
                    ang = i * 0.52
                    dx = math.cos(ang) * shock_r * 0.7
                    dy = math.sin(ang) * shock_r * 0.7
                    trail_w = int(2 * (1-t))
                    pygame.draw.line(surf, self.shock_trail, 
                                   (cx + dx*0.3, cy + dy*0.3), 
                                   (cx + dx, cy + dy), trail_w)

        # 1. FLASH (invariato)
        if self.age < 3:
            r = 140 * (1 - self.age/3)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), int(r))

        # 2. NUVOLA UNIFICATA (invariata - perfetta silhouette)
        if self.age > 0:
            t = min(1.0, self.age / 12)
            scale = self.ease_out_back(t)
            alpha = 255
            if self.age > 40:
                alpha = int(255 * (1 - (self.age - 40) / 15))
            
            if alpha > 0:
                res_scale = 2; base_size = 420; ss_size = base_size * res_scale; mid = ss_size // 2
                c_surf = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
                
                outline_pad = 4 * res_scale; shadow_pad = 0
                light_offset_x = -6 * res_scale; light_offset_y = -6 * res_scale
                
                # LAYER 1: OUTLINE NERO
                for p in self.puffs:
                    r = (p['r'] * scale * res_scale) + outline_pad
                    dist = p['dist'] * scale * res_scale
                    px = mid + math.cos(p['ang']) * dist
                    py = mid + math.sin(p['ang']) * dist
                    pygame.draw.circle(c_surf, self.deep_black, (int(px), int(py)), int(r))
                
                # LAYER 2: OMBRA
                for p in self.puffs:
                    r = (p['r'] * scale * res_scale)
                    dist = p['dist'] * scale * res_scale
                    px = mid + math.cos(p['ang']) * dist
                    py = mid + math.sin(p['ang']) * dist
                    pygame.draw.circle(c_surf, self.smoke_shadow, (int(px), int(py)), int(r))

                # LAYER 3: LUCE (spostata)
                for p in self.puffs:
                    r = (p['r'] * scale * res_scale)
                    dist = p['dist'] * scale * res_scale
                    px = mid + math.cos(p['ang']) * dist + light_offset_x
                    py = mid + math.sin(p['ang']) * dist + light_offset_y
                    pygame.draw.circle(c_surf, self.smoke_light, (int(px), int(py)), int(r))

                final_cloud = pygame.transform.smoothscale(c_surf, (base_size, base_size))
                if alpha < 255: final_cloud.set_alpha(alpha)
                surf.blit(final_cloud, (cx - base_size//2, cy - base_size//2))

        # M2: DETRITI CON TRAIL GLOW + ROTAZIONE
        if self.age > 1:
            for d in self.debris:
                if d['life'] > 0.1:
                    px = cx + d['x']; py = cy + d['y']
                    # Trail: 3 segmenti sfumati con rotazione
                    trail_len = 18 * d['life']
                    for i, col in enumerate(d['trail_cols']):
                        seg_len = trail_len * (0.3 + i*0.23)
                        trail_ang = d['rot'] + i * 0.3
                        ex = px + math.cos(trail_ang) * seg_len
                        ey = py + math.sin(trail_ang) * seg_len
                        w = max(1, int(3 * d['life'] * (1 - i*0.4)))
                        pygame.draw.line(surf, col, (px, py), (ex, ey), w)

        # M3: TESTO "BOOM!" CON GLITCH CYBERPUNK
        if 2 < self.age < 50:
            txt_scale = 1.0
            if self.age < 10:
                t = (self.age - 2) / 8
                txt_scale = 1.0 + math.sin(t * 3.14) * 0.15
            
            alpha_txt = 255
            if self.age > 35:
                alpha_txt = int(255 * (1 - (self.age - 35) / 15))

            if alpha_txt > 0:
                # M3: Glitch shake + offset cromatico
                glitch_x = random.randint(-1, 1) * (self.age % 3 == 0)
                glitch_y = random.randint(-1, 1) * (self.age % 3 == 0)
                
                t_surf = font_xl.render("BOOM!", True, (255, 255, 255))
                w = int(t_surf.get_width() * 0.85 * txt_scale)
                h = int(t_surf.get_height() * 0.85 * txt_scale)
                
                if w > 0 and h > 0:
                    scaled_t = pygame.transform.scale(t_surf, (w, h))
                    tx = cx - w // 2 + glitch_x; ty = cy - h // 2 + glitch_y
                    
                    # Outline con glitch multi-colore
                    outline_surf = scaled_t.copy()
                    outline_surf.fill(self.deep_black, special_flags=pygame.BLEND_RGBA_MULT)
                    outline_surf.set_alpha(alpha_txt)
                    for off in [(2,2), (-2,2), (1,-1), (-1,1)]:
                        surf.blit(outline_surf, (tx + off[0], ty + off[1]))
                    
                    # M3: Main testo con glow palette
                    main_surf = scaled_t.copy()
                    glow_col = self.palette.get('neon_glow', self.primary_color)
                    main_surf.fill(glow_col, special_flags=pygame.BLEND_RGBA_MULT)
                    main_surf.set_alpha(alpha_txt)
                    surf.blit(main_surf, (tx, ty))
                    
                    # M3: Glitch cromatico (rosso/ciano offset)
                    red_chan = scaled_t.copy()
                    red_chan.fill((255, 0, 0, 180), special_flags=pygame.BLEND_RGBA_MULT)
                    cyan_chan = scaled_t.copy()
                    cyan_chan.fill((0, 255, 255, 120), special_flags=pygame.BLEND_RGBA_MULT)
                    surf.blit(red_chan, (tx + 1, ty))
                    surf.blit(cyan_chan, (tx - 1, ty))







obstacle_surfaces_cache = None










def create_obstacle_surfaces():
    global obstacle_surfaces_cache
    
    pipe_width = 70
    cap_height = 30
    cap_extra_width = 10
    
    COLOR_CENTER = (255, 80, 255)
    COLOR_MID_BRIGHT = (220, 50, 240)
    COLOR_MID = (160, 30, 180)
    COLOR_DARK = (100, 15, 120)
    COLOR_EDGE = (50, 8, 60)
    
    body_height = 100
    body_surf = pygame.Surface((pipe_width, body_height), pygame.SRCALPHA)
    
    center_x = pipe_width / 2
    
    for x in range(pipe_width):
        dist = abs(x - center_x) / (pipe_width / 2)
        
        if dist < 0.15:
            t = dist / 0.15
            color = tuple(int(COLOR_CENTER[i] * (1 - t) + COLOR_MID_BRIGHT[i] * t) for i in range(3))
        elif dist < 0.45:
            t = (dist - 0.15) / 0.3
            color = tuple(int(COLOR_MID_BRIGHT[i] * (1 - t) + COLOR_MID[i] * t) for i in range(3))
        elif dist < 0.80:
            t = (dist - 0.45) / 0.35
            color = tuple(int(COLOR_MID[i] * (1 - t) + COLOR_DARK[i] * t) for i in range(3))
        else:
            t = (dist - 0.80) / 0.2
            color = tuple(int(COLOR_DARK[i] * (1 - t) + COLOR_EDGE[i] * t) for i in range(3))
        
        pygame.draw.line(body_surf, color, (x, 0), (x, body_height))
    
    for x in range(int(center_x - pipe_width * 0.08), int(center_x + pipe_width * 0.08)):
        pygame.draw.line(body_surf, (255, 150, 255, 100), (x, 0), (x, body_height))
    
    body_surf = body_surf.convert_alpha()
    
    cap_w = pipe_width + cap_extra_width
    cap_top_surf = pygame.Surface((cap_w, cap_height), pygame.SRCALPHA)
    cap_center_x = cap_w / 2
    ellipse_height = 10
    
    for y in range(ellipse_height):
        t = y / ellipse_height
        ellipse_width = cap_w * math.sqrt(1 - (1 - t) ** 2)
        x_start = int((cap_w - ellipse_width) / 2)
        x_end = int((cap_w + ellipse_width) / 2)
        
        shade = 0.25 + 0.75 * t
        color = tuple(int(COLOR_DARK[i] * shade) for i in range(3))
        pygame.draw.line(cap_top_surf, color, (x_start, y), (x_end, y))
    
    for x in range(cap_w):
        dist = abs(x - cap_center_x) / (cap_w / 2)
        
        if dist < 0.15:
            t = dist / 0.15
            color = tuple(int(COLOR_CENTER[i] * (1 - t) + COLOR_MID_BRIGHT[i] * t) for i in range(3))
        elif dist < 0.45:
            t = (dist - 0.15) / 0.3
            color = tuple(int(COLOR_MID_BRIGHT[i] * (1 - t) + COLOR_MID[i] * t) for i in range(3))
        elif dist < 0.80:
            t = (dist - 0.45) / 0.35
            color = tuple(int(COLOR_MID[i] * (1 - t) + COLOR_DARK[i] * t) for i in range(3))
        else:
            t = (dist - 0.80) / 0.2
            color = tuple(int(COLOR_DARK[i] * (1 - t) + COLOR_EDGE[i] * t) for i in range(3))
        
        pygame.draw.line(cap_top_surf, color, (x, ellipse_height), (x, cap_height))
    
    cap_top_surf = cap_top_surf.convert_alpha()
    
    cap_bottom_surf = pygame.Surface((cap_w, cap_height), pygame.SRCALPHA)
    cap_body_height = cap_height - ellipse_height
    
    for x in range(cap_w):
        dist = abs(x - cap_center_x) / (cap_w / 2)
        
        if dist < 0.15:
            t = dist / 0.15
            color = tuple(int(COLOR_CENTER[i] * (1 - t) + COLOR_MID_BRIGHT[i] * t) for i in range(3))
        elif dist < 0.45:
            t = (dist - 0.15) / 0.3
            color = tuple(int(COLOR_MID_BRIGHT[i] * (1 - t) + COLOR_MID[i] * t) for i in range(3))
        elif dist < 0.80:
            t = (dist - 0.45) / 0.35
            color = tuple(int(COLOR_MID[i] * (1 - t) + COLOR_DARK[i] * t) for i in range(3))
        else:
            t = (dist - 0.80) / 0.2
            color = tuple(int(COLOR_DARK[i] * (1 - t) + COLOR_EDGE[i] * t) for i in range(3))
        
        pygame.draw.line(cap_bottom_surf, color, (x, 0), (x, cap_body_height))
    
    for y in range(ellipse_height):
        t = 1 - (y / ellipse_height)
        ellipse_width = cap_w * math.sqrt(1 - (1 - t) ** 2)
        x_start = int((cap_w - ellipse_width) / 2)
        x_end = int((cap_w + ellipse_width) / 2)
        
        shade = 0.25 + 0.75 * (1 - t)
        color = tuple(int(COLOR_DARK[i] * shade) for i in range(3))
        pygame.draw.line(cap_bottom_surf, color, (x_start, cap_body_height + y), (x_end, cap_body_height + y))
    
    cap_bottom_surf = cap_bottom_surf.convert_alpha()
    
    obstacle_surfaces_cache = {
        'body': body_surf,
        'cap_top': cap_top_surf,
        'cap_bottom': cap_bottom_surf,
        'width': pipe_width,
        'cap_extra': cap_extra_width
    }
    
    print(f"✓ Tubi creati")













create_obstacle_surfaces()



# Variabile globale per memorizzare la palette scelta
_selected_palette = None

def get_or_select_palette():
    """Seleziona una palette casuale solo la prima volta"""
    global _selected_palette
    if _selected_palette is None:
        _selected_palette = random.choice(CYBERPUNK_PALETTES)
    return _selected_palette




@dataclass
class Obstacle:
    x: float
    y: float
    width: int = 70
    gap_height: int = 230
    passed: bool = False
    _palette: dict = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        self._palette = random.choice(CYBERPUNK_PALETTES)
    
    def draw(self, surf):
        # Cambio chiave cache per forzare il ridisegno con il nuovo stile
        cache_key = f"{self._palette['name']}_{id(self._palette)}_cyber_toon"
        
        if cache_key not in obstacle_surfaces_cache:
            self._create_surfaces_for_palette(cache_key)
        
        surfaces = obstacle_surfaces_cache[cache_key]
        body_surf = surfaces['body']
        cap_top_surf = surfaces['cap_top']
        cap_bottom_surf = surfaces['cap_bottom']
        cap_extra = surfaces['cap_extra']
        
        cap_height = cap_top_surf.get_height()
        scr_height = surf.get_height()
        
        top_pipe_bottom = int(self.y)
        y_pos = 0
        body_height = body_surf.get_height()
        
        # --- DISEGNO TUBO SUPERIORE ---
        while y_pos < top_pipe_bottom - cap_height:
            remaining = min(body_height, top_pipe_bottom - cap_height - y_pos)
            area = (0, 0, body_surf.get_width(), remaining)
            surf.blit(body_surf, (int(self.x), y_pos), area)
            y_pos += body_height
        
        # --- DISEGNO CAP SUPERIORE ---
        cap_x = int(self.x) - cap_extra // 2
        cap_y = top_pipe_bottom - cap_height
        surf.blit(cap_top_surf, (cap_x, cap_y))
        
        # --- DISEGNO CAP INFERIORE ---
        bottom_pipe_top = int(self.y + self.gap_height)
        surf.blit(cap_bottom_surf, (cap_x, bottom_pipe_top))
        
        # --- DISEGNO TUBO INFERIORE ---
        y_pos = bottom_pipe_top + cap_height
        while y_pos < scr_height:
            remaining = min(body_height, scr_height - y_pos)
            area = (0, 0, body_surf.get_width(), remaining)
            surf.blit(body_surf, (int(self.x), y_pos), area)
            y_pos += body_height
    
    def _create_surfaces_for_palette(self, cache_key):
        # Corpo del tubo
        body_surf = self._create_cyber_toon_pipe(self.width, 50, is_cap=False)
        
        # Tappi del tubo
        cap_top_surf = self._create_cyber_toon_pipe(self.width, 34, is_cap=True)
        cap_bottom_surf = cap_top_surf
        
        cap_extra = cap_top_surf.get_width() - self.width
        
        obstacle_surfaces_cache[cache_key] = {
            'body': body_surf,
            'cap_top': cap_top_surf,
            'cap_bottom': cap_bottom_surf,
            'cap_extra': cap_extra
        }
    
    def _create_cyber_toon_pipe(self, base_width, height, is_cap=False):
        """
        Crea una superficie stile 'Cyber-Toon':
        - Outline neri spessi (Fumetto)
        - Shading netto senza sfumature (Cel-shading)
        - Dettagli Neon (Cyberpunk)
        """
        import pygame
        
        # Dimensioni
        total_width = base_width + 12 if is_cap else base_width
        surf = pygame.Surface((total_width, height), pygame.SRCALPHA)
        
        # Colori
        base_c = self._palette['objects']
        neon_c = self._palette['lights']
        
        # Creiamo varianti "Cel-Shaded" (piatte, senza gradienti)
        # Colore base leggermente scurito per far saltare il neon
        main_fill = tuple(max(0, c - 20) for c in base_c) 
        # Ombra netta (molto scura per contrasto fumetto)
        shadow_fill = tuple(max(0, c - 80) for c in base_c)
        # Highlight netto (quasi bianco/pastello)
        highlight_fill = tuple(min(255, c + 60) for c in base_c)
        
        outline_color = (0, 0, 0)
        border_thick = 3 # Bordo più spesso per effetto cartoon
        
        # 1. SFONDO (Outline)
        surf.fill(outline_color)
        
        # Calcolo area interna (Gestione tiling per il corpo)
        y_start = border_thick if is_cap else 0
        inner_height = (height - border_thick * 2) if is_cap else height
        
        # 2. RIEMPIMENTO BASE
        rect_main = pygame.Rect(border_thick, y_start, 
                                total_width - border_thick*2, 
                                inner_height)
        pygame.draw.rect(surf, main_fill, rect_main)
        
        # 3. SHADING NETTO (Lato destro in ombra)
        # Dividiamo il tubo in: Luce (sx), Base (centro), Ombra (dx)
        shadow_width = total_width // 4
        shadow_x = total_width - border_thick - shadow_width
        shadow_rect = pygame.Rect(shadow_x, y_start, shadow_width, inner_height)
        pygame.draw.rect(surf, shadow_fill, shadow_rect)
        
        # 4. HIGHLIGHT NETTO (Lato sinistro)
        high_width = 4
        high_x = border_thick + 4
        high_rect = pygame.Rect(high_x, y_start, high_width, inner_height)
        pygame.draw.rect(surf, highlight_fill, high_rect)
        
        # 5. DETTAGLIO CYBERPUNK (Linea Neon)
        if not is_cap:
            # Una linea verticale luminosa che separa la zona base dall'ombra
            neon_strip_w = 2
            neon_x = shadow_x - 4 # Appena prima dell'ombra
            neon_rect = pygame.Rect(neon_x, y_start, neon_strip_w, inner_height)
            pygame.draw.rect(surf, neon_c, neon_rect)
        else:
            # SE È UN CAP (TAPPO)
            
            # A. Bulloni agli angoli (cerchietti scuri)
            bolt_color = shadow_fill
            r = 3
            # Top-Left
            pygame.draw.circle(surf, bolt_color, (border_thick + 6, y_start + 6), r)
            # Top-Right
            pygame.draw.circle(surf, bolt_color, (total_width - border_thick - 6, y_start + 6), r)
            # Bottom-Left
            pygame.draw.circle(surf, bolt_color, (border_thick + 6, y_start + inner_height - 6), r)
            # Bottom-Right
            pygame.draw.circle(surf, bolt_color, (total_width - border_thick - 6, y_start + inner_height - 6), r)
            
            # B. Barra Sensore Luminosa Centrale
            bar_h = 6
            bar_w = total_width - 24
            bar_x = (total_width - bar_w) // 2
            bar_y = y_start + (inner_height - bar_h) // 2
            
            # Sfondo barra (scuro)
            pygame.draw.rect(surf, (20, 20, 20), (bar_x, bar_y, bar_w, bar_h))
            # Luce interna (neon)
            pygame.draw.rect(surf, neon_c, (bar_x + 2, bar_y + 2, bar_w - 4, bar_h - 4))

        return surf








obstacle_surfaces_cache = {}













# Per resettare la palette e sceglierne una nuova:
def reset_palette():
    """Resetta la palette per sceglierne una nuova al prossimo ostacolo"""
    global _selected_palette
    _selected_palette = None
    obstacle_surfaces_cache.clear()








def generate_stars(scr_w, scr_h, num_stars):
    """Genera stelle multi-layer con profondità"""
    stars = []
    
    for i in range(num_stars):
        depth_roll = random.random() ** 2
        
        if depth_roll < 0.6:  # 60% - Stelle lontane
            depth = random.uniform(0.1, 0.3)
            size = 1
            brightness = random.uniform(0.3, 0.6)
            twinkle_speed = random.uniform(0.3, 0.8)
            color_variety = random.choice([
                (100, 120, 180), (120, 130, 200), (90, 100, 150)
            ])
        elif depth_roll < 0.85:  # 25% - Stelle medie
            depth = random.uniform(0.3, 0.6)
            size = random.choice([1, 1, 2])
            brightness = random.uniform(0.5, 0.8)
            twinkle_speed = random.uniform(0.5, 1.2)
            color_variety = random.choice([
                (150, 180, 255), (180, 200, 255), (200, 210, 255), (255, 220, 180)
            ])
        else:  # 15% - Stelle vicine
            depth = random.uniform(0.6, 1.0)
            size = random.choice([2, 2, 3])
            brightness = random.uniform(0.7, 1.0)
            twinkle_speed = random.uniform(0.8, 1.8)
            color_variety = random.choice([
                (255, 255, 255), (255, 240, 220), (220, 240, 255), 
                (255, 200, 150), (150, 200, 255)
            ])
        
        stars.append({
            'x': random.uniform(0, scr_w),
            'y': random.uniform(0, scr_h),
            'size': size,
            'brightness': brightness,
            'base_brightness': brightness,
            'twinkle_speed': twinkle_speed,
            'twinkle_offset': random.uniform(0, math.pi * 2),
            'color': color_variety,
            'depth': depth,
            'type': random.choice(['normal', 'normal', 'normal', 'pulsar', 'shimmer']),
            'pulse_phase': random.uniform(0, math.pi * 2),
        })
    
    return stars


def draw_starfield():
    """Starfield multi-layer con parallax"""
    scr_w = screen.get_width()
    scr_h = screen.get_height()
    time_ms = pygame.time.get_ticks()
    time_sec = time_ms * 0.001
    
    # Ordina per depth
    sorted_stars = sorted(game.stars, key=lambda s: s['depth'])
    
    for star in sorted_stars:
        # Parallax
        parallax_speed = 0.3 + star['depth'] * 1.2
        star['x'] = (star['x'] - parallax_speed) % scr_w
        
        # Animazioni
        if star['type'] == 'pulsar':
            pulse = abs(math.sin(time_sec * 0.8 + star['pulse_phase']))
            brightness_mult = 0.4 + pulse * 0.6
        elif star['type'] == 'shimmer':
            shimmer = math.sin(time_sec * 4 + star['pulse_phase']) * 0.5 + 0.5
            brightness_mult = 0.6 + shimmer * 0.4
        else:
            twinkle = math.sin(time_sec * star['twinkle_speed'] + star['twinkle_offset'])
            brightness_mult = 0.6 + 0.4 * twinkle
        
        final_brightness = star['base_brightness'] * brightness_mult
        color = tuple(int(c * final_brightness) for c in star['color'])
        
        x, y = int(star['x']), int(star['y'])
        
        # Rendering ottimizzato
        if star['size'] == 1:
            # Disegna un rettangolo 1x1 invece di usare set_at
            pygame.draw.rect(screen, color, (x, y, 1, 1))
        elif star['size'] == 2:
            pygame.draw.rect(screen, color, (x, y, 2, 2))
            # Per l'alone (fade_color), disegna rettangoli adiacenti o un cerchio sfumato
        else:
            pygame.draw.circle(screen, color, (x, y), 2)
            glow_color = tuple(int(c * 0.5) for c in color)
            pygame.draw.circle(screen, glow_color, (x, y), 2, 1)
            
            if final_brightness > 0.8 and 2 < x < scr_w - 3 and 2 < y < scr_h - 3:
                flare_color = tuple(int(c * 0.3) for c in color)
                screen.set_at((x - 3, y), flare_color)
                screen.set_at((x + 3, y), flare_color)
                screen.set_at((x, y - 3), flare_color)
                screen.set_at((x, y + 3), flare_color)



def lerp(a, b, t):
    """Interpolazione lineare smooth per AI"""
    return a + (b - a) * t

class Game:
    def __init__(self):
        self.state = "MENU"
        self.player_y = SCREEN_HEIGHT // 2
        self.player_size = 22
        self.velocity = 0.0
        self.score = 0
        self.high_score = 0
        self.obstacles = []
        self.particles = []
        self.score_popups = []
        self.level_notifications = []
        self.spawn_timer = 0
        self.spawn_interval = 115
        self.base_obstacle_speed = 5.5
        self.obstacle_speed = 5.5
        self.difficulty = 1.0
        self.combo = 0
        self.combo_timer = 0
        self.fullscreen = False
        self.ai_active = False  # AI spenta di default[file:1]
        self.ai_prediction_distance = 200  # Distanza per prevedere ostacoli

        self.current_level = 1
        self.current_palette_index = 0
        self.next_palette_index = 1
        self.transition_progress = 0.0
        self.is_transitioning = False
        
        self.calib_silence = []
        self.calib_shout = []
        self.silence_threshold = 0.05
        self.shout_threshold = 0.15
        self.calibrated = False
        self.calib_timer = 0
        self.calib_duration = 90
        
        self.menu_pulse = 0.0
        self.stars = generate_stars(SCREEN_WIDTH, SCREEN_HEIGHT, 700)
        
        # EQUALIZER TOGGLE
        self.show_equalizer = False
        self.explosion_animation = None
        
        self.load_calibration()

    def check_level_up(self):
        new_level = (self.score // 20) + 1
        
        if new_level > self.current_level:
            self.current_level = new_level
            
            self.is_transitioning = True
            self.transition_progress = 0.0
            self.current_palette_index = self.next_palette_index
            self.next_palette_index = (self.next_palette_index + 1) % len(CYBERPUNK_PALETTES)
            
            self.obstacle_speed = self.base_obstacle_speed * (1.0 + (self.current_level - 1) * 0.06)
            
            self.level_notifications.append(LevelNotification(self.current_level))
            play_sound(SOUND_LEVELUP)
            
            print(f"✓ Level {self.current_level}")

    def save_calibration(self):
        data = {
            "silence": self.silence_threshold,
            "shout": self.shout_threshold,
            "high_score": self.high_score
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
            self.calibrated = True
        except Exception as e:
            print(f"⚠ Errore salvataggio: {e}")

    def load_calibration(self):
        if not os.path.exists(CONFIG_FILE):
            self.calibrated = False
            return
            
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.silence_threshold = data.get("silence", 0.05)
                self.shout_threshold = data.get("shout", 0.15)
                self.high_score = data.get("high_score", 0)
                self.calibrated = True
                print(f"✓ Calibrazione caricata")
        except Exception as e:
            print(f"⚠ Errore caricamento: {e}")
            self.calibrated = False
    
    def toggle_fullscreen(self):
        global screen
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        else:
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
        
        scr_w = screen.get_width()
        scr_h = screen.get_height()
        self.stars = generate_stars(scr_w, scr_h, 700)

game = Game()
























def draw_player(x, y, velocity, color=NEON_CYAN):
    angle = np.clip(velocity * 3.2, -35, 75)
    bird_size = game.player_size * 2.8
    surf_size = int(bird_size * 2.1)
    bird_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    center_x = center_y = surf_size // 2
    
    time = pygame.time.get_ticks() * 0.001
    
    # ==== 1) BLOOM SFUMATO PRO ====
    pulse = 1.0 + 0.08 * math.sin(time * 3.2)
    max_radius = int(game.player_size * 2.3 * pulse)
    
    for layer in range(3):
        layer_radius = max_radius - layer * 8
        if layer_radius < 3: break
        t = layer_radius / max_radius
        alpha = int(160 * t * t * math.exp(-layer * 0.4) * pulse)
        if alpha < 2: continue
        bloom_color = (color[0], color[1], color[2], alpha)
        pygame.draw.circle(bird_surface, bloom_color, (center_x, center_y), layer_radius)
    
    core_color = (min(255, color[0]*1.4), min(255, color[1]*1.4), min(255, color[2]*1.4), 220)
    pygame.draw.circle(bird_surface, core_color, (center_x, center_y), int(game.player_size*0.6))
    
    # ==== 2) CODA PIUMOSA (5 Piume) FIXATA ====
    tail_attach_x = center_x - game.player_size * 0.95
    tail_attach_y = center_y
    
    rise_factor = max(0.0, min(1.0, -velocity / 12.0))
    tail_wave = math.sin(time * 4.1 + velocity * 0.1) * 0.12
    tail_spread = game.player_size * 0.42 * (1.0 + rise_factor * 0.6)
    
    # FIX: Colori senza starred expression
    tail_main_r = min(255, int((color[0] + NEON_GREEN[0]) * 0.55))
    tail_main_g = min(255, int((color[1] + NEON_GREEN[1]) * 0.55))
    tail_main_b = min(255, int((color[2] + NEON_GREEN[2]) * 0.55))
    tail_main = (tail_main_r, tail_main_g, tail_main_b)
    tail_tip = (min(255, tail_main_r*1.25), min(255, tail_main_g*1.25), min(255, tail_main_b*1.25))
    
    for feather_idx in range(5):
        feather_offset = (feather_idx - 2) * game.player_size * 0.18
        feather_wave = tail_wave * (1.0 + feather_idx * 0.15)
        
        feather_pts = [
            (tail_attach_x - game.player_size * 0.9, 
             tail_attach_y + feather_offset - tail_spread * 0.6 + feather_wave),
            (tail_attach_x - game.player_size * 0.4, 
             tail_attach_y + feather_offset * 0.7 + feather_wave * 1.2),
            (tail_attach_x + game.player_size * 0.15,
             tail_attach_y + feather_offset * 0.4 + feather_wave * 0.8)
        ]
        
        shadow_pts = [(int(px+1.5), int(py+1.5)) for px, py in feather_pts]
        pygame.draw.polygon(bird_surface, (20, 15, 35, 160), shadow_pts)
        pygame.draw.polygon(bird_surface, tail_main, [(int(px), int(py)) for px, py in feather_pts])
        pygame.draw.aalines(bird_surface, tail_tip, False, [(int(px), int(py)) for px, py in feather_pts[::-1]], 1)
    
    spine_pts = [
        (int(tail_attach_x - game.player_size * 0.75), int(tail_attach_y)),
        (int(tail_attach_x + game.player_size * 0.1), int(tail_attach_y))
    ]
    spine_glow = (min(255, tail_main[0]*1.3), min(255, tail_main[1]*1.3), min(255, tail_main[2]*1.3))
    pygame.draw.aalines(bird_surface, spine_glow, False, spine_pts, 2)
    
    # ==== 3) CORPO ====
    body_size = game.player_size * 0.98
    body_surf = pygame.Surface((int(body_size*2.4), int(body_size*1.8)), pygame.SRCALPHA)
    pygame.draw.ellipse(body_surf, color, (0, 0, int(body_size*2.4), int(body_size*1.8)))
    
    hl_offset = int(velocity * 0.15)
    pygame.draw.ellipse(body_surf, (255, 255, 255, 0), (4+hl_offset, 2, int(body_size*1.1), int(body_size*0.7)), 0)
    pygame.draw.ellipse(body_surf, (*color, 0), (0, 0, int(body_size*2.4), int(body_size*1.8)), 3)
    
    bird_surface.blit(body_surf, (center_x - body_size*1.2, center_y - body_size*0.9))
    
    # ==== 4) OMBRA ====
    shadow_size = game.player_size * 1.9
    shadow_surf = pygame.Surface((int(shadow_size*1.1), int(shadow_size*0.6)), pygame.SRCALPHA)
    shadow_alpha = min(90, 50 + int(abs(velocity) * 5) + int(pulse * 10))
    
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha//2), (0, 0, int(shadow_size*1.1), int(shadow_size*0.6)))
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), (2, 1, int(shadow_size*0.95), int(shadow_size*0.45)))
    
    s_off_x = int(velocity * 0.35) + int(math.sin(time*2)*1.5)
    bird_surface.blit(shadow_surf, (center_x - shadow_size*0.55 + s_off_x, center_y - shadow_size*0.25 + 5))
    
    # ==== 5) ALI ====
    flap_time = time * 8.3
    primary_flap = game.player_size * 0.38 * math.sin(flap_time)
    secondary_flap = game.player_size * 0.22 * math.sin(flap_time + 0.8)
    
    # Ala primaria
    wing1_x = center_x - game.player_size * 0.68
    wing1_y = center_y + primary_flap * 0.7
    wing1_w, wing1_h = game.player_size * 0.65, game.player_size * 0.38
    wing1_surf = pygame.Surface((int(wing1_w*2.2), int(wing1_h*2.2)), pygame.SRCALPHA)
    
    dark_wing = (min(60, color[0]*0.4), min(200, color[1]*0.75), min(30, color[2]*0.4))
    wing_core = (min(40, dark_wing[0]*0.8), min(160, dark_wing[1]*0.8), min(20, dark_wing[2]*0.8))
    
    pygame.draw.ellipse(wing1_surf, (0,0,0,140), (1,1,int(wing1_w*2.1),int(wing1_h*2.1)))
    pygame.draw.ellipse(wing1_surf, dark_wing, (3,2,int(wing1_w*2),int(wing1_h*2)))
    pygame.draw.ellipse(wing1_surf, wing_core, (int(wing1_w*0.3), int(wing1_h*0.3), int(wing1_w*1.4), int(wing1_h*1.3)))
    pygame.draw.ellipse(wing1_surf, (255,255,255,0), (0,0,int(wing1_w*2.2),int(wing1_h*2.2)), 2)
    
    bird_surface.blit(wing1_surf, (int(wing1_x-wing1_w*1.1), int(wing1_y-wing1_h*1.1)))
    
    # Ala secondaria
    wing2_x = center_x - game.player_size * 0.55
    wing2_y = center_y + secondary_flap * 0.9
    wing2_w, wing2_h = game.player_size * 0.42, game.player_size * 0.24
    wing2_surf = pygame.Surface((int(wing2_w*2.1), int(wing2_h*2.1)), pygame.SRCALPHA)
    
    pygame.draw.ellipse(wing2_surf, dark_wing, (2,1,int(wing2_w*1.9),int(wing2_h*1.9)))
    pygame.draw.ellipse(wing2_surf, wing_core, (int(wing2_w*0.35), int(wing2_h*0.35), int(wing2_w*1.2), int(wing2_h*1.2)))
    pygame.draw.ellipse(wing2_surf, (255,255,255,0), (0,0,int(wing2_w*2.1),int(wing2_h*2.1)), 1)
    
    bird_surface.blit(wing2_surf, (int(wing2_x-wing2_w*1.05), int(wing2_y-wing2_h*1.05)))
    
    # ==== 6) OCCHIO ====
    eye_x = center_x + int(game.player_size * 0.36)
    eye_y = center_y - int(game.player_size * 0.29)
    eye_size = 11
    
    pygame.draw.circle(bird_surface, (255, 240, 235), (eye_x, eye_y), eye_size+1)
    pygame.draw.circle(bird_surface, (255,255,255), (eye_x, eye_y), eye_size)
    
    iris_size = 7
    pygame.draw.circle(bird_surface, (160, 220, 255), (eye_x+1, eye_y-1), iris_size)
    pygame.draw.circle(bird_surface, (120, 200, 240), (eye_x+1, eye_y-1), iris_size-1)
    
    pupil_offset_x = int(velocity * 0.25) + int(math.sin(time*5)*0.8)
    pupil_offset_y = int(rise_factor * (-1.2))
    pupil_x, pupil_y = eye_x + pupil_offset_x, eye_y + pupil_offset_y
    pygame.draw.circle(bird_surface, (30, 30, 70), (pupil_x, pupil_y), 4)
    pygame.draw.circle(bird_surface, (255,255,255), (pupil_x-1, pupil_y-1), 2)
    pygame.draw.circle(bird_surface, (240, 245, 255), (pupil_x+1, pupil_y), 2)
    
    pygame.draw.circle(bird_surface, (100, 80, 140), (eye_x, eye_y), eye_size, 2)
    
    # ==== 7) BECCO ====
    beak_size = game.player_size * 0.55
    beak_pts = [
        (center_x + int(beak_size * 1.85), center_y - int(beak_size * 0.75)),
        (center_x + int(beak_size * 3.2), center_y + int(velocity * 0.1)),
        (center_x + int(beak_size * 1.85), center_y + int(beak_size * 0.75))
    ]
    
    beak_shadow = [(px+1, py+1) for px, py in beak_pts]
    pygame.draw.polygon(bird_surface, (180, 100, 35), beak_shadow)
    pygame.draw.polygon(bird_surface, NEON_ORANGE, beak_pts)
    
    hl_pts = [(px*0.92 + center_x*0.08, py*0.94 + center_y*0.06) for px, py in beak_pts]
    pygame.draw.polygon(bird_surface, (255, 255, 0, 160), hl_pts)
    pygame.draw.aalines(bird_surface, NEON_YELLOW, True, beak_pts, 1)
    
    # ==== 8) RENDER FINALE ====
    rotated = pygame.transform.rotate(bird_surface, -angle)
    rot_rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rot_rect)
























def draw_player_original(x, y, velocity, color=NEON_CYAN):
    """Player con alone morbido, coda triangolo piumosa e occhio dolce, ottimizzato"""
    angle = np.clip(velocity * 3.5, -40, 85)

    bird_size = game.player_size * 3
    surf_size = int(bird_size * 2.2)
    bird_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    center_x = center_y = surf_size // 2

    # ==== 1) ALONE SFUMATO UNIFORME ====
    glow_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    max_radius = int(game.player_size * 2.0)
    for r in range(max_radius, 0, -1):
        t = r / max_radius
        alpha = int(130 * t * t)
        if alpha <= 0:
            continue
        glow_color = (color[0], color[1], color[2], alpha)
        pygame.draw.circle(glow_surface, glow_color, (center_x, center_y), r)
    bird_surface.blit(glow_surface, (0, 0))

    # ==== 2) CODA TRIANGOLO MORBIDA, ACCORCIATA E DINAMICA ====
    tail_attach_x = center_x - game.player_size
    tail_attach_y = center_y

    # apertura in base a quanto sale (velocity < 0)
    rise_factor = max(0.0, min(1.0, -velocity / 10.0))
    flap = game.player_size * 0.38 * rise_factor

    # piccola oscillazione
    wave = math.sin(pygame.time.get_ticks() / 200.0) * game.player_size * 0.08

    base_x = tail_attach_x - game.player_size * 0.85
    base_top = (
        base_x,
        tail_attach_y - game.player_size * 0.45 - flap * 0.3 + wave * 0.3,
    )
    base_bottom = (
        base_x,
        tail_attach_y + game.player_size * 0.45 + flap + wave * 0.3,
    )
    tip = (tail_attach_x, tail_attach_y)
    tail_tri = [base_top, base_bottom, tip]

    # colore principale coda (mix corpo + verde)
    tail_main_color = (
        int((color[0] + NEON_GREEN[0]) * 0.5),
        int((color[1] + NEON_GREEN[1]) * 0.5),
        int((color[2] + NEON_GREEN[2]) * 0.5),
    )
    tail_light_color = (
        min(255, int(tail_main_color[0] * 1.1)),
        min(255, int(tail_main_color[1] * 1.1)),
        min(255, int(tail_main_color[2] * 1.1)),
    )

    # ombra coda
    shadow_tri = [(int(px + 2), int(py + 2)) for (px, py) in tail_tri]
    pygame.draw.polygon(bird_surface, (15, 10, 30, 140), shadow_tri)

    # triangolo principale
    pygame.draw.polygon(bird_surface, tail_main_color, [(int(px), int(py)) for px, py in tail_tri])

    # spina centrale
    spine_points = [
        (
            int((base_top[0] + base_bottom[0]) * 0.5),
            int((base_top[1] + base_bottom[1]) * 0.5),
        ),
        (int(tip[0]), int(tip[1])),
    ]
    pygame.draw.aalines(bird_surface, tail_light_color, False, spine_points, 2)

    # bordo esterno
    pygame.draw.aalines(
        bird_surface,
        tail_light_color,
        True,
        [(int(px), int(py)) for px, py in tail_tri],
        1,
    )

    # raccordo tondo tra corpo e coda
    pygame.draw.circle(
        bird_surface, tail_main_color, (int(tail_attach_x), int(tail_attach_y)), 4
    )

    # ==== 3) CORPO ====
    pygame.draw.circle(bird_surface, color, (center_x, center_y), game.player_size)
    pygame.draw.circle(bird_surface, WHITE, (center_x, center_y), game.player_size, 3)
    pygame.draw.circle(
        bird_surface, color, (center_x, center_y), game.player_size - 1, 2
    )

    # ==== 4) OMBRA SOTTO ====
    shadow_surf = pygame.Surface((game.player_size * 2, game.player_size), pygame.SRCALPHA)
    shadow_alpha = min(80, 45 + int(abs(velocity) * 6))
    pygame.draw.ellipse(
        shadow_surf,
        (0, 0, 0, shadow_alpha),
        (0, 0, game.player_size * 2, game.player_size),
    )
    s_off = int(velocity * 0.4)
    bird_surface.blit(
        shadow_surf,
        (center_x - game.player_size + s_off,
         center_y - game.player_size // 2 + 4),
    )





    # ==== 5) ALA PERFETTA - SFONDO TRASPARENTE + ALA SOLIDA ====

    flap_time = pygame.time.get_ticks() / 90.0
    wing_flap = int(game.player_size * 0.35 * math.sin(flap_time))

    wing_x = center_x - int(game.player_size * 0.72)
    wing_y = center_y + wing_flap

    # SINGOLO COLORE SCURO
    DARK_WING_GREEN = (35, 180, 10)

    wing_w = game.player_size // 2 + 4
    wing_h = game.player_size // 3 + 3

    # Superficie TRASPARENTE (SRCALPHA per sfondo)
    wing_surf = pygame.Surface((wing_w * 2 + 6, wing_h * 2 + 6), pygame.SRCALPHA)

    # 🔹 LAYER 1: BORDO NERO (solo contorno)
    pygame.draw.ellipse(wing_surf, (0, 0, 0), 
                    (1, 1, wing_w * 2 + 2, wing_h * 2 + 2), 2)

    # 🔹 LAYER 2: ALA SOLIDA (colore pieno)
    pygame.draw.ellipse(wing_surf, DARK_WING_GREEN, 
                    (3, 3, wing_w * 2 - 2, wing_h * 2 - 2))

    # 🔹 LAYER 3: SFUMATURA CENTRALE
    dark_center = (25, 140, 8)
    pygame.draw.ellipse(wing_surf, dark_center, 
                    (wing_w // 2 + 3, wing_h // 2 + 3, wing_w * 1.2 - 4, wing_h * 1.2 - 4))

    # 🔹 POSIZIONAMENTO
    bird_surface.blit(wing_surf, (wing_x - wing_w - 1, wing_y - wing_h - 1))













    # ==== 6) OCCHIO DOLCE ====
    eye_x = center_x + int(game.player_size * 0.35)
    eye_y = center_y - int(game.player_size * 0.28)

    pygame.draw.circle(bird_surface, (255, 225, 245), (eye_x, eye_y), 10)
    pygame.draw.circle(bird_surface, WHITE, (eye_x, eye_y), 9)

    iris_color = (140, 210, 255)
    pygame.draw.circle(bird_surface, iris_color, (eye_x, eye_y), 6)

    pupil_offset_x = int(velocity * 0.22)
    pupil_x = eye_x + pupil_offset_x
    pygame.draw.circle(bird_surface, (25, 25, 60), (pupil_x, eye_y), 4)
    pygame.draw.circle(bird_surface, WHITE, (pupil_x - 2, eye_y - 2), 2)
    pygame.draw.circle(bird_surface, (235, 235, 255), (pupil_x + 1, eye_y + 1), 2)

    pygame.draw.circle(bird_surface, (90, 70, 120), (eye_x, eye_y), 10, 2)

    # ==== 7) BECCO ====
    beak_pts = [
        (center_x + game.player_size - 1, center_y - 4),
        (center_x + game.player_size + 11, center_y),
        (center_x + game.player_size - 1, center_y + 4),
    ]
    beak_shadow = [(px + 1, py + 1) for (px, py) in beak_pts]
    pygame.draw.polygon(bird_surface, (170, 90, 25), beak_shadow)
    pygame.draw.polygon(bird_surface, NEON_ORANGE, beak_pts)
    pygame.draw.aalines(bird_surface, NEON_YELLOW, True, beak_pts, 1)

    # ==== 8) ROTAZIONE E BLIT ====
    rotated = pygame.transform.rotate(bird_surface, -angle)
    rot_rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rot_rect)


def draw_player_2(x, y, velocity, color=NEON_GREEN):   
    angle = max(-30, min(60, velocity * 4))
    player_size = game.player_size * 1.4
    
    surf_size = int(player_size * 5.2)
    bird_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    center_x = center_y = surf_size // 2
    
    current_time = pygame.time.get_ticks()
    
    # ==== 1) GLOW PROFONDO ====
    glow_max_radius = int(player_size * 2.1)
    for r in range(glow_max_radius, 0, -2):
        alpha = int(160 * (r / glow_max_radius) ** 2.4)
        if alpha > 10:
            pygame.draw.circle(bird_surface, (*color, alpha), (center_x, center_y), r)
    
    # ==== 2) CODA 3D - 4 PIUME ====
    tail_pivot_x = center_x - player_size * 0.65
    tail_pivot_y = center_y
    
    # Piuma 1 SUPERIORE
    tail1_pts = [
        (tail_pivot_x - player_size * 0.72, tail_pivot_y - player_size * 0.58),
        (tail_pivot_x + player_size * 0.10, tail_pivot_y - player_size * 0.38),
        (tail_pivot_x - player_size * 0.28, tail_pivot_y + player_size * 0.05)
    ]
    pygame.draw.polygon(bird_surface, (0, 0, 0), tail1_pts, 4)
    pygame.draw.polygon(bird_surface, (12, 135, 2), tail1_pts)
    pygame.draw.aalines(bird_surface, (35, 170, 15), False, 
                       [tail1_pts[0], (tail1_pts[0][0]*0.5+tail1_pts[1][0]*0.5, tail1_pts[0][1]*0.5+tail1_pts[1][1]*0.5)], 2)
    
    # Piuma 2 MEDIA-SINISTRA
    tail2_pts = [
        (tail_pivot_x - player_size * 0.68, tail_pivot_y - player_size * 0.15),
        (tail_pivot_x + player_size * 0.20, tail_pivot_y + player_size * 0.08),
        (tail_pivot_x - player_size * 0.25, tail_pivot_y + player_size * 0.38)
    ]
    pygame.draw.polygon(bird_surface, (0, 0, 0), tail2_pts, 4)
    pygame.draw.polygon(bird_surface, (22, 150, 8), tail2_pts)
    pygame.draw.aalines(bird_surface, (40, 180, 20), False, 
                       [tail2_pts[0], (tail2_pts[0][0]*0.5+tail2_pts[1][0]*0.5, tail2_pts[0][1]*0.5+tail2_pts[1][1]*0.5)], 2)
    
    # Piuma 3 MEDIA-DESTRA
    tail3_pts = [
        (tail_pivot_x - player_size * 0.62, tail_pivot_y + player_size * 0.10),
        (tail_pivot_x + player_size * 0.28, tail_pivot_y + player_size * 0.25),
        (tail_pivot_x - player_size * 0.18, tail_pivot_y + player_size * 0.50)
    ]
    pygame.draw.polygon(bird_surface, (0, 0, 0), tail3_pts, 4)
    pygame.draw.polygon(bird_surface, (28, 160, 10), tail3_pts)
    pygame.draw.aalines(bird_surface, (50, 190, 25), False, 
                       [tail3_pts[0], (tail3_pts[0][0]*0.5+tail3_pts[1][0]*0.5, tail3_pts[0][1]*0.5+tail3_pts[1][1]*0.5)], 2)
    
    # Piuma 4 INFERIORE
    tail4_pts = [
        (tail_pivot_x - player_size * 0.75, tail_pivot_y + player_size * 0.40),
        (tail_pivot_x + player_size * 0.15, tail_pivot_y + player_size * 0.28),
        (tail_pivot_x - player_size * 0.42, tail_pivot_y + player_size * 0.62)
    ]
    pygame.draw.polygon(bird_surface, (0, 0, 0), tail4_pts, 4)
    pygame.draw.polygon(bird_surface, (35, 175, 12), tail4_pts)
    pygame.draw.aalines(bird_surface, (60, 200, 30), False, 
                       [tail4_pts[0], (tail4_pts[0][0]*0.5+tail4_pts[1][0]*0.5, tail4_pts[0][1]*0.5+tail4_pts[1][1]*0.5)], 2)
    
    # ==== 3) CORPO ====
    body_radius = int(player_size * 0.98)
    pygame.draw.circle(bird_surface, (8, 90, 0), (center_x + 2, center_y + 3), body_radius + 1)
    pygame.draw.circle(bird_surface, color, (center_x, center_y), body_radius)
    pygame.draw.circle(bird_surface, (0, 0, 0), (center_x, center_y), body_radius, 3)
    pygame.draw.circle(bird_surface, (*color, 220), 
                      (center_x - int(player_size * 0.35), center_y - int(player_size * 0.2)), 
                      int(body_radius * 0.65))
    pygame.draw.circle(bird_surface, color, (center_x, center_y), body_radius - 2, 1)
    
    # ==== 4) ALA BIOMECCANICA ====
    flap_time = current_time * 0.0080
    flap_progress = (math.sin(flap_time) + 1) / 2
    
    if flap_progress < 0.7:
        wing_angle = math.sin(flap_progress * math.pi * 0.714) * 32
    else:
        wing_angle = 32 - (flap_progress - 0.7) * 32 * 3.33
    
    wing_center_x = center_x - int(player_size * 0.38)
    wing_center_y = center_y + int(player_size * 0.22)
    
    wing_w = int(player_size * 0.82)
    wing_h = int(player_size * 0.50)
    
    wing_surf = pygame.Surface((wing_w * 2 + 4, wing_h * 2 + 4), pygame.SRCALPHA)
    
    pygame.draw.ellipse(wing_surf, (0, 0, 0), (1, 1, wing_w * 2 + 2, wing_h * 2 + 2), 3)
    pygame.draw.ellipse(wing_surf, (42, 188, 18), (4, 4, wing_w * 2 - 4, wing_h * 2 - 4))
    pygame.draw.ellipse(wing_surf, (28, 165, 8), 
                       (wing_w // 2 + 2, wing_h // 2 + 2, wing_w * 0.9, wing_h * 0.9))
    pygame.draw.ellipse(wing_surf, (60, 210, 35), 
                       (6, 6, wing_w * 1.5, wing_h * 0.7), 2)
    
    rotated_wing = pygame.transform.rotate(wing_surf, -wing_angle)
    wing_rect = rotated_wing.get_rect(center=(wing_center_x, wing_center_y))
    bird_surface.blit(rotated_wing, wing_rect.topleft)
    
    # ==== 5) BECCO 3D ====
    beak_height = int(body_radius * 0.66)
    
    beak_pts = [
        (int(center_x + player_size * 0.52), int(center_y - beak_height * 0.32)),
        (int(center_x + player_size * 1.62), int(center_y)),
        (int(center_x + player_size * 0.52), int(center_y + beak_height * 0.32))
    ]
    
    shadow_beak = [(int(p[0] + 2), int(p[1] + 2)) for p in beak_pts]
    pygame.draw.polygon(bird_surface, (100, 80, 10), shadow_beak)
    
    pygame.draw.polygon(bird_surface, (0, 0, 0), beak_pts, 3)
    pygame.draw.polygon(bird_surface, (255, 175, 45), beak_pts)
    
    beak_top_mid = ((beak_pts[0][0] + beak_pts[1][0]) // 2, 
                    (beak_pts[0][1] + beak_pts[1][1]) // 2)
    beak_bot_mid = ((beak_pts[2][0] + beak_pts[1][0]) // 2, 
                    (beak_pts[2][1] + beak_pts[1][1]) // 2)
    
    shade_pts = [beak_pts[1], beak_bot_mid, beak_top_mid]
    pygame.draw.polygon(bird_surface, (220, 125, 15), shade_pts)
    
    pygame.draw.aalines(bird_surface, (255, 200, 80), False, [beak_pts[0], beak_pts[2]], 1)
    
    # ==== 6) OCCHIO ====
    eye_x = int(center_x + player_size * 0.33)
    eye_y = int(center_y - player_size * 0.32)
    
    pygame.draw.circle(bird_surface, (255, 255, 255), (eye_x, eye_y), 11)
    pygame.draw.circle(bird_surface, (0, 0, 0), (eye_x, eye_y), 11, 2)
    
    iris_shift = min(max(velocity * 0.20, -4), 4)
    iris_x = int(eye_x + iris_shift)
    
    pygame.draw.circle(bird_surface, (100, 195, 255), (iris_x, eye_y), 6)
    pygame.draw.circle(bird_surface, (30, 40, 120), (iris_x + 1, eye_y), 3)
    pygame.draw.circle(bird_surface, (255, 255, 255), (iris_x + 3, eye_y - 2), 2)
    pygame.draw.circle(bird_surface, (200, 220, 255), (iris_x + 2, eye_y - 1), 1)
    pygame.draw.circle(bird_surface, (0, 0, 0, 80), (eye_x + 1, eye_y + 2), 12, 1)
    
    # ==== 7) OMBRA DINAMICA ====
    shadow_surf = pygame.Surface((int(player_size * 2.3), int(player_size)), pygame.SRCALPHA)
    shadow_alpha = min(80, 40 + int(abs(velocity) * 6))
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), 
                       (0, 0, int(player_size * 2.3), int(player_size)))
    
    shadow_offset_x = int(velocity * 0.35)
    shadow_pos_x = int(center_x - player_size * 1.15 + shadow_offset_x)
    shadow_pos_y = int(center_y - player_size // 2 + 6)
    
    bird_surface.blit(shadow_surf, (shadow_pos_x, shadow_pos_y))
    
    # ==== 8) ROTAZIONE FINALE ====
    rotated = pygame.transform.rotate(bird_surface, -angle)
    rot_rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rot_rect)










def reset_celestial_objects():
    """Reset completo degli oggetti celesti"""
    if hasattr(game, 'celestial_objects'):
        delattr(game, 'celestial_objects')
    print("✓ Sfondo resettato - Pianeti randomizzati")







# ============================================
# CACHE PIANETI GLOBALE (DEVE ESSERE PRIMA DELLA FUNZIONE)
# ============================================
# Cache globale (assicurati sia definita globalmente)
planet_cache = {}









def draw_planet_cached(screen, x, y, radius, base_color, planet_type='rocky', alpha=255):
    """
    Pianeta scuro con texture, shading morbido e anelli. Supporta alpha per transizioni.
    """
    import pygame, math, random

    radius = max(1, int(radius))
    base_color = tuple(int(max(0, min(255, c))) for c in base_color)
    cache_key = f"{planet_type}_{radius}_{base_color}_vDarkNoGlow_v5"

    if cache_key not in planet_cache:
        surf_size = radius * 6
        center = surf_size // 2
        final_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

        # COLORI BASE SCURI
        r, g, b = base_color
        r = max(0, min(255, int(r * 0.65)))
        g = max(0, min(255, int(g * 0.65)))
        b = max(0, min(255, int(b * 0.65)))
        avg = (r + g + b) / 3
        r = int(r * 0.85 + avg * 0.15)
        g = int(g * 0.85 + avg * 0.15)
        b = int(b * 0.85 + avg * 0.15)

        col_base = (r, g, b)
        col_shadow = (max(0, r-75), max(0, g-75), max(0, b-75))
        col_light = (min(255, r+30), min(255, g+30), min(255, b+30))

        tex_size = radius * 2
        texture = pygame.Surface((tex_size, tex_size), pygame.SRCALPHA)
        seed = hash(cache_key) % 100000

        # TEXTURE PER TIPO
        if planet_type == 'gas_giant':
            texture.fill(col_base)
            for yy in range(tex_size):
                norm_y = yy / tex_size
                wave = math.sin(norm_y * 10 + seed) * 0.20 + math.sin(norm_y * 30) * 0.10
                factor = 0.95 + wave * 0.4
                line_color = (min(255, max(0, int(r * factor))), min(255, max(0, int(g * factor))), min(255, max(0, int(b * factor))))
                pygame.draw.line(texture, line_color, (0, yy), (tex_size, yy))
            if seed % 3 == 0:
                spot_y = int(tex_size * 0.6)
                spot_r = radius // 3
                pygame.draw.ellipse(texture, col_shadow, (radius - spot_r, spot_y - spot_r//2, spot_r*2, spot_r))

        elif planet_type == 'rocky':
            texture.fill(col_base)
            for i in range(4):
                noise_r = radius // 2 + (seed + i*13) % (radius // 2 + 4)
                nx = (seed * i * 37) % tex_size
                ny = (seed * i * 97) % tex_size
                noise_col = col_shadow if i % 2 == 0 else col_light
                pygame.draw.circle(texture, (*noise_col, 45), (nx, ny), noise_r)

            band_h = max(2, radius // 5)
            band_y = radius - band_h // 2
            band_col = (min(255, col_light[0] + 10), min(255, col_light[1] + 10), min(255, col_light[2] + 10))
            pygame.draw.rect(texture, (*band_col, 65), (0, band_y, tex_size, band_h))

            random.seed(seed + 1234)
            for _ in range(4):
                sx = random.randint(int(radius * 1.0), tex_size - 3)
                sy = random.randint(3, tex_size - 3)
                pygame.draw.circle(texture, (235, 235, 235, 120), (sx, sy), 1)
                pygame.draw.circle(texture, (230, 230, 230, 60), (sx, sy), 2, 1)

            random.seed(seed + 4321)
            for _ in range(2):
                fx1 = random.randint(int(radius * 0.2), int(radius * 1.1))
                fy1 = random.randint(int(radius * 0.2), int(tex_size * 0.9))
                fx2 = fx1 + random.randint(radius // 3, radius)
                fy2 = fy1 + random.randint(-radius // 4, radius // 4)
                pygame.draw.line(texture, (15, 10, 18, 140), (fx1, fy1), (fx2, fy2), 1)

        elif planet_type == 'ice':
            texture.fill((175, 210, 230))
            for i in range(7):
                p1 = (random.randint(0, tex_size), random.randint(0, tex_size))
                p2 = (random.randint(0, tex_size), random.randint(0, tex_size))
                pygame.draw.line(texture, (90, 130, 180, 180), p1, p2, 1)
            cap_h = int(tex_size * 0.25)
            cap = pygame.Surface((tex_size, cap_h), pygame.SRCALPHA)
            cap.fill((225, 235, 245, 190))
            texture.blit(cap, (0, 0))

        else:
            texture.fill(col_base)

        # MASCHERA + SHADING
        mask = pygame.Surface((tex_size, tex_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
        texture.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        shadow_layer = pygame.Surface((tex_size, tex_size), pygame.SRCALPHA)
        shadow_offset = int(radius * 0.4)
        pygame.draw.circle(shadow_layer, (0, 0, 0, 90), (radius + shadow_offset, radius + shadow_offset), radius)
        highlight_pos = (int(radius * 0.58), int(radius * 0.58))
        pygame.draw.circle(shadow_layer, (255, 255, 255, 22), highlight_pos, radius // 3)
        shadow_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        texture.blit(shadow_layer, (0, 0))

        rim_layer = pygame.Surface((tex_size, tex_size), pygame.SRCALPHA)
        pygame.draw.circle(rim_layer, (255, 255, 255, 35), (radius, radius), radius - 1, 1)
        rim_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        texture.blit(rim_layer, (0, 0))

        planet_rect = texture.get_rect(center=(center, center))

        # ANELLI
        has_rings = planet_type in ('saturn', 'ringed')
        if has_rings:
            ring_color_base = (max(0, int(col_base[0] * 0.8)), max(0, int(col_base[1] * 0.8)), max(0, int(col_base[2] * 0.8)))
            rings = [(radius * 1.6, radius * 1.8), (radius * 2.0, radius * 2.2)] if planet_type == 'ringed' else [(radius * 1.5, radius * 2.4)]

            rings_back = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            rings_front = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            tilt = 0.26 + min(0.06, radius * 0.0018)

            for r_in, r_out in rings:
                w_ring = int(r_out * 2.3)
                h_ring = int(w_ring * tilt)
                cx, cy = center, center
                num_bands = 7
                step = (r_out - r_in) / num_bands

                for b in range(num_bands):
                    cr = r_in + b * step
                    cw = int(cr * 2.3)
                    ch = int(cw * tilt)
                    band_t = b / max(1, num_bands - 1)
                    rc = int(ring_color_base[0] * (0.9 + 0.1 * band_t))
                    gc = int(ring_color_base[1] * (0.9 + 0.1 * band_t))
                    bc = int(ring_color_base[2] * (0.9 + 0.1 * band_t))
                    a = 145 if b % 2 == 0 else 90
                    offset_x = cx - cw // 2
                    offset_y = cy - ch // 2
                    rect = (offset_x, offset_y, cw, ch)

                    pygame.draw.ellipse(rings_back, (rc, gc, bc, a), rect, 1)
                    pygame.draw.ellipse(rings_front, (rc, gc, bc, a), rect, 1)

            final_surf.blit(rings_back, (0, 0))

        final_surf.blit(texture, planet_rect.topleft)

        if has_rings:
            front_mask = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            pygame.draw.rect(front_mask, (255, 255, 255, 255), (0, center, surf_size, surf_size - center))
            rings_front.blit(front_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            final_surf.blit(rings_front, (0, 0))

        planet_cache[cache_key] = final_surf

    # BLIT CON ALPHA
    surf = planet_cache[cache_key]
    if alpha < 255:
        surf = surf.copy()
        surf.set_alpha(alpha)
    screen.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))














def draw_blood_background():
    scr_h = screen.get_height()
    scr_w = screen.get_width()
    
    # 1. MUSICA CHIPTUNE HORROR OTTIMIZZATA (non blocca più il gioco)
    if not hasattr(game, 'blood_music_playing'):
        sample_rate = 22050
        full_samples = []
        
        # Melodia horror semplificata (ottava più bassa, più atmosferica)
        melody_notes = [
            130.81,  # Do3
            155.56,  # Mib3
            174.61,  # Fa3
            146.83,  # Re3
            130.81,  # Do3
            116.54,  # Si2
            103.83,  # Lab2
            130.81,  # Do3
        ]
        
        # DURATA RIDOTTA: 0.4 secondi per nota invece di 5!
        note_duration = 0.4
        
        # Loop breve ma efficace (circa 3.2 secondi totali)
        for note in melody_notes:
            samples_per_note = int(sample_rate * note_duration)
            for i in range(samples_per_note):
                t = i / sample_rate
                
                # Square wave principale (duty cycle 25% per suono più pieno)
                phase = (t * note) % 1.0
                square = 0.6 if phase < 0.25 else -0.3
                
                # Sub-bass (un'ottava sotto)
                sub_phase = (t * note * 0.5) % 1.0
                sub = 0.3 if sub_phase < 0.3 else -0.15
                
                # Drone atmosferico continuo (molto grave)
                drone = math.sin(2 * math.pi * 65.41 * t) * 0.15
                
                # Envelope: attack rapido, decay medio
                if t < 0.02:
                    envelope = t / 0.02  # Attack 20ms
                else:
                    envelope = math.exp(-(t - 0.02) * 2.5)  # Decay
                
                # Mix dei segnali
                wave = (square * 0.5 + sub * 0.3 + drone) * envelope
                
                # Clipping sicuro e conversione
                sample = int(127 + max(-120, min(120, wave * 80)))
                full_samples.append(sample)
        
        # Crea il sound buffer
        sound_buffer = bytearray(full_samples)
        horror_melody = pygame.mixer.Sound(buffer=sound_buffer)
        
        # Play in loop su canale dedicato
        channel = pygame.mixer.Channel(1)
        channel.play(horror_melody, -1)  # -1 = loop infinito
        channel.set_volume(0.22)  # Volume ridotto per non coprire SFX
        
        game.blood_horror_channel = channel
        game.blood_music_playing = True
    
    # 2. INIZIALIZZAZIONE GRAFICA (una sola volta)
    if not hasattr(game, 'blood_initialized'):
        # Sfondo gradiente rosso scuro
        game.blood_bg_surface = pygame.Surface((scr_w, scr_h))
        for y in range(scr_h):
            r = int(12 * (y / scr_h))
            pygame.draw.line(game.blood_bg_surface, (r + 2, 0, 0), (0, y), (scr_w, y))
        
        # TESCHIO COMPLETO
        game.skull_surf = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        bone = (45, 35, 30, 255)
        dark = (20, 10, 10, 255)
        edge = (70, 55, 50, 255)
        cx, cy = scr_w // 2, scr_h // 2
        
        # Cranio principale
        pygame.draw.ellipse(game.skull_surf, bone, (cx-250, cy-220, 500, 380))
        pygame.draw.ellipse(game.skull_surf, bone, (cx-280, cy-180, 560, 320), 15)
        pygame.draw.arc(game.skull_surf, bone, (cx-200, cy-250, 400, 200), 0, math.pi, 30)
        pygame.draw.ellipse(game.skull_surf, bone, (cx-260, cy-100, 100, 120))
        pygame.draw.ellipse(game.skull_surf, bone, (cx+160, cy-100, 100, 120))
        
        # Occhi
        pygame.draw.ellipse(game.skull_surf, dark, (cx-160, cy-100, 100, 80))
        pygame.draw.ellipse(game.skull_surf, dark, (cx+60, cy-100, 100, 80))
        pygame.draw.ellipse(game.skull_surf, edge, (cx-160, cy-100, 100, 80), 5)
        pygame.draw.ellipse(game.skull_surf, edge, (cx+60, cy-100, 100, 80), 5)
        
        # Naso
        nose_points = [(cx-10, cy-40), (cx-50, cy+30), (cx, cy+60), (cx+50, cy+30)]
        pygame.draw.polygon(game.skull_surf, dark, nose_points)
        pygame.draw.polygon(game.skull_surf, edge, nose_points, 4)
        
        # Zigomi
        pygame.draw.arc(game.skull_surf, bone, (cx-220, cy-20, 200, 180), 0, math.pi, 25)
        pygame.draw.arc(game.skull_surf, bone, (cx+20, cy-20, 200, 180), 0, math.pi, 25)
        
        # Mascella
        pygame.draw.arc(game.skull_surf, bone, (cx-220, cy+20, 440, 240), 0, math.pi, 35)
        pygame.draw.rect(game.skull_surf, bone, (cx-160, cy+120, 320, 100), border_radius=40)
        
        # Denti superiori
        for i in range(12):
            x = cx - 170 + i*30
            points = [(x-10, cy+20), (x+10, cy+20), (x, cy+60)]
            pygame.draw.polygon(game.skull_surf, bone, points)
            pygame.draw.polygon(game.skull_surf, edge, points, 2)
        
        # Denti inferiori
        for i in range(10):
            x = cx - 140 + i*35
            points = [(x-15, cy+130), (x+15, cy+130), (x, cy+180)]
            pygame.draw.polygon(game.skull_surf, bone, points)
            pygame.draw.polygon(game.skull_surf, edge, points, 2)
        
        # Dettagli oscuri
        pygame.draw.ellipse(game.skull_surf, dark, (cx-100, cy+140, 200, 80))
        pygame.draw.line(game.skull_surf, dark, (cx-200, cy+50), (cx-150, cy+100), 20)
        pygame.draw.line(game.skull_surf, dark, (cx+150, cy+100), (cx+200, cy+50), 20)
        
        # Ritaglio occhi e naso (blend sottrattivo)
        holes_surf = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        pygame.draw.ellipse(holes_surf, (255,255,255,255), (cx-160, cy-100, 100, 80))
        pygame.draw.ellipse(holes_surf, (255,255,255,255), (cx+60, cy-100, 100, 80))
        pygame.draw.polygon(holes_surf, (255,255,255,255), nose_points)
        game.skull_surf.blit(holes_surf, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
        
        # Particelle di sangue (3 layer di pioggia)
        game.rain_layers = []
        game.rain_layers.append([{
            'x': random.randint(0, scr_w), 
            'y': random.randint(-scr_h, scr_h), 
            'speed': random.uniform(5, 8), 
            'len': random.randint(5, 10), 
            'width': 1, 
            'color': (110, 10, 10)
        } for _ in range(60)])
        
        game.rain_layers.append([{
            'x': random.randint(0, scr_w), 
            'y': random.randint(-scr_h, scr_h), 
            'speed': random.uniform(11, 16), 
            'len': random.randint(12, 22), 
            'width': 2, 
            'color': (180, 30, 30)
        } for _ in range(35)])
        
        game.rain_layers.append([{
            'x': random.randint(0, scr_w), 
            'y': random.randint(-scr_h, scr_h), 
            'speed': random.uniform(19, 26), 
            'len': random.randint(25, 45), 
            'width': 3, 
            'color': (240, 60, 60)
        } for _ in range(18)])
        
        # Lacrime di sangue verticali
        game.blood_tears = []
        for col in [scr_w//6, scr_w//2, scr_w*5//6]:
            for _ in range(3):
                game.blood_tears.append({
                    'fixed_x': col, 
                    'start_y': random.randint(scr_h//6, scr_h//3),
                    'life': random.randint(300, 600), 
                    'max_life': 0,
                    'length': random.randint(60, 120), 
                    'speed': random.uniform(0.8, 1.8)
                })
        
        game.lightning_timer = 0
        game.lightning_alpha = 0
        game.blood_initialized = True

    # 3. LOGICA FULMINE
    if game.lightning_timer > 0:
        game.lightning_timer -= 1
    else:
        if random.random() < 0.006:
            game.lightning_timer = random.randint(80, 250)
            game.lightning_alpha = random.randint(220, 255)
    
    if game.lightning_alpha > 0:
        game.lightning_alpha -= 10
        if game.lightning_alpha < 0:
            game.lightning_alpha = 0

    # 4. RENDERING
    # Sfondo
    screen.blit(game.blood_bg_surface, (0, 0))
    
    # Teschio (visibile solo durante fulmine)
    if game.lightning_alpha > 30:
        game.skull_surf.set_alpha(min(220, int(game.lightning_alpha * 0.85)))
        screen.blit(game.skull_surf, (0, 0))
    
    # Flash del fulmine
    if game.lightning_alpha > 0:
        flash_surf = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        flash_surf.fill((255, 220, 220, int(game.lightning_alpha * 0.3)))
        screen.blit(flash_surf, (0, 0))
    
    # Pioggia di sangue con effetto vento
    current_time = pygame.time.get_ticks() / 1000.0
    wind_offset = math.sin(current_time) * 2
    
    for layer_idx, layer in enumerate(game.rain_layers):
        for drop in layer:
            drop['y'] += drop['speed']
            drop['x'] += wind_offset * (layer_idx * 0.5)
            
            # Reset goccia se esce dallo schermo
            if drop['y'] > scr_h:
                drop['y'] = random.randint(-60, -10)
                drop['x'] = random.randint(0, scr_w)
                # Splash occasionale per le gocce veloci
                if layer_idx == 2 and random.random() > 0.5:
                    pygame.draw.circle(screen, (200, 50, 50), (int(drop['x']), scr_h - 2), 3)
            
            # Wrap orizzontale
            if drop['x'] > scr_w:
                drop['x'] -= scr_w
            elif drop['x'] < 0:
                drop['x'] += scr_w
            
            # Colore (schiarisce durante fulmine)
            color = drop['color']
            if game.lightning_alpha > 80:
                color = (255, 200, 200)
            
            # Disegna goccia
            pygame.draw.line(screen, color, 
                           (int(drop['x']), int(drop['y'])), 
                           (int(drop['x'] + wind_offset), int(drop['y'] + drop['len'])), 
                           drop['width'])
    
    # Lacrime verticali persistenti
    new_tears = []
    for tear in game.blood_tears:
        tear['max_life'] += 1
        progress = min(1.0, tear['max_life'] / tear['life'])
        current_y = tear['start_y'] + (progress * scr_h * 0.8)
        
        # Fade out verso il basso
        alpha = int(255 * (1.0 - progress * 0.7))
        if alpha < 20:
            continue
        
        # Disegna la lacrima
        length = int(tear['length'] * (1.0 - progress * 0.4))
        for i in range(length):
            fade = i / length
            col_intensity = int(80 * (1.0 - fade) * (alpha / 255))
            width = max(1, int(4 * (1.0 - fade)))
            x_offset = math.sin(i * 0.15 + progress * 10) * 2
            
            pygame.draw.line(screen, (col_intensity, 10, 10), 
                           (int(tear['fixed_x'] + x_offset), int(current_y + i)), 
                           (int(tear['fixed_x'] + x_offset * 0.7), int(current_y + i + 1)), 
                           width)
        
        new_tears.append(tear)
    
    game.blood_tears = new_tears
    
    # Rigenera lacrime terminate
    if len(game.blood_tears) < 6:
        for col in [scr_w//6, scr_w//2, scr_w*5//6]:
            if len(game.blood_tears) < 9:
                game.blood_tears.append({
                    'fixed_x': col, 
                    'start_y': random.randint(scr_h//6, scr_h//3),
                    'life': random.randint(300, 600), 
                    'max_life': 0,
                    'length': random.randint(60, 120), 
                    'speed': random.uniform(0.8, 1.8)
                })









def draw_background_toys():
    scr_h = screen.get_height()
    scr_w = screen.get_width()
    
    # 1. PULIZIA - Cielo blu notte MOLTO più scuro
    top_color = (2, 5, 12)
    bottom_color = (10, 25, 45)
    
    for y in range(0, scr_h, 2):
        progress = y / scr_h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * progress)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * progress)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * progress)
        pygame.draw.rect(screen, (r, g, b), (0, y, scr_w, 2))
    
    # 2. SINTESI TUONO (Una volta sola) - MANTENUTO
    if not hasattr(draw_background_toys, 'thunder_sound'):
        try:
            freq = 44100
            duration = 1.2
            n_samples = int(freq * duration)
            buf = array.array('h', [0] * n_samples)
            
            value = 0
            max_amp = 20000
            
            for i in range(n_samples):
                value += random.randint(-1500, 1500)
                if value > max_amp: value -= 1600
                if value < -max_amp: value += 1600
                env = min(1.0, i / 1000.0) if i < 1000 else 1.0 - ((i - 1000) / (n_samples - 1000))
                buf[i] = int(value * env)
            
            draw_background_toys.thunder_sound = pygame.mixer.Sound(buffer=buf)
            draw_background_toys.thunder_sound.set_volume(0.5)
            draw_background_toys.thunder_channel = pygame.mixer.Channel(0)
        except:
            draw_background_toys.thunder_sound = None

    current_time = pygame.time.get_ticks()
    
    # 3. INIZIALIZZAZIONE FULMINI
    if not hasattr(draw_background_toys, 'lightning_data'):
        draw_background_toys.lightning_data = {
            'active': False,
            'segments': [],
            'flash_time': 0,
            'last_flash': 0,
            'flash_decay': 0,
            'thunder_delay': 0
        }
    
    lightning = draw_background_toys.lightning_data
    
    # Trigger Tempesta (2-6s)
    if current_time - lightning['last_flash'] > random.randint(2000, 6000):
        lightning['last_flash'] = current_time
        lightning['flash_decay'] = 1.0
        lightning['thunder_delay'] = random.randint(200, 800)
        
        # Genera Fulmine ramificato (da top casuale a fondo)
        start_x = random.randint(scr_w//4, scr_w*3//4)
        end_x = random.randint(scr_w//4, scr_w*3//4)
        lightning['segments'] = [(start_x, 0, end_x, scr_h)]
        lightning['active'] = True

    # 4. TUONO DOPO DELAY
    if lightning['thunder_delay'] > 0:
        lightning['thunder_delay'] -= 16
        if lightning['thunder_delay'] <= 0 and draw_background_toys.thunder_sound:
            draw_background_toys.thunder_channel.play(draw_background_toys.thunder_sound)

    # 5. DISEGNA FULMINI CON GLOW MULTI-LAYER
    if lightning['active']:
        glow_intensity = lightning['flash_decay']
        
        # Layer 1-3: Glow blu (multi-spessore)
        for glow_layer in range(3):
            glow_width = int(8 * glow_intensity * (0.4 + glow_layer * 0.2))
            glow_color = (int(100 * glow_intensity), int(150 * glow_intensity), int(255 * glow_intensity))
            
            for seg in lightning['segments']:
                start = (int(seg[0]), int(seg[1]))
                end = (int(seg[2]), int(seg[3]))
                pygame.draw.line(screen, glow_color, start, end, glow_width)
                
                # Rami secondari (30% chance)
                if random.random() < 0.3 and len(seg) == 4:
                    mid_x = (start[0] + end[0]) // 2
                    mid_y = (start[1] + end[1]) // 2
                    branch_end_x = mid_x + random.randint(-80, 80)
                    branch_end_y = mid_y + random.randint(30, 80)
                    pygame.draw.line(screen, glow_color, (mid_x, mid_y), 
                                   (branch_end_x, branch_end_y), glow_width//2)
        
        # Layer 4: Core bianco caldo (spessore 2px)
        core_color = (int(255 * glow_intensity), int(240 * glow_intensity), int(200 * glow_intensity))
        for seg in lightning['segments']:
            start = (int(seg[0]), int(seg[1]))
            end = (int(seg[2]), int(seg[3]))
            pygame.draw.line(screen, core_color, start, end, 2)
        
        # Decay rapido
        lightning['flash_decay'] *= 0.88
        if lightning['flash_decay'] < 0.02:
            lightning['active'] = False

    # 6. FLASH SCHERMO GIGANTE (sopra tutto)
    if lightning['flash_decay'] > 0.1:
        flash_alpha = int(120 * lightning['flash_decay'])
        flash_surf = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, flash_alpha))
        screen.blit(flash_surf, (0, 0))
    
    # 7. SKIPA se livello sangue
    if hasattr(game, 'current_level') and game.current_level >= 20:
        draw_blood_background()
        return





























def draw_background():
    scr_h = screen.get_height()
    scr_w = screen.get_width()

    # 1. PULIZIA
    screen.fill(DARK_BG)
    if game.current_level >= 23:
        draw_blood_background()
        return
    

    if game.current_level >= 20:
        draw_background_toys()
        return

    draw_background_toys
    # 2. LOGICA TRANSIZIONE LEGATA AL SCORE (OGNI PUNTO SFUMA)
    steps_per_transition = 20
    base_index = (game.score // steps_per_transition) % len(CYBERPUNK_PALETTES)
    next_index = (base_index + 1) % len(CYBERPUNK_PALETTES)
    t = (game.score % steps_per_transition) / steps_per_transition

    palette1 = CYBERPUNK_PALETTES[base_index]
    palette2 = CYBERPUNK_PALETTES[next_index]

    # 3. CIELO GRADIENT (INTERPOLATO)
    sky_top = lerp_color(palette1['sky_top'], palette2['sky_top'], t)
    sky_bottom = lerp_color(palette1['sky_bottom'], palette2['sky_bottom'], t)

    step = 4
    for y in range(0, scr_h, step):
        progress = y / scr_h
        color = lerp_color(sky_top, sky_bottom, progress ** 0.8)
        pygame.draw.rect(screen, color, (0, y, scr_w, step))

    scroll_offset = game.score * 2
    current_time = pygame.time.get_ticks()

    # 4. STELLE
    for star in game.stars:
        twinkle = math.sin(current_time * star['twinkle_speed'] * 0.3 + star['twinkle_offset'])
        alpha = int(255 * star['brightness'] * (0.75 + 0.25 * twinkle))
        alpha = max(0, min(255, alpha))
        color = tuple(int(c * alpha / 255) for c in star['color'])
        star_x = int(star['x'])
        star_y = int(star['y'])

        if star['size'] <= 1:
            if 0 <= star_x < scr_w and 0 <= star_y < scr_h:
                screen.set_at((star_x, star_y), color)
        else:
            surf = pygame.Surface((star['size'] * 2, star['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*star['color'], alpha), (star['size'], star['size']), star['size'])
            screen.blit(surf, (star_x - star['size'], star_y - star['size']))

    # 5. SOLE "ECLISSI CYBERPUNK" (INTERPOLATO)
    ground_height = 120
    ground_y = scr_h - ground_height
    sun_radius = int(scr_h * 0.16)
    sun_x = scr_w // 2
    sun_y_pos = ground_y + int(sun_radius * 0.25)

    core1 = palette1.get('nebula', (20, 20, 30))
    core2 = palette2.get('nebula', (20, 20, 30))
    rim1 = palette1.get('sky_bottom', (200, 200, 200))
    rim2 = palette2.get('sky_bottom', (200, 200, 200))

    sun_core_color = lerp_color(core1, core2, t)
    sun_rim_color = lerp_color(rim1, rim2, t)

    glow_radius = int(sun_radius * 1.3)
    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*sun_rim_color, 35), (glow_radius, glow_radius), glow_radius)
    screen.blit(glow_surf, (sun_x - glow_radius, sun_y_pos - glow_radius))

    pygame.draw.circle(screen, sun_core_color, (sun_x, sun_y_pos), sun_radius)
    pygame.draw.circle(screen, sun_rim_color, (sun_x, sun_y_pos), sun_radius, 3)
    inner_ring_radius = int(sun_radius * 0.7)
    inner_ring_color = lerp_color(sun_core_color, sun_rim_color, 0.3)
    pygame.draw.circle(screen, inner_ring_color, (sun_x, sun_y_pos), inner_ring_radius, 1)

    # 6. PIANETI (NO OVERLAP + ANELLI + BLENDING)
    global planet_cache
    if 'planet_cache' not in globals():
        planet_cache = {}

    # *** SPAWN PIANETI CON ANELLI - ZERO SOVRAPPOSIZIONI ***
    if not hasattr(game, 'celestial_objects') or len(game.celestial_objects) == 0:
        game.celestial_objects = []
        random.seed(int(time.time() * 1000))
        planet_types = ['saturn', 'ringed', 'gas_giant', 'rocky', 'ice']
        num_planets = random.randint(3, 5)  # Meno pianeti = più spazio
        
        placed = []  # (x, y, total_radius_con_anelli)
        
        for i in range(num_planets):
            attempts = 0
            placed_success = False
            
            while attempts < 200:  # Più tentativi per precisione
                p_type = random.choice(planet_types)
                base_size = random.randint(22, 48)
                
                # RADIUS TOTALE con anelli (sicurezza 100%)
                ring_multiplier = 2.8 if p_type in ['saturn', 'ringed'] else 1.4
                total_radius = base_size * ring_multiplier
                
                # POSIZIONE con margini ampi
                px = random.uniform(total_radius * 2.5, scr_w - total_radius * 2.5)
                py = random.uniform(total_radius * 2, scr_h * 0.38)  # Più alto
                
                # *** VERIFICA ANTI-SOVRAPPOSIZIONE RIGIDA ***
                safe = True
                for ox, oy, orad in placed:
                    dist = math.sqrt((px - ox)**2 + (py - oy)**2)
                    min_dist = (total_radius + orad) * 1.6  # 60% EXTRA SICUREZZA
                    if dist < min_dist:
                        safe = False
                        break
                
                # NO vicino al player (x=150)
                if abs(px - 150) < total_radius * 3:
                    safe = False
                
                if safe:
                    placed.append((px, py, total_radius))
                    speed = random.uniform(0.008, 0.016) * random.choice([-1, 1])
                    
                    game.celestial_objects.append({
                        'type': 'planet',
                        'x': px,
                        'y': py,
                        'size': base_size,  # Solo base_size per draw_planet_cached
                        'planet_type': p_type,
                        'speed': speed,
                        'color_idx': i % 3,
                        'total_radius': total_radius  # Per future verifiche
                    })
                    placed_success = True
                    break
                
                attempts += 1
            
            if not placed_success:
                print(f"Warning: Pianeta {i+1} scartato dopo 200 tentativi")

    # COLORI PIANETI PER ENTRAMBE LE PALETTE
    def get_planet_colors(pal):
        c1 = pal.get('nebula', (80, 40, 120))
        c2 = pal.get('nebulaaccent', (120, 60, 180))  # Corretto: nebulaaccent
        c3 = ((c1[0]+c2[0])//2, (c1[1]+c2[1])//2, (c1[2]+c2[2])//2)
        return [c1, c2,  c3]

    cols_start = get_planet_colors(palette1)
    cols_end = get_planet_colors(palette2)
    alpha_end = int(t * 255)

    # Disegna pianeti con movimento parallax
    for obj in game.celestial_objects:
        # Movimento infinito
        obj['x'] += obj['speed'] * 0.8
        if obj['x'] < -obj['total_radius'] * 2:
            obj['x'] = scr_w + obj['total_radius'] * 2
        
        obj_x = int(obj['x'] + scroll_offset * obj['speed'] * 0.5)
        obj_y = int(obj['y'])
        idx = obj['color_idx']

        # Palette 1 (base)
        draw_planet_cached(screen, obj_x, obj_y, obj['size'], cols_start[idx], 
                          obj['planet_type'], alpha=255)
        # Palette 2 (overlay sfumato)
        if t > 0.01:
            draw_planet_cached(screen, obj_x, obj_y, obj['size'], cols_end[idx], 
                              obj['planet_type'], alpha=alpha_end)

    # 7. TERRENO (INTERPOLATO)
    ground_top = lerp_color(palette1['ground_top'], palette2['ground_top'], t)
    ground_bottom = lerp_color(palette1['ground_bottom'], palette2['ground_bottom'], t)

    for y in range(0, ground_height, 2):
        progress = y / ground_height
        color = lerp_color(ground_top, ground_bottom, progress ** 0.7)
        pygame.draw.rect(screen, color, (0, ground_y + y, scr_w, 2))







# EQUALIZER - Toggle with E key
def draw_equalizer(level):
    if not game.show_equalizer:
        return
    
    scr_w = screen.get_width()
    scr_h = screen.get_height()
    
    # Dimensioni più compatte
    eq_w = 120
    eq_h = 150
    eq_x = scr_w - eq_w - 15
    eq_y = scr_h - eq_h - 15
    
    num_bars = 6
    bar_width = (eq_w - (num_bars + 1) * 4) // num_bars
    
    # Background più elegante con effetto glass
    bg_surf = pygame.Surface((eq_w, eq_h), pygame.SRCALPHA)
    pygame.draw.rect(bg_surf, (15, 15, 25, 200), (0, 0, eq_w, eq_h), border_radius=10)
    pygame.draw.rect(bg_surf, NEON_CYAN, (0, 0, eq_w, eq_h), 2, border_radius=10)
    
    # Gradiente interno per effetto depth
    for i in range(3):
        alpha = 30 - i * 10
        pygame.draw.rect(bg_surf, (*NEON_CYAN, alpha), 
                        (i+1, i+1, eq_w-2*(i+1), eq_h-2*(i+1)), 
                        border_radius=10-i)
    
    screen.blit(bg_surf, (eq_x, eq_y))
    
    # Titolo compatto
    title_text = font_xs.render("AUDIO", True, NEON_CYAN)
    screen.blit(title_text, (eq_x + eq_w // 2 - title_text.get_width() // 2, eq_y + 8))
    
    bar_area_y = eq_y + 30
    bar_area_h = eq_h - 55
    
    for i in range(num_bars):
        bar_x = eq_x + 6 + i * (bar_width + 4)
        
        # Variazione più fluida
        variation = random.uniform(0.8, 1.0) if level > 0.1 else random.uniform(0.05, 0.2)
        bar_level = min(level * variation, 1.0)
        bar_height = int(bar_area_h * bar_level)
        
        if bar_height < 2:
            bar_height = 2
        
        # Colori più vibranti
        if bar_level < 0.35:
            color_top = (0, 255, 150)
            color_bottom = (0, 100, 50)
        elif bar_level < 0.7:
            color_top = (0, 200, 255)
            color_bottom = (0, 80, 150)
        else:
            color_top = (255, 50, 150)
            color_bottom = (150, 0, 80)
        
        bar_y_start = bar_area_y + bar_area_h - bar_height
        
        # Barre con gradiente smooth
        bar_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        
        for y in range(bar_height):
            progress = y / max(1, bar_height)
            r = int(color_bottom[0] + (color_top[0] - color_bottom[0]) * progress)
            g = int(color_bottom[1] + (color_top[1] - color_bottom[1]) * progress)
            b = int(color_bottom[2] + (color_top[2] - color_bottom[2]) * progress)
            
            pygame.draw.line(bar_surf, (r, g, b), (0, y), (bar_width, y))
        
        screen.blit(bar_surf, (bar_x, bar_y_start))
        
        # Bordo sottile
        pygame.draw.rect(screen, (255, 255, 255, 180), 
                        (bar_x, bar_y_start, bar_width, bar_height), 1, border_radius=2)
        
        # Glow sulla punta solo se la barra è alta
        if bar_level > 0.5:
            glow_surf = pygame.Surface((bar_width + 6, 6), pygame.SRCALPHA)
            glow_alpha = int(150 * (bar_level - 0.5) * 2)
            pygame.draw.ellipse(glow_surf, (*color_top, glow_alpha), 
                              (0, 0, bar_width + 6, 6))
            screen.blit(glow_surf, (bar_x - 3, bar_y_start - 3))
    
    # Linee di riferimento sottili
    for i in range(1, 4):
        line_y = bar_area_y + (bar_area_h // 3) * i
        pygame.draw.line(screen, (60, 60, 80, 100), 
                        (eq_x + 6, line_y), 
                        (eq_x + eq_w - 6, line_y), 1)
    
    # Valore RMS compatto
    rms_text = font_xs.render(f"{current_rms:.2f}", True, (200, 200, 255))
    screen.blit(rms_text, (eq_x + eq_w // 2 - rms_text.get_width() // 2, eq_y + eq_h - 18))
    
    # Indicatore di picco
    if level > 0.85:
        peak_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(peak_surf, (255, 0, 100, 200), (4, 4), 4)
        pygame.draw.circle(peak_surf, (255, 100, 150, 100), (4, 4), 3)
        screen.blit(peak_surf, (eq_x + eq_w - 14, eq_y + 6))















def draw_vignette(surf):
    """Optimized vignette effect"""
    scrw = surf.get_width()
    scrh = surf.get_height()
    
    vignette_surf = pygame.Surface((scrw // 2, scrh // 2), pygame.SRCALPHA)
    center_x, center_y = vignette_surf.get_width() // 2, vignette_surf.get_height() // 2
    max_radius = math.sqrt(center_x**2 + center_y**2)
    
    for radius in range(int(max_radius), 0, -5):
        alpha = int((1 - radius / max_radius) * 100)
        pygame.draw.circle(vignette_surf, (0, 0, 0, alpha), (center_x, center_y), radius)
    
    vignette_scaled = pygame.transform.smoothscale(vignette_surf, (scrw, scrh))
    surf.blit(vignette_scaled, (0, 0))





def draw_menu():
    screen.fill(DARK_BG)
    draw_starfield()
    
    scr_w = screen.get_width()
    scr_h = screen.get_height()
    center_x = scr_w // 2
    
    game.menu_pulse += 0.05
    
    # === TITLE ===
    pulse_scale = 1.0 + math.sin(game.menu_pulse * 2) * 0.03
    title = font_xl.render("VOICE RUNNER", True, NEON_CYAN)
    scaled_w = int(title.get_width() * pulse_scale)
    scaled_h = int(title.get_height() * pulse_scale)
    
    if scaled_w > 0 and scaled_h > 0:
        title_scaled = pygame.transform.scale(title, (scaled_w, scaled_h))
        title_x = center_x - scaled_w // 2
        title_y = 100
        
        # Subtle glow
        glow_surf = pygame.Surface((scaled_w + 30, scaled_h + 30), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*NEON_CYAN, 40), (0, 0, scaled_w + 30, scaled_h + 30), border_radius=15)
        screen.blit(glow_surf, (title_x - 15, title_y - 15))
        screen.blit(title_scaled, (title_x, title_y))
    
    # === SUBTITLE ===
    subtitle = font_sm.render("SYNTH EDITION", True, NEON_MAGENTA)
    sub_y = 170
    screen.blit(subtitle, (center_x - subtitle.get_width() // 2, sub_y))
    
    # === STATUS & ACTION ===
    status_y = 250
    
    if game.calibrated:
        status_text = "READY"
        status_color = NEON_GREEN
        action_text = "PRESS SPACE"
    else:
        status_text = "NOT CALIBRATED"
        status_color = NEON_ORANGE
        action_text = "PRESS SPACE TO CALIBRATE"
    
    # Status
    status_surf = font_sm.render(status_text, True, status_color)
    screen.blit(status_surf, (center_x - status_surf.get_width() // 2, status_y))
    
    # Action with pulse
    action_pulse = 1.0 + math.sin(game.menu_pulse * 4) * 0.08
    action_surf = font_lg.render(action_text, True, WHITE)
    action_w = int(action_surf.get_width() * action_pulse)
    action_h = int(action_surf.get_height() * action_pulse)
    
    if action_w > 0 and action_h > 0:
        action_scaled = pygame.transform.scale(action_surf, (action_w, action_h))
        action_x = center_x - action_w // 2
        action_y = 290
        
        # Subtle glow
        glow_alpha = int(30 + 20 * math.sin(game.menu_pulse * 4))
        glow_surf = pygame.Surface((action_w + 20, action_h + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*WHITE, glow_alpha), (0, 0, action_w + 20, action_h + 20), border_radius=8)
        screen.blit(glow_surf, (action_x - 10, action_y - 10))
        screen.blit(action_scaled, (action_x, action_y))
    
    # === INSTRUCTIONS ===
    instr_y = 380
    
    instructions = [
        "Control with voice - Avoid obstacles",
        "SPACE: Jump/Start  |  C: Calibrate  |  F: Fullscreen"
    ]
    
    for i, text in enumerate(instructions):
        instr_surf = font_xs.render(text, True, GRAY)
        screen.blit(instr_surf, (center_x - instr_surf.get_width() // 2, instr_y + i * 25))
    
    # === DEVELOPER CREDIT ===
    dev_y = 460
    dev_text = "Developed by Indecenti"
    dev_surf = font_xs.render(dev_text, True, NEON_PURPLE)
    
    # Decorative line above credit
    line_length = dev_surf.get_width() + 40
    line_y = dev_y - 8
    line_x_start = center_x - line_length // 2
    line_x_end = center_x + line_length // 2
    pygame.draw.line(screen, NEON_PURPLE, (line_x_start, line_y), (line_x_end, line_y), 1)
    
    screen.blit(dev_surf, (center_x - dev_surf.get_width() // 2, dev_y))
    
    # === HIGH SCORE ===
    hs_y = 550
    
    hs_label = font_sm.render("HIGH SCORE", True, NEON_ORANGE)
    screen.blit(hs_label, (center_x - hs_label.get_width() // 2, hs_y))
    
    hs_value = font_xl.render(f"{game.high_score}", True, WHITE)
    screen.blit(hs_value, (center_x - hs_value.get_width() // 2, hs_y + 40))
    
    # === STATUS BAR (Bottom) ===
    status_bar_y = scr_h - 25
    
    # Mode
    fs_status = "FULLSCREEN" if game.fullscreen else "WINDOWED"
    fs_color = NEON_GREEN if game.fullscreen else DARK_GRAY
    fs_surf = font_xs.render(fs_status, True, fs_color)
    
    # Controller
    if len(joysticks) > 0:
        joy_text = f"CONTROLLER x{len(joysticks)}"
        joy_surf = font_xs.render(joy_text, True, NEON_PURPLE)
        
        total_width = fs_surf.get_width() + 40 + joy_surf.get_width()
        fs_x = center_x - total_width // 2
        joy_x = fs_x + fs_surf.get_width() + 40
        
        screen.blit(fs_surf, (fs_x, status_bar_y))
        screen.blit(joy_surf, (joy_x, status_bar_y))
    else:
        screen.blit(fs_surf, (center_x - fs_surf.get_width() // 2, status_bar_y))
    
    # Vignette
    draw_vignette(screen)















def draw_calibration():
    screen.fill(DARK_BG)
    draw_starfield()
    
    scr_w = screen.get_width()
    scr_h = screen.get_height()
    
    bar_width = 650
    bar_x = scr_w // 2 - bar_width // 2
    bar_y = 420
    
    if game.state == "CALIBRATE_SILENCE":
        color = NEON_GREEN
        phase_text = "PHASE 1: SILENCE"
        desc = "🤫 Don't make any noise for 1.5 seconds..."
        rms_list = game.calib_silence
    else:
        color = NEON_MAGENTA
        phase_text = "PHASE 2: SHOUT!"
        desc = "📢 SCREAM, CLAP, WHISTLE - GO LOUD!"
        rms_list = game.calib_shout
    
    title = font_xl.render(phase_text, True, color)
    screen.blit(title, (scr_w // 2 - title.get_width() // 2, 80))
    
    desc_text = font_md.render(desc, True, WHITE)
    screen.blit(desc_text, (scr_w // 2 - desc_text.get_width() // 2, 180))
    
    # Large RMS display
    rms_display = font_xl.render(f"{current_rms:.4f}", True, color)
    rms_w = rms_display.get_width()
    rms_h = rms_display.get_height()
    
    # Glow effect on RMS
    for r in range(40, 0, -8):
        glow_alpha = int(100 * (1 - r / 40))
        if glow_alpha > 0:
            glow_surf = pygame.Surface((rms_w + r * 2, rms_h + r * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, glow_alpha), 
                           (0, 0, glow_surf.get_width(), glow_surf.get_height()), 
                           border_radius=20)
            screen.blit(glow_surf, (scr_w // 2 - (rms_w + r * 2) // 2, 260 - r))
    
    screen.blit(rms_display, (scr_w // 2 - rms_w // 2, 260))
    
    # Progress bar with enhanced styling
    pygame.draw.rect(screen, DARK_GRAY, (bar_x - 3, bar_y - 3, bar_width + 6, 50), border_radius=8)
    
    progress = game.calib_timer / game.calib_duration
    fill_width = int(bar_width * progress)
    
    # Gradient fill
    for i in range(fill_width):
        t = i / max(1, fill_width)
        grad_color = lerp_color((color[0] // 2, color[1] // 2, color[2] // 2), color, t)
        pygame.draw.line(screen, grad_color, (bar_x + i, bar_y), (bar_x + i, bar_y + 44))
    
    pygame.draw.rect(screen, color, (bar_x, bar_y, bar_width, 44), 3, border_radius=5)
    
    pct = int(100 * progress)
    pct_text = font_lg.render(f"{pct}%", True, WHITE)
    screen.blit(pct_text, (scr_w // 2 - pct_text.get_width() // 2, bar_y + 7))
    
    if rms_list:
        mean_val = np.mean(rms_list)
        max_val = np.max(rms_list)
        stats = font_sm.render(f"Mean: {mean_val:.4f} | Max: {max_val:.4f}", True, GRAY)
        screen.blit(stats, (scr_w // 2 - stats.get_width() // 2, 520))
    
    draw_vignette(screen)













def _draw_comic_text(screen, text_surf, pos, outline_color=(0, 0, 0), outline_px=2):
    """Text-only comic outline, leggero e carino"""
    x, y = pos

    # contorno semplice in 4 direzioni (fumettistico ma leggero)
    if outline_px > 0:
        offsets = [(-outline_px, 0), (outline_px, 0),
                   (0, -outline_px), (0, outline_px)]
        for ox, oy in offsets:
            outline_surf = text_surf.copy()
            # riempie il testo copiato con il colore del contorno
            outline_surf.fill(outline_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(outline_surf, (x + ox, y + oy))

    # testo principale
    screen.blit(text_surf, (x, y))






def draw_game():
    """Compact comic-style HUD, text-only, fully compatible"""

    # === BACKGROUND & CORE ELEMENTS ===
    draw_background()

    for obs in game.obstacles:
        obs.draw(screen)

    for p in game.particles:
        p.draw(screen)

    for popup in game.score_popups:
        popup.draw(screen)

    for notif in game.level_notifications:
        notif.draw(screen)

    # leggermente più a destra se lo avevi già spostato
    draw_player(150, game.player_y, game.velocity)

    # === COMPACT HORIZONTAL HUD (TEXT-ONLY) ===
    scr_w, scr_h = screen.get_size()
    current_time = pygame.time.get_ticks()

    # Niente linee / rettangoli di sfondo: solo testo in alto
    hud_y = 10  # margine superiore

    # --- LEFT: SCORE (piccolo badge) ---
    score_label = font_xs.render("SCORE", True, NEON_CYAN)
    score_value = font_md.render(str(game.score), True, NEON_GREEN)

    _draw_comic_text(screen, score_label, (20, hud_y), outline_color=(10, 10, 10))
    _draw_comic_text(screen, score_value, (20, hud_y + score_label.get_height() + 2),
                     outline_color=(0, 0, 0))

    # --- CENTER: LEVEL (fumettistico) ---
    level_text = font_md.render(f"LEVEL {game.current_level}", True, NEON_CYAN)
    level_x = scr_w // 2 - level_text.get_width() // 2
    _draw_comic_text(screen, level_text, (level_x, hud_y + 4),
                     outline_color=(0, 0, 0))

    # --- RIGHT: SPEED (solo testo, nessuna barra/linea) ---
    speed_color = _get_speed_color(game.obstacle_speed)
    speed_label = font_xs.render("SPEED", True, NEON_CYAN)
    speed_value = font_md.render(f"{game.obstacle_speed:.1f}", True, speed_color)

    speed_value_x = scr_w - speed_value.get_width() - 20
    speed_label_x = speed_value_x + speed_value.get_width() - speed_label.get_width()

    _draw_comic_text(screen, speed_label, (speed_label_x, hud_y),
                     outline_color=(10, 10, 10))
    _draw_comic_text(screen, speed_value,
                     (speed_value_x, hud_y + speed_label.get_height() + 2),
                     outline_color=(0, 0, 0))

    # === COMBO DISPLAY (fumetto sotto HUD) ===
    if game.combo > 0:
        _draw_combo_display(screen, game.combo, scr_w, current_time)

    # === AUDIO VISUALIZER / HINT ===
    level = min(1.0, (current_rms - game.silence_threshold) /
                max(0.01, game.shout_threshold - game.silence_threshold))
    level = max(0.0, level)

    if game.show_equalizer:
        draw_equalizer(level)
    #else:
        #hint_alpha = min(150, int(abs(math.sin(current_time * 0.001)) * 180))
        #hint_text = font_xs.render("Press 'E' / Y for Equalizer", True, DARK_GRAY)
        #hint_surf = hint_text.copy()
        #hint_surf.set_alpha(hint_alpha)
        #screen.blit(hint_surf, (scr_w - hint_text.get_width() - 15, scr_h - 30))

    # === VIGNETTE ===
    draw_vignette(screen)





# === HELPER FUNCTIONS ===

def _draw_optimized_glow(screen, text_surf, pos, color, intensity=50):
    """Minimal glow for compact HUD"""
    x, y = pos
    w, h = text_surf.get_size()
    
    # Single glow layer for performance
    for r in range(10, 0, -5):
        glow_alpha = int(intensity * (1 - r / 10) * 0.65)
        if glow_alpha > 0:
            glow_surf = pygame.Surface((w + r * 2, h + r * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, glow_alpha), 
                           (0, 0, glow_surf.get_width(), glow_surf.get_height()), 
                           border_radius=6)
            screen.blit(glow_surf, (x - r, y - r), special_flags=pygame.BLEND_ALPHA_SDL2)


def _get_speed_color(speed):
    """Dynamic color progression"""
    if speed < 5.0:
        return GRAY
    elif speed < 8.0:
        return NEON_CYAN
    elif speed < 12.0:
        return NEON_ORANGE
    else:
        return NEON_MAGENTA


def _draw_combo_display(screen, combo, scr_w, current_time):
    """Compact combo display - NO render se combo=1"""
    # *** FIX: Non mostrare combo=1 ***
    if combo <= 1:
        return  # Niente da mostrare
    
    # Progressive styling
    if combo < 3:
        combo_color = NEON_YELLOW
        pulse_speed = 0.008
    elif combo < 5:
        combo_color = NEON_ORANGE
        pulse_speed = 0.012
    else:
        combo_color = NEON_MAGENTA
        pulse_speed = 0.016
    
    # Smooth pulse
    combo_pulse = 1.0 + math.sin(current_time * pulse_speed) * 0.1
    combo_text = font_lg.render(f"COMBO ×{combo}", True, combo_color)
    
    # Safe scaling
    combo_w = max(1, int(combo_text.get_width() * combo_pulse))
    combo_h = max(1, int(combo_text.get_height() * combo_pulse))
    
    combo_x = scr_w // 2 - combo_w // 2
    combo_y = 70  # Positioned just below HUD
    
    # Glow for high combos
    if combo >= 5:
        _draw_optimized_glow(screen, combo_text, (combo_x, combo_y), 
                           combo_color, intensity=60)
    
    combo_scaled = pygame.transform.scale(combo_text, (combo_w, combo_h))
    screen.blit(combo_scaled, (combo_x, combo_y))



























def draw_gameover():
    # --- SETUP & CONFIGURAZIONE ---
    screen.fill(DARK_BG)
    draw_starfield()
    
    scr_w, scr_h = screen.get_width(), screen.get_height()
    cx, cy = scr_w // 2, scr_h // 2
    time_ms = pygame.time.get_ticks()
    
    # Animazioni base
    pulse_slow = (math.sin(time_ms * 0.003) + 1) * 0.5  # 0.0 a 1.0 lento
    pulse_fast = (math.sin(time_ms * 0.008) + 1) * 0.5  # 0.0 a 1.0 veloce
    
    # 1. BACKGROUND ATMOSFERICO (Vignetta profonda)
    overlay = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
    overlay.fill((5, 10, 20, 200)) # Blu notte profondo
    screen.blit(overlay, (0, 0))
    
    # Particelle ambientali
    for i in range(10):
        angle = (time_ms * 0.0002) + (i * (6.28 / 10))
        rad_x = scr_w * 0.4
        rad_y = scr_h * 0.35
        p_x = cx + math.cos(angle) * rad_x
        p_y = cy + math.sin(angle * 1.5) * rad_y
        
        alpha = int(100 + math.sin(time_ms * 0.002 + i) * 50)
        pygame.draw.circle(screen, (*NEON_CYAN, alpha), (int(p_x), int(p_y)), 2)

    # 2. TITOLO "GAME OVER" (Stile Cyberpunk Glitch)
    title_y = scr_h * 0.18
    base_scale = 1.1 + (pulse_slow * 0.05)
    offset_x = int(4 * pulse_fast)
    
    # Livello Rosso
    title_r = font_xl.render("GAME OVER", True, (255, 0, 50))
    w_r, h_r = int(title_r.get_width() * base_scale), int(title_r.get_height() * base_scale)
    title_r = pygame.transform.scale(title_r, (w_r, h_r))
    screen.blit(title_r, title_r.get_rect(center=(cx - offset_x, title_y)))
    
    # Livello Ciano
    title_c = font_xl.render("GAME OVER", True, (0, 255, 255))
    title_c = pygame.transform.scale(title_c, (w_r, h_r))
    screen.blit(title_c, title_c.get_rect(center=(cx + offset_x, title_y)))
    
    # Livello Principale
    title_main = font_xl.render("GAME OVER", True, NEON_MAGENTA)
    title_main = pygame.transform.scale(title_main, (w_r, h_r))
    title_rect = title_main.get_rect(center=(cx, title_y))
    screen.blit(title_main, title_rect)
    
    pygame.draw.line(screen, (0,0,0,100), (title_rect.left, title_rect.centery), (title_rect.right, title_rect.centery), 2)

    # 3. PANNELLO SCORE (HUD CENTRALE)
    panel_w, panel_h = 380, 220
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (cx, cy + 20)
    
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel_surf.fill((15, 20, 30, 220))
    
    border_color = (*NEON_GREEN, 150)
    pygame.draw.rect(panel_surf, border_color, panel_surf.get_rect(), width=2, border_radius=15)
    
    pygame.draw.line(panel_surf, NEON_GREEN, (40, 15), (panel_w-40, 15), 1)
    pygame.draw.line(panel_surf, NEON_GREEN, (40, panel_h-15), (panel_w-40, panel_h-15), 1)

    screen.blit(panel_surf, panel_rect)

    # -- CONTENUTO PANNELLO --
    lvl_txt = font_md.render(f"LEVEL {game.current_level}", True, NEON_CYAN)
    lvl_rect = lvl_txt.get_rect(center=(cx, panel_rect.top + 40))
    screen.blit(lvl_txt, lvl_rect)
    
    score_lbl = font_sm.render("FINAL SCORE", True, (150, 150, 150))
    screen.blit(score_lbl, score_lbl.get_rect(center=(cx, panel_rect.centery - 20)))
    
    score_val = font_xl.render(str(game.score), True, WHITE)
    score_shadow = font_xl.render(str(game.score), True, (NEON_GREEN[0], NEON_GREEN[1], NEON_GREEN[2]))
    screen.blit(score_shadow, score_shadow.get_rect(center=(cx, panel_rect.centery + 22)))
    screen.blit(score_val, score_val.get_rect(center=(cx, panel_rect.centery + 20)))
    
    hs_y = panel_rect.bottom - 40
    if game.score >= game.high_score:
        rec_color = NEON_ORANGE
        rec_scale = 1.0 + (pulse_fast * 0.1)
        rec_txt = font_md.render("NEW RECORD!", True, rec_color)
        w_rec = int(rec_txt.get_width() * rec_scale)
        h_rec = int(rec_txt.get_height() * rec_scale)
        rec_scaled = pygame.transform.scale(rec_txt, (w_rec, h_rec))
        screen.blit(rec_scaled, rec_scaled.get_rect(center=(cx, hs_y)))
    else:
        best_txt = font_sm.render(f"BEST: {game.high_score}", True, (255, 200, 50))
        screen.blit(best_txt, best_txt.get_rect(center=(cx, hs_y)))

    # 4. ACTION BAR (INPUTS)
    bottom_y = scr_h - 80
    
    # TASTO SPACE
    btn_w, btn_h = 240, 44
    btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
    btn_rect.center = (cx, bottom_y)
    
    glow_alpha = int(100 + pulse_slow * 100)
    pygame.draw.rect(screen, (*NEON_GREEN, glow_alpha), btn_rect.inflate(4, 4), width=2, border_radius=8)
    pygame.draw.rect(screen, NEON_GREEN, btn_rect, border_radius=8)
    
    restart_txt = font_md.render("PRESS SPACE", True, (0, 0, 0))
    screen.blit(restart_txt, restart_txt.get_rect(center=btn_rect.center))
    
    # INPUT SECONDARI
    sec_y = bottom_y + 45
    col_gray = (180, 180, 180)
    
    # [CORRETTO] Uso centery invece di centerY
    key_a = font_sm.render("[ A ]", True, col_gray)
    key_a_rect = key_a.get_rect(right=cx - 10, centery=sec_y)
    screen.blit(key_a, key_a_rect)
    
    sep = font_sm.render("|", True, (80, 80, 80))
    screen.blit(sep, sep.get_rect(center=(cx, sec_y)))
    
    # [CORRETTO] Uso centery invece di centerY
    mic_txt = font_sm.render("SHOUT", True, col_gray)
    mic_rect = mic_txt.get_rect(left=cx + 10, centery=sec_y)
    screen.blit(mic_txt, mic_rect)
    
    esc_surf = font_sm.render("ESC: MENU", True, (80, 80, 80))
    screen.blit(esc_surf, (20, scr_h - 30))

    draw_vignette(screen)




def reset_game():
    """Reset completo del gioco - SFONDO RESETTATO PER PRIMO"""
    scrh = screen.get_height()

    # Reset sfondo PRIMA COSA
    reset_celestial_objects()

    game.player_y = scrh // 2
    game.velocity = 0.0
    game.score = 0
    game.combo = 0
    game.current_level = 1
    game.current_palette_index = 0
    game.next_palette_index = 1
    game.transition_progress = 0.0
    game.is_transitioning = False
    game.obstacle_speed = game.base_obstacle_speed
    game.difficulty = 1.0
    game.obstacles = []
    game.particles = []
    game.score_popups = []
    game.level_notifications = []
    game.spawn_timer = 0
    game.spawn_interval = 115

    game.state = "GAME"
    play_sound(SOUND_BOOM, force=True)


running = True
print("✓ Game loop avviato")

# ============================================
# VOICE TRIGGER CONFIGURATION
# ==============================
# ==============
MENU_START_RMS_THRESHOLD = 0.0035      # Soglia RMS fissa per menu
MENU_START_DURATION_SEC = 0.2        # Durata minima suono in secondi
MENU_START_VISUAL_FEEDBACK = False   # Mostra barra progresso

# ============================================
# INIZIALIZZAZIONE GIOCO
# ============================================
game = Game()

# ============================================
# VARIABILI GLOBALI VOICE TRIGGER (IMPORTANTE!)
# ============================================
voice_start_timer = 0.0              # Timer progressivo
voice_trigger_cooldown = 0           # Cooldown anti-spam

# ============================================
# GAME LOOP
# ============================================
running = True
print("🎮 Game loop avviato")


while running:
    clock.tick(60)
    
    # ===== VOICE TRIGGER - MENU STATE =====
    if game.state == "MENU":
        if current_rms > MENU_START_RMS_THRESHOLD:
            # Incrementa timer (0.0 -> 1.0 in 1 secondo)
            voice_start_timer = min(1.0, voice_start_timer + (1.0 / (MENU_START_DURATION_SEC * 60)))
            
            if voice_start_timer >= 1.0:
                reset_game()
                voice_start_timer = 0.0
                voice_trigger_cooldown = 30
        else:
            # Reset rapido se RMS scende sotto soglia
            voice_start_timer = max(0.0, voice_start_timer - 0.05)
    
    # ===== VOICE TRIGGER - GAME OVER STATE =====
    elif game.state == "GAME_OVER":
        if current_rms > MENU_START_RMS_THRESHOLD:
            voice_start_timer = min(1.0, voice_start_timer + (1.0 / (MENU_START_DURATION_SEC * 60)))
            
            if voice_start_timer >= 1.0:
                reset_game()
                voice_start_timer = 0.0
                voice_trigger_cooldown = 30
        else:
            voice_start_timer = max(0.0, voice_start_timer - 0.05)
    
    else:
        voice_start_timer = 0.0
    
    # Decremento cooldown
    if voice_trigger_cooldown > 0:
            voice_trigger_cooldown -= 1





    # *** AI LOGIC - TARGET TRACKING (Reattiva e Sicura) ***
    if game.state == "GAME" and game.ai_active:
        # 1. TROVA L'OSTACOLO RILEVANTE
        # Cerca il primo ostacolo che ha il bordo destro ANCORA davanti al player
        # (Player X è fisso a 150)
        target_obs = None
        for obs in game.obstacles:
            if obs.x + obs.width > 130:  # 140 è un margine prima del player (150)
                target_obs = obs
                break
        
        # 2. CALCOLA IL TARGET Y
        if target_obs:
            # Il target non è il centro perfetto, ma leggermente più in basso
            # perché saltare è istantaneo, cadere è lento. Stare bassi è più sicuro.
            gap_center = target_obs.y + (target_obs.gap_height * 0.70)
            
            # 3. ANALISI POSIZIONE
            # Siamo sotto il target?
            is_low = game.player_y > gap_center
            
            # Stiamo cadendo? (Velocity positiva = giù)
            is_falling = game.velocity > 0
            
            # Distanza verticale dal tubo superiore (sicurezza)
            dist_to_top_pipe = game.player_y - target_obs.y
            
            # 4. DECISIONE DI SALTO
            # Salta SOLO se:
            # A. Siamo sotto il target E stiamo cadendo (o siamo quasi fermi)
            # B. NON siamo troppo vicini al tubo superiore (Safety Cap)
            
            if is_low:
                # Se siamo molto bassi (emergenza), salta anche se stiamo già salendo un po'
                must_jump = False
                
                if game.player_y > target_obs.y + target_obs.gap_height - 30:
                    must_jump = True # Emergenza terra/tubo basso
                elif is_falling:
                    must_jump = True # Mantenimento quota standard
                
                if must_jump:
                    # *** CRITICAL SAFETY CHECK ***
                    # Se saltiamo ora (-9.5), dove saremo tra 3 frame?
                    # Se finiamo dentro il tubo sopra, NON SALTARE, aspetta di scendere.
                    future_y_after_jump = game.player_y + (-9.5 * 3) # Proiezione salto
                    
                    # Salta solo se non ci schiantiamo contro il tubo sopra
                    if future_y_after_jump > target_obs.y + game.player_size + 10:
                        game.velocity = -9.0  # Salto standard controllato
                        
        else:
            # Nessun ostacolo (inizio gioco o tra i tubi) -> Resta al centro
            if game.player_y > screen.get_height() // 2:
                if game.velocity > 0:
                    game.velocity = -7.0












    # Events (Keyboard + Joypad)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.save_calibration()
            running = False
            
        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game.state != "MENU":
                    game.save_calibration()
                    reset_celestial_objects()
                    game.state = "MENU"
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # + o =
                if game.state == "GAME":
                    game.obstacle_speed = min(game.obstacle_speed + 0.5, 120.0)  # Max 20
                    print(f"✓ Velocità: {game.obstacle_speed:.1f}")
            elif event.key == pygame.K_MINUS:
                if game.state == "GAME":
                    game.obstacle_speed = max(game.obstacle_speed - 0.5, 2.0)   # Min 2
                    print(f"✓ Velocità: {game.obstacle_speed:.1f}")
            if event.key == pygame.K_f:
                if game.state == "MENU":
                    game.toggle_fullscreen()
            
            # TOGGLE EQUALIZER with E
            if event.key == pygame.K_e:
                if game.state == "GAME":
                    game.show_equalizer = not game.show_equalizer
                    print(f"✓ Equalizer: {'ON' if game.show_equalizer else 'OFF'}")
            
            if event.key == pygame.K_c:
                if game.state == "MENU":
                    game.calibrated = False
                    game.calib_silence = []
                    game.calib_shout = []
                    game.calib_timer = 0
                    game.state = "CALIBRATE_SILENCE"
                    play_sound(SOUND_BEEP, force=True)

            if event.key == pygame.K_SPACE:
                if game.state == "MENU":
                    if game.calibrated:
                        reset_game()
                    else:
                        game.calib_silence = []
                        game.calib_shout = []
                        game.calib_timer = 0
                        game.state = "CALIBRATE_SILENCE"
                        play_sound(SOUND_BEEP, force=True)
                        
                elif game.state == "GAME_OVER":
                    reset_game()
            
            # *** AI TOGGLE - TASTO I ***
            if event.key == pygame.K_i:
                if game.state == "GAME":
                    game.ai_active = not game.ai_active
                    print(f"AI {'ON' if game.ai_active else 'OFF'}")

        # Joypad buttons (invariato)
        if event.type == pygame.JOYBUTTONDOWN:
            # A button (0) = Start/Jump
            if event.button == 0:
                if game.state == "MENU":
                    if game.calibrated:
                        reset_game()
                    else:
                        game.calib_silence = []
                        game.calib_shout = []
                        game.calib_timer = 0
                        game.state = "CALIBRATE_SILENCE"
                        play_sound(SOUND_BEEP, force=True)
                        
                elif game.state == "GAME_OVER":
                    reset_game()
            
            # B button (1) = Back
            elif event.button == 1:
                if game.state != "MENU":
                    game.save_calibration()
                    reset_celestial_objects()
                    game.state = "MENU"
            
            # Y button (3) = Toggle Equalizer
            elif event.button == 3:
                if game.state == "GAME":
                    game.show_equalizer = not game.show_equalizer
                    print(f"✓ Equalizer: {'ON' if game.show_equalizer else 'OFF'}")
            
            # START button (7) = Toggle Fullscreen
            elif event.button == 7:
                if game.state == "MENU":
                    game.toggle_fullscreen()
    
    scr_w = screen.get_width()
    scr_h = screen.get_height()
    
    if game.state == "MENU":
        draw_menu()
    
    elif game.state in ["CALIBRATE_SILENCE", "CALIBRATE_SHOUT"]:
        game.calib_timer += 1
        
        if game.state == "CALIBRATE_SILENCE" and current_rms > 0:
            game.calib_silence.append(current_rms)
        elif game.state == "CALIBRATE_SHOUT" and current_rms > 0:
            game.calib_shout.append(current_rms)
        
        if game.calib_timer >= game.calib_duration:
            if game.state == "CALIBRATE_SILENCE":
                game.calib_timer = 0
                game.state = "CALIBRATE_SHOUT"
                play_sound(SOUND_WHOOSH, force=True)
            else:
                if game.calib_silence:
                    game.silence_threshold = np.mean(game.calib_silence) * 1.3
                if game.calib_shout:
                    game.shout_threshold = np.max(game.calib_shout) * 0.75
                
                game.save_calibration()
                reset_game()
        
        draw_calibration()
    
    elif game.state == "GAME":
        if current_rms > game.silence_threshold:
            level = (current_rms - game.silence_threshold) / (game.shout_threshold - game.silence_threshold)
            level = max(0.0, min(1.0, level))
        else:
            level = 0.0
                
        # *** AI HA GIA' MODIFICATO velocity SE ATTIVA ***
        gravity = 0.45 + (game.current_level - 1) * 0.040  # +0.035/livello [file:1]
        jump_power = 9.5 + (game.current_level - 1) * 0.95  # +0.45/livello

        game.velocity += gravity
        if level > 0.1 and not game.ai_active:  # Voice solo se AI spenta
            game.velocity = -jump_power * (level ** 0.75)
        game.velocity = max(-11 - (game.current_level - 1) * 0.5, 
                        min(15 + (game.current_level - 1) * 0.3, 
                            game.velocity))
        game.player_y += game.velocity
        # Resto della tua logica GAME identica...
        if game.player_y < game.player_size:
            game.player_y = game.player_size
            game.velocity = 0
            for _ in range(10):
                game.particles.append(Particle(150, game.player_y, random.uniform(-4, 4), random.uniform(-5, 0), NEON_GREEN, 40, random.randint(4, 8)))
            play_sound(SOUND_BEEP)
        
        if game.player_y > scr_h - game.player_size:
            game.player_y = scr_h - game.player_size
            game.velocity = 0
            for _ in range(10):
                game.particles.append(Particle(150, game.player_y, random.uniform(-4, 4), random.uniform(0, 5), NEON_MAGENTA, 40, random.randint(4, 8)))
            play_sound(SOUND_BEEP)
        
        game.spawn_timer += 1 
        if game.spawn_timer > game.spawn_interval:
            gap_y = random.randint(160, scr_h - 260)
            game.obstacles.append(Obstacle(x=scr_w, y=gap_y, gap_height=int(235 - game.difficulty * 4)))
            game.spawn_timer = 0
            
            # Calcola l'intervallo in base al livello corrente
            base_min = 80
            base_max = 160
            level_reduction = (game.current_level - 1) * 8
            min_interval = max(35, base_min - level_reduction)
            max_interval = max(50, base_max - level_reduction)
            game.spawn_interval = random.randint(min_interval, max_interval)

        for obs in game.obstacles[:]:
            obs.x -= game.obstacle_speed
            
            if not obs.passed and obs.x + obs.width // 2 < 150:
                obs.passed = True

                game.combo += 1
                game.combo_timer = 57
                if game.combo > 5:
                    game.combo = 5
                points = max(1, game.combo)  # Minimo 1, combo moltiplica
                game.score += points

                game.score_popups.append(ScorePopup(150, game.player_y, points))  # Mostra punti reali

                for _ in range(15):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2.5, 8)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    game.particles.append(Particle(150, game.player_y, vx, vy, NEON_GREEN, 45, random.randint(5, 9)))
                
                play_sound(SOUND_WHOOSH)
                game.check_level_up()
            
            if obs.x < -obs.width:
                game.obstacles.remove(obs)
            
            player_rect = pygame.Rect(150 - game.player_size, game.player_y - game.player_size, 
                                     game.player_size * 2, game.player_size * 2)
            
            top_pipe = pygame.Rect(obs.x, 0, obs.width, obs.y)
            bottom_pipe = pygame.Rect(obs.x, obs.y + obs.gap_height, obs.width, scr_h - (obs.y + obs.gap_height))
            
            if player_rect.colliderect(top_pipe) or player_rect.colliderect(bottom_pipe):
                # Particelle iniziali impatto
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(5, 12)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    game.particles.append(Particle(150, game.player_y, vx, vy, NEON_ORANGE, 45, random.randint(5, 10)))

                # ESPLOSIONE MIGLIORATA
                game.explosion_animation = ComicExplosion(150, game.player_y)
                game.state = "EXPLODING"

                play_sound(SOUND_COLLISION, force=True)

                if game.score > game.high_score:
                    game.high_score = game.score
                    game.save_calibration()

                reset_celestial_objects()
        
        game.particles = [p for p in game.particles if p.update()]
        game.score_popups = [sp for sp in game.score_popups if sp.update()]
        game.level_notifications = [ln for ln in game.level_notifications if ln.update()]
        
        if game.combo_timer > 0:
            game.combo_timer -= 1
            if game.combo_timer == 0:
                game.combo = 0
        
        draw_game()
        
        # *** AI INDICATOR VISIVO ***
        if game.ai_active:
            ai_text = font_sm.render("AI ON", True, NEON_GREEN)

    elif game.state == "EXPLODING":
        # Tutta la tua logica EXPLODING invariata...
        if game.explosion_animation:
            if not game.explosion_animation.update():
                game.explosion_animation = None
                game.state = "GAME_OVER"
        else:
            game.state = "GAME_OVER"

        shake_x = 0
        shake_y = 0
        if game.explosion_animation and game.explosion_animation.age < 10:
            intensity = int((10 - game.explosion_animation.age) * 1.8)
            shake_x = random.randint(-intensity, intensity)
            shake_y = random.randint(-intensity, intensity)

        draw_background()

        for obs in game.obstacles:
            obs.draw(screen)

        for p in game.particles:
            p.draw(screen)

        if game.explosion_animation:
            game.explosion_animation.draw(screen)

        if shake_x != 0 or shake_y != 0:
            temp_surf = screen.copy()
            screen.fill(DARK_BG)
            screen.blit(temp_surf, (shake_x, shake_y))

    elif game.state == "GAME_OVER":
        draw_gameover()
    
    pygame.display.flip()










print("✓ Chiusura gioco...")
pygame.quit()
stream.stop()
stream.close()
sys.exit(0)
