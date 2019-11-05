import ctypes
import datetime
import json
import random
import sys
import threading
import time
import winreg
import winsound
import copy

import escpos.exceptions
import requests
from PyQt5 import QtWidgets, QtCore, QtGui
from escpos.printer import Dummy, Usb
from loguru import logger
from usb.core import USBError, NoBackendError

import gui

# DEBUG
sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook


SETTINGS_FILE = "settings.json"
SETTINGS = json.loads(open(SETTINGS_FILE).read())
LOGON_CODE = SETTINGS["hoppie"]["login-code"]
SERVER_ADDR = SETTINGS["hoppie"]["address"]

session = requests.session()
session.headers.update({"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0"})

station_name = ""

connection_kill_switch = False
is_hoppie_connected = False

message_log_text = ""
message_log = []

# Generic functions and classes


def load_settings():
    global SETTINGS

    SETTINGS = json.loads(open(SETTINGS_FILE).read())


def write_settings():
    global SETTINGS

    open(SETTINGS_FILE, "w").write(json.dumps(SETTINGS, sort_keys=True, indent=2))


def setup_logging():
    logger.remove()

    logpath = winreg.ExpandEnvironmentStrings("%appdata%\\ThomasPain\\ACARS\\logs")

    logger.add(logpath + "\\error.log", level="ERROR", rotation="5 MB")


def start_new_thread(function, arguments, daemon=False):
    # Creates a new thread and runs it

    threading.Thread(target=function, args=arguments, daemon=daemon).start()


class PosPrinter:
    def __init__(self, product_id, vendor_id, ignore_enable_flag=False):
        self.product_id = product_id
        self.vendor_id = vendor_id

        self._printer = None

        ender = "\n\nPrinting disabled"
        if ignore_enable_flag:
            ender = ""

        if not (SETTINGS["printer"]["enable"] and ignore_enable_flag):
            return

        self.failed = True
        try:
            self._printer = Usb(self.product_id, self.vendor_id)
            self._printer.hw("INIT")
            self.failed = False
        except escpos.exceptions.USBNotFoundError:
            popup_message("Printer not found - please check the printer is plugged in and turned on and that the vendor"
                          f" and product IDs correct.{ender}",
                          error=True)
            if ignore_enable_flag:
                SETTINGS["printer"]["enable"] = False
        except USBError as e:
            if "Errno 13" in str(e):
                popup_message(f"USB error 13 - it looks like something else is using the printer.\n\n{ender}",
                              error=True)
                if ignore_enable_flag:
                    SETTINGS["printer"]["enable"] = False
            else:
                popup_message(f"{e}{ender}", error=True)
                logger.exception("Unrecognised USB error")
                if ignore_enable_flag:
                    SETTINGS["printer"]["enable"] = False
        except NoBackendError:
            popup_message(f"There was an issue connecting to the printer. Please refer to the documentation.{ender}",
                          error=True)
            logger.exception("No backend was available - Possible mis-installation of libusb-1.0.dll or WinUSB driver.")
            if ignore_enable_flag:
                SETTINGS["printer"]["enable"] = False

    def print(self, data):
        if self._printer is None:
            helper.add_event((lambda: True), (lambda: popup_message("Printer not initialised.\n\nPrinting disabled.",
                                                                    error=True)))
            SETTINGS["printer"]["enable"] = False
            return
        self._printer._raw(data)

    def close(self):
        self._printer = None

    def reset(self):
        self.close()
        try:
            self._printer = Usb(self.product_id, self.vendor_id)
        except:
            self._printer = None

    def update_ids(self, product_id, vendor_id):
        self.product_id = product_id
        self.vendor_id = vendor_id
        self.reset()


