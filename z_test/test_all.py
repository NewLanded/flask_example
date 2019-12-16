if __name__ == '__main__':
    import pytest

    pytest.main(["-s", "--tb=short", "--disable-warnings", "--html=./report.html"])
