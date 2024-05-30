class PytestTestRunner:
    """Runs pytest to discover and run tests."""

    def __init__(self, verbosity=1, failfast=False, keepdb=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        "en"

    def run_tests(self, test_labels, *args, **kwargs):
        """Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """
        import os

        import pytest

        os.environ["DJANGO_SETTINGS_MODULE"] = "base.settings.test"

        argv = []
        if self.verbosity == 0:
            argv.append("--quiet")
        if self.verbosity == 2:
            argv.append("--verbose")
        if self.verbosity == 3:
            argv.append("-vv")
        if self.failfast:
            argv.append("--exitfirst")
        if self.keepdb:
            argv.append("--reuse-db")

        argv.extend(test_labels)
        return pytest.main(argv, *args, **kwargs)
