from django.utils.translation import ugettext_lazy as _

COMMENT, MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED = range(6)

COMMENT_ACTION = (
    (COMMENT, _("comment")),
    (MOVED, _("topic moved")),
    (CLOSED, _("topic closed")),
    (UNCLOSED, _("topic unclosed")),
    (PINNED, _("topic pinned")),
    (UNPINNED, _("topic unpinned")),
)
