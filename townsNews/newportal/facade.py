import ast
import os
from collections import Counter
from datetime import date, timedelta
from newportal.builder_facade import BuildersFacadeOneThree, BuildersFacadeSix, BuildersFacadeTwo
from newportal.models import Author, Article, ProhibitedWord
from newportal.observer_facade import ObserverFacadeError, ObserverFacadeActivity, ObserverFacadeTracker, \
    ObserverFacadeWord, ObserverFacadeCount
from newportal.strategy_facade import StrategiesFacadeOneThree, StrategiesFacadeTwo, StrategiesFacadeSix


# MAIN FACADES
# Головний фасад для спостерігачів помилок
class NewsFacadeError:
    def __init__(self, request,
                 observer_facade: ObserverFacadeError = None,
                 builders_facade_one_three: BuildersFacadeOneThree = None,
                 builders_facade_two: BuildersFacadeTwo = None,
                 builders_facade_six: BuildersFacadeSix = None,
                 strategies_facade_one_three: StrategiesFacadeOneThree = None,
                 strategies_facade_two: StrategiesFacadeTwo = None,
                 strategies_facade_six: StrategiesFacadeSix = None) -> None:
        self.observer_facade = observer_facade or ObserverFacadeError()
        self.builders_facade_one_three = builders_facade_one_three or BuildersFacadeOneThree(request)
        self.builders_facade_two = builders_facade_two or BuildersFacadeTwo(request)
        self.builders_facade_six = builders_facade_six or BuildersFacadeSix(request)
        self.strategies_facade_one_three = strategies_facade_one_three or StrategiesFacadeOneThree()
        self.strategies_facade_two = strategies_facade_two or StrategiesFacadeTwo()
        self.strategies_facade_six = strategies_facade_six or StrategiesFacadeSix()

    def build_and_notify(self, articles):
        self.observer_facade.attach_observers()

        blocks = {}

        strategy_one = self.strategies_facade_one_three.select_strategy('one_article')
        builder_one = strategy_one.build_block(articles)
        blocks['one_article_block'] = builder_one.get_block()
        strategy_two = self.strategies_facade_two.select_strategy('two_articles')
        builder_two = strategy_two.build_block(articles)
        blocks['two_articles_block'] = builder_two.get_block()
        strategy_three = self.strategies_facade_one_three.select_strategy('three_articles')
        builder_three = strategy_three.build_block(articles)
        blocks['three_articles_block'] = builder_three.get_block()
        strategy_six = self.strategies_facade_six.select_strategy('six_articles')
        builder_six = strategy_six.build_block(articles)
        blocks.update(builder_six.get_block())

        self.observer_facade.notify_observers()

        return blocks

    def get_errors(self):
        unique_errors = set()

        try:
            with open('errors.txt', 'r') as txt_file:
                for line in txt_file:
                    line = line.strip()
                    if line:
                        unique_errors.add(line)
        except FileNotFoundError:
            return ["Файл з помилками не знайдено."]

        if not unique_errors:
            return ["Наразі немає актуальних помилок."]

        return list(unique_errors)

    def clean_errors(self, errors):
        cleaned_errors = []
        for error in errors:
            cleaned_error = error.strip(", ").strip()
            if cleaned_error:
                cleaned_errors.append(cleaned_error)
        return list(set(cleaned_errors))


