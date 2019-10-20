def Muskingum(C1, C2, C3, Qn0_t1, Qn0_t0, Qn1_t0):
    ''' Simulates hydrological routing '''
    Qn1_t1 = C1 * Qn0_t1 + C2 * Qn0_t0 + C3 * Qn1_t0
    return Qn1_t1