def request(mode, recipient, message):
    if station_name == "":
        popup_message("Select a callsign and connect to Hoppie before attempting to send messages", error=True)
        return
    elif not is_hoppie_connected:
        popup_message("Connect to Hoppie before attempting to send messages", error=True)
        return

    args = {"logon": LOGON_CODE, "from": station_name}

    ui.statusbar.showMessage("Sending message...")
    ui.disconnectButton.setEnabled(False)
    ui.connectionStatusLabel.setText("Working...")

    try:
        r = session.post(SERVER_ADDR, data={**args, "to": recipient, "type": mode, "packet": message})
    except requests.exceptions.ConnectionError as e:
        ui.statusbar.showMessage("Unable to send message")
        logger.exception("Error occurred during request.")
        popup_message(f"Unable to send message due to a connection error.\n\n{str(e)}\n\nDisconnected.")
        stop_message_poll()

        return

    if not r.ok:
        popup_message(f"The URL that was set appears to be invalid because a HTTP {r.status_code} was returned. You can"
                      f" leave the URL field blank in the settings dialog to have it reset to default.\n\nDisconnected."
                      )
        logger.error(f"URL invalid, returned {r.status_code}")
        stop_message_poll()

        return

    ui.disconnectButton.setEnabled(True)
    ui.connectionStatusLabel.setText("Connected")

    if "error" in r.text[:5]:
        ui.statusbar.showMessage("Unable to send message")
        popup_message(f"Error when sending message\n\"{r.text}\"", error=True)
        return False
    else:
        # success
        ui.statusbar.showMessage("Message sent!")
        popup_message("Message sent!")
        return True


# Common GUI functions


def popup_message(text, error=False):
    # Shows standard message dialog
    # If error is set to true, an error soud will also be played asynchronously

    msg = QtWidgets.QMessageBox()
    msg.setText(text)
    if error:
        start_new_thread(winsound.PlaySound, arguments=("SystemHand", winsound.SND_ALIAS))
    msg.exec()


def popup_confirmation(text):
    # Shows confirmation dialog and plays confirmation sound asynchronously
    # Returns true or false

    confirm = QtWidgets.QMessageBox()
    start_new_thread(winsound.PlaySound, arguments=("SystemQuestion", winsound.SND_ALIAS))
    return confirm.question(None, "", text, confirm.Yes | confirm.No)


def popup_input(text):
    text, ok_pressed = QtWidgets.QInputDialog.getText(None, "", text, QtWidgets.QLineEdit.Normal, "")
    if ok_pressed and text != "":
        return text
    else:
        return False


# Main window GUI functions and classes


def print_message(message, header):
    # Prints message based on set template with set formatting. Applies header specified also.

    bold_emphasis = b"\x1b\x21\x08"  # Sets text to bold
    second_typeface_emphasis = b"\x1b\x21\x01"  # Selects font B (different code to actual font size stuff)
    reset_emphasis = b"\x1b\x21\x00"  # Reset emphasis
    font_size_2x = b"\x1d\x21\x10"  # Change text size to 2x
    font_reset = b"\x1d\x21\x00"  # Reset text size

    dpos = Dummy()

    # print header
    dpos._raw(reset_emphasis)
    dpos._raw(font_size_2x)
    dpos.text(header + "\n")
    dpos._raw(font_reset)

    # print associated time
    dpos._raw(second_typeface_emphasis)
    dpos.text(f"Received {datetime.datetime.utcfromtimestamp(message.time).strftime('%d-%H%Mz')}")
    dpos.text("\n")
    dpos._raw(reset_emphasis)

    # print message type
    dpos._raw(bold_emphasis)
    dpos.text("Type: ")
    dpos._raw(reset_emphasis)
    dpos.text("{}\n".format(message.mode))

    # print sender
    dpos._raw(bold_emphasis)
    dpos.text("From: ")
    dpos._raw(reset_emphasis)
    dpos.text("{}\n".format(message.sender))

    # print message
    dpos._raw(bold_emphasis)
    dpos.text("Message: ")
    dpos._raw(reset_emphasis)
    dpos.text("{}\n\n\n".format(message.message))

    pos.print(dpos.output)

    helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage("Commands sent to printer")))


class HoppieMessage:
    # Message structure used for message interchange

    def __init__(self):
        self.sender = None
        self.recipient = None
        self.mode = None
        self.message = None
        self.time = None


