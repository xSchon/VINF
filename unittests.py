import unittest
from searcher import Searcher


def find_substring_in_list(substring, string_list):
    """Check string against list of strings"""
    return [item for item in string_list if substring in item]

class TestSearcher(unittest.TestCase):
    """Create unittests for different situations from the indexer. 10/10 should pass in order to be satisfied with the search."""
    searcher = Searcher()

    """ Three simple searches based on countries """
    def test_slovak_search(self):
        """Find if Neon is found between Slovak players (rightfully)"""
        response = self.searcher.search_index(fields_to_search=['BirthCountry'],queries=['Slovakia'], results_amount='All', printable_cols=['PlayerName'])
        result = find_substring_in_list('Neon', response)
        self.assertIn('Neon', ''.join(result))
        

    def test_korean_search(self):
        """Find if Faker is found between Korean players"""
        response = self.searcher.search_index(fields_to_search=['BirthCountry'],queries=['Korea'], results_amount='All', printable_cols=['PlayerName'])
        result = find_substring_in_list('Faker', response)
        self.assertIn('Faker', ''.join(result))


    def test_negative_slovak_search(self):
        """Find if Faker (Korean player) is found between Korean players"""
        response = self.searcher.search_index(fields_to_search=['BirthCountry'],queries=['Slovakia'], results_amount='All', printable_cols=['PlayerName'])
        result = find_substring_in_list('Faker', response)
        self.assertNotIn('Faker', ''.join(result))

    """ Test for checking feedback length """
    def test_results_length(self):
        """Check if we get sufficient response of length given PlayerName"""
        response = self.searcher.search_index(fields_to_search=['PlayerName'],queries=['Perkz'], results_amount='All', printable_cols=['Team'])
        self.assertTrue(len(response) > 0)


    def test_zeroed_results_length(self):
        """Querying nonsense (Slovakia on Role) expected is no result"""
        response = self.searcher.search_index(fields_to_search=['Role'],queries=['Slovakia'], results_amount='All', printable_cols=['Team'])
        self.assertEqual(len(response), 0)

    """Tests of wiki dumped data connection to main data"""
    def test_fico_neon(self):
        """Check if Fico from Slovakia country (wiki dumped data) is found related to Slovak Players"""
        response = self.searcher.search_index(fields_to_search=['CountryInfo', 'InfoBox'],queries=['Fico', 'Fico'], results_amount='All', printable_cols=['BirthCountry'])
        result = find_substring_in_list('Slovakia', response)
        self.assertIn('Slovakia', ''.join(result))

    def test_sports_relation(self):
        """Check if Humanoid (Czech player) can be found via Czech popular sport (Ice hockey)"""
        response = self.searcher.search_index(fields_to_search=['BirthCountry', 'Sports'],queries=['Czech', 'Ice Hockey'], results_amount='All', printable_cols=['PlayerName'],search_type='AND')
        result = find_substring_in_list('Humanoid', response)
        self.assertIn('Humanoid', ''.join(result))

    """ Error argument tests """
    def test_type_error_message(self):
        """Test for error by sending nonsense (int 1 to expected fields_to_search)"""
        with self.assertRaises(TypeError):
            self.searcher.search_index(fields_to_search=1, queries=["Search"])

    def test_missing_arguments(self):
        """Test for error by missing required positional arguments"""
        with self.assertRaises(TypeError):
            self.searcher.search_index()

    """Compliacted query test"""
    def test_long_g2_bot_query(self):
        """Check if there is a player in more complicated query (there should be precisely one)"""
        response = self.searcher.search_index(fields_to_search=['Age', 'ChampionsStats', 'Team', 'TournamentResults', 'Role'],
        queries=['22.0', 'Lucian', 'G2', 'Worlds', 'Bot'], results_amount='All', printable_cols=['PlayerName'],search_type='AND')
        self.assertEqual(len(response), 1)


if __name__ == '__main__':
    unittest.main()