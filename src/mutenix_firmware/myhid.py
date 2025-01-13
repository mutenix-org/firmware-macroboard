import usb_hid

IN_REPORT_LENGTH = 8
OUT_REPORT_LENGTH = 8

MACROBOARD_DESCRIPTOR2 = bytes(
    (
        0x06,
        0xFF,
        0x42,  # UsagePage(Generic Desktop[1])
        0x09,
        0x01,  # UsageId(System Control[128])
        0xA1,
        0x01,  # Collection(Application)
        0x85,
        0x01,  # ReportId(1)
        0x09,
        0x01,  # UsageId(System Microphone Mute[169])
        0x15,
        0x00,  # LogicalMinimum(0)
        0x26,
        0xFF,
        0x00,  # LogicalMaximum(255)
        0x95,
        IN_REPORT_LENGTH,  # ReportCount
        0x75,
        0x08,  # ReportSize(8)
        0x81,
        0x02,  # InReport (Outgoing from this device, into host)
        0x85,
        0x01,  # ReportId(1)
        0x09,
        0x01,  # UsageId(System Microphone Mute[169])
        0x15,
        0x00,  # LogicalMinimum(0)
        0x26,
        0xFF,
        0x00,  # LogicalMaximum(255)
        0x95,
        OUT_REPORT_LENGTH,  # ReportCount
        0x75,
        0x08,  # ReportSize(8 bit)
        0x91,
        0x02,  # input
        0x85,
        0x02,  # ReportId(2)
        0x09,
        0x02,  # UsageId(Update)
        0x15,
        0x00,  # LogicalMinimum(0)
        0x26,
        0xFF,
        0x00,  # LogicalMaximum(255)
        0x95,
        0x24,  # ReportCount
        0x75,
        0x08,  # ReportSize(8 bit)
        0x81,
        0x02,  # InReport (Outgoing from this device, into host)
        0x85,
        0x02,  # ReportId(2)
        0x09,
        0x02,  # UsageId(Update)
        0x15,
        0x00,  # LogicalMinimum(0)
        0x26,
        0xFF,
        0x00,  # LogicalMaximum(255)
        0x96,
        0x60,
        0x00,  # ReportCount
        0x75,
        0x08,  # ReportSize(8 bit)
        0x91,
        0x02,  # input
        0xC0,  # End Collection
    ),
)

stupid_macroboard = usb_hid.Device(
    report_descriptor=MACROBOARD_DESCRIPTOR2,
    usage_page=0x01,  # Consumer Devices
    usage=0x80,  # Consumer Control
    report_ids=(1, 2),  # Descriptor uses report ID 2.
    in_report_lengths=(IN_REPORT_LENGTH, 24),
    out_report_lengths=(OUT_REPORT_LENGTH, 60),
)
