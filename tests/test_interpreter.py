from box_language.interpreter import Interpreter, BoxError


def test_print_and_variable():
    output = []
    Interpreter(output.append).run(
        "#Start#\nP {123321} box {A}!\n>{A}\n#End#"
    )
    assert output == [123321]


def test_yesli_and_nosli():
    output = []
    Interpreter(output.append).run(
        "#Start#\n"
        "P {7} box {A}!\n"
        "P {7} box {B}!\n"
        "yesli box {A}==box {B} to P {equal}!\n"
        "Nosli P {not equal}!\n"
        "#End#"
    )
    assert output == ["equal"]


def test_missing_start():
    try:
        Interpreter().run("P {hello}!\n#End#")
    except BoxError as exc:
        assert "Err start not found" in str(exc)
    else:
        raise AssertionError("Expected BoxError")
