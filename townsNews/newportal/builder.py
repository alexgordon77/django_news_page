from abc import ABC, abstractmethod
import random
from newportal.observer import NewsBlockSubject, Observer


# BUILDER
class NewsBlockBuilder(ABC):
    def __init__(self, request=None):
        self._block = {}
        self.subject = NewsBlockSubject(self._block, request)

    @abstractmethod
    def build_block(self, articles) -> None:
        pass

    def get_block(self):
        return self._block

    def attach_observer(self, observer: Observer):
        self.subject.attach(observer)

    def notify_observers(self):
        self.subject.notify()


class OneArticleBlockBuilder(NewsBlockBuilder):
    def __init__(self, request=None):
        super().__init__(request)

    def build_block(self, articles):
        if articles:
            selected_article = random.choice(articles)
            self._block['one_article_block'] = selected_article
            articles.remove(selected_article)
        self.notify_observers()


class TwoArticlesBlockBuilder(NewsBlockBuilder):
    def __init__(self, request=None):
        super().__init__(request)

    def build_block(self, articles):
        if len(articles) >= 2:
            selected_articles = random.sample(articles, 2)
            self._block['two_articles_block'] = selected_articles
            for article in selected_articles:
                articles.remove(article)
        self.notify_observers()


class ThreeArticlesBlockBuilder(NewsBlockBuilder):
    def __init__(self, request=None):
        super().__init__(request)

    def build_block(self, articles):
        if len(articles) >= 3:
            selected_articles = random.sample(articles, 3)
            self._block['three_articles_block'] = selected_articles
            for article in selected_articles:
                articles.remove(article)
        self.notify_observers()


class SixArticlesBlockBuilder(NewsBlockBuilder):
    def __init__(self, request=None):
        super().__init__(request)

    def build_block(self, articles):
        selected_articles = self._select_articles(articles, 6)

        self._block['six_articles_block'] = selected_articles[:3]

        # Додаємо 'six_articles_block2' тільки якщо є хоча б 4 статті
        if len(selected_articles) > 3:
            self._block['six_articles_block2'] = selected_articles[3:]

        # Видаляємо використані статті з оригінального списку
        for article in selected_articles:
            articles.remove(article)

        self.notify_observers()

    def _select_articles(self, articles, n):
        return random.sample(articles, min(len(articles), n))
