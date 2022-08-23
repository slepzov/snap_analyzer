from django.test import TestCase

from snap_analyzer_django.views import pars
import shutil

class ViewsTestCase(TestCase):
    def test_pars(self):
        shutil.copy2(r'snap_analyzer\snap_analyzer_django\tests\test_files\snap.7811AX0-1.220810.142302.tgz', r'snap_analyzer\snap_analyzer_django\tests\snap.7811AX0-1.220810.142302.tgz')
        result = pars('snap_analyzer\snap_analyzer_django\\tests\snap.7811AX0-1.220810.142302.tgz')
        ex = {'product_name': 'Yadro CX1-33', 'type': '2072-324', 'serial_number': '7811AX0',
              'code_level': '8.3.1.6', 'date_timestamp': '14:23:02', 'number_of_enclosure': 3}
        self.assertEqual(ex, result)