# Головний фасад для спостерігачів активності
class NewsFacadeActivity:
    def __init__(self, request,
                 observer_facade: ObserverFacadeActivity = None,
                 builders_facade_one_three: BuildersFacadeOneThree = None,
                 builders_facade_two: BuildersFacadeTwo = None,
                 builders_facade_six: BuildersFacadeSix = None,
                 strategies_facade_one_three: StrategiesFacadeOneThree = None,
                 strategies_facade_two: StrategiesFacadeTwo = None,
                 strategies_facade_six: StrategiesFacadeSix = None) -> None:
        self.request = request
        self.observer_facade = observer_facade or ObserverFacadeActivity()
        self.builders_facade_one_three = builders_facade_one_three or BuildersFacadeOneThree(request)
        self.builders_facade_two = builders_facade_two or BuildersFacadeTwo(request)
        self.builders_facade_six = builders_facade_six or BuildersFacadeSix(request)
        self.strategies_facade_one_three = strategies_facade_one_three or StrategiesFacadeOneThree()
        self.strategies_facade_two = strategies_facade_two or StrategiesFacadeTwo()
        self.strategies_facade_six = strategies_facade_six or StrategiesFacadeSix()

    def build_and_notify(self, articles):
        self.observer_facade.attach_observers()

        blocks = {}
        strategy_one = self.strategies_facade_one_three.select_strategy('one_article')
        blocks['one_article_block'] = strategy_one.build_block(articles).get_block()
        strategy_two = self.strategies_facade_two.select_strategy('two_articles')
        blocks['two_articles_block'] = strategy_two.build_block(articles).get_block()
        strategy_three = self.strategies_facade_one_three.select_strategy('three_articles')
        blocks['three_articles_block'] = strategy_three.build_block(articles).get_block()
        strategy_six = self.strategies_facade_six.select_strategy('six_articles')
        blocks.update(strategy_six.build_block(articles).get_block())

        self.observer_facade.notify_observers()
        return blocks

    def generate_activity_report(self):
        author_activity = Counter()
        try:
            with open('author_activity.log', 'r') as file:
                for line in file:
                    if "Активність авторів:" in line:
                        data = line.split("Активність авторів:")[-1].strip()
                        activity_data = ast.literal_eval(data)
                        author_activity.update(activity_data)
        except FileNotFoundError:
            author_activity = {"Файл 'author_activity.log' не знайдено": 0}

        # Завантажуємо авторів із бази даних
        authors = Author.objects.all()
        name_to_author = {author.name.strip(): {'id': author.id, 'name': author.name} for author in authors}

        # Формуємо список авторів із ID
        sorted_author_activity = [
            {
                'id': name_to_author.get(name, {}).get('id', None),  # ID автора
                'name': name,  # Ім'я автора
                'count': count,  # Кількість статей
            }
            for name, count in sorted(author_activity.items(), key=lambda x: x[1], reverse=True)
            if name in name_to_author  # Фільтруємо авторів, які є в базі
        ]

        block_views = Counter()
        try:
            with open('user_activity.log', 'r') as file:
                for line in file:
                    if "переглянув блок новин" in line:
                        block = line.strip().split("переглянув блок новин.")[0].split()[-1]
                        block_views[block] += 1
        except FileNotFoundError:
            block_views = {"Файл 'user_activity.log' не знайдено": 0}

        sorted_block_views = sorted(block_views.items(), key=lambda x: x[1], reverse=True)

        return {
            'sorted_author_activity': sorted_author_activity,
            'sorted_block_views': sorted_block_views,
        }


# Головний фасад для спостерігачів трекінгу
class NewsFacadeTracker:
    def __init__(self, request,
                 observer_facade: ObserverFacadeTracker = None,
                 builders_facade_one_three: BuildersFacadeOneThree = None,
                 builders_facade_two: BuildersFacadeTwo = None,
                 builders_facade_six: BuildersFacadeSix = None,
                 strategies_facade_one_three: StrategiesFacadeOneThree = None,
                 strategies_facade_two: StrategiesFacadeTwo = None,
                 strategies_facade_six: StrategiesFacadeSix = None) -> None:
        self.request = request
        self.observer_facade = observer_facade or ObserverFacadeTracker()
        self.builders_facade_one_three = builders_facade_one_three or BuildersFacadeOneThree(request)
        self.builders_facade_two = builders_facade_two or BuildersFacadeTwo(request)
        self.builders_facade_six = builders_facade_six or BuildersFacadeSix(request)
        self.strategies_facade_one_three = strategies_facade_one_three or StrategiesFacadeOneThree()
        self.strategies_facade_two = strategies_facade_two or StrategiesFacadeTwo()
        self.strategies_facade_six = strategies_facade_six or StrategiesFacadeSix()

    def build_and_notify(self, articles):
        self.observer_facade.attach_observers()

        blocks = {}
        strategy_one = self.strategies_facade_one_three.select_strategy('one_article')
        blocks['one_article_block'] = strategy_one.build_block(articles).get_block()
        strategy_two = self.strategies_facade_two.select_strategy('two_articles')
        blocks['two_articles_block'] = strategy_two.build_block(articles).get_block()
        strategy_three = self.strategies_facade_one_three.select_strategy('three_articles')
        blocks['three_articles_block'] = strategy_three.build_block(articles).get_block()
        strategy_six = self.strategies_facade_six.select_strategy('six_articles')
        blocks.update(strategy_six.build_block(articles).get_block())

        self.observer_facade.notify_observers()
        return blocks

    def get_sorted_article_views(self):
        article_views = Counter()

        # Читаємо перегляди з логів
        try:
            with open('popular_articles.log', 'r') as file:
                for line in file:
                    if "Популярні статті:" in line:
                        data = line.split("Популярні статті:")[-1].strip()
                        views_data = ast.literal_eval(data)
                        article_views.update(views_data)
        except FileNotFoundError:
            article_views = {}

        # Завантажуємо статті з бази даних
        articles = Article.objects.all()
        title_to_article = {article.title.strip(): {'id': article.id, 'title': article.title} for article in articles}

        # Формуємо список словників
        sorted_article_views = [
            {
                'id': title_to_article.get(title, {}).get('id', None),
                'title': title,
                'views': count,
            }
            for title, count in sorted(article_views.items(), key=lambda x: x[1], reverse=True)
            if title in title_to_article
        ]

        return sorted_article_views

    def get_sorted_article_saves(self):
        article_saves = Counter()

        # Читаємо збереження з логів
        try:
            with open('article_saves.log', 'r') as file:
                for line in file:
                    if "Статтю" in line and "зберегли" in line:
                        title = line.split("'")[1].strip()
                        saves = int(line.split()[-2])
                        article_saves[title] += saves
        except FileNotFoundError:
            article_saves = {}

        # Завантажуємо статті з бази даних
        articles = Article.objects.all()
        title_to_article = {article.title.strip(): {'id': article.id, 'title': article.title} for article in articles}

        # Формуємо список словників
        sorted_article_saves = [
            {
                'id': title_to_article.get(title, {}).get('id', None),  # ID статті
                'title': title,  # Назва статті
                'saves': count,  # Кількість збережень
            }
            for title, count in sorted(article_saves.items(), key=lambda x: x[1], reverse=True)
            if title in title_to_article
        ]

        return sorted_article_saves


