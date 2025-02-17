# **********************************************************************
#
# Copyright (c) 2003-2013 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************
#
# Ice version 3.5.1
#
# <auto-generated>
#
# Generated from file `Metrics.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

import Ice, IcePy
import Ice_Metrics_ice

# Included module Ice
_M_Ice = Ice.openModule('Ice')

# Included module IceMX
_M_IceMX = Ice.openModule('IceMX')

# Start of module IceMX
__name__ = 'IceMX'

if 'TopicMetrics' not in _M_IceMX.__dict__:
    _M_IceMX.TopicMetrics = Ice.createTempClass()
    class TopicMetrics(_M_IceMX.Metrics):
        '''Provides information on IceStorm topics.'''
        def __init__(self, id='', total=0, current=0, totalLifetime=0, failures=0, published=0, forwarded=0):
            _M_IceMX.Metrics.__init__(self, id, total, current, totalLifetime, failures)
            self.published = published
            self.forwarded = forwarded

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::IceMX::Metrics', '::IceMX::TopicMetrics')

        def ice_id(self, current=None):
            return '::IceMX::TopicMetrics'

        def ice_staticId():
            return '::IceMX::TopicMetrics'
        ice_staticId = staticmethod(ice_staticId)

        def __str__(self):
            return IcePy.stringify(self, _M_IceMX._t_TopicMetrics)

        __repr__ = __str__

    _M_IceMX.TopicMetricsPrx = Ice.createTempClass()
    class TopicMetricsPrx(_M_IceMX.MetricsPrx):

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_IceMX.TopicMetricsPrx.ice_checkedCast(proxy, '::IceMX::TopicMetrics', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_IceMX.TopicMetricsPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

    _M_IceMX._t_TopicMetricsPrx = IcePy.defineProxy('::IceMX::TopicMetrics', TopicMetricsPrx)

    _M_IceMX._t_TopicMetrics = IcePy.defineClass('::IceMX::TopicMetrics', TopicMetrics, -1, (), False, False, _M_IceMX._t_Metrics, (), (
        ('published', (), IcePy._t_long, False, 0),
        ('forwarded', (), IcePy._t_long, False, 0)
    ))
    TopicMetrics._ice_type = _M_IceMX._t_TopicMetrics

    _M_IceMX.TopicMetrics = TopicMetrics
    del TopicMetrics

    _M_IceMX.TopicMetricsPrx = TopicMetricsPrx
    del TopicMetricsPrx

if 'SubscriberMetrics' not in _M_IceMX.__dict__:
    _M_IceMX.SubscriberMetrics = Ice.createTempClass()
    class SubscriberMetrics(_M_IceMX.Metrics):
        '''Provides information on IceStorm subscribers.'''
        def __init__(self, id='', total=0, current=0, totalLifetime=0, failures=0, queued=0, outstanding=0, delivered=0):
            _M_IceMX.Metrics.__init__(self, id, total, current, totalLifetime, failures)
            self.queued = queued
            self.outstanding = outstanding
            self.delivered = delivered

        def ice_ids(self, current=None):
            return ('::Ice::Object', '::IceMX::Metrics', '::IceMX::SubscriberMetrics')

        def ice_id(self, current=None):
            return '::IceMX::SubscriberMetrics'

        def ice_staticId():
            return '::IceMX::SubscriberMetrics'
        ice_staticId = staticmethod(ice_staticId)

        def __str__(self):
            return IcePy.stringify(self, _M_IceMX._t_SubscriberMetrics)

        __repr__ = __str__

    _M_IceMX.SubscriberMetricsPrx = Ice.createTempClass()
    class SubscriberMetricsPrx(_M_IceMX.MetricsPrx):

        def checkedCast(proxy, facetOrCtx=None, _ctx=None):
            return _M_IceMX.SubscriberMetricsPrx.ice_checkedCast(proxy, '::IceMX::SubscriberMetrics', facetOrCtx, _ctx)
        checkedCast = staticmethod(checkedCast)

        def uncheckedCast(proxy, facet=None):
            return _M_IceMX.SubscriberMetricsPrx.ice_uncheckedCast(proxy, facet)
        uncheckedCast = staticmethod(uncheckedCast)

    _M_IceMX._t_SubscriberMetricsPrx = IcePy.defineProxy('::IceMX::SubscriberMetrics', SubscriberMetricsPrx)

    _M_IceMX._t_SubscriberMetrics = IcePy.defineClass('::IceMX::SubscriberMetrics', SubscriberMetrics, -1, (), False, False, _M_IceMX._t_Metrics, (), (
        ('queued', (), IcePy._t_int, False, 0),
        ('outstanding', (), IcePy._t_int, False, 0),
        ('delivered', (), IcePy._t_long, False, 0)
    ))
    SubscriberMetrics._ice_type = _M_IceMX._t_SubscriberMetrics

    _M_IceMX.SubscriberMetrics = SubscriberMetrics
    del SubscriberMetrics

    _M_IceMX.SubscriberMetricsPrx = SubscriberMetricsPrx
    del SubscriberMetricsPrx

# End of module IceMX

Ice.sliceChecksums["::IceMX::SubscriberMetrics"] = "ab5eddbb2d0449f94b4808b6cf92552"
Ice.sliceChecksums["::IceMX::TopicMetrics"] = "afc516f773371c41f4f612d9e9629c"
