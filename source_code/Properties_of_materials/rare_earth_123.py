# Importing python libraries and other funcions
import numpy as np

# Function BCRE123 starts here
def critical_magnetic_field_re123(T, TC0M, BC20M, alpha):
    """
    ######################################################################
    #    REAL FUNCTION BCRE123(T, TC0M, BC20M, alpha)
    ######################################################################
    #
    # Critical field, in T, for Re-123 as a function of temperature.
    # Validity range: B > 8 T; T < 40 K
    #
    #        References
    #        ----------
    # R. Wesche, Report on CS Winding Pack Design and Analysis, January 16,
    # 2017, EFDA_D_2MRPVA (Section 2.2, pag. 6 of 37).
    #
    #
    # variable    I/O       meaning        units
    # --------------------------------------------------------------------
    #   T     x    absolute temperature      K
    #   TC0M  x    critical temperature (B=0)    K
    #   BC20M     x    upper critical field (T=0)    T
    #   BCRe123     x      Upper critical field      T
    #
    # Other functions called: NONE
    #
    # Author : R.Bonifetto @ Politecnico di Torino
    # Version: 1  28.6.2017
    #
    ##############################################################################
    # Translation and optimization from Fortran: D.Placido PoliTo 06/2020
    # Tested against temperature [1.5,35] K @ fixed magnetic field [8.5,10,13] T,
    # against magnetic field [8.1,13] T # fixed temperatutre [5,15,35] K and
    # agains temperature and magnetic filed with sin and cos shape respectively
    # along 100 m of conductor. D.Placido PoliTo 06/2020
    ##############################################################################
    """

    if TC0M < 1.0e-6:
        raise ValueError("ERROR> From BcRe123\nTc0m = 0\nSTOP BcRe123!")

    if BC20M < 1.0e-6:
        raise ValueError("ERROR> From BcRe123\nBC20M = 0\nSTOP BcRe123!")

    T = np.array(T)
    BCRE123 = np.zeros(T.shape)
    # * NORMALISED TEMPERATURE T/TC0
    TLCASE = T / TC0M

    # Find element index in TLCASE such that TLCASE < 1.0 (cdp, 06/2020)
    TLCASE_ind = np.nonzero(TLCASE < 1.0)  # this is a tuple (cdp, 06/2020)
    if TLCASE_ind[0].size == 0:  # empty index array (cdp, 06/2020)
        return BCRE123

    # * CRITICAL FIELD
    BCRE123[TLCASE_ind[0]] = BC20M * (1.0e0 - TLCASE[TLCASE_ind[0]]) ** alpha

    return BCRE123


# Function CONDRE123 starts here
def thermal_conductivity_re123(TT):

    """
    ##############################################################################
    #         FUNCTION CONDRE123(T)
    ##############################################################################
    #
    # Thermal conductivity of Re-123 as a function of temperature T, for
    # 4 <= T <= 300 K.
    #
    #                        References
    #                        ----------
    #
    # A.D. Berger
    # Stability of Superconducting Cables with Twisted Stacked YBCO Coated
    # Conductors
    # Plasma Science and Fusion Center (PSFC) / RR-11-15, MIT, Feb. 2012.
    #
    # variable    I/O               meaning                        units
    # --------------------------------------------------------------------
    #   T         x            absolute temperature                  K
    #   CORE123     x          thermal conductivity                W/m K
    #
    # Author : R.Bonifetto @ Politecnico di Torino
    # Version: 1  28.6.2017
    #
    ##############################################################################
    # Translation from Fortran to Python: D.Placido PoliTo 10/07/2020
    # Tested against temperature in range [4,300] K: D.Placido PoliTo 11/07/2020
    ##############################################################################
    """

    TT = np.array(TT)
    CONDRE123 = np.zeros(TT.shape)
    TMIN = 4.0
    TMAX = 300.0

    TT = np.minimum(TT, TMAX)
    TT = np.maximum(TT, TMIN)

    A = np.array([-1.266103106492942e-5, -1.316704893540544e-9])
    B = np.array([0.002670105477219, 2.636151594117440e-06])
    C = np.array([-0.197035302542769, -0.001601689632073])
    D = np.array([4.933962659604384, 0.428760641312538])
    E = np.array([29.651536939501670, -53.306643333287260])
    F = np.array([66.578192505447330, 3.682252343338599e03])

    intervals = [(TT <= 70.0), (TT > 70.0)]
    behaviour = [
        lambda TT: (
            A[0] * TT ** 5
            + B[0] * TT ** 4
            + C[0] * TT ** 3
            + D[0] * TT ** 2
            + E[0] * TT
            + F[0]
        ),
        lambda TT: (
            A[1] * TT ** 5
            + B[1] * TT ** 4
            + C[1] * TT ** 3
            + D[1] * TT ** 2
            + E[1] * TT
            + F[1]
        ),
    ]

    CONDRE123 = np.piecewise(TT, intervals, behaviour)

    return CONDRE123


