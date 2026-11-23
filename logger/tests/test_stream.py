import pytest

from logger.stream import Status, parse

LINE = b"3600000,512,498,601,587,93,120,tracking"


def test_parses_documented_example():
    assert parse(LINE) == Status(3600000, 512, 498, 601, 587, 93, 120, "tracking")


def test_strips_crlf_and_whitespace():
    assert parse(LINE + b"\r\n") == parse(LINE)
    assert parse(b"  " + LINE + b" \n") == parse(LINE)


def test_parked_state():
    assert parse(b"0,0,0,0,0,0,90,parked").state == "parked"


def test_accepts_boundaries():
    assert parse(b"4294967295,1023,0,1023,0,180,165,tracking") == Status(
        4294967295, 1023, 0, 1023, 0, 180, 165, "tracking"
    )
    assert parse(b"0,0,1023,0,1023,0,15,parked").tilt == 15


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"\r\n",
        b"87,1,tracking",
        b"1,2,3,4,5,6,60",
        b"1,2,3,4,5,6,60,tracking,extra",
        b"1,2,3,4,5,6,60,TRACKING",
        b"1,2,3,4,5,6,60,sleeping",
        b"1,abc,3,4,5,6,60,tracking",
        b"1,2.5,3,4,5,6,60,tracking",
        b"1,+2,3,4,5,6,60,tracking",
        b"-1,2,3,4,5,6,60,tracking",
        b"1, 2,3,4,5,6,60,tracking",
        b"1,,3,4,5,6,60,tracking",
        b"4294967296,2,3,4,5,6,60,tracking",
        b"1,1024,3,4,5,6,60,tracking",
        b"1,2,3,4,1024,6,60,tracking",
        b"1,2,3,4,5,181,60,tracking",
        b"1,2,3,4,5,6,14,tracking",
        b"1,2,3,4,5,6,166,tracking",
        b"\x00\xff\xfe garbage",
        "1,١,3,4,5,6,60,tracking".encode(),  # Arabic-Indic digit one
        b"1," * 40 + b"tracking",
    ],
)
def test_rejects_malformed(raw):
    assert parse(raw) is None
