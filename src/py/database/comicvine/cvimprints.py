# encoding: utf-8

'''
This module is used to find imprint names for publishers in the ComicVine 
database.  

@author: Cory Banack
'''

# =============================================================================
def find_parent_publisher(imprint_s):
   '''
   This method takes a publisher string that might be an imprint of another 
   publisher.  If it is a known imprint, the method returns a different 
   publisher string representing the parent publisher for that imprint.  If it 
   is not an imprint, this method returns the original passed in string.
   
   Both the passed in and returned strings for these methods must EXACTLY
   match their corresponding values in the ComicVine database (i.e. case, 
   punctation, etc.)
   ''' 
   parent_s = imprint_s
   imprint_s = imprint_s.strip() # because the tables below are stripped, too
   if imprint_s in __imprint_map:
      parent_s = __imprint_map[imprint_s]
   return parent_s


# the publishers that we know about that have at least one imprint
__MARVEL = "Marvel"    # http://marvel.wikia.com/Imprints
__DC = "DC Comics"
__DARKHORSE = "Dark Horse Comics"
__MALIBU = "Malibu"    # http://en.wikipedia.org/wiki/Malibu_Comics
__AMRYL =  "Amryl Entertainment"
__AVATAR = "Avatar Press"
__WIZARD = "Wizard"
__TOKYOPOP = "Tokyopop"
__DYNAMITE = "Dynamite Entertainment"
__IMAGE = "Image"
__HEROIC = "Heroic Publishing"
__KODANSHA = "Kodansha"
__PENGUIN = "Penguin Group"
__HAKUSENSHA = "Hakusensha"
__APE = "Ape Entertainment"
__NBM = "Nbm"
__RADIO = "Radio Comix"
__SLG = "Slg Publishing"
__TOKUMA = "Tokuma Shoten"


# the mapping of imprint names to their parent publisher names
__imprint_map = {
   "2000AD": __DC,
   "Adventure": __MALIBU,
   "Aircel Publishing": __MALIBU,
   "America's Best Comics": __DC, # originally image
   "Wildstorm": __DC,
   "Antimatter": __AMRYL,
   "Apparat": __AVATAR,
   "Black Bull": __WIZARD,
   "Blu Manga": __TOKYOPOP,
   "Chaos! Comics": __DYNAMITE,
   "Cliffhanger": __DC,
   "CMX": __DC,
   "Comic Bom Bom": __KODANSHA,
   "ComicsLit": __NBM,
   "Curtis Magazines": __MARVEL,
   "Dark Horse Books": __DARKHORSE,
   "Dark Horse Manga": __DARKHORSE,
   "Desperado Publishing": __IMAGE,
   "Epic": __MARVEL, 
   "Eternity": __MALIBU,
   "Focus": __DC, 
   "Helix": __DC,
   "Hero Comics": __HEROIC,
   "Homage comics": __DC, # i.e. wildstorm
   "Hudson Street Press": __PENGUIN,
   "Icon Comics": __MARVEL,
   "Impact": __DC,
   "Jets Comics": __HAKUSENSHA,
   "KiZoic": __APE,
   "Marvel Digital Comics Unlimited" : __MARVEL,
   "Marvel Knights": __MARVEL,
   "Marvel Music": __MARVEL,
   "Marvel Soleil": __MARVEL,
   "Marvel UK": __MARVEL,
   "Maverick": __DARKHORSE, 
   "Max": __MARVEL,
   "Milestone": __DC,
   "Minx": __DC,
   "Papercutz": __NBM,
   "Paradox Press": __DC,
   "Piranha Press": __DC,
   "Razorline": __MARVEL,
   "ShadowLine": __IMAGE,
   "Sin Factory Comix" : __RADIO,
   "Skybound" : __IMAGE,
   "Slave Labor": __SLG,
   "Star Comics": __MARVEL,
   "Tangent Comics": __DC,
   "Tokuma Comics": __TOKUMA,
   "Ultraverse": __MALIBU,
   "Vertigo": __DC,
   "Zuda Comics": __DC,
}
