#!/usr/local/lcls/package/python/current/bin/python

from epics import PV
import stopper_constants as sc

def get_stoppers():
    """Return MAD names of aall stopers that have models"""
    return sc.STOPPERS.keys()

class Stopper(object):
    def __init__(self, stopper='AOM'):
        if stopper not in sc.STOPPERS.keys():
            raise ValueError('{0} is not a recognized stopper'.format(stopper))
        stopper_dict = sc.STOPPERS[stopper]
        self._stopper = stopper
        self._ctrl_pv = PV(stopper_dict['ctrl'])
        self._closed_state = stopper_dict['closed']
        self._opened_state = stopper_dict['open']
        self._open_clbk = None
        self._close_clbk = None
        self._cmd_active = False
        self._ctrl_vars = self._ctrl_pv.get_ctrlvars()['enum_strs']

    @property
    def state(self):
        """Get enabled state"""
        return self._ctrl_vars[self._ctrl_pv.get()]

    @property
    def states(self):
        """Get possible stopper states"""
        return self._ctrl_vars

    @property
    def stopper(self):
        """Get stopper name"""
        return self_stopper

    def open(self, usr_clbk=None):
        """Open the stopper, """
        if self._cmd_acitve:
            print('Stopper is currently being commanded, aborting')
            return

        if self._ctrl_vars[self._ctrl_pv.get()] == self._opened_state:
            print('Stopper {0}: {1}'.format(self._stopper, 'Already Open'))
            return

        if usr_clbk:
            self._open_clbk = clbk

        self._cmd_acitve = True
        self._ctrl_pv.add_callback(self._opened, index=0)
        self._ctrl_pv.put(self._opened_state)
        
    def _opened(self, value=None, **kw):
        """Run user callback, this should only be a signal for GUI, this
        puts us outside our context and will not function properly if it's not
        a """
        if self._ctrl_vars[value] == self._opened_state:
            print('Stopper {0} is now open'.format(self._stopper))

            if self._open_clbk:
                self._open_clbk()
                self._open_clbk = None

            self._ctrl_pv.remove_callback(index=0)
            self._cmd_active = False

    def close(self, usr_clbk=None):
        """Open the stopper, """
        if self._cmd_acitve:
            print('Stopper is currently being commanded, aborting')
            return

        if self._ctrl_vars[self._ctrl_pv.get()] == self._closed_state:
            print('Stopper {0}: {1}'.format(self._stopper, 'Already Closed'))
            usr_clbk()
            return

        if usr_clbk:
            self._close_clbk = clbk

        self._cmd_active = True
        self._ctrl_pv.add_callback(self._closed, index=0)
        self._ctrl_pv.put(self._closed_state)
        
    def _closed(self, value=None, **kw):
        """Run user callback, this should only be a signal for GUI, this
        puts us outside our context and will not function properly if it's not
        a """
        if self._ctrl_vars[value] == self._closed_state:
            print('Stopper {0} is now closed'.format(self._stopper))

            if self._close_clbk:
                self._close_clbk()
                self._close_clbk = None

            self._ctrl_pv.remove_callback(index=0)
            self._cmd_active = False