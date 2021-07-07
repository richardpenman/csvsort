import unittest
import logging

from csvsort import csvsort

logging.basicConfig(level=logging.DEBUG)
logging.info("start unittest")



class CsvSortTest(unittest.TestCase):

    def test_single(self):
        logging.info("test csvsort multile file")
        csvsort(
            input_filename=[
                'tests/students_1.csv',
                'tests/students_2.csv',
            ],
            columns=[0],
            output_filename='tests/students_all.csv',
        )


if __name__ == "__main__":
    unittest.main()