def hoppie_connection_thread():
    # Function written to be run in it's own thread, polls SERVER_ADDR with specifc POST args
    # Decodes response, and passes that to the handle_new_message function.
    # If connection_kill_switch is set to true, the thread will end

    global connection_kill_switch
    global is_hoppie_connected

    is_hoppie_connected = True

    while True:

        if connection_kill_switch:
            is_hoppie_connected = False
            return

        args = {"logon": LOGON_CODE, "from": station_name}

        helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage("Checking for new messages")))

        try:
            r = session.post(SERVER_ADDR, data={**args, "type": "poll", "to": "SERVER"})
        except requests.exceptions.ConnectionError as e:
            is_hoppie_connected = False

            logger.exception("Error occurred during message polling")

            def finfunc():
                popup_message("Unable to connect to Hoppie.\n\nDisconnected.")
                stop_message_poll()

            helper.add_event((lambda: is_hoppie_connected is False), finfunc)

            return

        if not r.ok:
            is_hoppie_connected = False

            def finfunc():
                popup_message(
                    f"The URL that was set appears to be invalid because a HTTP {r.status_code} was returned. You can"
                    f" leave the URL field blank in the settings dialog to have it reset to default.\n\nDisconnected.")
                stop_message_poll()

            logger.error(f"URL {SERVER_ADDR} invalid, returned {r.status_code}")
            helper.add_event((lambda: is_hoppie_connected is False), finfunc)

            return

        response = r.text

        if response == "ok ":  # no new messages
            helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage("No new messages - waiting")))

        elif response[:2] == "ok":  # new messages to be parsed

            helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage("New messages found - handling")))

            response = response[3:].split("} {")
            response[0] = response[0][1:]  # remove leading { from first message

            for index, item in enumerate(response):
                helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage(f"Parsing message {index+1}")))

                output = HoppieMessage()

                split = item.split("{")  # split between message and info items
                output.message = split[1].strip("} ")
                split = split[0].strip().split(" ")  # split info items
                output.sender = split[0]
                output.recipient = station_name
                output.mode = split[1]
                output.time = int(datetime.datetime.utcnow().timestamp())

                response[index] = output  # rewrite parsed back into response list

                del output

            for item in response:
                helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage("Printing messages")))

                handle_new_message(item)

            helper.add_event((lambda: True), (lambda: ui.statusbar.showMessage("Messages handled - waiting")))

        time.sleep(SETTINGS["hoppie"]["poll-interval"])


def begin_message_poll():
    # Triggered by ui.connectButton
    # Starts thread for SERVER_ADDR polling, disables ui.connectButton and enables ui.disconnectButton and updates the
    #  status indicator label. It also logs the connection in the message log
    # Checks to ensure a callsign is entered before performing any actions

    global ui
    global connection_kill_switch
    global message_log_text

    if station_name == "":
        popup_message("Select a callsign before attempting to connect to Hoppie", error=True)
    else:
        connection_kill_switch = False
        start_new_thread(hoppie_connection_thread, (), True)

        message_log_text += f"[{datetime.datetime.utcnow().strftime('%d-%H%Mz')}] Connected as {station_name}\n"
        helper.log_update(message_log_text)

        ui.disconnectButton.setEnabled(True)
        ui.connectButton.setEnabled(False)
        ui.connectionStatusLabel.setText("Connected!")
        ui.statusbar.showMessage("Connection established")


def stop_message_poll():
    # Triggered by ui.disconnectButton
    # Triggers killswitch for SERVER_ADDR polling, disables ui.disconnectButton, sets ui.connectionStatusLabel to
    #  "Working..." and creates a new helper event. If is_hoppie_connected is true, it executes finfunc. This enables
    #  ui.connectButton, updates ui.connectionStatusLabel to disconnected and logs the disconnection in the message log.

    global ui
    global connection_kill_switch
    global is_hoppie_connected
    global message_log_text

    connection_kill_switch = True

    ui.disconnectButton.setEnabled(False)
    ui.connectionStatusLabel.setText("Working...")
    ui.statusbar.showMessage("Waiting for daemon to stop...")

    def finfunc():
        global message_log_text
        message_log_text += f"[{datetime.datetime.utcnow().strftime('%d-%H%Mz')}] Disconnected\n\n"
        helper.log_update(message_log_text)

        ui.disconnectButton.setEnabled(False)
        ui.connectButton.setEnabled(True)
        ui.connectionStatusLabel.setText("Disconnected")
        ui.statusbar.showMessage("Daemon stopped - disconnected.")

    helper.add_event((lambda: False if is_hoppie_connected else True), finfunc)

    del finfunc


