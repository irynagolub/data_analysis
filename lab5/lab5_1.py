# Лабораторна робота №5
# ФБ-25 Голубєва Ірина

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons

def run_harmonic_visualizer():
    DEFAULT_AMPLITUDE = 1.0
    DEFAULT_FREQUENCY = 1.0
    DEFAULT_PHASE = 0.0
    DEFAULT_NOISE_LEVEL = 0.0
    DEFAULT_NOISE_VARIANCE = 0.1
    SHOW_NOISE_DEFAULT = True
    RANDOM_NOISE = np.random.normal(0, 1, 1000)

    def generate_harmonic(amplitude, frequency, phase, noise_level, noise_variance, display_noise=True):
        t = np.linspace(0, 10, 1000)
        harmonic_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        if display_noise:
            noise = noise_level + np.sqrt(noise_variance) * RANDOM_NOISE
            harmonic_signal += noise
        return t, harmonic_signal

    def refresh_display(event):
        t, harmonic_output = generate_harmonic(amplitude_slider.val, frequency_slider.val,
                                               phase_slider.val, noise_level_slider.val,
                                               noise_variance_slider.val, show_noise_checkbox.get_status()[0])
        line.set_data(t, harmonic_output)
        fig.canvas.draw_idle()

    def restore_defaults(event):
        amplitude_slider.reset()
        frequency_slider.reset()
        phase_slider.reset()
        noise_level_slider.reset()
        noise_variance_slider.reset()
        refresh_display(None)

    def recreate_noise(event):
        global RANDOM_NOISE
        RANDOM_NOISE = np.random.normal(0, 1, 1000)
        refresh_display(None)

    fig, ax = plt.subplots(figsize=(10, 5))
    plt.subplots_adjust(left=0.25, bottom=0.4)

    t, harmonic_output = generate_harmonic(DEFAULT_AMPLITUDE, DEFAULT_FREQUENCY, DEFAULT_PHASE, 
                                           DEFAULT_NOISE_LEVEL, DEFAULT_NOISE_VARIANCE, SHOW_NOISE_DEFAULT)
    line, = ax.plot(t, harmonic_output, lw=2, color='blue')

    ax.set_title('Harmonic with Noise')

    amplitude_slider = Slider(plt.axes([0.25, 0.3, 0.65, 0.03]), 'Amplitude', 0.1, 5.0, valinit=DEFAULT_AMPLITUDE)
    frequency_slider = Slider(plt.axes([0.25, 0.25, 0.65, 0.03]), 'Frequency', 0.1, 5.0, valinit=DEFAULT_FREQUENCY)
    phase_slider = Slider(plt.axes([0.25, 0.20, 0.65, 0.03]), 'Phase', -np.pi, np.pi, valinit=DEFAULT_PHASE)
    noise_level_slider = Slider(plt.axes([0.25, 0.15, 0.65, 0.03]), 'Noise Level', -1.0, 1.0, valinit=DEFAULT_NOISE_LEVEL)
    noise_variance_slider = Slider(plt.axes([0.25, 0.10, 0.65, 0.03]), 'Noise Variance', 0.01, 1.0, valinit=DEFAULT_NOISE_VARIANCE)

    reset_button = Button(plt.axes([0.25, 0.05, 0.1, 0.04]), 'Reset')
    reset_button.on_clicked(restore_defaults)

    new_noise_button = Button(plt.axes([0.4, 0.05, 0.1, 0.04]), 'New Noise')
    new_noise_button.on_clicked(recreate_noise)

    show_noise_checkbox = CheckButtons(plt.axes([0.55, 0.05, 0.15, 0.05]), ['Show Noise'], [SHOW_NOISE_DEFAULT])

    amplitude_slider.on_changed(refresh_display)
    frequency_slider.on_changed(refresh_display)
    phase_slider.on_changed(refresh_display)
    noise_level_slider.on_changed(refresh_display)
    noise_variance_slider.on_changed(refresh_display)
    show_noise_checkbox.on_clicked(refresh_display)

    plt.show()

run_harmonic_visualizer()
