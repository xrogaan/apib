# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=80:


bodyparts = {
    'head':     ['TOP'],
    'nose':     ['head'],
    'neck':     ['TOP'],
    'arm':      ['LEFT', 'RIGHT','MIDDLE'],
    'hand':     ['arm'],
    'finger':   ['hand'],
    'leg':      ['LEFT', 'RIGHT', 'BOTTOM'],
    'foot':     ['leg'],
    'eye':      ['head'],
    'torso':    ['MIDDLE','CENTRAL'],
    'tooth':    ['head']
}

attacks = {
    'kick': {
        'used': ['foot']
     },
    'punch': {
        'used': ['hand']
    },
    'bit': {
        'used': ['tooth']
    },
    'headbutt': {
        'used': ['head']
    }
}

# parry from %bodypart with %bodypart
parry = [
        '',
        ]

strings = [
        '%(nick)s is tearing ',
        ]
