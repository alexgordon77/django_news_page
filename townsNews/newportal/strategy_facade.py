from newportal.strategy import OneArticleSelectionStrategy, ThreeArticlesSelectionStrategy, ArticleSelectionStrategy, \
    TwoArticlesSelectionStrategy, SixArticlesSelectionStrategy


# STRATEGY FACADE ONE-THREE
class StrategiesFacadeOneThree:
    def __init__(self,
                 one_article_strategy: OneArticleSelectionStrategy = None,
                 three_articles_strategy: ThreeArticlesSelectionStrategy = None) -> None:
        self.one_article_strategy = one_article_strategy or OneArticleSelectionStrategy()
        self.three_articles_strategy = three_articles_strategy or ThreeArticlesSelectionStrategy()

    def select_strategy(self, strategy_type: str) -> ArticleSelectionStrategy:
        if strategy_type == 'one_article':
            return self.one_article_strategy
        elif strategy_type == 'three_articles':
            return self.three_articles_strategy
        else:
            raise ValueError(f"Невідома стратегія: {strategy_type}")


# STRATEGY FACADE TWO
class StrategiesFacadeTwo:
    def __init__(self, two_articles_strategy: TwoArticlesSelectionStrategy = None) -> None:
        self.two_articles_strategy = two_articles_strategy or TwoArticlesSelectionStrategy()

    def select_strategy(self, strategy_type: str) -> ArticleSelectionStrategy:
        if strategy_type == 'two_articles':
            return self.two_articles_strategy
        else:
            raise ValueError(f"Невідома стратегія: {strategy_type}")


# STRATEGY FACADE SIX
class StrategiesFacadeSix:
    def __init__(self, six_articles_strategy: SixArticlesSelectionStrategy = None) -> None:
        self.six_articles_strategy = six_articles_strategy or SixArticlesSelectionStrategy()

    def select_strategy(self, strategy_type: str) -> ArticleSelectionStrategy:
        if strategy_type == 'six_articles':
            return self.six_articles_strategy
        else:
            raise ValueError(f"Невідома стратегія: {strategy_type}")