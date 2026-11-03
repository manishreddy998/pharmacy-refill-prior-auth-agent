from streamlit.testing.v1 import AppTest
def test_dashboard_renders():
    at = AppTest.from_file("../dashboard/app.py", default_timeout=60).run()
    assert not at.exception
    assert at.metric[0].value == "300"
