import usb_hid

IN_REPORT_LENGTH = 8
OUT_REPORT_LENGTH = 8

MACROBOARD_DESCRIPTOR2 = bytes((
    0x06, 0xFF, 0x42,         # UsagePage(Generic Desktop[1])
    0x09, 0x01,               # UsageId(System Control[128])
    0xA1, 0x01,               # Collection(Application)

    0x85, 0x01,               # ReportId(1)
    0x09, 0x01,               # UsageId(System Microphone Mute[169])
    0x15, 0x00,               # LogicalMinimum(0)
    0x26, 0xFF, 0x00,         # LogicalMaximum(255)
    0x95, IN_REPORT_LENGTH,   # ReportCount
    0x75, 0x08,               # ReportSize(8)
    0x81, 0x02,               # InReport (Outgoing from this device, into host)

    0x85, 0x01,               # ReportId(1)
    0x09, 0x01,               # UsageId(System Microphone Mute[169])
    0x15, 0x00,               # LogicalMinimum(0)
    0x26, 0xFF, 0x00,         # LogicalMaximum(255)
    0x95, OUT_REPORT_LENGTH,  # ReportCount
    0x75, 0x08,               # ReportSize(8 bit)
    0x91, 0x02,               # input
    
    0x85, 0x02,               # ReportId(2)
    0x09, 0x02,               # UsageId(Update)
    0x15, 0x00,               # LogicalMinimum(0)
    0x26, 0xFF, 0x00,         # LogicalMaximum(255)
    0x95, 0x24,               # ReportCount
    0x75, 0x08,               # ReportSize(8 bit)
    0x81, 0x02,               # InReport (Outgoing from this device, into host)
    
    0x85, 0x02,               # ReportId(2)
    0x09, 0x02,               # UsageId(Update)
    0x15, 0x00,               # LogicalMinimum(0)
    0x26, 0xFF, 0x00,         # LogicalMaximum(255)
    0x96, 0x60, 0x00,               # ReportCount
    0x75, 0x08,               # ReportSize(8 bit)
    0x91, 0x02,               # input
    
    0xC0,                     # End Collection
))

stupid_macroboard = usb_hid.Device(
    report_descriptor=MACROBOARD_DESCRIPTOR2,
    usage_page=0x01,           # Consumer Devices
    usage=0x80,                # Consumer Control
    report_ids=(1,2),           # Descriptor uses report ID 2.
    in_report_lengths=(IN_REPORT_LENGTH,24),
    out_report_lengths=(OUT_REPORT_LENGTH,60),
)
KEYBOARD_DESCRIPTOR = bytes((
    0x05, 0x01,        # Usage Page (Generic Desktop Ctrls)
    0x09, 0x06,        # Usage (Keyboard)
    0xA1, 0x01,        # Collection (Application)
    0x85, 0x03,        #   Report ID (3)
    0x05, 0x07,        #   Usage Page (Kbrd/Keypad)
    0x19, 0xE0,        #   Usage Minimum (0xE0)
    0x29, 0xE7,        #   Usage Maximum (0xE7)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x08,        #   Report Count (8)
    0x81, 0x02,        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x95, 0x01,        #   Report Count (1)
    0x75, 0x08,        #   Report Size (8)
    0x81, 0x01,        #   Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x95, 0x05,        #   Report Count (5)
    0x75, 0x01,        #   Report Size (1)
    0x05, 0x08,        #   Usage Page (LEDs)
    0x19, 0x01,        #   Usage Minimum (Num Lock)
    0x29, 0x05,        #   Usage Maximum (Kana)
    0x91, 0x02,        #   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
    0x95, 0x01,        #   Report Count (1)
    0x75, 0x03,        #   Report Size (3)
    0x91, 0x01,        #   Output (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
    0x95, 0x06,        #   Report Count (6)
    0x75, 0x08,        #   Report Size (8)
    0x15, 0x00,        #   Logical Minimum (0)
    0x26, 0xFF, 0x00,  #   Logical Maximum (255)
    0x05, 0x07,        #   Usage Page (Kbrd/Keypad)
    0x19, 0x00,        #   Usage Minimum (0x00)
    0x2A, 0xFF, 0x00,  #   Usage Maximum (0xFF)
    0x81, 0x00,        #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0xC0               # End Collection
))
stupid_keyboard = usb_hid.Device(
    report_descriptor=KEYBOARD_DESCRIPTOR ,
    usage_page=0x01,           # Consumer Devices
    usage=0x06,                # Consumer Control
    report_ids=(3,),           # Descriptor uses report ID 2.
    # This device sends 1 byte in its report.
    in_report_lengths=(8,),
    # It does not receive any reports.
    out_report_lengths=(1,),
)