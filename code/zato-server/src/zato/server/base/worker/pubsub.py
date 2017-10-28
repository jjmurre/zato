# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class PubSub(WorkerImpl):
    """ Publish/subscribe-related functionality for worker objects.
    """

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_CREATE(self, msg):
        self.pubsub.create_topic(msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.pubsub.edit_topic(del_name, msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(self, msg):
        self.pubsub.delete_topic(msg.id)

# ################################################################################################################################
