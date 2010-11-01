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
        'messages': {
            'normal':   'Ouch, that did hurt!',
            'missed':   "Improve your AIM - Improve yourself. You just missed " \
                        "me, faggot!",
            'critical': "Yeah, thanks to you. You just destroyed my "+part+'.',
            'powerless':"Ah ah, that kick doesn't even frighten a bug !",
        }
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
    'stabs': {
        'used': ['hand', 'dagger']
    }
}

# modifiers: critical, powerless, miss
# 1 doesn't do anything
weapons = {
    'dagger': [0.5, 0.5, 1]
}

# parry from %bodypart with %bodypart
parry = [
        '',
        ]

strings = [
        '%(nick)s is tearing ',
        ]
