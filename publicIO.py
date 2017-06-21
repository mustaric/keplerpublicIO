# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 21:17:23 2017

Code to interact with the public data set.
Uses the robovetter Input and Output files for INV/SS1/INJ
The DR25 KOI table download.

@author: sthompson  - Susan Thompson
@Date: April 24, 2017
"""
from astropy.io import ascii
import pandas as p
import numpy as np


class DR25_IO(object):
    """
    First attempt at object oriented with IO for reading in the public
    data from NexScI for DR25 catalog.
    The IO class contains information about where the data is stored.
    """
    def __init__(self,ddir='/Users/sthompson/kepler/DR25/publicData/'):
        self.ddir=ddir
        self.dr25koiname='other/q1_q17_dr25_koi.tbl'
        self.datatypes=['obs','inv','scr1','inj1']  #observed, inverted, scrambled, injected
        self.rvroot='RoboVet-Public/kplr_dr25_'
        self.rvinroot='_robovetter_input.txt'
        self.rvoutroot='_robovetter_output.txt'
        self.banned='other/Banned-TCEs.txt'
        self.cleanroot='other/kplr_droplist_'
        self.d2root='tces/kplr_dr25_'
        self.cumkoiname='other/cumulative_koi.tbl'
        self.prevkois='other/q1q17-status.csv'

    def loadKOITable(self):

        """
        Load the KOI table as downloaded from NExScI in Ipac format
        Return a pandas dataframe
        """
        datafile=self.ddir+self.dr25koiname
        tabledata=ascii.read(datafile)
        
        koidf=tabledata.to_pandas()
    
        #Some rearranging of names to make working easier.    
        tceids=map(lambda x,y: "%09i-%02i" % (x,y) , koidf.kepid,koidf.koi_tce_plnt_num )
        
        koidf['disp'] = koidf.koi_pdisposition
        koidf['period'] = koidf.koi_period
        koidf['mes'] = koidf.koi_max_mult_ev
        koidf['NT'] = koidf.koi_fpflag_nt
        koidf['SS'] = koidf.koi_fpflag_ss
        koidf['CO'] = koidf.koi_fpflag_co
        koidf['Rp'] = koidf.koi_prad
        koidf['TCE_ID'] = tceids    
        koidf.set_index('TCE_ID',inplace=True)
    
        return koidf
        
    def loadCumKOITable(self):
        """
        Load the KOI table as downloaded from NExScI in Ipac format
        Return a pandas dataframe
        """
        datafile=self.ddir+self.cumkoiname
        tabledata=ascii.read(datafile)
        
        koidf=tabledata.to_pandas()
        
        colnames=['koiname','kepid','tce','date','auth','fitFile',\
                    'CentroidFile','status','dispFlag','comment']
        prekois=p.read_csv(self.ddir+self.prevkois,sep='|',comment='#',names=colnames)
        dr24cumkois=prekois.koiname
        cumkois=koidf.kepoi_name
        newlist=set(cumkois) - set(dr24cumkois)
        print len(newlist)
    
        #Some rearranging of names to make working easier.    
        #tceids=map(lambda x,y: "%09u-%02u" % (x,y) , koidf.kepid,koidf.koi_tce_plnt_num )
        koidf.set_index('kepoi_name',inplace=True)
        koidf['disp'] = koidf.koi_pdisposition
        koidf['period'] = koidf.koi_period
        koidf['mes'] = koidf.koi_max_mult_ev
        koidf['NT'] = koidf.koi_fpflag_nt
        koidf['SS'] = koidf.koi_fpflag_ss
        koidf['CO'] = koidf.koi_fpflag_co
        koidf['Rp'] = koidf.koi_prad
        koidf['New'] = np.zeros(len(koidf),dtype=bool)
        #Set a column called new for the new KOIs
        newones=koidf.index.isin(newlist)
        for v in newlist:
            koidf.set_value(v,'New',True)        
    
        return koidf
        

    def loadRVin(self,datatype):
        """
        Load the robovetter input or output and return a Data frame.
        datatype is INJ,INV, SS1, OPS
        in out is 'in' or 'out'
        """       
        datafile=self.ddir + self.rvroot + datatype + self.rvinroot         
        tabledata=ascii.read(datafile)
        df=tabledata.to_pandas()
        df.set_index('TCE_ID',inplace=True)

        return df        
 
    def loadRVout(self,datatype):
        """
        Load RV output file in Jeff's funny format.
        """
        datafile=self.ddir + self.rvroot + datatype + self.rvoutroot
        colnames=('TCE_ID','score','disp','NT','SS','CO','EM','flags')
        df=p.read_csv(datafile,sep=' ',skiprows=1,header=None,\
                        names=colnames,index_col='TCE_ID')
        return df
        
    def loadInj(self,expmes=True):
        """
        Return dataframes for INJ,INV,SS1,OPS and KOI Table
        Clean the INV and SS1
        Remove Banned from the OPS
        """
        dtype=self.datatypes[3]
        injin=self.loadRVin(dtype)
        injout=self.loadRVout(dtype)
        inj=injin.merge(injout,how='outer',right_index=True, left_index=True)
        d2inj=self.loadD2Data(dtype)
        inj=inj.merge(d2inj,how='inner',right_index=True,left_index=True,suffixes=('_x',''))
        
        #Loadin teh Expected MES from D.0
        #This isn't complete because I don't have D.0 yet.
        if expmes:
            pass
        
        return inj
    
    def loadInOut(self,datatype='ops',clean=True):
        """
        Load and merge the Inverted or SS1 data set, and clean it
        Takes INV or SS1. 
        This is not for OPS or INJ or combining INV and SS1
        """
        if datatype==self.datatypes[0]:
            print "Use loadOps(banned=True) instead"
            return 
            
        invin=self.loadRVin(datatype)
        invout=self.loadRVout(datatype)
        inv=invin.merge(invout,how='outer',right_index=True, left_index=True)
        d2inv=self.loadD2Data(datatype)
        inv=inv.merge(d2inv,how='inner',right_index=True,left_index=True,suffixes=('_x',''))
        if clean:
            cleanlist=self.cleanlist(datatype)
            tces=inv.index
            #Select only those that are actually in the inv 
            hasthese=set(tces) & set(cleanlist)
            print len(hasthese)
            inv.drop(hasthese,inplace=True,errors='ignore',axis=0)
        
        return inv
        
    def loadBothFA(self,clean=True):
        """
        Load and merge the SS1 and INV sets and then combine them into
        one dataframe
        """
        inv=self.loadInOut(datatype=self.datatypes[1],clean=clean)
        ss1=self.loadInOut(datatype=self.datatypes[2],clean=clean)
        df=p.concat([inv,ss1],ignore_index=True)
        
        return df
    
    def loadInv(self,clean=True):
        """
        Load and merge the SS1 and INV sets and then combine them into
        one dataframe
        """
        inv=self.loadInOut(datatype=self.datatypes[1],clean=clean)
        
        return inv
        
    def loadScr(self,clean=True):
        """
        Load and merge the SS1 and INV sets and then combine them into
        one dataframe
        """
        inv=self.loadInOut(datatype=self.datatypes[2],clean=clean)
        
        return inv
        
    
    def loadOps(self,banned=True):
        """
        Load the ops TCEs and remove those on the banned list
        """
        opsin=self.loadRVin(self.datatypes[0])
        opsout=self.loadRVout(self.datatypes[0])
        ops=opsin.merge(opsout,how='outer',right_index=True,left_index=True)
        d2ops=self.loadD2Data(self.datatypes[0])
        ops=ops.merge(d2ops,how='inner',right_index=True,left_index=True,suffixes=('_x',''))
        
        if banned:
            banlist=self.loadBannedTCEs()
            ops.drop(banlist,inplace=True)
            
        return ops
    
    def loadBannedTCEs(self):
        """
        Get list of TCEs that are banned from creating a KOI.
        """
        datafile=self.ddir + self.banned
        banlist=np.loadtxt(datafile,usecols=[0],dtype=str)
        
        return banlist
    
    def cleanlist(self,datatype):
        """
        GEt list of TCEs that were cleaned from SS1 or INV
        """
        datafile=self.ddir + self.cleanroot + datatype + '.txt'
        print datafile
        cleanlist=np.loadtxt(datafile,usecols=[0],dtype=str,skiprows=8,comments='#')
        
        return cleanlist
    
    def loadD2Data(self,datatype):
        """
        Read in the D.2 data files for INJ,INV,OPS,SS1
        """
        datafile=self.ddir + self.d2root + datatype +'_tces.txt'
                
        tabledata=ascii.read(datafile)
        df=tabledata.to_pandas()
        df.set_index('TCE_ID',inplace=True)
        
        return df