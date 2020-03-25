#!/usr/local/lcls/package/python/current/bin/python

def stopper2_dict(name, ctrl, status):
    stopper_dict = {
        'ctrl': 'SIOC:SYS0:MP01:DISABLE_' + ctrl,
        'open': name + ' Allowed',
        'closed': name + ' Disabled',
        'status': status
    }

    return stopper_dict

STOPPERS = {
    'AOM': stopper2_dict('AOM', 'AOM', 'MPLN:GUNB:MP01:1:RTM_DO'),
    'MPS': stopper2_dict('Shutter', 'BEAM', 'SHUT:GUNB:100:CLOSED_STATUS_MPSC')
}
