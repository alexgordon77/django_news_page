from newportal.builder import OneArticleBlockBuilder, ThreeArticlesBlockBuilder, TwoArticlesBlockBuilder, \
    SixArticlesBlockBuilder


# BUILDER FACADE ONE-THREE
class BuildersFacadeOneThree:
    def __init__(self, request,
                 one_article_block: OneArticleBlockBuilder = None,
                 three_articles_block: ThreeArticlesBlockBuilder = None) -> None:
        self.one_article_block = one_article_block or OneArticleBlockBuilder(request)
        self.three_articles_block = three_articles_block or ThreeArticlesBlockBuilder(request)

    def build_one_article_block(self, articles) -> dict:
        self.one_article_block.build_block(articles)
        return self.one_article_block.get_block()

    def build_three_articles_block(self, articles) -> dict:
        self.three_articles_block.build_block(articles)
        return self.three_articles_block.get_block()


# BUILDER FACADE TWO
class BuildersFacadeTwo:
    def __init__(self, request, two_articles_block: TwoArticlesBlockBuilder = None) -> None:
        self.two_articles_block = two_articles_block or TwoArticlesBlockBuilder(request)

    def build_two_articles_block(self, articles) -> dict:
        self.two_articles_block.build_block(articles)
        return self.two_articles_block.get_block()


# BUILDER FACADE SIX
class BuildersFacadeSix:
    def __init__(self, request, six_articles_block: SixArticlesBlockBuilder = None) -> None:
        self.six_articles_block = six_articles_block or SixArticlesBlockBuilder(request)

    def build_six_articles_block(self, articles) -> dict:
        self.six_articles_block.build_block(articles)
        return self.six_articles_block.get_block()