############################TESTS ON POTENTIALS################################
import numpy

#Test whether the normalization of the potential works
def test_normalize_potential():
    from galpy import potential
    #Grab all of the potentials
    pots= [p for p in dir(potential) 
           if ('Potential' in p and not 'plot' in p and not 'RZTo' in p 
               and not 'evaluate' in p)]
    rmpots= ['Potential','MWPotential','MovingObjectPotential',
             'interpRZPotential', 'linearPotential', 'planarAxiPotential',
             'planarPotential', 'verticalPotential']
    for p in rmpots:
        pots.remove(p)
    for p in pots:
        #if not 'NFW' in p: continue #For testing the test
        #Setup instance of potential
        tclass= getattr(potential,p)
        tp= tclass()
        if not hasattr(tp,'normalize'): continue
        tp.normalize(1.)
        try:
            assert((tp.Rforce(1.,0.)+1.)**2. < 10.**-16.)
        except AssertionError:
            raise AssertionError("Normalization of %s potential fails" % p)
        tp.normalize(.5)
        try:
            assert((tp.Rforce(1.,0.)+.5)**2. < 10.**-16.)
        except AssertionError:
            raise AssertionError("Normalization of %s potential fails" % p)


#Test whether the derivative of the potential is minus the force
def test_forceAsDeriv_potential():
    from galpy import potential
    #Grab all of the potentials
    pots= [p for p in dir(potential) 
           if ('Potential' in p and not 'plot' in p and not 'RZTo' in p 
               and not 'evaluate' in p)]
    rmpots= ['Potential','MWPotential','MovingObjectPotential',
             'interpRZPotential', 'linearPotential', 'planarAxiPotential',
             'planarPotential', 'verticalPotential']
    for p in rmpots:
        pots.remove(p)
    Rs= numpy.array([0.5,1.,2.])
    Zs= numpy.array([0.,.125,-.125,0.25,-0.25]) #Zs are phis for planarPots
    #tolerances in log10
    tol= {}
    tol['default']= -10.
    tol['DoubleExponentialDiskPotential']= -6. #these are more difficult
    tol['RazorThinExponentialDiskPotential']= -8.
    for p in pots:
        #if not 'NFW' in p: continue #For testing the test
        #Setup instance of potential
        tclass= getattr(potential,p)
        tp= tclass()
        #raise AttributeError("Do something about potentials without normalize")
        if hasattr(tp,'normalize'): tp.normalize(1.)
        print "Working on %s" % p       
        #Set tolerance
        if p in tol.keys(): ttol= tol[p]
        else: ttol= tol['default']
        #Radial force
        for ii in range(len(Rs)):
            for jj in range(len(Zs)):
                dr= 10.**-8.
                newR= Rs[ii]+dr
                dr= newR-Rs[ii] #Representable number
                if isinstance(tp,potential.linearPotential): 
                    mpotderivR= (tp(Rs[ii])-tp(Rs[ii]+dr))/dr
                    tRforce= tp.force(Rs[ii])
                else:
                    mpotderivR= (tp(Rs[ii],Zs[jj])-tp(Rs[ii]+dr,Zs[jj]))/dr
                    tRforce= tp.Rforce(Rs[ii],Zs[jj])
                try:
                    if tRforce**2. < 10.**-ttol:
                        assert(mpotderivR**2. < 10.**-ttol)
                    else:
                        assert((tRforce-mpotderivR)**2./tRforce**2. < 10.**ttol)
                except AssertionError:
                    #print mpotderivR, tRforce
                    raise AssertionError("Calculation of the Radial force as the Radial derivative of the %s potential fails; diff = %e, rel. diff = %e" % (p,numpy.fabs(tRforce-mpotderivR), numpy.fabs((tRforce-mpotderivR)/tRforce)))
        #Vertical force, if it exists
        if isinstance(tp,potential.planarPotential) \
                or isinstance(tp,potential.linearPotential): continue
        for ii in range(len(Rs)):
            for jj in range(len(Zs)):
                dz= 10.**-8.
                newZ= Zs[jj]+dz
                dz= newZ-Zs[jj] #Representable number
                mpotderivz= (tp(Rs[ii],Zs[jj])-tp(Rs[ii],Zs[jj]+dz))/dz
                tzforce= tp.zforce(Rs[ii],Zs[jj])
                try:
                    if tzforce**2. < 10.**-ttol:
                        assert(mpotderivz**2. < 10.**-ttol)
                    else:
                        assert((tzforce-mpotderivz)**2./tzforce**2. < 10.**-ttol)
                except AssertionError:
                    raise AssertionError("Calculation of the vertical force as the vertical derivative of the %s potential fails; diff = %e, rel. diff = %e" % (p,numpy.fabs(mpotderivz),numpy.fabs((tzforce-mpotderivz)/tzforce)))
