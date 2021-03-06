#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pywikibot
import re
import csv

from pywikibot import pagegenerators as pg

afbeeldingCLAIM = u'P18'

def list_template_usage(site_obj, tmpl_name):
    name = "{}:{}".format(site_obj.namespace(10), tmpl_name)
    tmpl_page = pywikibot.Page(site_obj, name)
    ref_gen = pg.ReferringPageGenerator(tmpl_page, onlyTemplateInclusion=True)
    filter_gen = pg.NamespaceFilterPageGenerator(ref_gen, namespaces=[0])
    generator = site_obj.preloadpages(filter_gen, pageprops=True)
    return generator

def GetAfbeeldingInfobox(page):
    """
    Takes page object and returns the afbeelding

    The function expects a Page object (pywikibot.Page()). 
    """
    res = re.compile('\|(\s)*afbeelding(\s)*=(\s)*(.+)').search(page.text)
    if res:
        result = res.group(4)
    else:
        result = ""
    if result[:1] == "|":
      result = ""       
    elif result[:2] == "}}":
      result = ""        
    return result
    
def GetP18fromWikidata(page):
  item = pywikibot.ItemPage.fromPage(page)
  try:  
    item_dict = item.get()
    clm_dict = item_dict["claims"]
    clm_list = clm_dict[afbeeldingCLAIM]
    clm_trgt = clm_list[0].getTarget()
    afbeeldingnaam = clm_trgt.title()[5:]
  except:
    afbeeldingnaam = ""   
  return (afbeeldingnaam)

def GetP18fromWikidata2(item):
  try:  
    item_dict = item.get()
    clm_dict = item_dict["claims"]
    clm_list = clm_dict[afbeeldingCLAIM]
    clm_trgt = clm_list[0].getTarget()
    afbeeldingnaam = clm_trgt.title()[5:]
  except:
    afbeeldingnaam = ""   
  return (afbeeldingnaam.strip())
    
def GetWikidataID(page):
  item = pywikibot.ItemPage.fromPage(page)
  return ( item )    

def p18existsinpage(afbP18, page):
    if afbP18 == "":    
        return "Nee"
    elif page.text.replace('_',' ').find(afbP18.replace('_',' ')) > -1:
        return 'Ja'
    return 'Nee'
    
def comparestrings(str1, str2):
  if str1.replace('_',' ').strip() == str2.replace('_',' ').strip():
    return 'Ja'
  return 'Nee'     

site = pywikibot.Site('nl', 'wikipedia')

## Edit next line to use an other template
tmpl_gen = list_template_usage(site, "Infobox kunstenaar")
    
with open("kunstenaars.csv", "w", newline="", encoding='utf-8') as csvf:
  with open("kunstenaars_aandacht.csv", "w", newline="", encoding='utf-8') as csvf2:
    counter = 0
    fields = ["pagetitle", "wikidataID", "afbeelding in infobox", "afbeelding in P18", "P18 op pagina aanwezig", "P18 in infobox", "P18 buiten infobox gebruikt"] #, "P18 in code pagina"]
    writer = csv.DictWriter(csvf, fieldnames=fields)
    writer.writeheader()
    writer2 = csv.DictWriter(csvf2, fieldnames=fields)
    writer2.writeheader()
    for page in tmpl_gen:
        afbininfobox = GetAfbeeldingInfobox(page)
        item = GetWikidataID(page)
        wdid = item.title()
        if afbininfobox.find("|")>-1 and (afbininfobox.find('{{wd|property|raw|P18}}') <0 or afbininfobox.find('|claim') <0):
          if afbininfobox.find('{{wd|property|raw|P18}}') >-1 or afbininfobox.find('|claim') >-1:
            pass
          else:
            print (page.title()) 
        afbP18 = GetP18fromWikidata2(item)
        afbP18InPagina = p18existsinpage(afbP18, page)
        issameimage = comparestrings(afbininfobox, afbP18)
        if afbP18InPagina == "Ja" and issameimage == "Nee":
            attention = "Ja"
            writer2.writerow({"pagetitle": page.title(), "wikidataID": wdid, "afbeelding in infobox": afbininfobox, "afbeelding in P18": afbP18, "P18 op pagina aanwezig": afbP18InPagina, "P18 in infobox": issameimage, "P18 buiten infobox gebruikt": attention})
        else:  
            attention = "Nee"
        writer.writerow({"pagetitle": page.title(), "wikidataID": wdid, "afbeelding in infobox": afbininfobox, "afbeelding in P18": afbP18, "P18 op pagina aanwezig": afbP18InPagina, "P18 in infobox": issameimage, "P18 buiten infobox gebruikt": attention})
