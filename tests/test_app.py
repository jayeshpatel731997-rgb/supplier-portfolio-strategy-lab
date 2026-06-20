from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"


def test_streamlit_app_renders_without_exceptions():
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    assert not app.exception
    assert app.title[0].value == "Supplier Portfolio Strategy Lab"
    assert len(app.metric) >= 7
    assert len(app.dataframe) >= 2
    rendered_markdown = "\n".join(element.value for element in app.markdown)
    assert "Game Theory Lens: Which Sourcing Game Should We Play?" in rendered_markdown
    assert "Strategic quadrant" in rendered_markdown
    assert "Buyer objective" in rendered_markdown
    assert "Supplier behavior assumption" in rendered_markdown
    assert "What to avoid" in rendered_markdown
    assert "Next sourcing action" in rendered_markdown
    assert "Nash Bargaining Calculator" in rendered_markdown
