# encoding: utf-8

'''
This module contains all unittests for the storyarcparser module.

Created on Feb 2, 2012
@author: cbanack
'''

from unittest import TestCase
from unittest.loader import TestLoader
from storyarcparser import init, shutdown, extract, _extract, prime
from dbmodels import IssueRef

#==============================================================================
def load_tests(loader, tests, pattern):
   ''' Returns all of the testcases in this module as a testsuite '''
   return TestLoader().loadTestsFromTestCase(TestStoryArcParser) 

#==============================================================================
class TestStoryArcParser(TestCase):

   # --------------------------------------------------------------------------
   def test_extract_from_one_digit(self):
      ''' Test basic titles with the required 'one' as the digit '1' '''
      self.assertEquals("The Grey", _extract(r"The Grey part 1  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt 1  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt. 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey # 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey #1  "))
      self.assertEquals("The Grey", _extract(r"  The Grey no. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey number 1"))
      self.assertEquals("The Grey", _extract(r"The Grey num 1"))
      self.assertEquals("The Grey", _extract(r"   The Grey num. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey epiSode 1"))
      self.assertEquals("The Grey", _extract(r"The Grey ep. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey vol. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey vol 1"))
      self.assertEquals("The Grey", _extract(r"The Grey VOLUME 1"))
      self.assertEquals("The Grey", _extract(r"The Grey ch. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey chapter 1"))
      
   # --------------------------------------------------------------------------
   def test_extract_from_one_word(self):
      ''' Test basic titles with the required 'one' as the word 'one' '''
      self.assertEquals("The Grey", _extract(r"The Grey part one  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt one  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt. One  "))
      self.assertEquals("The Grey", _extract(r"The Grey # ONE  "))
      self.assertEquals("The Grey", _extract(r"The Grey #one  "))
      self.assertEquals("The Grey", _extract(r"  The Grey no. One"))
      self.assertEquals("The Grey", _extract(r"The Grey number one"))
      self.assertEquals("The Grey", _extract(r"The Grey num oNe"))
      self.assertEquals("The Grey", _extract(r"   The Grey num. oNE"))
      self.assertEquals("The Grey", _extract(r"The Grey epiSode One"))
      self.assertEquals("The Grey", _extract(r"The Grey ep. One"))
      self.assertEquals("The Grey", _extract(r"The Grey vol. One"))
      self.assertEquals("The Grey", _extract(r"The Grey vol one"))
      self.assertEquals("The Grey", _extract(r"The Grey VOLUME One"))
      self.assertEquals("The Grey", _extract(r"The Grey ch. one"))
      self.assertEquals("The Grey", _extract(r"The Grey chapter one"))
      
   # --------------------------------------------------------------------------
   def test_extract_from_one_roman(self):
      ''' Test basic titles with the required 'one' as the roman 'i' '''
      self.assertEquals("The Grey", _extract(r"The Grey part i  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt I  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt. I "))
      self.assertEquals("The Grey", _extract(r"The Grey epiSode i"))
      self.assertEquals("Family Guy", _extract(r"Family Guy ep. I"))
      self.assertEquals("The Grey", _extract(r"The Grey vol. I"))
      self.assertEquals("The Grey", _extract(r"The Grey vol i"))
      self.assertEquals("The Grey", _extract(r"The Grey bk. i"))
      self.assertEquals("The Grey", _extract(r"The Grey ch. i"))
      self.assertEquals("The Grey", _extract(r"The Grey chapter I"))
      
   # --------------------------------------------------------------------------
   def test_extract_with_punctuation(self):
      ''' Test basic titles with delimiting punctuation '''
      self.assertEquals("The Grey", _extract(r"The Grey, part 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey,part 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey , part 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey- part 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey - bk. 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey-part 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey: part 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey:book 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey :  part 1  "))
      self.assertEquals("The Grey", _extract(r"  The Grey,pt 1  "))
      self.assertEquals("The Grey", _extract(r"  The Grey-pt. 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey -# 1  "))
      self.assertEquals("The Grey", _extract(r"The Grey: #1  "))
      self.assertEquals("The Grey", _extract(r"  The Grey: no. 1"))
      self.assertEquals("The Grey", _extract(r"  The Grey : no. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey, number 1"))
      self.assertEquals("The Grey", _extract(r"The Grey,num 1"))
      self.assertEquals("The Grey", _extract(r"   The Grey: num. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey - epiSode 1"))
      self.assertEquals("The Grey", _extract(r"The Grey, ep. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey , vol. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey, vol 1"))
      self.assertEquals("The Grey", _extract(r"The Grey - VOLUME 1"))
      self.assertEquals("The Grey", _extract(r"The Grey: ch. 1"))
      self.assertEquals("The Grey", _extract(r"The Grey: chapter 1"))
      
      self.assertEquals("The Grey", _extract(r"The Grey, part one  "))
      self.assertEquals("The Grey", _extract(r"  The Grey: pt one  "))
      self.assertEquals("The Grey", _extract(r"  The Grey - pt. One  "))
      self.assertEquals("The Grey", _extract(r"The Grey: # ONE  "))
      self.assertEquals("The Grey", _extract(r"The Grey, #one  "))
      self.assertEquals("The Grey", _extract(r"  The Grey - no. One"))
      self.assertEquals("The Grey", _extract(r"The Grey - number one"))
      self.assertEquals("The Grey", _extract(r"The Grey, num oNe"))
      self.assertEquals("The Grey", _extract(r"   The Grey: num. oNE"))
      self.assertEquals("The Grey", _extract(r"The Grey-epiSode One"))
      self.assertEquals("The Grey", _extract(r"The Grey: ep. One"))
      self.assertEquals("The Grey", _extract(r"The Grey, vol. One"))
      self.assertEquals("The Grey", _extract(r"The Grey-vol one"))
      self.assertEquals("The Grey", _extract(r"The Grey -VOLUME One"))
      self.assertEquals("The Grey", _extract(r"The Grey :ch. one"))
      self.assertEquals("The Grey", _extract(r"The Grey: book one"))
      
      self.assertEquals("The Grey", _extract(r"The Grey- part i  "))
      self.assertEquals("The Grey", _extract(r"  The Grey: pt I  "))
      self.assertEquals("The Grey", _extract(r"  The Grey, pt. I "))
      self.assertEquals("The Grey", _extract(r"The Grey: epiSode i"))
      self.assertEquals("The Grey", _extract(r"The Grey - ep. I"))
      self.assertEquals("The Grey", _extract(r"The Grey ,vol. I"))
      self.assertEquals("The Grey", _extract(r"The Grey, vol i"))
      self.assertEquals("The Grey", _extract(r"The Grey-VOLUME i"))
      self.assertEquals("The Grey", _extract(r"The Grey:ch. i"))
      self.assertEquals("The Grey", _extract(r"The Grey,   chapter I"))
      
   def test_extract_from_brackets(self):
      ''' Test basic titles with the required 'one' inside brackets '''
      self.assertEquals("The Grey", _extract(r"The Grey (part 1)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (pt 1  )"))
      self.assertEquals("The Grey", _extract(r"  The Grey (pt. 1  )"))
      self.assertEquals("The Grey", _extract(r"The Grey( # 1)  "))
      self.assertEquals("The Grey", _extract(r"The Grey (#1)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (no. 1)"))
      self.assertEquals("The Grey", _extract(r"The Grey (number 1)"))
      self.assertEquals("The Grey", _extract(r"The Grey ( num 1 )"))
      self.assertEquals("The Grey", _extract(r"   The Grey (num. 1 )"))
      self.assertEquals("The Grey", _extract(r"The Grey [epiSode 1]"))
      self.assertEquals("The Grey", _extract(r"The Grey [ep. 1]"))
      self.assertEquals("The Grey", _extract(r"The Grey [ vol. 1]"))
      self.assertEquals("The Grey", _extract(r"The Grey [ vol 1]"))
      self.assertEquals("The Grey", _extract(r"The Grey [ VOLUME 1]"))
      self.assertEquals("The Grey", _extract(r"The Grey [ch. 1]"))
      self.assertEquals("The Grey", _extract(r"The Grey [ chapter 1]"))
      
      self.assertEquals("The Grey", _extract(r"The Grey ( part one)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey ( pt one)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey [pt. One]  "))
      self.assertEquals("The Grey", _extract(r"The Grey [# ONE  ]"))
      self.assertEquals("The Grey", _extract(r"The Grey [#one  ]"))
      self.assertEquals("The Grey", _extract(r"  The Grey [no. One]"))
      self.assertEquals("The Grey", _extract(r"The Grey (number one)"))
      self.assertEquals("The Grey", _extract(r"The Grey (num oNe)"))
      self.assertEquals("The Grey", _extract(r"   The Grey ( num. oNE)"))
      self.assertEquals("The Grey", _extract(r"The Grey ( epiSode One )"))
      self.assertEquals("The Grey", _extract(r"The Grey - ( ep. One )"))
      self.assertEquals("The Grey", _extract(r"The Grey : [vol. One]"))
      self.assertEquals("The Grey", _extract(r"The Grey, [ vol one]"))
      self.assertEquals("The Grey", _extract(r"The Grey [book One]"))
      self.assertEquals("The Grey", _extract(r"The Grey ( ch. one  )"))
      self.assertEquals("The Grey", _extract(r"The Grey [chapter one]"))

      self.assertEquals("The Grey", _extract(r"The Grey (part i)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (pt I  )"))
      self.assertEquals("The Grey", _extract(r"  The Grey (pt. I) "))
      self.assertEquals("The Grey", _extract(r"The Grey (epiSode i)"))
      self.assertEquals("The Grey", _extract(r"The Grey, ( ep. I)"))
      self.assertEquals("The Grey", _extract(r"The Grey -(vol. I)"))
      self.assertEquals("The Grey", _extract(r"The Grey: (vol i)"))
      self.assertEquals("The Grey", _extract(r"The Grey    ( VoLUME i)"))
      self.assertEquals("The Grey", _extract(r"The Grey [ch. i]"))
      self.assertEquals("The Grey", _extract(r"The Grey   [chapter I]"))
   
   # --------------------------------------------------------------------------
   def test_extract_with_of(self):
      ''' Test basic titles with 'of' in the storyarc numbering '''
      self.assertEquals("The Grey", _extract(r"The Grey part 1 of 3  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt 1 (of 4)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt. 1 of three  "))
      self.assertEquals("The Grey", _extract(r"The Grey # 1of4 "))
      self.assertEquals("The Grey", _extract(r"The Grey #1of 5  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (no. 1 of 5)"))
      self.assertEquals("The Grey", _extract(r"The Grey book 1 (of 1)"))
      self.assertEquals("The Grey", _extract(r"The Grey num 1of 54"))
      self.assertEquals("The Grey", _extract(r"   The Grey (num. 1 of four) "))
      self.assertEquals("The Grey", _extract(r"The Grey epiSode 1 of 2"))
      self.assertEquals("The Grey", _extract(r"The Grey ep. 1 of 3"))
      self.assertEquals("The Grey", _extract(r"The Grey (vol. 1 of 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey vol 1 (of FIVE)"))
      self.assertEquals("The Grey", _extract(r"The Grey VOLUME 1 of 2"))
      self.assertEquals("The Grey", _extract(r"The Grey (ch. 1 of 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey (chapter 1 of FOUR  )"))
      
      self.assertEquals("The Grey", _extract(r"The Grey, (part one of 3)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey: pt one of 3 "))
      self.assertEquals("The Grey", _extract(r"  The Grey - (pt. One of Four)"))
      self.assertEquals("The Grey", _extract(r"The Grey #1 (of four)  "))
      self.assertEquals("The Grey", _extract(r"The Grey, (#1 of 4)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (no. One of 2)"))
      self.assertEquals("The Grey", _extract(r"The Grey (number one of 4)"))
      self.assertEquals("The Grey", _extract(r"The Grey num oNe (of three)"))
      self.assertEquals("The Grey", _extract(r"   The Grey (num. oNE of 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey (epiSode One of four)"))
      self.assertEquals("The Grey", _extract(r"The Grey ep. One (of three)"))
      self.assertEquals("The Grey", _extract(r"The Grey (vol. One of 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey vol one (of 5)"))
      self.assertEquals("The Grey", _extract(r"The Grey (VOLUME One of 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey (ch. one of four)"))
      self.assertEquals("The Grey", _extract(r"The Grey (chapter one of 3)"))
      
   # --------------------------------------------------------------------------
   def test_extract_with_slash(self):
      ''' Test basic titles with 'slashes' in the storyarc numbering '''
      self.assertEquals("The Grey", _extract(r"The Grey part 1 \ 3  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt 1/4  "))
      self.assertEquals("The Grey", _extract(r"  The Grey pt. 1 / three  "))
      self.assertEquals("The Grey", _extract(r"The Grey # 1\4 "))
      self.assertEquals("The Grey", _extract(r"The Grey #1\ 5  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (no. 1 / 5)"))
      self.assertEquals("The Grey", _extract(r"The Grey number 1 (/ 1)"))
      self.assertEquals("The Grey", _extract(r"The Grey num 1/ 54"))
      self.assertEquals("The Grey", _extract(r"   The Grey (num. 1 \ four) "))
      self.assertEquals("The Grey", _extract(r"The Grey epiSode 1 / 2"))
      self.assertEquals("The Grey", _extract(r"The Grey ep. 1 / 3"))
      self.assertEquals("The Grey", _extract(r"The Grey (vol. 1 / 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey vol 1 (/FIVE)"))
      self.assertEquals("The Grey", _extract(r"The Grey VOLUME 1 / 2"))
      self.assertEquals("The Grey", _extract(r"The Grey (ch. 1 \ 3)"))
      self.assertEquals("The Grey", _extract(r"The Grey (chapter 1 / FOUR  ) "))
      
      self.assertEquals("The Grey", _extract(r"The Grey, (part one / 3)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey: pt one / 3 "))
      self.assertEquals("The Grey", _extract(r"  The Grey - (pt. One/Four) "))
      self.assertEquals("The Grey", _extract(r"The Grey #1 (/ four)  "))
      self.assertEquals("The Grey", _extract(r"The Grey, (#1/4)  "))
      self.assertEquals("The Grey", _extract(r"  The Grey (no. One\2)"))
      self.assertEquals("The Grey", _extract(r"The Grey (number one\4)"))
      self.assertEquals("The Grey", _extract(r"The Grey num oNe (\ three)"))
      self.assertEquals("The Grey", _extract(r"   The Grey (num. oNE/3)"))
      self.assertEquals("The Grey", _extract(r"The Grey (epiSode One/four)"))
      self.assertEquals("The Grey", _extract(r"The Grey ep. One (/three)"))
      self.assertEquals("The Grey", _extract(r"The Grey (vol. One/3)"))
      self.assertEquals("The Grey", _extract(r"The Grey book one (/5)"))
      self.assertEquals("The Grey", _extract(r"The Grey (VOLUME One/3)"))
      self.assertEquals("The Grey", _extract(r"The Grey (ch. one/four)"))
      self.assertEquals("The Grey", _extract(r"The Grey (chapter one\3)"))
   
   # --------------------------------------------------------------------------
   def test_extract_extra_text(self):
      ''' Test basic titles with text following the storyarc numbering '''
      self.assertEquals("The Grey", _extract(r"The Grey, Part 1: quickening"))
      self.assertEquals("The Grey", _extract(r"The Grey Part 1, 3 of time"))
      self.assertEquals("The Grey", _extract(r"The Grey:ep. 1 , the greyening"))
      self.assertEquals("The Grey", _extract(r"The Grey, ch. one; greyening"))
      self.assertEquals("The Grey", _extract(r"The Grey ch. one- not twoer"))
      self.assertEquals("The Grey", _extract(r"The Grey - ch. one; - not toer"))
      self.assertEquals("The Grey", _extract(r"The Grey-part i:: a title"))
      self.assertEquals("The Grey", _extract(r"The Grey:part i: 'two of 3'"))
      self.assertEquals("The Grey", _extract(r"The Grey   part i 'two of 3'"))
      self.assertEquals("The Grey", _extract(r'The Grey - chapter one "help!"'))
      self.assertEquals("The Grey", _extract(r'The Grey - ep. 1 (help!)'))
      self.assertEquals("The Grey", _extract(r'The Grey - ep. 1 ("help!")'))
      self.assertEquals("The Grey", _extract(r'The Grey - ep. 1 ["help!"]'))
      self.assertEquals("The Grey", _extract(r'The Grey - ep. 1 [3 lp!]'))
      self.assertEquals("The Grey", _extract(r'The Grey - ep. 1 {of what}'))

      ''' these ones SHOULD fail '''   
      self.assertEquals("", _extract(r"The Grey part one of two nope"))
      self.assertEquals("", _extract(r"The Grey: chapter one is cool"))
      self.assertEquals("", _extract(r"The Grey - ep i this isn't"))
      self.assertEquals("", _extract(r'The Grey - chapter one "a'))
      self.assertEquals("", _extract(r"The Grey - chapter one 'a"))
   
   
   # --------------------------------------------------------------------------
   def test_extract_utf8_chars(self):
      ''' Test basic titles with text containing non-ascii characters '''
      self.assertEquals("The Greβy", _extract(r"The Greβy, Part 1"))
      self.assertEquals("The Grey", _extract(r"The Grey Part 1, 3 of tβime"))
      self.assertEquals("The Greyβ", _extract(r"The Greyβ:ep. 1, dideβ"))
      
      
   # --------------------------------------------------------------------------
   def test_extract_quoted_arcs(self):
      ''' Test basic titles with text quotation marks around the arcname '''
      self.assertEquals("The Grey", _extract(r"'The Grey', Part 1"))
      self.assertEquals("The Grey", _extract(r'"The Grey", ch1'))
      self.assertEquals("The Grey", _extract(r" ' The Grey  ' , ep. one: cool"))
      
   # --------------------------------------------------------------------------
   def test_extract_empty_arcs(self):
      ''' Test basic titles with no arcname '''
      self.assertEquals("", _extract(r"1"))
      self.assertEquals("", _extract(r"   "))
      self.assertEquals("", _extract(r"part one  "))
      self.assertEquals("", _extract(r"volume one"))
      self.assertEquals("", _extract(r"book one"))
      self.assertEquals("", _extract(r": part one"))
      self.assertEquals("", _extract(r"- ch. one"))
      self.assertEquals("", _extract(r"episode 1"))
      self.assertEquals("", _extract(r"Part 1"))
      self.assertEquals("", _extract(r", Part 1 of 3"))
      
   # --------------------------------------------------------------------------
   def test_extract_strict_arcs(self):
      ''' Test basic titles whose arcs aren't  found in strict mode. '''
      self.assertEquals("The Grey", _extract(r"The Grey, 1", False))
      self.assertEquals("The Grey", _extract(r"The Grey One", False))
      self.assertEquals("The Grey", _extract(r"The Grey - I", False))
      self.assertEquals("The Grey", _extract(r"The Grey: I", False))
      
      self.assertEquals("", _extract(r"The Grey, 1"))
      self.assertEquals("", _extract(r"The Grey One"))
      self.assertEquals("", _extract(r"The Grey - I"))
      self.assertEquals("", _extract(r"The Grey: I"))
   
   # --------------------------------------------------------------------------
   def test_prime_simple(self):
      ''' Test basic issue title parsing in the prime() function. '''
      init()
      # "Dark Knight" is the only one that has two numbered arcs
      self.assertEquals(["Dark Knight"], prime([
         IssueRef("4", "1004", "White Knight part 1 of 4"),                                                
         IssueRef("5", "1005", "Dark Knight part 1 of 4"),                                                
         IssueRef("6", "1006", "Dark Knight part 2 of 4"),                                                
         IssueRef("7", "1007", "blah"),                                                
         IssueRef("8", "1008", "blah"),                                                
         IssueRef("9", "1009", "blah"),                                                
      ], True));
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_prime_lenient(self):
      ''' Test that issue titles can parse leniently in prime () '''
      init()
      # 'Purgatory One' and 'Death I' both require lenient parsing, but 
      # but you still need at least two entries before we call it an arc,
      # so only "Death I" qualifies 
      self.assertEquals(["Death"], prime([
         IssueRef("10", "1010", "Purgatory One"),                                                
         IssueRef("11", "1011", "Death, Prelude"),                                                
         IssueRef("12", "1012", " Death I"),                                                
         IssueRef("13", "1013", "'Death' II"),                                                
         IssueRef("14", "1014", "'Death' Conclusion"),                                                
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
      ], True));
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_prime_lenient_final(self):
      ''' Test that the last issue's story arc doesn't parse leniently '''
      # "The One" is the last (i.e. most recent) title so it can ignore our 
      # requirement that we have more than one issue in that arc, IFF it can
      # be strictly parsed.  But it can't, it only parses leniently, so no dice.
      init()
      self.assertEquals([], prime([
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
         IssueRef("17", "1017", "The One"),
      ], True));
      shutdown()
      
   # --------------------------------------------------------------------------
   def test_prime_strict_final(self):
      ''' test that the last issue's story arc parses strictly '''
      # "Rage" only works because it can be strictly parsed; the fact that it 
      # is the last (i.e. most recent) title lets it ignore our requirement that
      # we have more than one issue in that arc.
      init()
      self.assertEquals(["Rage"], prime([
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
         IssueRef("17", "1017", "Rage, ep. 1"),
      ], True));
      shutdown()
         
   # --------------------------------------------------------------------------
   def test_prime_mishmash(self):
      ''' tests a more complicated collection of issue titles in prime() '''
      init()
      self.assertEquals(["Bigger", "Dark Knight", "Death", "Rage"], prime([
         IssueRef("4", "1004", "White Knight part 1 of 4"),                                                
         IssueRef("5", "1005", "Dark Knight part 1 of 4"),                                                
         IssueRef("6", "1006", "Dark Knight part 2 of 4"),                                                
         IssueRef("7", "1007", "blah"),                                                
         IssueRef("8", "1008", "blah"),                                                
         IssueRef("9", "1009", "blah"),                                                
         IssueRef("10", "1010", "blah"),                                                
         IssueRef("11", "1011", "Death, Prelude"),                                                
         IssueRef("12", "1012", " Death I"),                                                
         IssueRef("13", "1013", "'Death' II"),                                                
         IssueRef("14", "1014", "'Death' Conclusion"),                                                
         IssueRef("15", "1015", "'Life' Prelude"),                                                
         IssueRef("16", "1016", "'Life' Conclusion"),
         IssueRef("17", "1017", "The One"),
         IssueRef("18", "1018", "Bigger Two"),
         IssueRef("19", "1019", "Bigger One"),
         IssueRef("20", "1020", "Rage, ep. 1"),
      ], True));
      shutdown()   
      
   # --------------------------------------------------------------------------
   def test_parsing_simple(self):
      ''' tests that priming and then parsing works properly '''
      init()
      
      self.assertEquals("", extract(r"  dark knight conclusion"))
      prime([ IssueRef("5", "1005", "Dark Knight part 1 of 4"),                                                 
              IssueRef("6", "1006", "Dark Knight part 2 of 4") ] ) 
      self.assertEquals("Dark Knight", extract(r"  dark knight conclusion"))
                                                                                                
      prime([ IssueRef("7", "1007", "blah"),                                                
              IssueRef("8", "1008", "blah"),                                                
              IssueRef("9", "1009", "blah"),                                                
              IssueRef("10", "1010", "blah"),                                                
              IssueRef("11", "1011", "Death, Prelude"),                                                
              IssueRef("12", "1012", " Death I"),                                                
              IssueRef("13", "1013", "'Death' II") ] )
      self.assertEquals("Dark Knight", extract(r"Dark knight Part 3"))
      # coryhigh: can we do anything about this sort of thing?
      self.assertEquals("Death", extract(r"Death in the Family"))
                                                         
      prime([ IssueRef("14", "1014", "'Death' Conclusion"),                                                
              IssueRef("15", "1015", "'Life' Prelude"),                                                
              IssueRef("16", "1016", "'Life' Conclusion"),
              IssueRef("17", "1017", "The One"),
              IssueRef("18", "1018", "Bigger Two"),
              IssueRef("19", "1019", "Bigger One"),
              IssueRef("20", "1020", "Rage, ep. 1") ] )
      self.assertEquals("Dark Knight", extract(r"DARK KNIGHT ep. 5"))
      self.assertEquals("Death", extract(r"Death V"))
      self.assertEquals("Rage", extract(r"Rage, ep. 1"))
      self.assertEquals("Bigger", extract(r"Bigger, part 3"))
      
      shutdown()   
   
   # coryhigh: make more unit tests