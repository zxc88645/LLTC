from lltc.command_parser import parse_command


def test_parse_known_commands():
    # The parser uses keyword heuristics rather than a static mapping, so the
    # input strings may contain additional words.
    assert parse_command("幫我查看這台作業系統版本") == "uname -a"
    assert parse_command("請幫我安裝CUDA") == "sudo apt install -y cuda-toolkit"
    assert parse_command("幫我檢查當前裝置有哪些設備") == "lspci"


def test_parse_unknown_command():
    assert parse_command("未知指令") is None
