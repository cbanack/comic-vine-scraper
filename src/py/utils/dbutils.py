'''
This module contains a variety of useful utility methods for working with
the database (db.py and dbmodels.py) modules.  In particular, this module
is for dealing with IssueRefs and SeriesRefs.

@author: Cory Banack
'''

#==============================================================================
def filter_series_refs(series_refs, ignored_publishers_sl, 
      ignore_before_year_n, ignore_after_year_n, never_ignore_threshold_n):
   ''' 
   Takes the given collection of SeriesRefs, and filters it down to a smaller
   collection based on the given criteria.  'ignore_publishers_sl' is a list 
   of publisher names (trimmed and lower cased).  If a series publisher matches 
   one of these names, it is filtered out of our returned results.
      
   'ignore_before_year_n' and 'ignore_after_year_n' will cause any series that
   was first published before or after the given year to be filtered out of our
   results.  And finally, 'never_ignore_threshold_n' set a threshold for
   filtering; we will never filter out any series that has at least this many
   issues, even if the other filtering criteria requires it.
   '''
   filtered_refs = set() 
   for series_ref in series_refs:
      if series_ref.issue_count_n >= never_ignore_threshold_n:
         year_passes_filter = True
         pub_passes_filter = True
      else:
         publisher_s = series_ref.publisher_s.lower().strip()
         year_passes_filter = series_ref.volume_year_n == -1 \
            or (series_ref.volume_year_n >= ignore_before_year_n \
            and series_ref.volume_year_n <= ignore_after_year_n) 
         pub_passes_filter = publisher_s not in ignored_publishers_sl
      if year_passes_filter and pub_passes_filter:    
         filtered_refs.add(series_ref)
   return filtered_refs

