from django.test import TestCase
from flake8.engine import get_style_guide
import flake8.main
import sys
from test_project import settings


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        From flake8
        """
        packages = settings.PACKAGES_TO_TEST

        # Prepare
        flake8_style = get_style_guide(parse_argv=True, config_file=flake8.main.DEFAULT_CONFIG)
        options = flake8_style.options

        if options.install_hook:
            from flake8.hooks import install_hook
            install_hook()

        # Save to file for later printing instead of printing now
        old_stdout = sys.stdout
        sys.stdout = out = open('syntax_output', 'w+')

        # Run the checkers
        report = flake8_style.check_files(paths=packages)

        sys.stdout = old_stdout

        # Print the final report
        options = flake8_style.options
        if options.statistics:
            report.print_statistics()
        if options.benchmark:
            report.print_benchmark()
        if report.total_errors:
            out.close()
            with open("syntax_output") as f:
                self.fail("{0} Syntax warnings!\n\n{1}".format(report.total_errors, f.read()))
