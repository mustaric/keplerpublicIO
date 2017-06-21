# keplerpublicIO
Input/Output code to read in the Kepler Data Prodcuts hosted at NASA exoplanet archive for DR25.

To use publicIO:
1) put the data files into an accessible directory, i.e. publicData as the following:

                publicData/
                
                    other/
                      Banned-TCEs.txt   (This file is attached here)
                      kplr_droplist_inv.txt  (This file is attached here)
                      kplr_droplist_scr1.txt   (This file is attached here)
                      q1_q17_dr25_koi.tbl  (this is a download of the dr25 KOI table at NExScI)
                    
                    RoboVet-Public/
                         kplr_dr25_inj1_robovetter_input
                         kplr_dr25_scr1_robovetter_output
                         kplr_dr25_inj1_robovetter_output
                         etc.  (see github.com/nasa/kepler-robovetter)
                    tces/
                      kplr_dr25_inj1_tces.txt 
                      kplr_dr25_inv_tces.txt  
                      kplr_dr25_scr1_tces.txt
 2) create a dr25 object with
           dr25=io.DR25_IO(ddir="/Users/sthompson/kepler/DR25/publicData/")
 3) load the information you want, using for example:
           observed TCE list
           ops=dr25.loadOps()
           inv=dr25.loadInv()
           scr1=dr25.loadScr1()
           inj1=dr25.loadInj1()
           koi = dr25.loadKOITable() 
           etc.
           See the code for which data you can load
