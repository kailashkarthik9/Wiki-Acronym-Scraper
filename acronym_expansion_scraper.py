import wikipediaapi
from collections import deque
import re
import json


class AcronymExpansionScraper:
    """
    This class encapsulates all the functionality related to scraping expansions for medical acronyms from Wikipedia
    It makes use of the python wrapper over Wikimedia APIs - Wikipedia-API (https://github.com/martin-majlis/Wikipedia-API/)
    To install the wrapper package run "pip install wikipedia-api"
    """

    def __init__(self):
        """
        The class constructor initializes the wiki library instance
        """
        self.wiki = wikipediaapi.Wikipedia('en')
        self.page = None
        self.medical_term_cues = ['medical', 'medicine', 'biological', 'biology', 'scientific', 'science']
        self.disambiguation_page_suffix = '_(disambiguation)'

    @staticmethod
    def print_sections(sections, level=0):
        """
        A developer utility to print all the sections in a wiki page
        :param sections: List of all sections in a page
        :param level: The nesting level of the first section in sections
        :return: None
        """
        for section in sections:
            print("%s: %s - %s" % ("*" * (level + 1), section.title, section.text[0:40]))
            AcronymExpansionScraper.print_sections(section.sections, level + 1)

    def load_page(self, query):
        """
        This method loads the wiki disambiguation page corresponding to the query and sets the class parameter page
        :param query: The query for which wiki is to be searched
        :return: None
        """
        self.page = self.wiki.page(query + self.disambiguation_page_suffix)
        if not self.page.exists():
            raise Exception(query + ' did not return a valid disambiguation page on Wikipedia')

    def is_medical_section(self, section_title):
        """
        This method analyzes the section's title to determine if it is a medical section
        :param section_title: The title of the section to be analyzed
        :return: Boolean determining if it is a medical section or not
        """
        section_title_lower = section_title.lower()
        cues_found = [True for cue in self.medical_term_cues if cue in section_title_lower]
        if cues_found:
            return True
        return False

    def get_medical_expansions(self):
        """
        This method gets all the medical expansions from the wiki disambiguation page
        :return: A list of all the medical expansions in the page
        """
        if not self.page:
            raise Exception('Wikipedia page uninitialized. Can\'t search page that doesn\'t exist')
        sections_to_scan = deque(self.page.sections)
        while sections_to_scan:
            section = sections_to_scan.pop()
            if self.is_medical_section(section.title):
                if section.sections:
                    for subsection in section.sections:
                        sections_to_scan.appendleft(subsection)
                else:
                    return section.text.split('\n')

    @staticmethod
    def load_abbreviations(file_name, threshold):
        expansions_file = open(file_name, 'r')
        lines = expansions_file.readlines()
        abbreviations = []
        for line in lines:
            abbreviation = re.split(r'[\t\n]', line)
            if int(abbreviation[1]) > threshold:
                abbreviations.append(abbreviation[0])
        return abbreviations

    @staticmethod
    def format_wiki_output(expansions):
        # Not Implemented Yet - Will have to split the expansions and definition and handle disjunctions
        return expansions


if __name__ == '__main__':
    sample_query = 'PT'

    expansion_scraper = AcronymExpansionScraper()
    abbreviations = expansion_scraper.load_abbreviations('abbreviation_counts.txt', 1)
    abbreviations_count = len(abbreviations)
    abbreviation_expansions = dict()
    for idx, abbreviation in enumerate(abbreviations):
        print(str(idx) + ' of ' + str(abbreviations_count))
        try:
            expansion_scraper.load_page(abbreviation)
            medical_expansions = expansion_scraper.get_medical_expansions()
            if medical_expansions:
                medical_expansions_formatted = expansion_scraper.format_wiki_output(medical_expansions)  # Not Implemented Yet
                abbreviation_expansions[abbreviation] = medical_expansions_formatted
        except:
            pass
    with open('abbreviations.json', 'w') as fp:
        json.dump(abbreviation_expansions, fp)
    # print(str(abbreviation_expansions))
