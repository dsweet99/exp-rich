from benchmarks import benchmarks as benchmarks_module
from benchmarks.benchmarks import TextSuite


def test_benchmarks_textsuite_importable():
    suite = TextSuite()
    suite.setup()
    suite.time_wrapping()
    suite.time_indent_guides()
    suite.time_fit()
    suite.time_split()
    suite.time_divide()
    suite.time_align_center()
    suite.time_render()
    assert benchmarks_module.TextSuite is TextSuite