# Function CPRE123 starts here
def isobaric_specific_heat_re123(TT):

    """
    ##############################################################################
    #             FUNCTION CPRE123(T)
    ##############################################################################
    #
    # Specific Heat of binary Re-123 in J/Kg K as a function of temperature,
    # for 4 <= T <= 300 K.
    #
    #                        References
    #                        ----------
    #
    # A.D. Berger
    # Stability of Superconducting Cables with Twisted Stacked YBCO Coated
    # Conductors
    # Plasma Science and Fusion Center (PSFC) / RR-11-15, MIT, Feb. 2012.
    #
    # variable    I/O               meaning                        units
    # --------------------------------------------------------------------
    #   T         x            absolute temperature                  K
    #   CPRE123     x          specific heat                       J/Kg K
    #
    # Other functions called: NONE
    #
    # Author : R.Bonifetto @ Politecnico di Torino
    # Version: 1  28.6.2017
    #
    ##############################################################################
    # Translation from Fortran to Python: D.Placido PoliTo 10/07/2020
    # Tested against temperature in range [4,300] K: D.Placido PoliTo 11/07/2020
    ##############################################################################
    """

    TT = np.array(TT)
    CPRE123 = np.zeros(TT.shape)
    TMIN = 4.0
    TMAX = 300.0

    TT = np.minimum(TT, TMAX)
    TT = np.maximum(TT, TMIN)

    AA = -7.567485538209158e-10
    BB = 6.351452642016898e-07
    CC = -1.947975786547597e-04
    DD = 0.023616673974415
    EE = 0.239331954284042
    FF = -1.096191721280114

    CPRE123 = AA * TT ** 5 + BB * TT ** 4 + CC * TT ** 3 + DD * TT ** 2 + EE * TT + FF

    return CPRE123


