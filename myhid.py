import usb_hid

IN_REPORT_LENGTH = 8
OUT_REPORT_LENGTH = 8

MACROBOARD_DESCRIPTOR = bytes((
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
    0xC0,                     # End Collection
))

stupid_macroboard = usb_hid.Device(
    report_descriptor=MACROBOARD_DESCRIPTOR,
    usage_page=0x01,           # Consumer Devices
    usage=0x80,                # Consumer Control
    report_ids=(1,),           # Descriptor uses report ID 2.
    # This device sends 1 byte in its report.
    in_report_lengths=(IN_REPORT_LENGTH,),
    # It does not receive any reports.
    out_report_lengths=(OUT_REPORT_LENGTH,),
)
