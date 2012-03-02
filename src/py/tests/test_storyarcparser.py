# encoding: utf-8

'''
This module contains all unittests for the storyarcparser module.

Created on Feb 2, 2012
@author: cbanack
'''

from unittest import TestCase
from unittest.loader import TestLoader
from storyarcparser import initialize, shutdown, extract, _ex_strict, prime
from dbmodels import IssueRef

#==============================================================================
def load_tests(loader, tests, pattern):
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestStoryArcParser) 

#==============================================================================
class TestStoryArcParser(TestCase):

   # --------------------------------------------------------------------------
   def test_ex_strict_from_one_digit(self):
      ''' Test basic titles with the required 'one' as the digit '1' '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt 1  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt. 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey # 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey #1  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey no. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey number 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey num 1"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey num. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey epiSode 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ep. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey VOLUME 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ch. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey chapter 1"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_from_one_word(self):
      ''' Test basic titles with the required 'one' as the word 'one' '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey part one  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt one  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt. One  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey # ONE  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey #one  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey no. One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey number one"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey num oNe"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey num. oNE"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey epiSode One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ep. One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol. One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol one"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey VOLUME One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ch. one"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey chapter one"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_from_one_roman(self):
      ''' Test basic titles with the required 'one' as the roman 'i' '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey part i  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt I  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt. I "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey epiSode i"))
      self.assertEquals("Family Guy", _ex_strict(r"Family Guy ep. I"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol. I"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey bk. i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ch. i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey chapter I"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_with_punctuation(self):
      ''' Test basic titles with delimiting punctuation '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey, part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey,part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey , part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey- part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - bk. 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey-part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey:book 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey :  part 1  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey,pt 1  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey-pt. 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey -# 1  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: #1  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey: no. 1"))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey : no. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, number 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey,num 1"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey: num. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - epiSode 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, ep. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey , vol. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, vol 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - VOLUME 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: ch. 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: chapter 1"))
      
      self.assertEquals("The Grey", _ex_strict(r"The Grey, part one  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey: pt one  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey - pt. One  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: # ONE  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, #one  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey - no. One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - number one"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, num oNe"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey: num. oNE"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey-epiSode One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: ep. One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, vol. One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey-vol one"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey -VOLUME One"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey :ch. one"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: book one"))
      
      self.assertEquals("The Grey", _ex_strict(r"The Grey- part i  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey: pt I  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey, pt. I "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: epiSode i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - ep. I"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ,vol. I"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, vol i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey-VOLUME i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey:ch. i"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey,   chapter I"))
      
   def test_ex_strict_from_brackets(self):
      ''' Test basic titles with the required 'one' inside brackets '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey (part 1)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (pt 1  )"))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (pt. 1  )"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey( # 1)  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (#1)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (no. 1)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (number 1)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ( num 1 )"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey (num. 1 )"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [epiSode 1]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ep. 1]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ vol. 1]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ vol 1]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ VOLUME 1]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ch. 1]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ chapter 1]"))
      
      self.assertEquals("The Grey", _ex_strict(r"The Grey ( part one)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey ( pt one)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey [pt. One]  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [# ONE  ]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [#one  ]"))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey [no. One]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (number one)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (num oNe)"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey ( num. oNE)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ( epiSode One )"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - ( ep. One )"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey : [vol. One]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, [ vol one]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [book One]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ( ch. one  )"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [chapter one]"))

      self.assertEquals("The Grey", _ex_strict(r"The Grey (part i)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (pt I  )"))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (pt. I) "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (epiSode i)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, ( ep. I)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey -(vol. I)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey: (vol i)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey    ( VoLUME i)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey [ch. i]"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey   [chapter I]"))
   
   # --------------------------------------------------------------------------
   def test_ex_strict_with_of(self):
      ''' Test basic titles with 'of' in the storyarc numbering '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey part 1 of 3  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt 1 (of 4)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt. 1 of three  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey # 1of4 "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey #1of 5  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (no. 1 of 5)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey book 1 (of 1)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey num 1of 54"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey (num. 1 of four) "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey epiSode 1 of 2"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ep. 1 of 3"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (vol. 1 of 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol 1 (of FIVE)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey VOLUME 1 of 2"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (ch. 1 of 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (chapter 1 of FOUR  )"))
      
      self.assertEquals("The Grey", _ex_strict(r"The Grey, (part one of 3)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey: pt one of 3 "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey - (pt. One of Four)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey #1 (of four)  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, (#1 of 4)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (no. One of 2)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (number one of 4)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey num oNe (of three)"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey (num. oNE of 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (epiSode One of four)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ep. One (of three)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (vol. One of 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol one (of 5)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (VOLUME One of 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (ch. one of four)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (chapter one of 3)"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_with_slash(self):
      ''' Test basic titles with 'slashes' in the storyarc numbering '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey part 1 \ 3  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt 1/4  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey pt. 1 / three  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey # 1\4 "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey #1\ 5  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (no. 1 / 5)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey number 1 (/ 1)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey num 1/ 54"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey (num. 1 \ four) "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey epiSode 1 / 2"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ep. 1 / 3"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (vol. 1 / 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey vol 1 (/FIVE)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey VOLUME 1 / 2"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (ch. 1 \ 3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (chapter 1 / FOUR  ) "))
      
      self.assertEquals("The Grey", _ex_strict(r"The Grey, (part one / 3)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey: pt one / 3 "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey - (pt. One/Four) "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey #1 (/ four)  "))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, (#1/4)  "))
      self.assertEquals("The Grey", _ex_strict(r"  The Grey (no. One\2)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (number one\4)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey num oNe (\ three)"))
      self.assertEquals("The Grey", _ex_strict(r"   The Grey (num. oNE/3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (epiSode One/four)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ep. One (/three)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (vol. One/3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey book one (/5)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (VOLUME One/3)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (ch. one/four)"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey (chapter one\3)"))
   
   # --------------------------------------------------------------------------
   def test_ex_strict_extra_text(self):
      ''' Test basic titles with text following the storyarc numbering '''
      self.assertEquals("The Grey", _ex_strict(r"The Grey, Part 1: quickening"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey Part 1, 3 of time"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey:ep. 1 , the greyening"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey, ch. one; greyening"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey ch. one- not twoer"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey - ch. one; - not toer"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey-part i:: a title"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey:part i: 'two of 3'"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey   part i 'two of 3'"))
      self.assertEquals("The Grey", _ex_strict(r'The Grey - chapter one "help!"'))
      self.assertEquals("The Grey", _ex_strict(r'The Grey - ep. 1 (help!)'))
      self.assertEquals("The Grey", _ex_strict(r'The Grey - ep. 1 ("help!")'))
      self.assertEquals("The Grey", _ex_strict(r'The Grey - ep. 1 ["help!"]'))
      self.assertEquals("The Grey", _ex_strict(r'The Grey - ep. 1 [3 lp!]'))
      self.assertEquals("The Grey", _ex_strict(r'The Grey - ep. 1 {of what}'))
      self.assertEquals("Cimmeria", _ex_strict(r"Cimmeria (Part 1): Hunter's Mn"))

      ''' these ones SHOULD fail '''   
      self.assertEquals("", _ex_strict(r"The Grey part one of two nope"))
      self.assertEquals("", _ex_strict(r"The Grey: chapter one is cool"))
      self.assertEquals("", _ex_strict(r"The Grey - ep i this isn't"))
      self.assertEquals("", _ex_strict(r'The Grey - chapter one "a'))
      self.assertEquals("", _ex_strict(r"The Grey - chapter one 'a"))
   
   
   # --------------------------------------------------------------------------
   def test_ex_strict_utf8_chars(self):
      ''' Test basic titles with text containing non-ascii characters '''
      self.assertEquals("The Greβy", _ex_strict(r"The Greβy, Part 1"))
      self.assertEquals("The Grey", _ex_strict(r"The Grey Part 1, 3 of tβime"))
      self.assertEquals("The Greyβ", _ex_strict(r"The Greyβ:ep. 1, dideβ"))
      
      
   # --------------------------------------------------------------------------
   def test_ex_strict_quoted_arcs(self):
      ''' Test basic titles with text quotation marks around the arcname '''
      self.assertEquals("The Grey", _ex_strict(r"'The Grey', Part 1"))
      self.assertEquals("The Grey", _ex_strict(r'"The Grey", ch1'))
      self.assertEquals("The Grey", _ex_strict(r" ' The Grey  ' , ep. one: cool"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_plural_arcs(self):
      ''' Test basic titles with plural arcnames '''
      self.assertEquals("Conan", _ex_strict(r"Conan Parts 1 and 2"))
      self.assertEquals("Conan", _ex_strict(r"Conan: books 1 and 2"))
      self.assertEquals("Conan", _ex_strict(r"Conan: vols. 1 and 2 of 5"))
      self.assertEquals("Conan", _ex_strict(r"Conan: chs. 1, 2 and 3"))
      self.assertEquals("Conan", _ex_strict(r"Conan: pts 1 & 2"))
      self.assertEquals("Conan", _ex_strict(r"Conan: part 1 and 2 & 3"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_empty_arcs(self):
      ''' Test basic titles with no arcname '''
      self.assertEquals("", _ex_strict(r"1"))
      self.assertEquals("", _ex_strict(r"   "))
      self.assertEquals("", _ex_strict(r"pt. i, 'The Quickening'"))
      self.assertEquals("", _ex_strict(r"part one  "))
      self.assertEquals("", _ex_strict(r"part one: the end  "))
      self.assertEquals("", _ex_strict(r"volume one"))
      self.assertEquals("", _ex_strict(r"number one"))
      self.assertEquals("", _ex_strict(r"no. one: the joker is back"))
      self.assertEquals("", _ex_strict(r"book one"))
      self.assertEquals("", _ex_strict(r"book one: prelude"))
      self.assertEquals("", _ex_strict(r": part one"))
      self.assertEquals("", _ex_strict(r"- ch. one"))
      self.assertEquals("", _ex_strict(r"episode 1"))
      self.assertEquals("", _ex_strict(r'ep. 1, "a new hope"'))
      self.assertEquals("", _ex_strict(r"Part 1"))
      self.assertEquals("", _ex_strict(r"Part 1 (of 3)"))
      self.assertEquals("", _ex_strict(r"(Part 1 of 3)"))
      self.assertEquals("", _ex_strict(r", Part 1 of 3"))
      
   # --------------------------------------------------------------------------
   def test_ex_strict_should_fail(self):
      ''' Test basic titles whose arcs aren't  found in strict mode. '''
      
      self.assertEquals("", _ex_strict(r"The Grey, 1"))
      self.assertEquals("", _ex_strict(r"The Grey One"))
      self.assertEquals("", _ex_strict(r"The Grey I"))
      self.assertEquals("", _ex_strict(r"The Grey - I"))
      self.assertEquals("", _ex_strict(r"The Grey: I"))
      self.assertEquals("", _ex_strict(r"The Grey: I"))
   
   # --------------------------------------------------------------------------
   def test_prime_simple(self):
      ''' Test basic issue title parsing in the prime() function. '''
      initialize()
      # "Dark Knight" is the only one that has two numbered arcs
      self.assertEquals(["Dark Knight"], prime([
         IssueRef("5", "1005", "Dark Knight part 1 of 4"),                                                
         IssueRef("6", "1006", "Dark Knight part 2 of 4"),                                                
         IssueRef("7", "1007", "blah"),                                                
         IssueRef("8", "1008", "blah"),                                                
         IssueRef("9", "1009", "blah"),                                                
      ], True));
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_prime_simple2(self):
      ''' Test basic issue title parsing in the prime() function. '''
      initialize()
      self.assertEquals(["Purgatory", "Death"], prime([
         IssueRef("9", "1009", "Purgatory Part One"),                                                
         IssueRef("10", "1010", "Purgatory Part iv"),                                                
         IssueRef("11", "1011", "Death, Prelude"),                                                
         IssueRef("12", "1012", " Death pt. I"),                                                
         IssueRef("13", "1013", "'Death' part II"),                                                
         IssueRef("14", "1014", "'Death' Conclusion"),                                                
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
      ], True));
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_prime_simple3(self):
      ''' Test basic issue title parsing in the prime() function. '''
      initialize()
      self.assertEquals(["Rage"], prime([
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
         IssueRef("17", "1017", "Rage, ep. 1"),
         IssueRef("18", "1018", "Rage, books three, four, and five"),
      ], True));
      shutdown()
      
      
   # --------------------------------------------------------------------------
   def test_prime_tricky1(self):
      ''' Test more complicated issue title parsing in the prime() function. '''
      
      # if two halves of a title can BOTH be parsed into arcs, then neither of
      # them is any good, ignore them both
      initialize()
      self.assertEquals([], prime([
         IssueRef("15", "1015", "Part 1 - Cool; Part 2 - Less Cool"),                                                
         IssueRef("16", "1016", "Part 3 - Rad; Part 4 - Less Rad"),
         IssueRef("17", "1017", "Parts 1 and 2"),
      ], True));
      
      self.assertEquals([], prime([
         IssueRef("15", "1015", "Dark Things, Part 3: Cyborg in Cogs part 2"),                                                
         IssueRef("16", "1016", "Dark Things, Chapter 3: What now? part 3"),                                                
      ], True));
      
      shutdown()
      
      
   # --------------------------------------------------------------------------
   def test_prime_tricky2(self):
      ''' Test more complicated issue title parsing in the prime() function. '''
      
      # don't let multiple colons mess things up!
      initialize()
      self.assertEquals(["JLA: Omega"], prime([
         IssueRef("15", "1015", "JLA: Omega, Part One: Worlds Collide"),                                                
         IssueRef("16", "1016", "JLA: Omega, Part Two: The Power"),
         IssueRef("17", "1017", "JLA: Omega, Part Three: D.C. Challenge!"),
      ], True));
      
      shutdown()
      
   # --------------------------------------------------------------------------
   def test_prime_tricky3(self):
      ''' Test more complicated issue title parsing in the prime() function. '''
   
      # words like 'the' and '!' can be ignored during comparision
      initialize()
      self.assertEquals(["Demon Ride!"], prime([
         IssueRef("15", "1015", "Demon Ride"),                                                
         IssueRef("16", "1016", "Demon Ride! Part Two: The Power"),
      ], True));
      shutdown()
      
      initialize()
      self.assertEquals(["Demon Ride"], prime([
         IssueRef("15", "1015", "Demon Ride, part One"),                                                
         IssueRef("16", "1016", "Demon Ride! Part Two: The Power"),
      ], True));
      shutdown()
      
      initialize()
      self.assertEquals(["Demon Ride"], prime([
         IssueRef("15", "1015", "Demon Ride, Part one"),                                                
         IssueRef("16", "1016", "Demon Ride! Part Two: The Power"),
         IssueRef("17", "1017", "Demon Ride!!!, Part 4"),                                                
      ], True));
      shutdown()
   
         
   # --------------------------------------------------------------------------
   def test_prime_mishmash(self):
      ''' tests a more complicated collection of issue titles in prime() '''
      initialize()
      self.assertEquals(["White Knight", "Dark Knight", "Death",
            "Bigger", "Rage"], prime([
         IssueRef("3", "1003", "White Knight part 1 of 4"),                                                
         IssueRef("4", "1004", "Dark Knight part 1 of 4"),                                                
         IssueRef("5", "1005", "Dark Knight part 2 of 4"),                                                
         IssueRef("6", "1006", "White Knight part 4 of 4"),                                                
         IssueRef("7", "1007", "blah"),                                                
         IssueRef("8", "1008", "blah"),                                                
         IssueRef("9", "1009", "blah"),                                                
         IssueRef("10", "1010", "blah"),                                                
         IssueRef("11", "1011", "Death, Prelude"),                                                
         IssueRef("12", "1012", " Death ch. I"),                                                
         IssueRef("13", "1013", "'Death' episode II"),                                                
         IssueRef("14", "1014", "'Death' Conclusion"),                                                
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
         IssueRef("17", "1017", "The One"),
         IssueRef("18", "1018", "Bigger book Two"),
         IssueRef("19", "1019", "Bigger bk One"),
         IssueRef("20", "1020", "Rage, ep. 1"),
         IssueRef("21", "1021", "Rage, eps. TWO and 3"),
      ], True));
      shutdown()   
      
   # --------------------------------------------------------------------------
   def test_matching_simple(self):
      ''' tests that matching issues to the primed arcs works properly '''
      initialize()
      
      # nothing should match before we've been primed!
      self.assertEquals("", extract(r"  dark knight conclusion"))
      self.assertEquals("", extract(r"Death part 1"))
      self.assertEquals("", extract(r"Rage, ep. 1"))
      self.assertEquals("", extract(r"Bigger, part 3"))
      
      # prime with "Dark Knight"
      prime([ IssueRef("5", "1005", "Dark Knight part 1 of 4"),                                                 
              IssueRef("6", "1006", "Dark Knight part 2 of 4") ] ) 
      self.assertEquals("Dark Knight", extract(r"  dark knight conclusion"))
      self.assertEquals("Dark Knight", extract(r"Dark knight Part 3"))
      self.assertEquals("Dark Knight", extract(r"DARK KNIGHT ep. 5"))
                                                                                                
      # prime with "Death"
      prime([ IssueRef("7", "1007", "blah"),                                                
              IssueRef("8", "1008", "blah"),                                                
              IssueRef("9", "1009", "blah"),                                                
              IssueRef("10", "1010", "blah"),                                                
              IssueRef("11", "1011", "Death, Prelude"),                                                
              IssueRef("12", "1012", " Death pt I"),                                                
              IssueRef("13", "1013", "'Death' ep II") ] )
      self.assertEquals("Death", extract(r"Death part 1"))
      self.assertEquals("Death", extract(r"Death episode V"))
                                                         
      # prime with "Bigger" and "Rage"
      prime([ IssueRef("14", "1014", "'Death' Conclusion"),                                                
              IssueRef("15", "1015", "'Life' Prelude"),                                                
              IssueRef("16", "1016", "'Life' Conclusion"),
              IssueRef("17", "1017", "The One"),
              IssueRef("18", "1018", "Bigger Book Two"),
              IssueRef("19", "1019", "Bigger Book One"),
              IssueRef("20", "1020", "Rage, ep. 1") ] )
      self.assertEquals("Bigger", extract(r"Bigger, part 3"))
      
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_matching_tricky(self):
      ''' tests that matching issues to the primed arcs works properly '''
      initialize()
      
      # there are complicated rules to see if a specific issue title can match 
      # our primed arcs.  the first part of the title must match the arc name,
      # but the second half must either start with : or -, for example, or it
      # must contain a trigger word like "chapter", "part", #, etc.
      
      # prime with "Dark Knight", "Death", "Bigger", and "Rage"
      prime([ IssueRef("5", "1005", "Dark Knight part 1 of 4"),                                                 
              IssueRef("6", "1006", "Dark Knight part 2 of 4"),
              IssueRef("11", "1011", "Death, Prelude"),                                                
              IssueRef("12", "1012", " Death pt I"),                                                
              IssueRef("13", "1013", "'Death' ep II"),
              IssueRef("14", "1014", "'Death' Conclusion"),                                                
              IssueRef("15", "1015", "'Life' Prelude"),                                                
              IssueRef("16", "1016", "'Life' Conclusion"),
              IssueRef("17", "1017", "The One"),
              IssueRef("18", "1018", "Bigger Book Two"),
              IssueRef("19", "1019", "Bigger Book One"),
              IssueRef("20", "1020", "Rage, ep. 1"),
              IssueRef("21", "1021", "Rage, ep. TWO") ] )
      
      self.assertEquals("Dark Knight", extract(r"  dark knight conclusion"))
      self.assertEquals("Dark Knight", extract(r"dark knight,PT 3"))
      self.assertEquals("Dark Knight", extract(r"dark knight: PT. 3"))
      self.assertEquals("Dark Knight", extract(r"dark knight no 5"))
      self.assertEquals("Dark Knight", extract(r"dark knight: no. 5"))
      self.assertEquals("Dark Knight", extract(r"Dark knight Part 3"))
      self.assertEquals("", extract(r"dark knight is cool"))
      self.assertEquals("", extract(r"dark knight abk aep ach apt ano anum "))
      self.assertEquals("", extract(r"dark knight: is cool"))
      self.assertEquals("Dark Knight", extract(r"dark knight"))
      self.assertEquals("Dark Knight", extract(r"   dark knight     "))
      self.assertEquals("Dark Knight", extract(r"dark knight: "))
      self.assertEquals("Dark Knight", extract(r"dark knight - "))
                                                                                                
      self.assertEquals("", extract(r"Death in the Family"))
      self.assertEquals("", extract(r"Death : whatever"))
      self.assertEquals("", extract(r"Death - sure"))
      self.assertEquals("Death", extract(r"Death part 1"))
      self.assertEquals("Death", extract(r"Death,pt 1"))
      self.assertEquals("Death", extract(r"Death no. 1"))
      self.assertEquals("Death", extract(r"Death number 1"))
      self.assertEquals("Death", extract(r"Death ep. ten"))
      self.assertEquals("Death", extract(r"Death, episode 4"))
      self.assertEquals("Death", extract(r"Death,volume 3"))
      self.assertEquals("Death", extract(r"Death vol. "))
      self.assertEquals("Death", extract(r"Death ch. five"))
      self.assertEquals("Death", extract(r"Death chapter 1"))
      self.assertEquals("Death", extract(r"Death bk 1"))
      self.assertEquals("Death", extract(r"Death, book 3"))
      self.assertEquals("Death", extract(r"Death Prelude"))
      self.assertEquals("Death", extract(r"Death prolog"))
      self.assertEquals("Death", extract(r"Death the prologue"))
      self.assertEquals("Death", extract(r"Death intro"))
      self.assertEquals("Death", extract(r"Death the Introduction"))
      self.assertEquals("Death", extract(r"Death begins"))
      self.assertEquals("Death", extract(r"Death the end"))
      self.assertEquals("Death", extract(r"Death final story"))
      self.assertEquals("Death", extract(r"Death the conclusion"))
      self.assertEquals("Death", extract(r"Death the last bit"))
      self.assertEquals("Death", extract(r"Death first class"))
      self.assertEquals("Death", extract(r"Death#5"))
      self.assertEquals("Death", extract(r"Death # 4"))
      
      self.assertEquals("Rage", extract(r"Rage, ep. 1"))
      self.assertEquals("", extract(r"Rage Against the Machine"))
      self.assertEquals("", extract(r"Rage, Against the Machine"))
      self.assertEquals("", extract(r"Rage - Against the Machine"))
      self.assertEquals("Rage", extract(r"Rage, the end"))
      self.assertEquals("Rage", extract(r"Rage Part 3 (of 4): 'The angering'"))
      self.assertEquals("Rage", extract(r"'Rage': chapter 4"))
      self.assertEquals("Rage", extract(r'"Rage" - chapter 5: the angering'))
      self.assertEquals("Rage", extract(r'"  rage  " :- book 6'))
      
      self.assertEquals("", extract(r"Bigger Than You"))
      self.assertEquals("", extract(r"Who is Bigger?"))
      self.assertEquals("Bigger", extract(r"Bigger, part 3"))
      self.assertEquals("Bigger", extract(r"Bigger ch. 3"))
      self.assertEquals("Bigger", extract(r"Bigger this is pt. 3"))
      self.assertEquals("Bigger", extract(r"Bigger book 3"))
      self.assertEquals("Bigger", extract(r"Bigger bk. 3"))
      self.assertEquals("Bigger", extract(r"Bigger #four"))
      self.assertEquals("Bigger", extract(r"Bigger #what"))
      self.assertEquals("Bigger", extract(r"Bigger; epilogue"))
      
      shutdown()   
      
   # --------------------------------------------------------------------------
   def test_matching_despite_punctuation(self):
      ''' tests that matching issues works even if punctuation differs a bit '''
      initialize()
      
      # prime with "I am Vampire"
      prime([ IssueRef("5", "1005", "I am Vampire part 1 of 4"),                                                 
              IssueRef("6", "1006", "I. Am. Vampire part 2 of 4"),
              IssueRef("7", "1007", "Kid and Play book 1"),                                                 
              IssueRef("8", "1008", "Kid & Play ep. 2") ] )
      
      self.assertEquals("I am Vampire", extract(r"I am Vampire"))
      self.assertEquals("I am Vampire", extract(r"I  am  Vampire"))
      self.assertEquals("I am Vampire", extract(r"I. am Vampire"))
      self.assertEquals("I am Vampire", extract(r"I.am Vampire"))
      self.assertEquals("I am Vampire", extract(r"I am V'ampire"))
      self.assertEquals("I am Vampire", extract(r"I am: Vampire"))
      self.assertEquals("I am Vampire", extract(r"I, am Vampire"))
      self.assertEquals("I am Vampire", extract(r"I am- Vampire"))
      self.assertEquals("I am Vampire", extract(r"i am vampire!"))
      self.assertEquals("I am Vampire", extract(r"i am 'vampire'"))
      self.assertEquals("I am Vampire", extract(r'i "am vampire"'))
      self.assertEquals("I am Vampire", extract(r'i am `vampire`'))
      self.assertEquals("Kid and Play", extract(r'Kid, and Play'))
      self.assertEquals("Kid and Play", extract(r'Kid & Play'))
      self.assertEquals("Kid and Play", extract(r'Kid & Play!'))
      
      shutdown()   
   
   # --------------------------------------------------------------------------
   def test_matching_from_forum1(self):
      ''' tests matching issues that were suggested in the comicrack forum '''
      initialize()
      
      prime([ IssueRef("55", "10055", "A Great Story Part 1"),                                                 
              IssueRef("56", "10056", "A Great Story!!, Part 2"),                                                 
              IssueRef("57", "10057", "A Great Story!: Part 3") ])
                                                             
      self.assertEquals("A Great Story", extract(r"A Great Story Part 1"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story, Part 2"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: Part 3"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story - Part 4"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story Pt 5"))                                              
      self.assertEquals("A Great Story", extract(r"A Great Story, Pt. 6"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: #7"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story- number 8"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story no. 9"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: Part 10of12"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: #11 (of 17)"))                                                 
      
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_matching_from_forum2(self):
      ''' tests matching issues that were suggested in the comicrack forum '''
      initialize()
      
      prime([ IssueRef("55", "10055", "A Great Story Part 1 of 15"),                                                 
              IssueRef("56", "10056", "A Great Story. chapter x"),                                                 
              IssueRef("57", "10057", "A Great Story. chapter xi") ])
                                                             
      self.assertEquals("A Great Story", extract(r"A Great Story Introduction"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story, Conclusion"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: Prologue"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story - Vol IV"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story Pt iii"))                                              
      self.assertEquals("A Great Story", extract(r"A Great Story, Chapter X"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: #VII"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story- book XI"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story no. ii"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: Part i of v"))                                                 
      self.assertEquals("A Great Story", extract(r"A Great Story: #iii (of 6)"))                                                 
      
      shutdown()
      
         
   # --------------------------------------------------------------------------
   def test_matching_from_forum3(self):
      ''' tests matching issues that were suggested in the comicrack forum '''
      initialize()
      
      prime([ IssueRef("65", "1001", "Healing Factor - Prologue"),                                                 
              IssueRef("66", "1002", "Healing Factor chapter 1"),                                                 
              IssueRef("67", "1003", "Healing Factor chapter 2"),                                                 
              IssueRef("68", "1004", "Healing Factor chapter 3"),                                                 
              IssueRef("69", "1005", "Healing Factor chapter 4 (finale)") ])
                                                             
      self.assertEquals("Healing Factor",
         extract(r"Healing Factor - Prologue"))                                                 
      self.assertEquals("Healing Factor",
         extract(r"Healing Factor chapter 1"))                                                 
      self.assertEquals("Healing Factor",
         extract(r"Healing Factor chapter 2"))                                                 
      self.assertEquals("Healing Factor",
         extract(r"Healing Factor chapter 3"))                                                 
      self.assertEquals("Healing Factor",
         extract(r"Healing Factor chapter 4 (finale)"))                                              
      
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_matching_from_forum4(self):
      ''' tests matching issues that were suggested in the comicrack forum '''
      initialize()
      
      prime([ IssueRef("504", "11", "Fear Itself, Part 1: City of Light"),                                                 
              IssueRef("505", "12", "Fear Itself, Part 2: Cracked Actor"),                                                 
              IssueRef("506", "13", "Fear Itself, Part 3- The Apostate"),                                                 
              IssueRef("507", "14", "Fear Itself Part 4 Fog of War"),                                                 
              IssueRef("508", "15", "Fear Itself, Part 5: If I Ever Get Out"),                                                 
              IssueRef("509", "16", "Fear Itself, Part 6: Mercy") ])
                                                             
      self.assertEquals("Fear Itself",
         extract(r"Fear Itself, Part 1: City of Light"))                                                 
      self.assertEquals("Fear Itself",
         extract(r"Fear Itself, Part 2: Cracked Actor"))                                                 
      self.assertEquals("Fear Itself",
         extract(r"Fear Itself, Part 3- The Apostate"))                                                 
      self.assertEquals("Fear Itself",
         extract(r"Fear Itself Part 4 Fog of War"))                                                 
      self.assertEquals("Fear Itself",
         extract(r"Fear Itself, Part 5: If I Ever Get Out"))                                              
      self.assertEquals("Fear Itself",
         extract(r"Fear, Itself, Part 6: Mercy"))                                              
      
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_matching_from_forum5(self):
      ''' tests matching issues that were suggested in the comicrack forum '''
      initialize()
      
      prime([ IssueRef("36", "11", "Monstrous, Part 1"),                                                 
              IssueRef("37", "12", "Monstrous, Part 2"),                                                 
              IssueRef("38", "13", '"Meanwhile" Part One'),                                                 
              IssueRef("39", "14", "Monstrous, Part 3"),                                                 
              IssueRef("40", "15", '"Meanwhile" Part Two'),                                                 
              IssueRef("41", "16", "Monstrous, Conclusion"),
              IssueRef("42", "17", "'Meanwhile', Conclusion") ])
                                                             
      self.assertEquals("Monstrous", extract(r"Monstrous, Part 1"))                                                 
      self.assertEquals("Monstrous", extract(r"Monstrous, Part 2"))                                                 
      self.assertEquals("Meanwhile", extract(r'"Meanwhile" Part One'))                                                 
      self.assertEquals("Monstrous", extract(r"Monstrous, Part 3"))                                                 
      self.assertEquals("Meanwhile", extract(r'"Meanwhile" Part Two'))                                              
      self.assertEquals("Monstrous", extract(r"Monstrous, Conclusion"))                                              
      self.assertEquals("Meanwhile", extract(r"'Meanwhile', Conclusion"))                                              
      
      shutdown()   
      
   # --------------------------------------------------------------------------
   def test_matching_from_forum6(self):
      ''' tests matching issues that were suggested in the comicrack forum '''
      initialize()
      
      prime([ IssueRef("31", "11", "Exogenetic, Part 1"),                                                 
              IssueRef("32", "12", "Exogenetic, Part 2"),                                                 
              IssueRef("33", "13", 'Exogenetic, Part 3'),                                                 
              IssueRef("34", "14", "Exogenetic, Part 4"),                                                 
              IssueRef("35", "15", 'Exogenetic, Conclusion'),                                                 
              IssueRef("44", "17", '"Exalted" Part 1'),
              IssueRef("45", "18", "Exalted, Part Two"),
              IssueRef("46", "19", "Exalted, Part Three") ])
                                                             
      self.assertEquals("Exogenetic", extract(r"Exogenetic, Part 1"))                                                 
      self.assertEquals("Exogenetic", extract(r"Exogenetic, Part 2"))                                                 
      self.assertEquals("Exogenetic", extract(r'Exogenetic, Part 3'))                                                 
      self.assertEquals("Exogenetic", extract(r"Exogenetic, Part 4"))                                                 
      self.assertEquals("Exogenetic", extract(r'Exogenetic, Conclusion'))                                              
      self.assertEquals("Exalted", extract(r'"Exalted" Part 1'))                                              
      self.assertEquals("Exalted", extract(r"Exalted, Part Two"))                                              
      self.assertEquals("Exalted", extract(r"Exalted, Part Three"))                                              
      
      shutdown()  