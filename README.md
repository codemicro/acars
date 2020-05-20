# ACARS

###### A new client for Hoppie's ACARS system, including POS printer integration

ACARS is a Python program written in order to make using Hoppie with your flight simulator and POS printer easy.

Only Windows is supported (will ~~possibly~~ absolutely not run on Linux)

### Installation

Installation is simple:

* ~~Either run the installer, or~~
* Install the required dependencies yourself

If you choose to install the dependencies yourself, you should first begin with an installation of Python 3.7 (64 or 32 bit, whichever your operating system is). Into this, install

* Requests (`requests`)
* Python-ESCPOS (`python-escpos`)
* Loguru (`loguru`)
* PyQt5 (`pyqt5`)

Once these have been installed, navigate to `<python>\Lib\site-packages\escpos\printer.py` and comment out or remove the following lines:

```python
try:
    check_driver = self.device.is_kernel_driver_active(0)
except NotImplementedError:
    passif check_driver is None or check_driver:
    try:
        self.device.detach_kernel_driver(0)
    except usb.core.USBError as e:
        if check_driver is not None:
            print("Could not detatch kernel driver: {0}".format(str(e)))
```

This is required because, while the ESCPOS library works on Windows, it is not designed to run on Windows, and hence sometimes does stuff like above, where it makes calls to the kernel for things that Windows just doesn't do.

### Setup

Now download the LibUSB library from [here](http://sourceforge.net/projects/libusb/files/libusb-1.0/libusb-1.0.20/libusb-1.0.20.7z/download), and depending on your system architecture, do the following operations:

* On 64-bit Windows:
  * Copy `MS64\dll\libusb-1.0.dll` to `C:\Windows\System32`
  * `MS64\static\libusb-1.0.lib` to `<python>\Lib`
* On 32-bit Windows:
  * Copy `MS32\dll\libusb-1.0.dll` to `C:\Windows\SysWOW64`
  * `MS32\static\libusb-1.0.lib` to `<python>\Lib`

This is required as Python needs access to the LIB file and the DLL file has to be in a location in the system PATH. The simplest place for this is System32.

At this point, you should have all the pre-requisites setup and you can install the new printer driver for the POS printer.

First off, download Zadig from [here](https://zadig.akeo.ie/). Connect your POS printer to your computer, run Zadig and go to "Options" and check "List all devices". 

Select your POS printer in the dropdown box, ensure the arrow points to WinUSB in the right hand box and press the "Replace driver" button. Ensure you also note the USB IDs (first being the product ID and second being the vendor ID).

If you wish to revert the driver to that supplied by the manufacturer, go to Device Manager, USB devices and select your USB printer. Right-click and uninstall the driver, making sure to check the "delete driver software box". Power cycle the printer and reinstall the manufacturer's driver.

TODO: Write settings setup

### Usage

TODO: Write this too. It's half past eleven, I can't be bothered with this.