# Головний фасад для спостерігачів заборонених слів та SEO
class NewsFacadeWord:
    def __init__(self, request,
                 observer_facade: ObserverFacadeWord = None,
                 builders_facade_one_three: BuildersFacadeOneThree = None,
                 builders_facade_two: BuildersFacadeTwo = None,
                 builders_facade_six: BuildersFacadeSix = None,
                 strategies_facade_one_three: StrategiesFacadeOneThree = None,
                 strategies_facade_two: StrategiesFacadeTwo = None,
                 strategies_facade_six: StrategiesFacadeSix = None) -> None:
        self.observer_facade = observer_facade or ObserverFacadeWord()
        self.builders_facade_one_three = builders_facade_one_three or BuildersFacadeOneThree(request)
        self.builders_facade_two = builders_facade_two or BuildersFacadeTwo(request)
        self.builders_facade_six = builders_facade_six or BuildersFacadeSix(request)
        self.strategies_facade_one_three = strategies_facade_one_three or StrategiesFacadeOneThree()
        self.strategies_facade_two = strategies_facade_two or StrategiesFacadeTwo()
        self.strategies_facade_six = strategies_facade_six or StrategiesFacadeSix()

    def build_and_notify(self, articles):
        articles_list = list(articles)

        self.observer_facade.attach_observers()

        blocks = {}

        strategy_one = self.strategies_facade_one_three.select_strategy('one_article')
        blocks['one_article_block'] = strategy_one.build_block(articles_list).get_block()

        strategy_two = self.strategies_facade_two.select_strategy('two_articles')
        blocks['two_articles_block'] = strategy_two.build_block(articles_list).get_block()

        strategy_three = self.strategies_facade_one_three.select_strategy('three_articles')
        blocks['three_articles_block'] = strategy_three.build_block(articles_list).get_block()

        strategy_six = self.strategies_facade_six.select_strategy('six_articles')
        blocks.update(strategy_six.build_block(articles_list).get_block())

        self.observer_facade.notify_observers()

        return {
            'blocks': blocks,
            'prohibited_words_data': self.get_prohibited_words_data(),
            'tags_data': self.get_tags_data(),
            'seo_data': self.get_seo_data(),
        }

    def get_prohibited_words_data(self):
        prohibited_words = ProhibitedWord.objects.values_list('word', flat=True)
        prohibited_words_data = []

        articles = Article.objects.all()

        for article in articles:
            found_words = [word for word in prohibited_words if word in article.article_text]
            if found_words:
                prohibited_words_data.append({
                    'id': article.id,
                    'title': article.title,
                    'words': ", ".join(found_words),
                })

        return prohibited_words_data

    def get_tags_data(self):
        tags_data = []
        articles = Article.objects.all().prefetch_related('tags')
        for article in articles:
            tags = ", ".join([tag.name for tag in article.tags.all()])
            tags_data.append({
                'id': article.id,
                'title': article.title,
                'tags': tags,
            })
        return tags_data

    def get_seo_data(self):
        seo_data = []
        seen_titles = set()

        try:
            with open('seo_title_issues.log', 'r') as file:
                for line in file:
                    if "не відповідає SEO-правилам" in line:
                        title = line.split("'")[1]
                        article = Article.objects.filter(title=title).first()
                        if article and article.title not in seen_titles:
                            seo_data.append({
                                'id': article.id,
                                'title': article.title,
                                'seo_check': "Ні"
                            })
                            seen_titles.add(article.title)

            all_articles = Article.objects.all()
            seo_issues_titles = {data['title'] for data in seo_data}

            for article in all_articles:
                if article.title not in seo_issues_titles and article.title not in seen_titles:
                    seo_data.append({
                        'id': article.id,
                        'title': article.title,
                        'seo_check': "Так"
                    })
                    seen_titles.add(article.title)
        except FileNotFoundError:
            pass

        return seo_data


