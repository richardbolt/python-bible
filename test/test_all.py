# Standard library imports
import unittest
from optparse import OptionParser
import sys

# Testable libraries
import test_stdref
import test_tokenizer
import test_vfilter
import test_models

loader = unittest.TestLoader()
suites = [
    loader.loadTestsFromModule(test_stdref),
    loader.loadTestsFromModule(test_tokenizer),
    loader.loadTestsFromModule(test_vfilter),
    #loader.loadTestsFromModule(test_models),
]
comprehensive_suite = unittest.TestSuite(suites)


def main(argv):
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--verbosity", type="int", dest="verbosity", default = 1)

    (opts, args) = parser.parse_args()
    #~ if len(args) != 1:
        #~ parser.error("incorrect number of arguments")

    result = unittest.TextTestRunner(verbosity=opts.verbosity).run(comprehensive_suite)

    if result.wasSuccessful():
        rc = 0
    else:
        rc = 1

    return rc



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
    #unittest.TextTestRunner().run(suite)
