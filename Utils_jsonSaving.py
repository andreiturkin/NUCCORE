import os
import json
from interval import interval

def __writeFile(append, fName, inx, IntervalRes, GlobalOptResMin, GlobalOptResMax):
    if append:
        with open(fName) as f:
            data = json.load(f)
    else:
        data = {}
        data['inputs'] = []
        data['IntervalgFuncs'] = []
        data['IntervalRes'] = []
        data['GlobalOptgFuncs'] = []
        data['GlobalOptRes'] = []

    data['inputs'].append({
        'x'     : '{}'.format(inx[0]),
        'y'     : '{}'.format(inx[1]),
        'angle' : '{}'.format(inx[2])
    })
    data['IntervalgFuncs'].append({
        'gFunc00': '{}'.format(IntervalRes[0]),
        'gFunc01': '{}'.format(IntervalRes[1]),
        'gFunc02': '{}'.format(IntervalRes[2]),
        'gFunc03': '{}'.format(IntervalRes[3]),
        'gFunc04': '{}'.format(IntervalRes[4]),
        'gFunc05': '{}'.format(IntervalRes[5]),
        'gFunc06': '{}'.format(IntervalRes[6]),
        'gFunc07': '{}'.format(IntervalRes[7]),
        'gFunc08': '{}'.format(IntervalRes[10]),
        'gFunc09': '{}'.format(IntervalRes[11]),
        'gFunc10': '{}'.format(IntervalRes[14]),
        'gFunc11': '{}'.format(IntervalRes[15]),
        'gFunc12': '{}'.format(IntervalRes[8]),
        'gFunc13': '{}'.format(IntervalRes[9]),
        'gFunc14': '{}'.format(IntervalRes[12]),
        'gFunc15': '{}'.format(IntervalRes[13]),
        'gFunc16': '{}'.format(IntervalRes[16]),
        'gFunc17': '{}'.format(IntervalRes[17])
    })
    data['GlobalOptgFuncs'].append({
        'gFunc00': 'globalopt{}'.format((GlobalOptResMin[0], GlobalOptResMax[0])),
        'gFunc01': 'globalopt{}'.format((GlobalOptResMin[1], GlobalOptResMax[1])),
        'gFunc02': 'globalopt{}'.format((GlobalOptResMin[2], GlobalOptResMax[2])),
        'gFunc03': 'globalopt{}'.format((GlobalOptResMin[3], GlobalOptResMax[3])),
        'gFunc04': 'globalopt{}'.format((GlobalOptResMin[4], GlobalOptResMax[4])),
        'gFunc05': 'globalopt{}'.format((GlobalOptResMin[5], GlobalOptResMax[5])),
        'gFunc06': 'globalopt{}'.format((GlobalOptResMin[6], GlobalOptResMax[6])),
        'gFunc07': 'globalopt{}'.format((GlobalOptResMin[7], GlobalOptResMax[7])),
        'gFunc08': 'globalopt{}'.format((GlobalOptResMin[10], GlobalOptResMax[10])),
        'gFunc09': 'globalopt{}'.format((GlobalOptResMin[11], GlobalOptResMax[11])),
        'gFunc10': 'globalopt{}'.format((GlobalOptResMin[14], GlobalOptResMax[14])),
        'gFunc11': 'globalopt{}'.format((GlobalOptResMin[15], GlobalOptResMax[15])),
        'gFunc12': 'globalopt{}'.format((GlobalOptResMin[8], GlobalOptResMax[8])),
        'gFunc13': 'globalopt{}'.format((GlobalOptResMin[9], GlobalOptResMax[9])),
        'gFunc14': 'globalopt{}'.format((GlobalOptResMin[12], GlobalOptResMax[12])),
        'gFunc15': 'globalopt{}'.format((GlobalOptResMin[13], GlobalOptResMax[13])),
        'gFunc16': 'globalopt{}'.format((GlobalOptResMin[16], GlobalOptResMax[16])),
        'gFunc17': 'globalopt{}'.format((GlobalOptResMin[17], GlobalOptResMax[17]))
    })
    data['IntervalRes'].append({
        'min': '{}'.format(max(interval(intl)[0][0] for x in IntervalRes for intl in x)),
        'max': '{}'.format(max(interval(intl)[0][1] for x in IntervalRes for intl in x))
    })
    data['GlobalOptRes'].append({
        'min': '{}'.format(max(GlobalOptResMin)),
        'max': '{}'.format(max(GlobalOptResMax))
    })
    with open(fName, 'w') as outfile:
        json.dump(data, outfile)

def saveDataToFile(fName, inx, intlres, goptresmin, goptresmax):
    print '...Saving data to {} for the following box:\n x={},\n y={},\n z={}'.format(fName, inx[0], inx[1], inx[2])
    if os.path.isfile(fName):
        __writeFile(True, fName, inx, intlres, goptresmin, goptresmax)
    else:
        __writeFile(False, fName, inx, intlres, goptresmin, goptresmax)