# Головний фасад для спостерігачів підрахунку статей та часу
class NewsFacadeCount:
    def __init__(self, request,
                 observer_facade: ObserverFacadeCount = None,
                 builders_facade_one_three: BuildersFacadeOneThree = None,
                 builders_facade_two: BuildersFacadeTwo = None,
                 builders_facade_six: BuildersFacadeSix = None,
                 strategies_facade_one_three: StrategiesFacadeOneThree = None,
                 strategies_facade_two: StrategiesFacadeTwo = None,
                 strategies_facade_six: StrategiesFacadeSix = None) -> None:
        self.observer_facade = observer_facade or ObserverFacadeCount()
        self.builders_facade_one_three = builders_facade_one_three or BuildersFacadeOneThree(request)
        self.builders_facade_two = builders_facade_two or BuildersFacadeTwo(request)
        self.builders_facade_six = builders_facade_six or BuildersFacadeSix(request)
        self.strategies_facade_one_three = strategies_facade_one_three or StrategiesFacadeOneThree()
        self.strategies_facade_two = strategies_facade_two or StrategiesFacadeTwo()
        self.strategies_facade_six = strategies_facade_six or StrategiesFacadeSix()
        self.creation_logs_file = os.path.join(os.path.dirname(__file__), "creation_times.txt")

    def build_and_notify(self, articles):
        self.observer_facade.attach_observers()

        blocks = {}

        strategy_one = self.strategies_facade_one_three.select_strategy('one_article')
        blocks['one_article_block'] = strategy_one.build_block(articles).get_block()
        strategy_two = self.strategies_facade_two.select_strategy('two_articles')
        blocks['two_articles_block'] = strategy_two.build_block(articles).get_block()
        strategy_three = self.strategies_facade_one_three.select_strategy('three_articles')
        blocks['three_articles_block'] = strategy_three.build_block(articles).get_block()
        strategy_six = self.strategies_facade_six.select_strategy('six_articles')
        blocks.update(strategy_six.build_block(articles).get_block())

        self.observer_facade.notify_observers()

        return blocks

    def get_creation_logs(self):
        logs = []
        if os.path.exists(self.creation_logs_file):
            with open(self.creation_logs_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if ": " in line:
                        block_type, time_info = line.split(": ", 1)
                        logs.append({
                            "block_type": block_type,
                            "time_info": time_info
                        })
        return logs

    def get_updates(self):
        last_7_days = date.today() - timedelta(days=180)
        recent_articles = Article.objects.filter(date_of_publication__gte=last_7_days)

        updates = []
        for article in recent_articles:
            updates.append({
                "id": article.id,  # Додаємо ID статті
                "timestamp": article.date_of_publication.strftime("%Y-%m-%d"),
                "message": article.title,  # Назва статті
            })

        return updates

    def get_overview_context(self):
        return {
            "creation_logs": self.get_creation_logs(),
            "updates": self.get_updates(),
        }


class FacadeMeta(type):
    FACADE_MAP = {
        "error": NewsFacadeError,
        "activity": NewsFacadeActivity,
        "tracker": NewsFacadeTracker,
        "word": NewsFacadeWord,
        "count": NewsFacadeCount,
    }

    def __call__(cls, facade_type, request, *args, **kwargs):
        facade_class = cls.FACADE_MAP.get(facade_type.lower())
        if facade_class is None:
            raise ValueError(f"Unknown facade type: {facade_type}")
        return facade_class(request, *args, **kwargs)


class Facade(metaclass=FacadeMeta):
    pass
