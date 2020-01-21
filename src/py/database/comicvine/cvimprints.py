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
__ACTIONLAB = "Action Lab"
__AMRYL =  "Amryl Entertainment"
__APE = "Ape Entertainment"
__AVATAR = "Avatar Press"
__BOOM = "Boom!"
__DARKHORSE = "Dark Horse Comics"
__DC = "DC Comics"
__DYNAMITE = "Dynamite Entertainment"
__HAKUSENSHA = "Hakusensha"
__HEROIC = "Heroic Publishing"
__IDW = "IDW Publishing"
__IMAGE = "Image"
__KODANSHA = "Kodansha"
__LION = "Lion Forge Comics"
__MALIBU = "Malibu"    # http://en.wikipedia.org/wiki/Malibu_Comics
__MARVEL = "Marvel"    # http://marvel.wikia.com/Imprints
__NBM = "Nbm"
__PENGUIN = "Penguin Group"
__RADIO = "Radio Comix"
__SLG = "Slg Publishing"
__TITAN = "Titan Comics"
__TOKUMA = "Tokuma Shoten"
__TOKYOPOP = "Tokyopop"
__WIZARD = "Wizard"


# the mapping of imprint names to their parent publisher names
__imprint_map = {
   "2000AD": __DC,
   "Adventure": __MALIBU,
   "Aircel Publishing": __MALIBU,
   "America's Best Comics": __DC, # originally image
   "Amerotica ": __NBM,
   "Antimatter": __AMRYL,
   "Apparat": __AVATAR,
   "Archaia": __BOOM,
   "Berger Books": __DARKHORSE,
   "BOOM! Box": __BOOM,
   "Boundless Comics": __AVATAR,
   "Black Bull": __WIZARD,
   "Black Crown": __IDW,
   "Blu Manga": __TOKYOPOP,
   "CMX": __DC,
   "Chaos! Comics": __DYNAMITE,
   "Cliffhanger": __DC,
   "Comic Bom Bom": __KODANSHA,
   "ComicsLit": __NBM,
   "Curtis Magazines": __MARVEL,
   "Danger Zone": __ACTIONLAB,
   "Dark Horse Books": __DARKHORSE,
   "Dark Horse Manga": __DARKHORSE,
   "Desperado Publishing": __IMAGE,
   "Epic": __MARVEL, 
   "Eternity": __MALIBU,
   "Eurotica ": __NBM,
   "Focus": __DC, 
   "Helix": __DC,
   "Hero Comics": __HEROIC,
   "Homage comics": __DC, # i.e. wildstorm
   "Hudson Street Press": __PENGUIN,
   "Icon Comics": __MARVEL,
   "Impact": __DC,
   "Jets Comics": __HAKUSENSHA,
   "KaBOOM!": __BOOM,
   "KiZoic": __APE,
   "Kodansha Comics Digital-First!": __KODANSHA,
   "Kodansha Comics USA": __KODANSHA,
   "MAD": __DC,
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
   "Quillion": __LION,
   "Razorline": __MARVEL,
   "Roar Comics": __LION,
   "ShadowLine": __IMAGE,
   "Silverline": __IMAGE,
   "Sin Factory Comix" : __RADIO,
   "Skybound" : __IMAGE,
   "Slave Labor": __SLG,
   "Star Comics": __MARVEL,
   "Tangent Comics": __DC,
   "Titan Books": __TITAN,
   "Todd McFarlane Productions": __IMAGE,
   "Tokuma Comics": __TOKUMA,
   "Top Cow": __IMAGE,
   "Top Shelf": __IDW,
   "Ultraverse": __MALIBU,
   "Vertical": __KODANSHA,
   "Vertigo": __DC,
   "Wildstorm": __DC,
   "Wildstorm": __DC,
   "Zuda Comics": __DC,
}
