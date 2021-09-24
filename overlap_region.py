#!/usr/bin/env python

import requests, sys
import re
import sys

#====================================================
# helper functions that fetch JSON from REST endpoints
def get_json(ext):
#======================================== 
    '''simple get function'''	

    server = "https://rest.ensembl.org"
    url = server+ext
    r = requests.get(url, headers={ "Content-Type" : "application/json"})
    
    if not r.ok:
        print ("There seems to be a problem with the JSON response - please see below:\n")
        r.raise_for_status()
        sys.exit()
    
    decoded = r.json()
    return decoded
#========================================
def print_features(f,species):
#======================================== 
    gene = f['id']
    length = f['end'] - f['start'] + 1
    print ("len=",length) 
    print ("chrom","start","end","strand","length",sep="\t")
    print (f['seq_region_name'],f['start'],f['end'],f['strand'],length,sep="\t")
        
    ##Get sequence
    ext2 = '/sequence/id/%s?species=%s;content-type=text/x-fasta'%(gene,species)
    prot_data = get_json(ext2)
    print(">%s\n%s" % (prot_data['id'],prot_data['seq']))
    #print (len(prot_data['seq']))


#======================================== 
def get_overlapping_features(species,region):
#======================================== 
    ##Info about species and region
    print ("species:",species)
    print ("region:",region)

    ## get the genes via the API
    print ("\n=====Genes===========\n")
    overlap_url = ("/overlap/region/" + species + "/" + region)
    ext = (overlap_url + "?ffeature=gene;content-type=application/json")
    overlap_data = get_json(ext)
    for overlap_feat in overlap_data:
        if overlap_feat['biotype'] == 'protein_coding':
            print_features(overlap_feat,species)
           
    ## now LTR repeats
    print ("\n=====LTR repeats===========\n")
    ext = (overlap_url + "?feature=repeat;content-type=application/json");
    overlap_data = get_json(ext)

    print ("description","start","end",sep="\t")
    for overlap_feat in overlap_data:
        ltr_match = re.search('LTR', overlap_feat['description'])
        if ltr_match:
            print(overlap_feat['description'],overlap_feat['start'],overlap_feat['end'],sep="\t")


    ## search for a specific variation source
    print ("\n=====SNPs===========\n")
    source_variation = 'CerealsDB';

    ext = (overlap_url + "?feature=variation;content-type=application/json");
    overlap_data = get_json(ext)

    print ("id","source","consequence",sep="\t")
    for overlap_feat in overlap_data:
        if overlap_feat['source'] == source_variation:
            print(overlap_feat['id'],overlap_feat['source'],overlap_feat['consequence_type'],sep="\t")

#======================================== 
#Main
species = 'triticum_aestivum';
region = '3D:379477845-379542988';
get_overlapping_features(species,region) #function call


