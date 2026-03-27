from tftp_client.protocol import build_rrq, build_wrq, build_ack, parse_packet, OP_RRQ


def test_build_rrq_starts_with_opcode():
    packet = build_rrq("file.txt")
    assert packet[:2] == b"\x00\x01"


def test_build_wrq_starts_with_opcode():
    packet = build_wrq("file.txt")
    assert packet[:2] == b"\x00\x02"


def test_parse_packet():
    packet = parse_packet(b"\x00\x01abc")
    assert packet.opcode == OP_RRQ
    assert packet.payload == b"abc"
