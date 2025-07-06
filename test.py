import unittest
import wordninja


class TestWordNinja(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(list(wordninja.split('derekanderson')), ['derek','anderson'])

    def test_with_underscores_etc(self):
        self.assertEqual(list(wordninja.split('derek anderson')), ['derek',' ','anderson'])
        self.assertEqual(list(wordninja.split('derek-anderson')), ['derek','-','anderson'])
        self.assertEqual(list(wordninja.split('derek_anderson')), ['derek','_','anderson'])
        self.assertEqual(list(wordninja.split('derek/anderson')), ['derek','/','anderson'])

    def test_caps(self):
        self.assertEqual(list(wordninja.split('DEREKANDERSON')), ['DEREK','ANDERSON'])

    def test_digits(self):
        self.assertEqual(list(wordninja.split('win32intel')), ['win','32','intel'])

    def test_apostrophes(self):
        self.assertEqual(list(wordninja.split("that'sthesheriff'sbadge")), ["that's","the","sheriff's","badge"])

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
        lm = wordninja.LanguageModel('custom', 'test_lang.txt.gz')
        self.assertEqual(list(lm.split('derek')), ['der','ek'])

if __name__ == '__main__':
    unittest.main()