def select_callsign():
    # Triggered by ui.saveCallsignButton
    # Takes contents of ui.callsignLineEdit, ensures something is there and that no polling is taking place and if all
    #  is good the contents are stored in station_name and the status indicator label is updated.

    global ui
    global station_name

    input_box_content = ui.callsignLineEdit.text()

    if is_hoppie_connected:
        popup_message("Disconnect from Hoppie before changing your callsign", error=True)
    elif input_box_content == "":
        popup_message("No callsign specified", error=True)
    else:
        ui.statusbar.showMessage("Callsign saved")
        station_name = input_box_content
        ui.currentCallsignLabel.setText(station_name)


def handle_new_message(message):
    # Used by hoppie_connection_thread
    # Plays a beep sound asynchronously, appends the entire message item to the message_log list, decodes it into a
    #  single text line, appends that to message_log_text, calls helper.update to update the message log box, and if the
    #  settings allow it, prints the message asynchronously.

    global ui
    global message_log
    global message_log_text

    ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)
    winsound.PlaySound("chime.wav", winsound.SND_ASYNC)

    message_log.append(message)

    final_text = ""

    final_text += f"[{datetime.datetime.utcfromtimestamp(message.time).strftime('%d-%H%Mz')}] "
    final_text += f"[{message.mode}] "
    final_text += f"From: {message.sender} - "
    final_text += message.message + "\n"

    message_log_text += final_text

    helper.log_update(message_log_text)

    if SETTINGS["printer"]["print-by-default"] and SETTINGS["printer"]["enable"]:
        start_new_thread(print_message, (message, "NEW MESSAGE"))


class HelperTool:
    # Used by handle_new_message, clear_message_log, begin_message_poll and stop_message_poll through an instance
    #   defined as helper
    # Required due to QHandler not being thread safe, which causes intermittent crashes if ui is modified from another
    #  thread that is not the GUI thread. This is initialised in the GUI thread, and modified from another thread, hence
    #  modifying ui from the GUI thread and not causing crashes.
    # __init__: defines self.text (str), self.updated (bool), self._timer (QTimer), sets the ontimeout and interval for
    #  the timer, and starts it
    # update: updates self.text with arg and sets self.updated to true.
    # clear: sets self.text to "" and sets self.updated to true
    # add_event: adds an event to self._events using a condition and action from the args
    # on_timeout: called on every timeout of self._timer. If self.updated is true, updates the ui.messageLogDisplay,
    #  sets the cursor to the end of that in order to create auto-scrolling and sets self.updated to false. Then, for
    #  every event added by add_event, if condition is true, the action is performed and that item is removed from
    #  the list of _events.

    def __init__(self):
        self.text = ""
        self.updated = False
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(lambda: self._on_timeout())
        self._timer.setInterval(100)
        self._timer.start()
        self._events = []

    def log_update(self, text):
        self.text = text
        self.updated = True

    def log_clear(self):
        self.text = ""
        self.updated = True

    def add_event(self, condition, action):
        self._events.append([condition, action])

    def _on_timeout(self):
        global ui

        if self.updated:
            ui.messageLogDisplay.setPlainText(self.text)
            ui.messageLogDisplay.moveCursor(QtGui.QTextCursor.End)
            self.updated = False

        for index, event in enumerate(self._events):
            if event[0]():
                event[1]()
                self._events.pop(index)


def clear_message_log():
    # Triggered by ui.clearMessageLogButton
    # As long as message_log_text is not empty and the user confirms the popup, the log box is cleared, message_log is
    #  reset to an empty list and message_log_text is reset to an empty string.

    global ui
    global message_log
    global message_log_text

    if message_log_text == "":
        popup_message("No messages received", error=True)
        return

    if popup_confirmation("Are you sure you want to clear all messages?"):
        helper.log_clear()
        message_log = []
        message_log_text = ""

    ui.statusbar.showMessage("Log cleared")


def save_message_log_to_file():
    # Triggered by ui.saveMessageLogButton
    # As long as message_log_text is not empty, a file save box will be shown for the user to save the file. If this
    #  selection has no file extension, .txt is added. The contents of message_log_text is given a header and saved to
    #  the file.

    global ui
    global message_log_text

    if message_log_text == "":
        popup_message("No messages received", error=True)
        return

    name, ok_pressed = QtWidgets.QFileDialog.getSaveFileName(None, "Save file")

    if not ok_pressed:
        return
    elif len(name.split(".")) == 1:
        name += ".txt"

    text = f"ACARS LOG generated {datetime.datetime.utcnow().strftime('%H%Mz %d/%m/%Y')}\n---------------------------" \
        f"---------\n\n" + message_log_text

    open(name, "w").write(text)

    ui.statusbar.showMessage(f"File saved as {name}")


