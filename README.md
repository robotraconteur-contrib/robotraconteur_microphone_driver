<p align="center"><img src="docs/figures/RRheader2.jpg"></p>

# Robot Raconteur Generic Microphone Driver

The Robot Raconteur Generic Microphone Driver provides a Robot Raconteur service for generic system microphones
based on the Python [`sounddevice` package](https://python-sounddevice.readthedocs.io/en/0.4.6/). This
driver is designed to allow the capture for a specified duration or streaming of audio. Capturing is accomplished
using the `capture_microphone` function, while the `microphone_stream` wire is used for streaming audio.

The specific microphone must be specified when starting the driver using the `--device=` options. The available
devices can be listed using the `--list-devices` option. Use the index corresponding to the desired device.
See the [`sounddevice` package](https://python-sounddevice.readthedocs.io/en/0.4.6/usage.html#device-selection) 
for more information. Device indexing is a direct passthrough from this package.

The current service definition used is `experimental.audio.microphone`. This service definition is standards
track and will be included in the standard `com.robotraconteur` types in the future.

See the `examples/` directory for examples using the driver.

## Installation

Install the driver using pip:

```
python -m pip install git+https://github.com/robotraconteur-contrib/robotraconteur_microphone_driver.git
```

## Running the Service

Start the driver using the default options:

```
robotraconteur-microphone-driver
```

Optionally start using a module if the entrypoint does not work:

```
python -m robotraconteur_microphone_driver
```

The following options are available:

* `--list-devices`: List the available sound devices and exit
* `--device=`: The integer index of the device to use. Use `--list-devices` to list available devices and their index
* `--samplerate=`: The sample rate to use for the audio. Defaults to 44000.
* `--channels`: The number of channels. Defaults to 1.

## Using the Service

The service is a wrapper around the Python `sounddevice` package, providing capture of a duration or streaming
of audio.  The following example shows how to use the service from Python to record for a duration and save a 
file. See the `examples/` directory for more examples. Other supported client languages
such as MATLAB or C++ can also be used to access the service.

```python
# Example recording audio for a duration and saving to a file

import wave
from RobotRaconteur.Client import *
import numpy as np
import matplotlib.pyplot as plt
# TODO: Read metadata for samplerate and channels
samplerate = 44000
channels = 1


c = RRN.ConnectService('rr+tcp://localhost:60828?service=microphone')

print("Begin recording")
recording = c.capture_microphone(2)
print("End recording")

audio=[]
for a in recording:
    for audio_data in a.audio_data:
        audio.append(a.audio_data)


first_channel = np.concatenate([a1[0] for a1 in audio])

first_channel_int16=(first_channel*32767).astype(np.int16)
plt.plot(first_channel_int16)
plt.show()
print(first_channel.shape)

with wave.open('output.wav', 'wb') as wav_file:
    # Set the WAV file parameters
    wav_file.setnchannels(channels)
    wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
    wav_file.setframerate(samplerate)

    # Write the audio data to the WAV file
    wav_file.writeframes(first_channel_int16.tobytes())

print('saving finished')
```

## License

Apache 2.0

## Acknowledgment

This work was supported in part by the Advanced Robotics for Manufacturing ("ARM") Institute under Agreement Number W911NF-17-3-0004 sponsored by the Office of the Secretary of Defense. The views and conclusions contained in this document are those of the authors and should not be interpreted as representing the official policies, either expressed or implied, of either ARM or the Office of the Secretary of Defense of the U.S. Government. The U.S. Government is authorized to reproduce and distribute reprints for Government purposes, notwithstanding any copyright notation herein.

This work was supported in part by the New York State Empire State Development Division of Science, Technology and Innovation (NYSTAR) under contract C160142. 

![](docs/figures/arm_logo.jpg) ![](docs/figures/nys_logo.jpg)
