import numpy as np
import pyaudio
import time
from scipy.signal import butter, lfilter

def visualize_main():
    """Main function to execute the program after user confirmation."""
    use_bandpass = get_user_choice("Enable bandpass filter? (y/n): ")
    use_noise_reduction = get_user_choice("Enable noise reduction? (y/n): ")
    
    if input("Type 'start' to begin listening: ").strip().lower() == 'start':
        print("Plotting ASCII Art. Press Ctrl+C to stop...")
        display_real_time_decibel_plot(use_bandpass, use_noise_reduction)
    else:
        print("Invalid input. Exiting...")

def get_user_choice(prompt):
    """Helper function to get user choice for enabling filters."""
    return input(prompt).strip().lower() == 'y'

def capture_audio_stream():
    """Capture real-time audio data from the microphone."""
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1  # Mono
    rate = 44100  # Record at 44100 samples per second

    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=rate,
                    frames_per_buffer=chunk,
                    input=True)

    return stream, p, chunk, rate

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Apply a bandpass filter to the data."""
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

def noise_reduction(data, window_size=5):
    """Apply a simple moving average filter for noise reduction."""
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def process_audio_data(data, fs, use_bandpass, use_noise_reduction):
    """Convert raw audio data into a NumPy array, apply filters, and compute the FFT."""
    audio_data = np.frombuffer(data, dtype=np.int16)
    if use_bandpass:
        audio_data = bandpass_filter(audio_data, 300, 3000, fs)
    if use_noise_reduction:
        audio_data = noise_reduction(audio_data)
    return np.abs(np.fft.fft(audio_data)[:len(audio_data) // 2])

def calculate_decibels(data):
    """Convert raw audio data to decibel levels."""
    rms = np.sqrt(np.mean(np.square(data)))
    return 20 * np.log10(rms) if rms > 0 else -np.inf

def get_sound_direction(data):
    """Simulate getting the sound direction from processed audio data."""
    max_amplitude_index = np.argmax(data)
    return (max_amplitude_index % 10, max_amplitude_index // 10)

def display_real_time_decibel_plot(use_bandpass, use_noise_reduction):
    """Display real-time decibel and audio waveform plot with ASCII art."""
    stream, p, chunk, rate = capture_audio_stream()
    decibels = []
    last_plot_time = time.time()

    try:
        while True:
            try:
                data = stream.read(chunk, exception_on_overflow=False)
                processed_data = process_audio_data(data, rate, use_bandpass, use_noise_reduction)
                decibel_level = calculate_decibels(processed_data)
                
                # Ensure valid decibel level (not NaN)
                if np.isnan(decibel_level):
                    decibel_level = 0
                
                direction = get_sound_direction(processed_data)
                decibels.append(decibel_level)
                
                if len(decibels) > 50:  # Limit the number of points plotted to avoid overflow
                    decibels.pop(0)
                
                if time.time() - last_plot_time >= 1:  # Update every 1 second
                    print("\033c", end="")  # Clear the terminal screen
                    print(plot_combined_ascii(decibels, processed_data, direction))
                    last_plot_time = time.time()
            
            except IOError as e:
                print(f"Input overflowed: {e}")
                stream.stop_stream()
                stream.close()
                stream, p, chunk, rate = capture_audio_stream()

    except KeyboardInterrupt:
        print("\nStopping audio capture...")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def plot_combined_ascii(decibels, audio_data, direction, width=100, height=20):
    """Combine decibel levels and audio waveform data into a single ASCII art plot within a border."""
    # ANSI color codes
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    RESET = '\033[0m'
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    max_val = np.max(audio_data)
    min_val = np.min(audio_data)
    scale_audio = (max_val - min_val) / width if max_val != min_val else 1  # Avoid division by zero

    for i in range(width):
        if i < len(audio_data):
            level_audio = int((audio_data[i] - min_val) / scale_audio)
            
            shift = direction[0] // 2
            level_audio = min(max(level_audio + shift, 0), height - 1)
            
            color = BLUE if i % 2 == 0 else GREEN
            for row in range(height):
                if row >= height - (level_audio // 2) - 1:
                    grid[row][i] = f"{color}█{RESET}"
    
    border_top_bottom = "+" + "-" * width + "+"
    grid_str = [border_top_bottom] + ['|' + ''.join(row) + '|' for row in grid] + [border_top_bottom]

    return "\n".join(grid_str)

if __name__ == "__main__":
    visualize_main()  # Call the main function to start the programmain()