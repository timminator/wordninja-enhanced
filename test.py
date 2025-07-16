import os
import unittest

import wordninja_enhanced as wordninja


class TestWordNinja(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(list(wordninja.split('derekanderson')), ['derek', 'anderson'])

    def test_with_underscores_etc(self):
        self.assertEqual(list(wordninja.split('derek anderson')), ['derek', ' ', 'anderson'])
        self.assertEqual(list(wordninja.split('derek-anderson')), ['derek', '-', 'anderson'])
        self.assertEqual(list(wordninja.split('derek_anderson')), ['derek', '_', 'anderson'])
        self.assertEqual(list(wordninja.split('derek/anderson')), ['derek', '/', 'anderson'])

    def test_caps(self):
        self.assertEqual(list(wordninja.split('DEREKANDERSON')), ['DEREK', 'ANDERSON'])

    def test_digits(self):
        self.assertEqual(list(wordninja.split('win32intel')), ['win', '32', 'intel'])

    def test_apostrophes(self):
        self.assertEqual(list(wordninja.split("that'sthesheriff'sbadge")), ["that's", "the", "sheriff's", "badge"])

    def test_candidates(self):
        expected = [
                ['derek', 'anderson'],
                ['derek', 'anders', 'on'],
                ['derek', 'and', 'ers', 'on']
        ]
        candidates_list = wordninja.candidates("derekanderson", 3)
        self.assertEqual(candidates_list, expected)

    def test_rejoin(self):
        self.assertEqual(wordninja.rejoin("that'sthesheriff's\"badge\" youarewearing!"), "that's the sheriff's \"badge\" you are wearing!")

    def test_custom_model(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        custom_dict_file_path = os.path.join(script_dir, 'test_lang.txt.gz')

        lm = wordninja.LanguageModel('custom', custom_dict_file_path)
        self.assertEqual(list(lm.split('derek')), ['der', 'ek'])

    def test_add_words(self):
        lm = wordninja.LanguageModel(
            language="en",
            add_words=['Palaeoloxodon'],
            blacklist=[],
        )
        self.assertEqual(lm.rejoin("Palaeoloxodonisanextinctgenusofelephant."), "Palaeoloxodon is an extinct genus of elephant.")

    def test_add_existing_words(self):
        lm = wordninja.LanguageModel(
            language="en",
            add_words=['inc'],
            blacklist=[],
            add_to_top=True,
            overwrite=True,
        )
        self.assertEqual(lm.rejoin("coinc"), "co inc")


if __name__ == '__main__':
    unittest.main()
