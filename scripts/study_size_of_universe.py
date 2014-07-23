#!/usr/bin/env python

from tests.test_files import TestFiles
import os
import json


def abs_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


with open(abs_path('data/primes-to-100k.txt'), 'r') as f:
    counter = 0
    for line in f:
        if not (counter % 10):
            prime = long(line.rstrip())
            print "Working with prime {}".format(prime)
            results = TestFiles.run_simulated_manually(
                'data/simulated.txt',
                universe_size=prime
            )
            c = results['stats']
            ti = results['uindex']
            print json.dumps(dict(
                stats=c.dict(),
                ratios=dict(
                    precision=c.get_precision(),
                    recall=c.get_recall()
                ),
                ti=ti
            ))
        counter += 1
