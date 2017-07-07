##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import unittest
import sys
import os
# COMPATIBILITY: since python 3.3 mock is included in unittest module
python_version = sys.version_info
if python_version[:2] <= (3, 3):
    import mock
    from mock import patch
else:
    import unittest.mock as mock
    from unittest.mock import patch

# pyConnectomist import
import pyconnectomist
from pyconnectomist.utils.pdftools import generate_pdf


class PDFReportCreator(unittest.TestCase):
    """ Test the PDF report creator:
    'pyconnectomist.utils.pdftools.generate_pdf'
    """
    def setUp(self):
        """ Define fucntion parameters.
        """
        self.kwargs = {
            "datapath": "/my/path/mock_datadir",
            "struct_file": os.path.join(
                os.path.abspath(os.path.dirname(pyconnectomist.__file__)),
                "utils", "resources", "pyconnectomist_qcfast.json"),
            "author": "Author",
            "client": "Client",
            "poweredby": "PoweredBy",
            "project": "Project",
            "timepoint": "Timepoint",
            "subject": "Subejct",
            "date": "Date",
            "title": "Title",
            "filename": "/my/path/mock_pdffile",
            "pagesize": None,
            "left_margin": 10,
            "right_margin": 10,
            "top_margin": 20,
            "bottom_margin": 20,
            "show_boundary": False,
            "verbose": 1
        }

    @mock.patch("pyconnectomist.utils.pdftools.PDFcreator.update")
    def test_normal_execution(self, mock_update):
        """ Test the normal behaviour of the function.
        """
        # Test execution
        generate_pdf(**self.kwargs)
        self.assertEqual(len(mock_update.call_args_list), 1)


if __name__ == "__main__":
    unittest.main()
