from abc import ABC, abstractmethod
from newportal.builder import OneArticleBlockBuilder, TwoArticlesBlockBuilder, ThreeArticlesBlockBuilder, \
    SixArticlesBlockBuilder


# STRATEGY
class ArticleSelectionStrategy(ABC):
    @abstractmethod
    def build_block(self, articles):
        pass


class OneArticleSelectionStrategy(ArticleSelectionStrategy):
    def build_block(self, articles):
        builder = OneArticleBlockBuilder()
        builder.build_block(articles)
        return builder


class TwoArticlesSelectionStrategy(ArticleSelectionStrategy):
    def build_block(self, articles):
        builder = TwoArticlesBlockBuilder()
        builder.build_block(articles)
        return builder


class ThreeArticlesSelectionStrategy(ArticleSelectionStrategy):
    def build_block(self, articles):
        builder = ThreeArticlesBlockBuilder()
        builder.build_block(articles)
        return builder


class SixArticlesSelectionStrategy(ArticleSelectionStrategy):
    def build_block(self, articles):
        builder = SixArticlesBlockBuilder()
        builder.build_block(articles)
        return builder


# DIRECTOR
class NewsBlockDirector:
    def __init__(self, strategy: ArticleSelectionStrategy = None):
        self._strategy = strategy

    def set_strategy(self, strategy: ArticleSelectionStrategy):
        self._strategy = strategy

    def construct_block(self, articles):
        if self._strategy:
            return self._strategy.build_block(articles)
        else:
            raise Exception("Стратегію не встановлено. Будь ласка, встановіть стратегію перед створенням блоку.")