def print_last_message():
    # Triggered by ui.printLastMessageButton
    # As long as the message_log list is not empty, the last message is printed.

    global ui
    global message_log

    if not SETTINGS["printer"]["enable"]:
        popup_message("Printing is disabled", error=True)
    elif len(message_log) == 0:
        popup_message("No messages received", error=True)
    else:
        print_message(message_log[-1], "ACARS")


def send_telex():
    global ui

    telex_box = ui.telexRecipientLine
    message_box = ui.telexMessageBox

    recipient = telex_box.text()
    message = message_box.toPlainText()

    if recipient == "" or message == "":
        popup_message("All fields must be completed")
    else:

        if request("telex", recipient, message):
            ui.telexRecipientLine.clear()
            ui.telexMessageBox.clear()


def send_inforeq():
    global ui
    global station_name

    airport_box = ui.infoAirportBox
    request_box = ui.infoTypeCombo

    airport = airport_box.text()

    if airport == "":
        popup_message("All fields must be completed")
    else:
        output_message = ""

        if request_box.currentText() == "Short TAF":
            output_message = "shorttaf"
        elif request_box.currentText() == "VATSIM ATIS":
            output_message = "vatatis"
        else:
            output_message = request_box.currentText()

        output_message += f" {airport}"
        output_message = output_message.upper()

        if request("inforeq", station_name, output_message):
            airport_box.clear()
            request_box.setCurrentIndex(0)


def send_cpdlc():
    global ui

    recipient_box = ui.cpdlcRecipientBox
    message_box = ui.cpdlcMessageBox
    response_box = ui.cpdlcReplyCombo
    response_checkbox = ui.cpdlcResponseCheck

    if recipient_box.text() == "" or message_box.toPlainText() == "":
        popup_message("All fields must be completed")
    else:

        first_try = True

        while True:
            response_id = "" if not response_checkbox.checkState() == 2 else popup_input(
                "Input ID of the message you are replying to" if first_try else "Input ID of the message you are "
                                                                                "replying to. This must be a number.")

            if not response_id:  # if cancel button is pressed False is returned
                return

            # Ensure number entered is an integer
            try:
                int(response_id)
                break
            except ValueError:
                first_try = False
                pass

        output_message = "/data2/"

        id = ""
        for i in range(random.randint(2, 4)):
            id += str(random.randint(1, 9) if i == 0 else random.randint(0, 9))

        output_message += f"{id}/{response_id}/"

        output_message += {  # Turns a reply required item into the code used in an CPDLC message
            "None required": "NE",
            "Yes": "Y",
            "No": "N",
            "Wilco/Unable": "WU",
            "Affirm/Negative": "AN",
            "Roger": "R"
        }.get(response_box.currentText())

        output_message += f"/{message_box.toPlainText().upper()}"

        if request("cpdlc", recipient_box.text(), output_message):
            recipient_box.clear()
            message_box.clear()
            response_box.setCurrentIndex(0)
            response_checkbox.setCheckState(0)

# Popups


def about_program():
    global AboutProgramWindow

    AboutProgramWindow = None

    import about

    AboutProgramWindow = QtWidgets.QWidget()
    ui = about.Ui_Form()
    ui.setupUi(AboutProgramWindow)

    label = QtWidgets.QLabel(ui.imageWidget)
    pixmap = QtGui.QPixmap("avatar.jpg")
    pixmap = pixmap.scaled(ui.imageWidget.frameGeometry().width(), ui.imageWidget.frameGeometry().height())
    label.setPixmap(pixmap)

    def garblefunc(_):

        def reverse(text):
            output = ""
            counter = len(text) - 1
            while True:
                output += text[counter]
                if counter == 0:
                    return output
                counter -= 1

        ui.mainLabel.setText(reverse(ui.mainLabel.text()))
        ui.versionLabel.setText(reverse(ui.versionLabel.text()))
        ui.madeLabel.setText(reverse(ui.madeLabel.text()))

    label.mousePressEvent = garblefunc

    del garblefunc

    AboutProgramWindow.show()

    del about
    return


