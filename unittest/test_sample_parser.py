#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2016 Fedele Mantuano (https://twitter.com/fedelemantuano)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import unittest

base_path = os.path.realpath(os.path.dirname(__file__))
root = os.path.join(base_path, '..')
sample_zip = os.path.join(root, 'unittest', 'samples', 'test.zip')
sample_zip_1 = os.path.join(root, 'unittest', 'samples', 'test1.zip')
sample_txt = os.path.join(root, 'unittest', 'samples', 'test.txt')
sys.path.append(root)
import src.modules.sample_parser as sample_parser


class TestSampleParser(unittest.TestCase):
    parser = sample_parser.SampleParser()

    def test_errors(self):
        with self.assertRaises(sample_parser.Base64Error):
            self.parser.fingerprints_from_base64("\test")

    def test_is_archive(self):
        """Test is_archive functions."""

        with open(sample_zip, 'rb') as f:
            data = f.read()
            data_base64 = data.encode('base64')

        sha1_archive = "8760ff1422cf2922b649b796cfb58bfb0ccf7801"

        # Test is_archive with write_sample=False
        result1 = self.parser.is_archive(data)
        self.assertEqual(True, result1)

        result2 = self.parser.is_archive_from_base64(data_base64)
        self.assertEqual(True, result2)

        self.assertEqual(result1, result2)

        # Test is_archive with write_sample=True
        result = self.parser.is_archive(data, write_sample=True)
        self.assertEqual(os.path.exists(result[1]), True)

        # Sample on disk
        with open(result[1], 'rb') as f:
            data_new = f.read()

        result = self.parser.fingerprints(data_new)
        self.assertEqual(sha1_archive, result[1])

        result = self.parser.is_archive_from_base64(
            data_base64,
            write_sample=True
        )
        self.assertEqual(True, result[0])
        self.assertEqual(os.path.exists(result[1]), True)

        # Test is_archive with write_sample=True
        result = self.parser.is_archive(data, write_sample=True)
        self.assertIsInstance(result, tuple)

    def test_fingerprints(self):
        """Test fingerprints functions."""

        with open(sample_zip, 'rb') as f:
            data = f.read()
            data_base64 = data.encode('base64')

        sha1_archive = "8760ff1422cf2922b649b796cfb58bfb0ccf7801"

        # Test fingerprints
        result1 = self.parser.fingerprints(data)[1]
        self.assertEqual(sha1_archive, result1)

        result2 = self.parser.fingerprints_from_base64(data_base64)[1]
        self.assertEqual(sha1_archive, result2)

        self.assertEqual(result1, result2)

    def test_parser_sample(self):
        """Test for parse_sample."""

        with open(sample_zip, 'rb') as f:
            data = f.read()

        with open(sample_txt, 'rb') as f:
            data_txt_base64 = f.read().encode('base64')

        self.parser.parse_sample(data, "test.zip")
        result = self.parser.result

        md5_file = "d41d8cd98f00b204e9800998ecf8427e"
        size_file = 0
        size_zip = 166

        self.assertIsInstance(result, dict)
        self.assertEqual(result['size'], size_zip)
        self.assertIsNotNone(result['files'])
        self.assertIsInstance(result['files'], list)
        self.assertEqual(len(result['files']), 1)
        self.assertEqual(result['files'][0]['size'], size_file)
        self.assertEqual(result['files'][0]['md5'], md5_file)
        self.assertEqual(result['files'][0]['filename'], "test.txt")
        self.assertEqual(result['files'][0]['payload'], data_txt_base64)

    def test_tika(self):
        parser = sample_parser.SampleParser(tika_enabled=True)

        with open(sample_zip_1, 'rb') as f:
            data = f.read()

        parser.parse_sample(data, "test1.zip")
        result = parser.result

        self.assertIn('tika', result)
        self.assertIsInstance(result['tika'], dict)
        self.assertIn('content', result['tika'])

        for i in result['files']:
            self.assertIn('tika', i)
            self.assertIsInstance(i['tika'], dict)
            self.assertIn('content', i['tika'])
            self.assertIn('google', i['tika']['content'])

        with open(sample_zip_1, 'rb') as f:
            data = f.read().encode('base64')

        parser.parse_sample_from_base64(data, "test2.zip")
        result = parser.result

        self.assertIn('tika', result)
        self.assertIsInstance(result['tika'], dict)
        self.assertIn('content', result['tika'])

        for i in result['files']:
            self.assertIn('tika', i)
            self.assertIsInstance(i['tika'], dict)
            self.assertIn('content', i['tika'])
            self.assertIn('google', i['tika']['content'])


if __name__ == '__main__':
    unittest.main()