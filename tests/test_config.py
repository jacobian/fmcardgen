from fmcardgen import config


def test_empty_config():
    cnf = config.Config()
    assert len(cnf.text_fields) == 1
    assert cnf.text_fields[0].source == "title"