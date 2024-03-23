import string
import random
from drf_spirit.models import Category


def word_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class CategoryFactory(object):
    def __init__(self, size=None, **kwargs):
        if size is not None:
            self.data = self.create_batch(size, **kwargs)
        else:
            self.data = self._create(**kwargs)

    def _create(self, **kwargs):
        title = word_generator()
        return Category.objects.create(title=title, **kwargs)

    def _create_batch(self, size=2, **kwargs):
        categories = [self._create(**kwargs) for _ in range(size)]
        return categories
