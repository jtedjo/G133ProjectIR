'''
Created on Oct 20, 2016
@author: Rohan Achar
'''
from rtypes.pcc.attributes import dimension, primarykey, predicate
from rtypes.pcc.types.subset import subset
from rtypes.pcc.types.set import pcc_set
from rtypes.pcc.types.projection import projection
from rtypes.pcc.types.impure import impure
from datamodel.search.server_datamodel import Link, ServerCopy

@pcc_set
class JtedjoEthandsJdkang2Link(Link):
    USERAGENTSTRING = "JtedjoEthandsJdkang2"

    @dimension(str)
    def user_agent_string(self):
        return self.USERAGENTSTRING

    @user_agent_string.setter
    def user_agent_string(self, v):
        # TODO (rachar): Make it such that some dimensions do not need setters.
        pass


@subset(JtedjoEthandsJdkang2Link)
class JtedjoEthandsJdkang2UnprocessedLink(object):
    @predicate(JtedjoEthandsJdkang2Link.download_complete, JtedjoEthandsJdkang2Link.error_reason)
    def __predicate__(download_complete, error_reason):
        return not (download_complete or error_reason)


@impure
@subset(JtedjoEthandsJdkang2UnprocessedLink)
class OneJtedjoEthandsJdkang2UnProcessedLink(JtedjoEthandsJdkang2Link):
    __limit__ = 1

    @predicate(JtedjoEthandsJdkang2Link.download_complete, JtedjoEthandsJdkang2Link.error_reason)
    def __predicate__(download_complete, error_reason):
        return not (download_complete or error_reason)

@projection(JtedjoEthandsJdkang2Link, JtedjoEthandsJdkang2Link.url, JtedjoEthandsJdkang2Link.download_complete)
class JtedjoEthandsJdkang2ProjectionLink(object):
    pass