# Function JCRE123 starts here
def critical_current_density_re123(T, B, TC0M, BC20M, c0):

    """
    ######################################################################
    # REAL FUNCTION JCRE123(T     ,B     ,TC0M  ,BC20M ,c0 ,ICOND)
    ######################################################################
    #
    # Critical (non-copper) current density, in A/m**2, for Re-123 as a
    # function of temperature and field.
    # Note that a lower limit is used on field and temperature to avoid
    # the 0-singularity.
    # Validity range: B > 8 T; T < 40 K
    #
    #    References
    #    ----------
    # R. Wesche, Report on CS Winding Pack Design and Analysis, January 16,
    # 2017, EFDA_D_2MRPVA (Section 2.2, pag. 6 of 37).
    #
    #
    # variable    I/O   meaning    units
    # --------------------------------------------------------------------
    #   T     x    absolute temperature  K
    #   B     x    magnetic field    T
    #   TC0M  x    critical temperature (B=0)    K
    #   BC20M     x    upper critical field (T=0)    T
    #   c0    x    normalization constant     A T/m**2
    #   JCRe-123    x  critical current density    A/m**2
    #
    # Other functions called: BCRE123
    #
    # Author : R.Bonifetto @ Politecnico di Torino
    # Version: 1  28.6.2017
    #
    ##############################################################################
    # Translation and optimization from Fortran: D.Placido PoliTo 06/2020
    # Tested against temperature [1.5,35] K @ fixed magnetic field [8.5,10,13] T,
    # against magnetic field [8.1,13] T # fixed temperatutre [5,15,35] K and
    # agains temperature and magnetic filed with sin and cos shape respectively
    # along 100 m of conductor. D.Placido PoliTo 06/2020
    ##############################################################################
    """

    ppp = 5.875e-1
    qqq = 1.7
    BLOW = 0.01
    alpha = 1.54121
    beta = 1.96679

    T = np.array(T)
    B = np.array(B)

    if len(T) == 1:
        T = T * np.ones(B.shape)
    if len(B) == 1:
        B = B * np.ones(T.shape)

    # JCRE123 initialization
    JCRE123 = np.zeros(T.shape)
    BLCASE = np.zeros(B.shape)
    TLCASE = np.zeros(B.shape)

    if TC0M < 1.0e-6:
        raise ValueError("ERROR> From JcRe123\nTc0m = 0\nSTOP JcRe123!")

    if BC20M < 1.0e-6:
        raise ValueError("ERROR> From JcRe123\nBC20M = 0\nSTOP JcRe123!")

    if c0 < 1.0e-6:
        raise ValueError("ERROR> From JcRe123\nc0 = 0\nSTOP JcRe123!")

    # * SET THE LOWER LIMIT FOR THE FIELD
    BLIM = np.maximum(B, BLOW)  # BLOW??

    # * NORMALISED TEMPERATURE T/TC0
    TLCASE = T / TC0M

    # Find element index in TLCASE such that TLCASE < 1.0 (cdp, 06/2020)
    TLCASE_ind = np.nonzero(TLCASE < 1.0)  # this is a tuple (cdp, 06/2020)
    if TLCASE_ind[0].size == 0:  # empty index array (cdp, 06/2020)
        return JCRE123

    # * NORMALISED FIELD B/BC0
    BLCASE[TLCASE_ind[0]] = BLIM[TLCASE_ind[0]] / (
        critical_magnetic_field_re123(T[TLCASE_ind[0]], TC0M, BC20M, alpha)
    )

    # Find element index such that BLCASE[TLCASE_ind[0]] < 1.0, only for those index JCRE123 will be evaluated, elsewere JCRE123 = 0.0 by initialization (cdp, 06/2020)
    ind = np.nonzero(BLCASE[TLCASE_ind[0]] < 1.0)  # this is a tuple (cdp, 06/2020)
    BLCASE_ind = TLCASE_ind[0][ind[0]]  # this is an array (cdp, 06/2020)
    if BLCASE_ind.size == 0:  # empty index array (cdp, 06/2020)
        return JCRE123

    # * JCRE123(T,B,EPSLON)
    JCRE123[BLCASE_ind] = (
        c0
        / BLIM[BLCASE_ind]
        * critical_magnetic_field_re123(T[BLCASE_ind], TC0M, BC20M, alpha) ** beta
        * BLCASE[BLCASE_ind] ** ppp
        * (1.0e0 - BLCASE[BLCASE_ind]) ** qqq
    )

    # * CHECK THAT JCRE123 > 0
    # Find element index such that JCRE123[BLCASE_ind] < 0, for these index JCRE123 = 0.0 (cdp, 2020)
    ind = np.nonzero(JCRE123[BLCASE_ind] < 0.0)  # this is a tuple (cdp, 06/2020)
    JC_ind = BLCASE_ind[ind[0]]  # this is an array (cdp, 06/2020)
    JCRE123[JC_ind] = 0.0

    return JCRE123