def about_inforeq():
    global AboutInfoReqWindow

    import aboutInfoReq
    AboutInfoReqWindow = QtWidgets.QWidget()
    ui = aboutInfoReq.Ui_AboutInfoReq()
    ui.setupUi(AboutInfoReqWindow)
    ui.pushButton.clicked.connect(lambda: AboutInfoReqWindow.close())
    AboutInfoReqWindow.show()

    del aboutInfoReq
    return


def show_settings():

    global pos

    def toggle_printing():

        if SettingsUi.enablePrintBox.checkState() == 2:  # box is checked, default
            SettingsUi.printDisableFrame.setEnabled(True)
        else:
            SettingsUi.printDisableFrame.setEnabled(False)

    def test_print():

        global pos

        pos.close()

        dp = Dummy()

        bold_emphasis = b"\x1b\x21\x08"  # Sets text to bold
        second_typeface_emphasis = b"\x1b\x21\x01"  # Selects font B (different code to actual font size stuff)
        reset_emphasis = b"\x1b\x21\x00"  # Reset emphasis
        font_size_2x = b"\x1d\x21\x10"  # Change text size to 2x
        font_reset = b"\x1d\x21\x00"  # Reset text size

        dp.text("Test print\n\n")

        dp._raw(reset_emphasis)
        dp._raw(font_size_2x)
        dp.text("Font size two" + "\n")
        dp._raw(font_reset)

        dp._raw(second_typeface_emphasis)
        dp.text("Typeface two\n")
        dp._raw(reset_emphasis)

        dp._raw(bold_emphasis)
        dp.text("Bold text\n")
        dp._raw(reset_emphasis)

        dp.text("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"£$%^&*()-=_+[]{}'#@~;:<>?,./\\|'")

        dp.cut()

        test_handle = PosPrinter(int("0x" + SettingsUi.printProductIDLine.text(), base=16),
                                 int("0x" + SettingsUi.printVendorIDLine.text(), base=16),
                                 ignore_enable_flag=True)
        if test_handle.failed:
            return

        test_handle.print(dp.output)
        test_handle.close()

        pos.reset()

        popup_message("Test printed!")

    def save():

        global SETTINGS
        global pos

        # Check there is stuff there is meant to be stuff
        conditions = [
            [SettingsUi.printProductIDLine.text() == "" and SettingsUi.enablePrintBox.checkState() == 2,
             "The printer product ID must have a value"],
            [SettingsUi.printVendorIDLine.text() == "" and SettingsUi.enablePrintBox.checkState() == 2,
             "The printer vendor ID must have a value"],
            [SettingsUi.hoppieLoginCodeLine.text() == "", "A Hoppie login code must be supplied"],
            [4 > SettingsUi.hoppiePollIntSpin.value() > 60, "The poll interval must be between 5 and 60 seconds."],
        ]

        issues = []
        for condition in conditions:
            if condition[0]:
                issues.append(condition[1])

        if len(issues) != 0:
            message = "There were issues with the save:\n\n"
            for issue in issues:
                message += issue + "\n"

            popup_message(message, error=True)

            return  # don't save

        def f(restart_hoppie):

            global SETTINGS
            global SettingsUi
            global SettingsWindow
            global pos

            original_settings = copy.deepcopy(SETTINGS)
            proto = copy.deepcopy(SETTINGS)

            # printer stuff
            proto["printer"]["enable"] = True if SettingsUi.enablePrintBox.checkState() == 2 else False
            proto["printer"]["product"] = "0x" + SettingsUi.printProductIDLine.text()
            proto["printer"]["vendor"] = "0x" + SettingsUi.printVendorIDLine.text()
            proto["printer"]["print-by-default"] = True if SettingsUi.printAutoPrintNewBox.checkState() == 2 else False

            # hoppie stuff
            server_line_text = SettingsUi.hoppieServerAddrLine.text()
            proto["hoppie"]["address"] = "http://www.hoppie.nl/acars/system/connect.html" if server_line_text == "" \
                else server_line_text
            proto["hoppie"]["login-code"] = SettingsUi.hoppieLoginCodeLine.text()
            proto["hoppie"]["poll-interval"] = SettingsUi.hoppiePollIntSpin.value()

            # audio stuff
            proto["audio"]["play-sound"] = True if SettingsUi.audioPlaySoundBox.checkState() == 2 else False

            if proto["printer"]["enable"] and (original_settings["printer"]["enable"] != proto["printer"]["enable"]):
                pos.product_id = int(proto["printer"]["product"], base=16)
                pos.vendor_id = int(proto["printer"]["vendor"], base=16)
                pos.reset()

            SETTINGS = proto
            write_settings()

            if restart_hoppie:
                begin_message_poll()

            popup_message("Settings saved!")
            SettingsWindow.close()

        if is_hoppie_connected:
            if popup_confirmation("This will disconnect you from Hoppie. You will be reconnected afterwards.\n\n"
                                  "Continue?"):
                SettingsWindow.setEnabled(False)
                # stop hoppie
                stop_message_poll()
                # wait for it to stop

                helper.add_event((lambda: not is_hoppie_connected), (lambda: f(True)))

            return

        f(False)

    global SETTINGS
    global SettingsWindow
    global SettingsUi

    import settings as SettingsGUI

    SettingsWindow = QtWidgets.QWidget()
    SettingsUi = SettingsGUI.Ui_SettingsWindow()
    SettingsUi.setupUi(SettingsWindow)

    # prefill values
    # printer
    SettingsUi.enablePrintBox.setChecked(SETTINGS["printer"]["enable"])
    SettingsUi.printDisableFrame.setEnabled(SETTINGS["printer"]["enable"])
    SettingsUi.printProductIDLine.setText(SETTINGS["printer"]["product"][2:])
    SettingsUi.printVendorIDLine.setText(SETTINGS["printer"]["vendor"][2:])
    SettingsUi.printAutoPrintNewBox.setChecked(SETTINGS["printer"]["print-by-default"])
    # hoppie
    SettingsUi.hoppieServerAddrLine.setText(
        "http://www.hoppie.nl/acars/system/connect.html" if SETTINGS["hoppie"]["address"] == "" else SETTINGS["hoppie"][
            "address"])
    SettingsUi.hoppieLoginCodeLine.setText(SETTINGS["hoppie"]["login-code"])
    SettingsUi.hoppiePollIntSpin.setValue(SETTINGS["hoppie"]["poll-interval"])
    # sound
    SettingsUi.audioPlaySoundBox.setChecked(SETTINGS["audio"]["play-sound"])

    # attach functions
    SettingsUi.enablePrintBox.clicked.connect(lambda: toggle_printing())
    SettingsUi.printTestPushButton.clicked.connect(lambda: test_print())
    SettingsUi.saveButton.clicked.connect(lambda: save())

    # show window
    SettingsWindow.show()

    del SettingsGUI

    return


setup_logging()

app = QtWidgets.QApplication(sys.argv)
# Setup GUI
MainWindow = QtWidgets.QMainWindow()
ui = gui.Ui_MainWindow()
ui.setupUi(MainWindow)

helper = HelperTool()
pos = PosPrinter(int(SETTINGS["printer"]["product"], base=16), int(SETTINGS["printer"]["vendor"], base=16))

ui.exitMenuAction.triggered.connect(lambda: sys.exit())
ui.aboutMenuAction.triggered.connect(lambda: about_program())
ui.settingsMenuAction.triggered.connect(lambda: show_settings())

ui.connectButton.clicked.connect(lambda: begin_message_poll())
ui.disconnectButton.clicked.connect(lambda: stop_message_poll())

ui.saveCallsignButton.clicked.connect(lambda: select_callsign())

ui.clearMessageLogButton.clicked.connect(lambda: clear_message_log())
ui.saveMessageLogButton.clicked.connect(lambda: save_message_log_to_file())
ui.printLastMessageButton.clicked.connect(lambda: print_last_message())

ui.telexSendButton.clicked.connect(lambda: send_telex())
ui.infoSendButton.clicked.connect(lambda: send_inforeq())
ui.infoTypeHelpButton.clicked.connect(lambda: about_inforeq())
ui.cpdlcSendButton.clicked.connect(lambda: send_cpdlc())

# shows gui
MainWindow.show()
sys.exit(app.exec_())