# Function TCSRE123 starts here
def current_sharing_temperature_re123(B, JOP, TC0M, BC20M, c0):
    """
    ######################################################################
    # REAL FUNCTION TCSRE123(B, JOP, TC0M, BC20M, c0)
    ######################################################################
    #
    # Current sharing temperature, in K, for Re-123 as a function of field.
    # The critical temperature is computed by iterative
    # inversion of the Jc(T,B) relation. Note that a minimum value
    # is used for the field and temperature to avoid the 0-singularity
    # Validity range: B > 8 T; T < 40 K
    #
    #        References
    #        ----------
    # R. Wesche, Report on CS Winding Pack Design and Analysis, January 16,
    # 2017, EFDA_D_2MRPVA (Section 2.2, pag. 6 of 37).
    #
    #
    # variable    I/O       meaning        units
    # --------------------------------------------------------------------
    #   B     x    magnetic field        T
    #   JOP   x    operating current density       A/m**2
    #   TC0M  x    critical temperature (B=0)    K
    #   BC20M     x    upper critical field (T=0)    T
    #   c0    x    normalization constant     A T/m**2
    #   TCSRe123    x      current sharing temperature       K
    #
    # Other functions called: TcsRe123
    #
    # Author : R.Bonifetto @ Politecnico di Torino
    # Version: 1  28.6.2017
    #
    ##############################################################################
    # Translation and optimization from Fortran: D.Placido PoliTo 06/2020
    # Tested against temperature [1.5,35] K @ fixed magnetic field [8.5,10,13] T,
    # against magnetic field [8.1,13] T # fixed temperatutre [5,15,35] K and
    # agains temperature and magnetic filed with sin and cos shape respectively
    # along 100 m of conductor. D.Placido PoliTo 06/2020
    ##############################################################################
    """

    def BL(TT, BB, TC0M, BC20M, alpha):
        BL = BB / (BC20M * (1 - TT / TC0M) ** alpha)
        return BL

    def RSDL(TT, BB, JJ, TC0M, BC20M, c0, ppp, qqq, alpha, beta):

        RSDL = (
            c0
            / BB ** (1 - beta)
            * BL(TT, BB, TC0M, BC20M, alpha) ** (ppp - beta)
            * (1 - BL(TT, BB, TC0M, BC20M, alpha)) ** qqq
            - JJ
        )
        return RSDL

    ppp = 5.875e-1
    qqq = 1.7
    BLOW = 0.01
    alpha = 1.54121
    beta = 1.96679

    if TC0M < 1.0e-6:
        raise ValueError("ERROR> From TcsRe123\nTc0m = 0\nSTOP TcsRe123#")

    if BC20M < 1.0e-6:
        raise ValueError("ERROR> From TcsRe123\nBC20M = 0\nSTOP TcsRe123#")

    if c0 < 1.0e-6:
        raise ValueError("ERROR> From TcsRe123\nc0 = 0\nSTOP TcsRe123#")

    B = np.array(B)

    # variable initialization
    TCSRE123 = np.zeros(B.shape)
    JC = np.zeros(B.shape)
    # BLCASE = np.zeros(B.shape)
    # TLCASE = np.zeros(B.shape)
    TCST = np.zeros(B.shape)

    # *SET THE LOWER LIMIT FOR THE FIELD
    BLIM = np.maximum(B, BLOW)
    Bstar = BLIM / BC20M
    # *CHECK THAT THE FIELD IS BELOW THE UPPER CRITICAL VALUE
    # Find element index in such that Bstar < 1.0 (cdp, 06/2020)
    Bstar_ind = np.nonzero(Bstar < 1.0)  # this is a tuple (cdp, 06/2020)
    if Bstar_ind[0].size == 0:  # empty index array (cdp, 06/2020)
        return TCSRE123

    JC[Bstar_ind[0]] = critical_current_density_re123(
        np.zeros(B[Bstar_ind].shape), B[Bstar_ind[0]], TC0M, BC20M, c0
    )
    # *CHECK THAT JOP IS BELOW THE UPPER CRITICAL VALUE
    # Find element index such that JC[Bstar_ind] < JOP (cdp, 06/2020)
    ind = np.nonzero(JC[Bstar_ind[0]] > JOP)  # this is a tuple (cdp, 06/2020)
    JC_ind = Bstar_ind[0][ind[0]]  # this is an array (cdp, 06/2020)
    if JC_ind.size == 0:
        return TCSRE123

    # *FIND THE NORMALISED TEMPERATURE TCS/TC0 BY "GRAND-MOTHER MODIFIED" OR "AUNT" METHOD #crb (January 29, 2018)
    for ii in range(len(JC_ind)):

        NEXT = 0
        NITER = 1
        DELTAT = 0.25e0

        while (NEXT < 3) and (NITER < 1000):

            R = RSDL(
                TCST[JC_ind[ii]],
                B[JC_ind[ii]],
                JOP,
                TC0M,
                BC20M,
                c0,
                ppp,
                qqq,
                alpha,
                beta,
            )
            if NITER == 1:
                ROLD = R
            PROD = R * ROLD

            if PROD < 0.0:
                NEXT = NEXT + 1
                TCST[JC_ind[ii]] = TCST[JC_ind[ii]] - DELTAT
                DELTAT = DELTAT / 10.0
            else:
                ROLD = R
            NITER = NITER + 1
            TCST[JC_ind[ii]] = TCST[JC_ind[ii]] + DELTAT
        # end while
        TCSRE123[JC_ind[ii]] = TCST[JC_ind[ii]] - 2.0 * DELTAT
    # end for #crb End (January 29, 2018)

    return TCSRE123


# Function rho_RE123 starts here
def density_re123():
    """
    RE123 density kg/m^3. It is assumed constant.
    Autor: D. Placido Polito 21/01/2021
    """
    return 6380.0


# end function rho_RE123 (cdp, 01/2021)
